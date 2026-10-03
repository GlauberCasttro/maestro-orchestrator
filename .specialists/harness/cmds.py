"""cmds — comandos de cs-state (cada um monta eventos e passa por engine.commit)."""
import copy
import os
import re

import engine
import hcore
from engine import Event, Refused, ref, transition, latest_deleg
from hcore import StateError


def _now():
    return hcore.now_iso()


def _ctx_ro(root, actor="lead"):
    return engine.Ctx(root, hcore.load_board(root), actor)


def _task(ctx, tid):
    t = ctx.find("task", tid)
    if t is None:
        raise Refused("task %s inexistente (cs-state status lista as tasks)" % tid)
    return t


def _deleg(ctx, tid, states=None):
    t = _task(ctx, tid)
    d = latest_deleg(t)
    if d is None:
        raise Refused("task %s sem delegação" % tid)
    if states and d["state"] not in states:
        raise Refused("delegação %s está em %s; esperado %s" % (d["id"], d["state"], "|".join(states)),
                      hint=engine.hint_for(ctx, "deleg", d))
    return t, d


def resolve_task_id(ctx, ident):
    """Aceita id de task ou de delegação."""
    if ctx.find("task", ident):
        return ident
    t = hcore.task_of_deleg(ctx.board, ident)
    if t:
        return t["id"]
    raise Refused("%s não é task nem delegação" % ident)


def _block_if_exhausted(ctx, task, deleg, to):
    if to != "REJECTED":
        return []
    import autonomy
    cap = autonomy.retry_cap(ctx, int(ctx.M["limits"]["max_retries"]))
    if int(deleg.get("retries") or 0) >= cap:
        return [["set", ref("task", task["id"]), "status", "BLOCKED"],
                ["set", ref("task", task["id"]), "block_reason", "tentativas esgotadas (%d retries): escalar ou reroute" % cap]]
    return []


# ================================================================ processo
def add_epic(root, actor, title, objective, metric=None):
    def build(ctx):
        eid = engine.next_id(ctx.board, "epic", "EPIC")
        e = {"id": eid, "state": "PROPOSED", "title": title, "objective": objective, "metric": metric, "created_at": _now()}
        return [Event("epic.add", eid, [["create", "epic", None, e]])]
    return engine.commit(root, actor, build)


def add_feature(root, actor, epic, title, spec, accept_cmds, accept_files=None):
    def build(ctx):
        if not ctx.find("epic", epic):
            raise Refused("épico %s inexistente" % epic)
        fid = engine.next_id(ctx.board, "feature", "FEAT")
        f = {"id": fid, "state": "BACKLOG", "epic": epic, "title": title, "spec": spec, "acceptance": list(accept_cmds or []),
             "acceptance_files": list(accept_files or []), "created_at": _now()}
        return [Event("feature.add", fid, [["create", "feature", None, f]])]
    return engine.commit(root, actor, build)


def add_sprint(root, actor, goal, budget):
    def build(ctx):
        sid = engine.next_id(ctx.board, "sprint", "SPRINT", 2)
        s = {"id": sid, "state": "PLANNED", "goal": goal, "budget": budget, "stories": [], "created_at": _now()}
        return [Event("sprint.add", sid, [["create", "sprint", None, s]])]
    return engine.commit(root, actor, build)


def add_story(root, actor, stype, feature, title, **kw):
    if stype not in ("us", "bug", "fix"):
        raise Refused("--type deve ser us|bug|fix")

    def build(ctx):
        if not ctx.find("feature", feature):
            raise Refused("feature %s inexistente" % feature)
        if kw.get("reopens"):
            old = ctx.find("story", kw["reopens"])
            if stype != "bug" or not old or old["state"] != "DONE":
                raise Refused("reabrir exige story DONE e uma nova story --type bug")
        sid = engine.next_id(ctx.board, "story", stype.upper())
        s = {"id": sid, "type": stype, "state": "BACKLOG", "feature": feature, "title": title, "findings": [], "created_at": _now()}
        for k in ("as_a", "i_want", "so_that", "criteria", "repro", "failing_test", "severity", "environment", "fixes",
                  "proving_test", "regression", "reopens"):
            if kw.get(k) not in (None, [], ""):
                s[k] = kw[k]
        return [Event("story.add", sid, [["create", "story", None, s]])]
    return engine.commit(root, actor, build)


