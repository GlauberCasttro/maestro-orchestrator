#!/usr/bin/env python3
"""cs-state — único dono das transições (épico, feature, sprint, story, sessão M1, delegação M2, task M3).

Raiz: --root > $CLAUDE_PROJECT_DIR > $CS_ROOT (nunca o diretório do script). Saída curta; recusa com
mensagem acionável (exit 1); estado ausente/incoerente → exit 2.
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
for _p in (HERE, os.path.join(os.path.dirname(os.path.dirname(HERE)), "memory")):
    if os.path.isdir(_p) and _p not in sys.path:
        sys.path.insert(0, _p)

import hcore  # noqa: E402
import j5  # noqa: E402
import engine  # noqa: E402
import cmds  # noqa: E402
import views  # noqa: E402

SEVERITY_ALIAS = {"critica": "critical", "crítica": "critical", "alta": "high", "media": "medium", "média": "medium",
                  "baixa": "low"}


def _csv(vals):
    out = []
    for v in vals or []:
        out.extend(x.strip() for x in v.split(",") if x.strip())
    return out


def _criteria(items):
    out = []
    for i, it in enumerate(items or []):
        parts = [p.strip() for p in it.split("|")]
        if len(parts) == 2:
            parts = ["AC-%d" % (i + 1)] + parts
        if len(parts) != 3:
            raise hcore.Refused("--criterion deve ser 'AC-n|Dado ... Quando ... Então ...|<test id>'")
        out.append({"id": parts[0], "gherkin": parts[1], "test": parts[2]})
    return out


def build_parser():
    ap = argparse.ArgumentParser(prog="cs-state", description=__doc__.splitlines()[0])
    ap.add_argument("--root")
    ap.add_argument("--actor", default=os.environ.get("CS_ACTOR", "lead"))
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("init")
    add = sub.add_parser("add").add_subparsers(dest="what")
    e = add.add_parser("epic")
    e.add_argument("--title", required=True)
    e.add_argument("--objective", required=True)
    e.add_argument("--metric")
    f = add.add_parser("feature")
    f.add_argument("--epic", required=True)
    f.add_argument("--title", required=True)
    f.add_argument("--spec")
    f.add_argument("--accept-cmd", action="append", default=[])
    f.add_argument("--accept-file", action="append", default=[])
    sp = add.add_parser("sprint")
    sp.add_argument("--goal", required=True)
    sp.add_argument("--budget", default="")
    st = add.add_parser("story")
    st.add_argument("--type", required=True, choices=["us", "bug", "fix"])
    st.add_argument("--feature")
    st.add_argument("--title", required=True)
    for k in ("as-a", "i-want", "so-that", "failing-test", "severity", "environment", "fixes", "proving-test",
              "regression", "reopens"):
        st.add_argument("--" + k)
    st.add_argument("--criterion", action="append", default=[])
    st.add_argument("--repro", action="append", default=[])
    t = add.add_parser("task")
    t.add_argument("--from", dest="from_file", help="brief em JSON5 (brief-schema.json5)")
    t.add_argument("--id")
    t.add_argument("--story")
    t.add_argument("--agent")
    t.add_argument("--title")
    t.add_argument("--goal")
    t.add_argument("--type")
    t.add_argument("--sprint")
    t.add_argument("--session")
    t.add_argument("--class", dest="klass")
    t.add_argument("--wave", type=int, default=1)
    t.add_argument("--depends-on", action="append", default=[])
    t.add_argument("--allowed-path", action="append", default=[])
    t.add_argument("--protected-path", action="append", default=[])
    t.add_argument("--verify-cmd")
    t.add_argument("--ac", action="append", default=[], help="'AC-n|critério|verification_command|test:<id>|reviewer'")
    t.add_argument("--ref", action="append", default=[])
    t.add_argument("--in", dest="scope_in", action="append", default=[])
    t.add_argument("--out", dest="scope_out", action="append", default=[])
    t.add_argument("--subtask", action="append", default=[])
    t.add_argument("--assume", action="append", default=[])
    t.add_argument("--context", default="")
    t.add_argument("--dod", action="append", default=[])
    t.add_argument("--hot-path", action="store_true")
    t.add_argument("--security-gate", action="store_true")
    t.add_argument("--readonly", action="store_true")
    t.add_argument("--handoff-to")
    t.add_argument("--scenario", action="append", default=[])
    t.add_argument("--ready", action="store_true")
    for lvl, trans in (("epic", ["activate", "done", "drop"]), ("feature", ["ready", "start", "done", "drop"]),
                       ("story", ["ready", "start", "review", "done", "reject", "requeue"])):
        p = sub.add_parser(lvl)
        p.add_argument("transition", choices=trans)
        p.add_argument("--id", required=True)
        p.add_argument("--reason")
    p = sub.add_parser("sprint")
    p.add_argument("transition", choices=["plan", "start", "review", "close"])
    p.add_argument("--id")
    p.add_argument("--goal")
    p.add_argument("--budget")
    p.add_argument("--stories", action="append", default=[])
    p.add_argument("--add", action="append", default=[])
    p.add_argument("--reason")
    p = sub.add_parser("session")
    p.add_argument("transition", choices=["start", "triage", "confirm", "answer", "plan", "execute", "replan", "verify",
                                          "review", "report", "close", "status"])
    p.add_argument("--request")
    p.add_argument("--mode", default="assistido", choices=["assistido", "autonomo"])
    p.add_argument("--class", dest="klass")
    p.add_argument("--why")
    p.add_argument("--assume", action="append", default=[])
    p.add_argument("--note")
    p.add_argument("--by")
    p.add_argument("--verdict")
    p.add_argument("--findings")
    for name in ("ready", "dispatch", "submit", "return", "verify", "review", "accept", "reject", "retry", "escalate",
                 "block", "reroute", "abstain", "delegate", "amend", "brief"):
        p = sub.add_parser(name)
        p.add_argument("task_pos", nargs="?")
        p.add_argument("--task")
        if name == "dispatch":
            p.add_argument("--model")
            p.add_argument("--tool-use-id")
        if name == "submit":
            p.add_argument("--files-changed", action="append", default=[])
            p.add_argument("--check", action="append", default=[])
            p.add_argument("--risk", action="append", default=[])
            p.add_argument("--handoff-notes", default="")
            p.add_argument("--from", dest="from_file")
        if name == "review":
            p.add_argument("--by", required=True)
            p.add_argument("--verdict", required=True)
            p.add_argument("--findings", default="")
        if name in ("reject", "escalate", "block", "reroute", "abstain", "return"):
            p.add_argument("--reason")
        if name == "retry":
            p.add_argument("--findings")
        if name == "reroute":
            p.add_argument("--agent", required=True)
            p.add_argument("--allowed-path", action="append", default=[])
        if name == "abstain":
            p.add_argument("--kind", default="other")
        if name == "amend":
            p.add_argument("--field", required=True)
            p.add_argument("--after", required=True, help="valor em JSON5 (ou texto simples)")
            p.add_argument("--reason", required=True)
            p.add_argument("--found-by")
        if name == "brief":
            p.add_argument("--phase", choices=["implement", "verify", "review"])
            p.add_argument("--agent")
    p = sub.add_parser("status")
    p.add_argument("--task")
    sub.add_parser("board")
    sub.add_parser("next")
    p = sub.add_parser("why")
    p.add_argument("id")
    p = sub.add_parser("autonomy")
    p.add_argument("action", choices=["start", "status", "stop", "report", "spend"])
    p.add_argument("--feature")
    p.add_argument("--story")
    p.add_argument("--spec")
    p.add_argument("--accept-cmd", action="append", default=[])
    p.add_argument("--accept-file", action="append", default=[])
    p.add_argument("--class", dest="klass")
    p.add_argument("--budget", default="")
    p.add_argument("--usd", type=float)
    p.add_argument("--reason")
    return ap


def _tid(a):
    tid = a.task or a.task_pos
    if not tid:
        raise hcore.Refused("informe a task (--task <id> ou posicional)")
    return tid


def _value(s):
    try:
        return j5.loads(s)
    except ValueError:
        return s


def run(a):
    root = hcore.resolve_root(a.root)
    actor = a.actor
    out = []
    c = a.cmd
    if c == "init":
        out.append("estado criado" if engine.init_state(root) else "estado já existe (idempotente)")
    elif c == "add":
        w = a.what
        if w == "epic":
            _, ev = cmds.add_epic(root, actor, a.title, a.objective, a.metric)
        elif w == "feature":
            _, ev = cmds.add_feature(root, actor, a.epic, a.title, a.spec, a.accept_cmd, a.accept_file)
        elif w == "sprint":
            import autonomy
            _, ev = cmds.add_sprint(root, actor, a.goal, autonomy.parse_budget(a.budget))
        elif w == "story":
            feature = a.feature
            if not feature and a.fixes:
                b = hcore.load_board(root)
                src = hcore.find(b, "story", a.fixes) or hcore.find(b, "story", (hcore.find(b, "task", a.fixes.split(":", 1)[-1]) or {}).get("story", ""))
                feature = (src or {}).get("feature")
            if not feature:
                raise hcore.Refused("--feature obrigatório (ou --fixes BUG-n de onde herdar a feature)")
            sev = SEVERITY_ALIAS.get((a.severity or "").lower(), a.severity)
            _, ev = cmds.add_story(root, actor, a.type, feature, a.title, as_a=a.as_a, i_want=a.i_want, so_that=a.so_that,
                                   criteria=_criteria(a.criterion), repro=a.repro, failing_test=a.failing_test, severity=sev,
                                   environment=a.environment, fixes=a.fixes, proving_test=a.proving_test,
                                   regression=a.regression, reopens=a.reopens)
        elif w == "task":
            spec = j5.load(a.from_file) if a.from_file else {}
            cli = {"id": a.id, "story": a.story, "agent": a.agent, "title": a.title, "goal": a.goal, "type": a.type,
                   "sprint": a.sprint, "session": a.session, "class": a.klass, "wave": a.wave,
                   "depends_on": _csv(a.depends_on), "allowed_paths": _csv(a.allowed_path),
                   "protected_paths": _csv(a.protected_path), "verification_command": a.verify_cmd,
                   "acceptance_criteria": a.ac, "dod": a.dod, "readonly": a.readonly,
                   "flags": {"hot_path": a.hot_path, "security_gate": a.security_gate},
                   "handoff": {"to": a.handoff_to, "scenarios": a.scenario} if a.handoff_to or a.scenario else None}
            for k, v in cli.items():
                if v not in (None, [], "", {}) and not (k == "wave" and v == 1 and "wave" in spec):
                    spec[k] = v
            br = dict(spec.get("briefing") or {})
            for k, v in (("references", a.ref), ("subtasks", a.subtask), ("assumptions", a.assume)):
                if v:
                    br[k] = v
            if a.context:
                br["context"] = a.context
            if a.scope_in or a.scope_out:
                br["scope"] = {"in": a.scope_in, "out": a.scope_out}
            spec["briefing"] = br
            if not spec.get("agent"):
                raise hcore.Refused("--agent obrigatório")
            _, ev = cmds.add_task(root, actor, spec, ready=a.ready)
        else:
            raise hcore.Refused("add epic|feature|sprint|story|task")
        out.append("criado: %s" % ", ".join(e["entity"] for e in ev if e.get("entity")))
    elif c in ("epic", "feature", "story"):
        _, ev = cmds.level_transition(root, actor, c, a.id, a.transition, {"reason": a.reason})
        out.append("%s %s → %s" % (c, a.id, a.transition))
    elif c == "sprint":
        sid = a.id
        stories = _csv(a.stories) + _csv(a.add)
        if a.transition == "plan" and not sid:
            b = hcore.load_board(root)
            planned = [s for s in b["sprints"] if s["state"] == "PLANNED"]
            if planned:
                sid = planned[-1]["id"]
            else:
                if not a.goal:
                    raise hcore.Refused("sem sprint PLANNED: passe --goal (e --budget) para criar")
                import autonomy
                _, ev = cmds.add_sprint(root, actor, a.goal, autonomy.parse_budget(a.budget or ""))
                sid = ev[0]["entity"]
        if not sid:
            b = hcore.load_board(root)
            want = {"start": "PLANNED", "review": "ACTIVE", "close": "REVIEW"}[a.transition]
            cand = [s["id"] for s in b["sprints"] if s["state"] == want]
            if not cand:
                raise hcore.Refused("nenhum sprint em %s (passe --id)" % want)
            sid = cand[-1]
        cmds.level_transition(root, actor, "sprint", sid, a.transition, {"add": stories, "reason": a.reason})
        out.append("sprint %s → %s" % (sid, a.transition))
    elif c == "session":
        if a.transition == "start":
            if not a.request:
                raise hcore.Refused("--request obrigatório (pedido do usuário, literal)")
            _, ev = cmds.session_start(root, actor, a.request, a.mode)
            out.append("sessão %s em TRIAGE → cs-state session triage --class ... --why ..." % ev[0]["entity"])
        elif a.transition == "status":
            ctx = engine.Ctx(root, hcore.load_board(root))
            s = cmds.active_session(ctx)
            out.append(views.why(ctx, s["id"]) if s else "nenhuma sessão ativa")
        else:
            cmds.session_cmd(root, actor, a.transition, {"class": a.klass, "why": a.why, "assume": a.assume, "note": a.note,
                                                         "by": a.by, "verdict": a.verdict, "findings": a.findings})
            out.append("sessão: %s ok" % a.transition)
    elif c == "ready":
        cmds.ready(root, actor, _tid(a))
        ctx = engine.Ctx(root, hcore.load_board(root))
        d = engine.latest_deleg(ctx.find("task", _tid(a)))
        out.append("BRIEFED %s — recomendação: model=%s (%s)" % (d["id"], (d.get("route") or {}).get("model"),
                                                               (d.get("route") or {}).get("band")))
        out.append("despache: " + views.next_for(ctx, "deleg", d))
    elif c == "dispatch":
        cmds.dispatch(root, actor, _tid(a), model=a.model, tool_use_id=a.tool_use_id,
                      procedencia="declarada-cli" if a.model else None)
        out.append("DISPATCHED %s" % _tid(a))
    elif c == "submit":
        sub = j5.load(a.from_file) if a.from_file else {}
        if a.files_changed:
            sub["files_changed"] = _csv(a.files_changed)
        if a.check:
            sub["checks_run"] = a.check
        if a.risk:
            sub["risks"] = a.risk
        if a.handoff_notes:
            sub["handoff_notes"] = a.handoff_notes
        cmds.submit(root, actor, _tid(a), sub)
        out.append("RETURNED %s → cs-state verify --task %s" % (_tid(a), _tid(a)))
    elif c == "return":
        cmds.return_(root, actor, _tid(a), a.reason or "protocol_failure: retorno sem submission")
        out.append("REJECTED %s (protocol_failure)" % _tid(a))
    elif c == "verify":
        _, ev = cmds.verify(root, actor, _tid(a))
        probs = ev[-1]["data"].get("problems") or []
        g = ev[-1]["data"].get("gate") or {}
        if probs:
            out.append("verify REPROVOU %s (exit %s):" % (_tid(a), g.get("exit_code")))
            out += ["  - " + p for p in probs[:8]]
        else:
            out.append("verify PASS %s (exit 0, output_sha256 %s) → review por gate" % (_tid(a), g.get("output_sha256", "")[:12]))
    elif c == "review":
        cmds.review(root, actor, _tid(a), a.by, a.verdict, a.findings)
        out.append("review %s registrada" % a.verdict)
    elif c == "accept":
        cmds.accept(root, actor, _tid(a))
        out.append("ACCEPTED %s" % _tid(a))
    elif c == "reject":
        cmds.reject(root, actor, _tid(a), a.reason)
        out.append("REJECTED %s" % _tid(a))
    elif c == "retry":
        cmds.retry(root, actor, _tid(a), a.findings)
        out.append("BRIEFED de novo (retry) %s" % _tid(a))
    elif c in ("escalate", "block"):
        cmds.escalate(root, actor, _tid(a), a.reason)
        out.append("ESCALATED %s (task BLOCKED)" % _tid(a))
    elif c == "reroute":
        cmds.reroute(root, actor, _tid(a), a.agent, a.reason, _csv(a.allowed_path) or None)
        out.append("REROUTED %s → %s (nova delegação PLANNED: cs-state ready --task %s)" % (_tid(a), a.agent, _tid(a)))
    elif c == "abstain":
        cmds.abstain(root, actor, _tid(a), a.kind, a.reason)
        out.append("ABSTAINED %s (conta contra cobertura, não precisão)" % _tid(a))
    elif c == "delegate":
        cmds.delegate(root, actor, _tid(a))
        out.append("nova delegação PLANNED para %s" % _tid(a))
    elif c == "amend":
        cmds.amend(root, actor, _tid(a), a.field, _value(a.after), a.reason, a.found_by)
        out.append("emenda registrada em %s.%s" % (_tid(a), a.field))
    elif c == "brief":
        import brief
        ctx = engine.Ctx(root, hcore.load_board(root))
        t = ctx.find("task", cmds.resolve_task_id(ctx, _tid(a)))
        out.append(brief.package(ctx, t, a.phase, a.agent))
    elif c == "status":
        out.append(views.status(engine.Ctx(root, hcore.load_board(root)), a.task))
    elif c == "board":
        out.append(views.board_tree(engine.Ctx(root, hcore.load_board(root))))
    elif c == "next":
        out += views.next_lines(engine.Ctx(root, hcore.load_board(root)))
    elif c == "why":
        out.append(views.why(engine.Ctx(root, hcore.load_board(root)), a.id))
    elif c == "autonomy":
        import autonomy
        if a.action == "start":
            m = autonomy.start(root, actor, a.feature or a.story, autonomy.parse_budget(a.budget), a.spec, a.accept_cmd or None,
                               a.accept_file or None, a.klass)
            out.append("mandato ACTIVE para %s (assinatura %s). Loop: cs-state next" % (m["target"], m["signature"][:12]))
        elif a.action == "status":
            m = autonomy.load(root)
            if not m:
                out.append("modo assistido (sem mandato)")
            else:
                b = hcore.load_board(root)
                esc = autonomy.detect_escalation(root, b, m) if m["state"] == "ACTIVE" else None
                out.append("mandato %s [%s] alvo %s orçamento %s" % (m["signature"][:12], m["state"], m["target"], m["budget"]))
                if m.get("escalation"):
                    out.append("escalada: %s" % m["escalation"]["condition"])
                elif esc:
                    out.append("condição de escalada detectada: %s" % esc[0])
        elif a.action == "stop":
            autonomy.stop(root, actor, a.reason or "parado")
            out.append("modo assistido; relatório em .specialists/state/autonomy-report.json5")
        elif a.action == "report":
            rep = autonomy.report(root)
            out.append(j5.dumps({k: rep[k] for k in ("target", "state", "elapsed_min", "acceptance_after", "escalation")}))
        elif a.action == "spend":
            m = autonomy.load(root)
            if not m:
                raise hcore.Refused("sem mandato")
            m.setdefault("spent", {})["usd"] = float(m["spent"].get("usd", 0)) + float(a.usd or 0)
            autonomy.save(root, m)
            out.append("gasto registrado: usd=%s" % m["spent"]["usd"])
    else:
        return None
    return out


def main(argv=None):
    ap = build_parser()
    a = ap.parse_args(argv)
    if not a.cmd:
        ap.print_help(sys.stderr)
        return 2
    try:
        out = run(a)
    except hcore.Refused as e:
        sys.stderr.write(e.render() + "\n")
        return 1
    except hcore.StateError as e:
        sys.stderr.write("cs-state: ESTADO: %s\n" % e)
        return 2
    if out is None:
        ap.print_help(sys.stderr)
        return 2
    print("\n".join(x for x in out if x))
    return 0


if __name__ == "__main__":
    sys.exit(main())