def level_transition(root, actor, kind, eid, tname, a=None):
    a = dict(a or {})

    def build(ctx):
        ent = ctx.find(kind, eid)
        extra = None
        if kind == "story" and tname == "requeue":
            def extra(to, probs):
                return [["append", ref("story", eid), "findings", {"at": _now(), "reason": a.get("reason")}]]
        if kind == "story" and tname == "reject":
            def extra(to, probs):
                return [["append", ref("story", eid), "findings", {"at": _now(), "reason": a.get("reason"), "rejected": True}]]
        if kind == "sprint" and tname == "plan":
            def extra(to, probs):
                cur = list(ent.get("stories") or [])
                return [["set", ref("sprint", eid), "stories", cur + [s for s in a.get("add") or [] if s not in cur]]]
        if kind == "sprint" and tname == "start":
            def extra(to, probs):
                return [["set", ref("sprint", eid), "started_at", _now()]]
        if kind == "sprint" and tname == "review":
            def extra(to, probs):
                delivered = [s for s in ent.get("stories") or [] if (ctx.find("story", s) or {}).get("state") == "DONE"]
                undone = [s for s in ent.get("stories") or [] if s not in delivered]
                ts = [t for t in ctx.board["tasks"] if t.get("sprint") == eid or t.get("story") in (ent.get("stories") or [])]
                metrics = {"stories": len(ent.get("stories") or []), "delivered": len(delivered),
                           "attempts": sum(t.get("attempts", 0) for t in ts),
                           "accepted_tasks": sum(1 for t in ts if t["status"] == "ACCEPTED")}
                return [["set", ref("sprint", eid), "review", {"at": _now(), "delivered": delivered,
                                                                "returned": [{"id": s, "reason": a.get("reason") or "não entregue no sprint"} for s in undone],
                                                                "metrics": metrics}]]
        if kind in ("feature", "story") and a.get("_runs") is None:
            pass
        ev = transition(ctx, kind, eid, tname, a, extra)
        if a.get("_runs"):
            ev.data["runs"] = [{k: r[k] for k in ("cmd", "exit_code", "output_sha256", "duration_s")} for r in a["_runs"]]
        evs = [ev]
        if kind == "sprint" and tname == "close":
            for item in (ent.get("review") or {}).get("returned") or []:
                s = ctx.find("story", item["id"])
                if s and s["state"] not in ("BACKLOG", "DONE"):
                    if s["state"] == "REJECTED" or s["state"] in ("READY", "IN_PROGRESS", "IN_REVIEW"):
                        evs.append(Event("story.requeue", s["id"], [
                            ["set", ref("story", s["id"]), "state", "BACKLOG"],
                            ["append", ref("story", s["id"]), "findings", {"at": _now(), "reason": item["reason"], "sprint": eid}]],
                            {"args": {"reason": item["reason"]}}))
        if kind == "story" and tname == "start":
            f = ctx.find("feature", ent.get("feature"))
            if f and f["state"] == "READY":
                evs.append(Event("feature.start", f["id"], [["set", ref("feature", f["id"]), "state", "IN_PROGRESS"]]))
        return evs
    return engine.commit(root, actor, build)


# ================================================================ M1
def session_start(root, actor, request, mode="assistido"):
    def build(ctx):
        act = [s["id"] for s in ctx.board["sessions"] if s["state"] != "IDLE"]
        if act:
            raise Refused("já existe sessão ativa: %s (feche com cs-state session close)" % ", ".join(act))
        sid = engine.next_id(ctx.board, "session", "S")
        s = {"id": sid, "state": "TRIAGE", "request": request, "mode": mode, "class": None, "why": None,
             "assumptions": [], "confirmation": None, "reviews": [], "created_at": _now()}
        return [Event("session.start", sid, [["create", "session", None, s]])]
    return engine.commit(root, actor, build)


def active_session(ctx):
    for s in reversed(ctx.board["sessions"]):
        if s["state"] != "IDLE":
            return s
    return None


def session_cmd(root, actor, tname, a=None):
    a = dict(a or {})

    def build(ctx):
        s = active_session(ctx)
        if s is None:
            raise Refused("nenhuma sessão ativa", hint="cs-state session start --request '<pedido do usuário>'")

        def extra(to, probs):
            ops = []
            if tname == "triage":
                ops += [["set", ref("session", s["id"]), "class", a["class"]], ["set", ref("session", s["id"]), "why", a["why"]]]
                for x in a.get("assume") or []:
                    ops.append(["append", ref("session", s["id"]), "assumptions", x])
            if tname == "confirm":
                ops.append(["set", ref("session", s["id"]), "confirmation", {"note": a["note"], "at": _now()}])
            if tname == "review":
                ops.append(["append", ref("session", s["id"]), "reviews", {"by": a["by"], "verdict": a["verdict"],
                                                                         "findings": a["findings"], "at": _now()}])
            return ops
        return [transition(ctx, "session", s["id"], tname, a, extra)]
    return engine.commit(root, actor, build)


# ================================================================ tasks / M2
def _ac_list(items):
    out = []
    for i, it in enumerate(items or []):
        if isinstance(it, dict):
            out.append(it)
            continue
        parts = [p.strip() for p in it.split("|")]
        if len(parts) == 2:
            parts = ["AC-%d" % (i + 1)] + parts
        if len(parts) != 3:
            raise Refused("--ac deve ser 'AC-n|critério|verified_by' (verified_by: verification_command|test:<id>|reviewer)")
        out.append({"id": parts[0], "criterion": parts[1], "verified_by": parts[2]})
    return out


def add_task(root, actor, spec, ready=False):
    """spec: dict no formato de brief-schema.json5 (campos do brief; o motor preenche o resto)."""
    spec = copy.deepcopy(spec)

    def build(ctx):
        story = ctx.find("story", spec.get("story") or "")
        if not story:
            raise Refused("toda task pertence a uma Story: --story US-n|BUG-n|FIX-n")
        if story["state"] in ("DONE", "REJECTED", "BACKLOG"):
            raise Refused("story %s em %s: só READY/IN_PROGRESS recebe task (DoR primeiro)" % (story["id"], story["state"]))
        sess = active_session(ctx)
        sid = spec.get("session") or (sess or {}).get("id")
        tid = spec.get("id")
        if not tid:
            seq = len(ctx.board["tasks"]) + 1
            typ = (spec.get("type") or "").upper()
            tid = "TASK-%s-%03d-%s" % (spec.get("sprint") or "00", seq, typ) if typ in engine.TASK_TYPES else "T-%d" % seq
        if not engine.ID_RE.match(tid) or ctx.find("task", tid):
            raise Refused("id de task inválido ou repetido: %s" % tid)
        ap = [hcore.norm_rel(p) for p in spec.get("allowed_paths") or []]
        pp = [hcore.norm_rel(p) for p in spec.get("protected_paths") or []]
        br = dict(spec.get("briefing") or {})
        br["invariants"] = engine.required_invariants(ctx, ap) if ap else []
        br.setdefault("references", [])
        br.setdefault("scope", {"in": [], "out": []})
        t = {
            "id": tid, "story": story["id"], "sprint": spec.get("sprint"), "session": sid, "agent": spec["agent"],
            "title": spec.get("title", ""), "goal": spec.get("goal", ""), "class": spec.get("class"),
            "wave": int(spec.get("wave") or 1), "depends_on": list(spec.get("depends_on") or []),
            "flags": spec.get("flags") or {"hot_path": False, "security_gate": False},
            "readonly": bool(spec.get("readonly")),
            "allowed_paths": ap, "protected_paths": pp, "briefing": br,
            "acceptance_criteria": _ac_list(spec.get("acceptance_criteria")), "dod": list(spec.get("dod") or []),
            "verification_command": engine.with_protection(spec.get("verification_command") or "", pp),
            "knowledge_context": knowledge_context(root, spec, ap), "handoff": spec.get("handoff") or {},
            "status": "DRAFT", "attempts": 0, "amendments": [], "submission": None, "reviews": [],
            "gate_report": {"build": None, "verdict": None, "by": None, "at": None},
            "created_at": _now(), "updated_at": _now(),
        }
        d = {"id": "%s.d1" % tid, "agent": t["agent"], "state": "PLANNED", "retries": 0, "created_at": _now()}
        evs = [Event("task.add", tid, [["create", "task", None, t], ["create", "deleg", tid, d]])]
        if ready:
            ctx2 = engine.Ctx(root, copy.deepcopy(ctx.board), actor)
            hcore.apply_ops(ctx2.board, evs[0].ops)
            evs.append(_ready_event(ctx2, t, d))
        return evs
    return engine.commit(root, actor, build)


def knowledge_context(root, spec, ap):
    try:
        import mem
        res = mem.search(root, "%s %s" % (spec.get("title", ""), " ".join(ap)), k=3, paths=ap)
        return [{"id": r["id"], "text": r["text"][:200]} for r in res]
    except Exception:
        return []


def _ready_event(ctx, task, d):
    import router

    def extra(to, probs):
        rec = router.recommend(ctx, task, d, act="dev")
        return [["set", ref("deleg", d["id"]), "route", rec]]
    return transition(ctx, "deleg", d["id"], "ready", {}, extra)


def ready(root, actor, tid):
    def build(ctx):
        t, d = _deleg(ctx, tid, ["PLANNED"])
        return [_ready_event(ctx, t, d)]
    return engine.commit(root, actor, build)


def dispatch(root, actor, ident, model=None, tool_use_id=None, procedencia=None, override_reason=None):
    def build(ctx):
        tid = resolve_task_id(ctx, ident)
        t, d = _deleg(ctx, tid, ["BRIEFED"])
        a = {"model": model, "tool_use_id": tool_use_id, "procedencia": procedencia}

        def extra(to, probs):
            base = engine.git_dirty(ctx.root)
            ops = [["inc", ref("task", tid), "attempts", 1],
                   ["set", ref("deleg", d["id"]), "attempt", t["attempts"] + 1],
                   ["set", ref("deleg", d["id"]), "dispatched_at", _now()],
                   ["set", ref("deleg", d["id"]), "tool_use_id", tool_use_id],
                   ["set", ref("deleg", d["id"]), "model", {"name": model, "procedencia": procedencia or "declarada-no-despacho"}],
                   ["set", ref("deleg", d["id"]), "baseline", base if base is not None else {"__nogit__": True}],
                   ["set", ref("task", tid), "reject_reason", None]]
            s = ctx.find("story", t["story"])
            if s and s["state"] == "READY":
                ops.append(["set", ref("story", s["id"]), "state", "IN_PROGRESS"])
                f = ctx.find("feature", s.get("feature"))
                if f and f["state"] == "READY":
                    ops.append(["set", ref("feature", f["id"]), "state", "IN_PROGRESS"])
            return ops
        return [transition(ctx, "deleg", d["id"], "dispatch", a, extra)]
    return engine.commit(root, actor, build)


def submit(root, actor, tid, submission):
    def build(ctx):
        t, d = _deleg(ctx, resolve_task_id(ctx, tid), ["DISPATCHED"])
        sub = dict(submission)
        sub.setdefault("risks", [])
        sub.setdefault("handoff_notes", "")
        sub.setdefault("abstain", None)
        sub["files_changed"] = [hcore.norm_rel(f) for f in sub.get("files_changed") or []]

        def extra(to, probs):
            s2 = dict(sub)
            s2["attempt"] = t["attempts"]
            s2["at"] = _now()
            return [["set", ref("task", t["id"]), "submission", s2]]
        return [transition(ctx, "deleg", d["id"], "submit", {"submission": sub}, extra)]
    return engine.commit(root, actor, build)


def return_(root, actor, tid, reason="protocol_failure: retorno sem submission"):
    def build(ctx):
        t, d = _deleg(ctx, resolve_task_id(ctx, tid), ["DISPATCHED"])

        def extra(to, probs):
            return [["set", ref("task", t["id"]), "reject_reason", reason]] + _block_if_exhausted(ctx, t, d, to)
        return [transition(ctx, "deleg", d["id"], "return", {"reason": reason}, extra)]
    return engine.commit(root, actor, build)


def verify(root, actor, tid):
    """Duas fases: executa FORA do lock (comando pode demorar), depois confirma sob lock."""
    ctx0 = _ctx_ro(root, actor)
    tid = resolve_task_id(ctx0, tid)
    t0, d0 = _deleg(ctx0, tid, ["RETURNED"])
    timeout = int(ctx0.cfg.get("verify_timeout_s", 900))
    build_run = engine.run_cmd(root, t0["verification_command"], timeout)
    ac_runs = []
    for ac in t0.get("acceptance_criteria") or []:
        vb = ac.get("verified_by") or ""
        if vb.startswith("test:"):
            cmd = engine.resolve_test(ctx0.cfg, vb[5:])
            r = engine.run_cmd(root, cmd, timeout) if cmd else {"exit_code": 127, "cmd": None}
            ac_runs.append({"ac": ac["id"], "test": vb[5:], "cmd": cmd, "exit_code": r["exit_code"],
                            "output_sha256": r.get("output_sha256")})
    files_changed = (t0.get("submission") or {}).get("files_changed") or []
    diff_problems = diff_check(ctx0, t0, d0, files_changed)
    lesson_failures = []
    try:
        import mem
        chk = mem.check(root, t0["agent"], files_changed, run=True)
        lesson_failures = ["lição %s violada: %s (check: %s)" % (f["id"], f["rule"], f.get("check")) for f in chk["failed"]]
    except ImportError:
        pass
    tree_files = sorted(set(files_changed) | set(engine.files_in_scope(root, t0["allowed_paths"])))
    build_run.update({"attempt": t0["attempts"], "tree_sha256": engine.tree_sha(root, tree_files), "tree_files": tree_files})
    gate = {"build": build_run, "ac_tests": ac_runs, "diff_problems": diff_problems, "lesson_failures": lesson_failures}
    os.makedirs(hcore.state_paths(root)["evidence"], exist_ok=True)

    def build(ctx):
        t, d = _deleg(ctx, tid, ["RETURNED"])
        if t["attempts"] != t0["attempts"] or d["id"] != d0["id"]:
            raise Refused("estado mudou durante o verify; rode de novo")

        def extra(to, probs):
            gr = {"build": {k: build_run[k] for k in ("exit_code", "at", "tree_sha256", "command_sha256", "output_sha256",
                                                      "duration_s", "cmd", "attempt", "tree_files", "timed_out")},
                  "ac_tests": ac_runs, "verdict": None, "by": None, "at": None}
            ops = [["set", ref("task", tid), "gate_report", gr]]
            if to == "REJECTED":
                ops.append(["set", ref("task", tid), "reject_reason", "verify: " + "; ".join(probs)[:1500]])
                ops += _block_if_exhausted(ctx, t, d, to)
            return ops
        ev = transition(ctx, "deleg", d["id"], "verify", {"_gate": gate}, extra)
        ev.data["gate"] = {"exit_code": build_run["exit_code"], "output_sha256": build_run["output_sha256"],
                           "tail": build_run["tail"][-600:], "ac_tests": ac_runs, "diff_problems": diff_problems,
                           "lesson_failures": lesson_failures}
        return [ev]
    return engine.commit(root, actor, build)


def diff_check(ctx, task, deleg, files_changed):
    """files_changed × git (desde o baseline do dispatch) × allowed_paths — nada fora."""
    P = []
    dirty = engine.git_dirty(ctx.root)
    if dirty is None:
        if ctx.cfg.get("require_git_diff_check", True):
            return ["não é repositório git: impossível conferir git diff × allowed_paths (fail-closed; config require_git_diff_check)"]
        return []
    base = deleg.get("baseline") or {}
    changed = {p for p, sha in dirty.items() if base.get(p, "__absent__") != sha}
    changed |= {p for p in base if p != "__nogit__" and p not in dirty}
    lead_ok = ctx.cfg.get("lead_write_allow") or []
    others = [x for x in ctx.board["tasks"] for dd in x.get("delegations") or []
              if dd["state"] in ("DISPATCHED", "RETURNED") and dd["id"] != deleg["id"]]
    for f in files_changed:
        if f not in changed:
            P.append("declarado em files_changed mas não alterado segundo git: %s" % f)
    for f in sorted(changed):
        if f.startswith(".specialists/") or hcore.matches_any(f, lead_ok):
            continue
        if hcore.matches_any(f, task["allowed_paths"]):
            if f not in files_changed:
                P.append("alterado e não declarado em files_changed: %s" % f)
            continue
        if any(hcore.matches_any(f, o["allowed_paths"]) for o in others):
            continue
        P.append("alterado FORA de allowed_paths: %s" % f)
    return P


def review(root, actor, tid, by, verdict, findings):
    def build(ctx):
        t, d = _deleg(ctx, resolve_task_id(ctx, tid), ["VERIFIED", "REVIEWED"])

        def extra(to, probs):
            r = {"by": by, "verdict": verdict, "findings": findings, "at": _now(), "attempt": t["attempts"], "delegation": d["id"]}
            gr = dict(t.get("gate_report") or {})
            gr.update({"verdict": verdict, "by": by, "at": r["at"]})
            return [["append", ref("task", t["id"]), "reviews", r], ["set", ref("task", t["id"]), "gate_report", gr]]
        return [transition(ctx, "deleg", d["id"], "review", {"by": by, "verdict": verdict, "findings": findings}, extra)]
    return engine.commit(root, actor, build)


def accept(root, actor, tid):
    def build(ctx):
        t, d = _deleg(ctx, resolve_task_id(ctx, tid), ["VERIFIED", "REVIEWED"])

        def extra(to, probs):
            ops = []
            st = ctx.find("story", t["story"])
            if st and st["state"] == "IN_PROGRESS":
                others = [x for x in ctx.board["tasks"] if x.get("story") == st["id"] and x["id"] != t["id"]]
                if all(x["status"] == "ACCEPTED" for x in others):
                    ops.append(["set", ref("story", st["id"]), "state", "IN_REVIEW"])
            return ops
        return [transition(ctx, "deleg", d["id"], "accept", {}, extra)]
    return engine.commit(root, actor, build)


def reject(root, actor, tid, reason):
    def build(ctx):
        t, d = _deleg(ctx, resolve_task_id(ctx, tid), ["RETURNED", "VERIFIED", "REVIEWED"])

        def extra(to, probs):
            return [["set", ref("task", t["id"]), "reject_reason", reason]] + _block_if_exhausted(ctx, t, d, to)
        return [transition(ctx, "deleg", d["id"], "reject", {"reason": reason}, extra)]
    return engine.commit(root, actor, build)


def retry(root, actor, tid, findings=None):
    def build(ctx):
        t, d = _deleg(ctx, resolve_task_id(ctx, tid), ["REJECTED"])
        f = findings or t.get("reject_reason")

        def extra(to, probs):
            import router
            nd = dict(d, retries=int(d.get("retries") or 0) + 1)
            return [["inc", ref("deleg", d["id"]), "retries", 1],
                    ["append", ref("deleg", d["id"]), "findings_in", {"at": _now(), "findings": f}],
                    ["set", ref("deleg", d["id"]), "route", router.recommend(ctx, t, nd, act="dev")],
                    ["set", ref("deleg", d["id"]), "route_override", None]]
        return [transition(ctx, "deleg", d["id"], "retry", {"findings": findings}, extra)]
    return engine.commit(root, actor, build)


def escalate(root, actor, tid, reason):
    def build(ctx):
        t, d = _deleg(ctx, resolve_task_id(ctx, tid))

        def extra(to, probs):
            return [["set", ref("task", t["id"]), "block_reason", "escalado: " + reason]]
        return [transition(ctx, "deleg", d["id"], "escalate", {"reason": reason}, extra)]
    return engine.commit(root, actor, build)


def reroute(root, actor, tid, agent, reason, allowed_paths=None):
    def build(ctx):
        t, d = _deleg(ctx, resolve_task_id(ctx, tid))
        ap = [hcore.norm_rel(p) for p in allowed_paths] if allowed_paths else None

        def extra(to, probs):
            n = len(t.get("delegations") or []) + 1
            nd = {"id": "%s.d%d" % (t["id"], n), "agent": agent, "state": "PLANNED", "retries": 0, "created_at": _now(),
                  "rerouted_from": d["id"]}
            ops = [["set", ref("task", t["id"]), "agent", agent], ["create", "deleg", t["id"], nd]]
            if ap:
                ops.append(["set", ref("task", t["id"]), "allowed_paths", ap])
                br = dict(t.get("briefing") or {})
                br["invariants"] = engine.required_invariants(ctx, ap)
                ops.append(["set", ref("task", t["id"]), "briefing", br])
            return ops
        return [transition(ctx, "deleg", d["id"], "reroute", {"reason": reason, "agent": agent, "allowed_paths": ap}, extra)]
    return engine.commit(root, actor, build)


def abstain(root, actor, tid, kind, reason):
    def build(ctx):
        t, d = _deleg(ctx, resolve_task_id(ctx, tid))

        def extra(to, probs):
            sub = dict(t.get("submission") or {"files_changed": [], "checks_run": [], "risks": [], "handoff_notes": ""})
            sub["abstain"] = {"kind": kind, "reason": reason, "at": _now()}
            return [["set", ref("task", t["id"]), "submission", sub],
                    ["append", ref("task", t["id"]), "abstentions", {"kind": kind, "reason": reason, "at": _now(), "delegation": d["id"]}]]
        return [transition(ctx, "deleg", d["id"], "abstain", {"reason": reason, "abstain_kind": kind}, extra)]
    return engine.commit(root, actor, build)


def delegate(root, actor, tid):
    """Nova delegação PLANNED depois de ABSTAINED (spec corrigida com amend)."""
    def build(ctx):
        t = _task(ctx, tid)
        d = latest_deleg(t)
        if d and d["state"] not in ("ABSTAINED",):
            raise Refused("nova delegação só após ABSTAINED (atual %s)" % d["state"])
        n = len(t.get("delegations") or []) + 1
        nd = {"id": "%s.d%d" % (t["id"], n), "agent": t["agent"], "state": "PLANNED", "retries": 0, "created_at": _now()}
        return [Event("delegation.create", nd["id"], [["create", "deleg", t["id"], nd]])]
    return engine.commit(root, actor, build)


AMENDABLE = ("title", "goal", "allowed_paths", "protected_paths", "verification_command", "acceptance_criteria",
             "dod", "depends_on", "wave", "briefing", "handoff", "flags")


def amend(root, actor, tid, field, after, reason, found_by=None):
    """Correção formal do brief (evento), nunca edição silenciosa. field pode ser pontuado:
    acceptance_criteria.AC-2 | briefing.scope.out | allowed_paths ..."""
    if not reason:
        raise Refused("--reason obrigatório")

    def build(ctx):
        t = _task(ctx, tid)
        top = field.split(".")[0]
        if top not in AMENDABLE:
            raise Refused("campo não emendável: %s (permitidos: %s)" % (field, ", ".join(AMENDABLE)))
        new_t = copy.deepcopy(t)
        before = _set_dotted(new_t, field, after)
        if top in ("allowed_paths", "protected_paths"):
            new_t[top] = [hcore.norm_rel(p) for p in new_t[top]]
        if top in ("verification_command", "protected_paths"):
            new_t["verification_command"] = engine.with_protection(new_t["verification_command"], new_t.get("protected_paths") or [])
        if top == "allowed_paths":
            br = dict(new_t.get("briefing") or {})
            br["invariants"] = engine.required_invariants(ctx, new_t["allowed_paths"])
            new_t["briefing"] = br
        d = latest_deleg(t)
        if d and d["state"] not in ("PLANNED",):
            probs = engine.brief_problems(ctx, new_t, d["agent"])
            if probs:
                raise Refused(["emenda deixaria o brief inválido:"] + probs)
        ops = []
        for k in set([top, "verification_command", "briefing"]):
            if new_t.get(k) != t.get(k):
                ops.append(["set", ref("task", tid), k, new_t.get(k)])
        ops.append(["append", ref("task", tid), "amendments", {"at": _now(), "by": actor, "field": field, "before": before,
                                                               "after": after, "reason": reason, "found_by": found_by}])
        return [Event("task.amend", tid, ops, {"args": {"field": field, "reason": reason}})]
    return engine.commit(root, actor, build)


def _set_dotted(obj, path, value):
    parts = path.split(".")
    cur = obj
    for i, p in enumerate(parts[:-1]):
        if isinstance(cur, list):
            cur = _list_by_id(cur, p)
        else:
            cur = cur.setdefault(p, {})
    last = parts[-1]
    if isinstance(cur, list):
        for i, it in enumerate(cur):
            if isinstance(it, dict) and it.get("id") == last:
                before = copy.deepcopy(it)
                if isinstance(value, dict):
                    cur[i] = dict(value, id=last)
                else:
                    cur[i]["criterion"] = value
                return before
        cur.append(dict(value, id=last) if isinstance(value, dict) else {"id": last, "criterion": value,
                                                                        "verified_by": "reviewer"})
        return None
    before = copy.deepcopy(cur.get(last))
    cur[last] = value
    return before


def _list_by_id(lst, ident):
    for it in lst:
        if isinstance(it, dict) and it.get("id") == ident:
            return it
    raise Refused("item %s não encontrado" % ident)


def override_model(root, actor, ident, model, reason):
    def build(ctx):
        tid = resolve_task_id(ctx, ident)
        t, d = _deleg(ctx, tid, ["BRIEFED", "REJECTED"])
        if not reason:
            raise Refused("override exige --reason")
        return [Event("delegation.override_model", d["id"], [
            ["set", ref("deleg", d["id"]), "route_override", {"model": model, "reason": reason, "at": _now(), "by": actor}]],
            {"args": {"model": model, "reason": reason}})]
    return engine.commit(root, actor, build)
