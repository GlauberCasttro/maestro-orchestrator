#!/usr/bin/env python3
"""guard — hooks do Claude Code (chamados por .claude/hooks/cs-guard.sh <modo>). FAIL-CLOSED.

Modos:
  pre-write      PreToolUse Write|Edit|MultiEdit|NotebookEdit
  pre-bash       PreToolUse Bash (análise conservadora; não analisável = bloqueio)
  pre-agent      PreToolUse Agent|Task (despacho só com id de delegação BRIEFED + model; dispara M2 dispatch)
  post-edit      PostToolUse Edit|Write|MultiEdit (check rápido do ecossistema; informa, não bloqueia)
  subagent-start SubagentStart (pacote S3 da fase, ≤10.000 chars, marcado como DADO)
  subagent-stop  SubagentStop (sem submission: pede submit 1×, depois protocol_failure)
  stop           Stop (modo autônomo: bloqueia a parada enquanto há trabalho e não há escalada)
  user-prompt    UserPromptSubmit (advisory: lembra de registrar correção; nunca bloqueia)
  session-start  SessionStart (injeta .claude/orchestrator.md + cs-session load)
  check-diff     CLI p/ plataformas sem hook (pre-commit/CI): arquivos alterados × território

Ator: payload com `agent_id` = subagente (`agent_type` = nome); sem `agent_id` = agente principal.
Fonte: https://code.claude.com/docs/en/hooks (Common input fields; PreToolUse/Stop decision control).
Raiz = $CLAUDE_PROJECT_DIR (nunca o diretório do script). Todo bloqueio e todo kill-switch vão para o
ledger. CS_GUARD_OFF=1 libera (e registra quem/quando) — exceto em modo autônomo, onde é ignorado.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
for _p in (HERE, os.path.join(os.path.dirname(os.path.dirname(HERE)), "memory")):
    if os.path.isdir(_p) and _p not in sys.path:
        sys.path.insert(0, _p)

import hcore  # noqa: E402
import bashscan  # noqa: E402

PRE_MODES = ("pre-write", "pre-bash", "pre-agent")
CORRECTION_RE = re.compile(
    r"(\bt[aá] errad|\best[aá] errad|\berrado\b|\bn[aã]o [ée] (assim|isso)|\bna verdade\b|\bcorrij|\bn[aã]o era\b|"
    r"\bdeveria (ser|ter)\b|\bem vez de\b|\bnunca (use|fa[cç]a)\b|\bthat'?s wrong\b|\byou got it wrong\b|\bshould (be|have)\b|"
    r"\binstead of\b|\bdon'?t use\b|\bincorrect\b)", re.I)


class Block(Exception):
    pass


def out_json(obj):
    sys.stdout.write(json.dumps(obj, ensure_ascii=False) + "\n")


def actor_of(p):
    if p.get("agent_id"):
        return {"main": False, "agent_type": p.get("agent_type"), "agent_id": p.get("agent_id")}
    return {"main": True, "agent_type": p.get("agent_type"), "agent_id": None}


def ledger(root, entry):
    try:
        hcore.ledger_append(root, entry)
        return True
    except Exception:
        return False


def harness_paths(root):
    h = os.path.join(root, ".specialists", "harness")
    b = os.path.join(root, ".specialists", "bin")
    out = {}
    for k, f in (("state", "state.py"), ("validate", "validate.py"), ("mem", "mem.py"), ("guard", "guard.py"),
                 ("session", "session.py"), ("route", "router.py")):
        out[k] = os.path.realpath(os.path.join(h, f))
    for k, f in (("bin_state", "cs-state"), ("bin_mem", "cs-mem"), ("bin_session", "cs-session"), ("bin_route", "cs-route")):
        out[k] = os.path.realpath(os.path.join(b, f))
    return out


# ================================================================ decisão de escrita
def dispatched_for(board, agent_type):
    out = []
    for t in board["tasks"]:
        ds = t.get("delegations") or []
        if ds and ds[-1]["agent"] == agent_type and ds[-1]["state"] == "DISPATCHED":
            out.append((t, ds[-1]))
    return out


def decide_write(root, board, cfg, actor, path, base=None):
    """None = permitido; senão o motivo. realpath sempre (X-01); lexical E real precisam passar."""
    if not isinstance(path, str) or not path:
        return "path ausente no payload"
    lex, real = hcore.resolve_target(root, path, base)
    if lex is None or real is None:
        return "escrita fora do projeto (%s → %s)" % (path, os.path.realpath(path if os.path.isabs(path) else os.path.join(base or root, path)))
    rels = sorted({lex, real})
    if "" in rels:
        return "escrita na raiz do projeto"
    for rel in rels:
        if hcore.matches_any(rel, cfg.get("protected") or []):
            return "%s é área protegida do harness (só cs-state/cs-mem escrevem)" % rel
        for p in cfg.get("protected") or []:
            if hcore.literal_prefix(p).startswith(rel.rstrip("/") + "/"):
                return "%s contém área protegida (%s): escrita/remoção bloqueada" % (rel, p)
        import autonomy
        fw = autonomy.forbidden_write(root, rel)
        if fw:
            return fw
    if actor["main"]:
        for rel in rels:
            if not hcore.matches_any(rel, cfg.get("lead_write_allow") or []):
                return "agente principal (tech-lead) não escreve produto: %s — delegue (cs-state next)" % rel
        return None
    at = actor.get("agent_type")
    if not at:
        return "subagente sem agent_type no payload (fail-closed)"
    ds = dispatched_for(board, at)
    if not ds:
        return "%s não tem delegação DISPATCHED: escrita bloqueada" % at
    if len(ds) > 1:
        return "%s tem %d delegações em voo: ambíguo (fail-closed)" % (at, len(ds))
    task = ds[0][0]
    frozen = cfg.get("frozen_paths") or []
    for rel in rels:
        if not hcore.matches_any(rel, task["allowed_paths"]):
            return "%s fora de allowed_paths de %s (%s)" % (rel, task["id"], ", ".join(task["allowed_paths"]))
        if hcore.matches_any(rel, task.get("protected_paths") or []):
            return "%s está em protected_paths de %s" % (rel, task["id"])
        if frozen and hcore.matches_any(rel, frozen):
            import engine
            ctx = engine.Ctx(root, board)
            s = ctx.session_of(task)
            if not (s and s.get("class") == "risco" and s.get("confirmation")):
                return "%s é área congelada: exige classe risco com confirmação do usuário" % rel
    return None


# ================================================================ Bash
STATE_SUB = {"main": {"init", "add", "epic", "feature", "story", "sprint", "session", "ready", "dispatch", "return", "verify",
                      "accept", "reject", "retry", "escalate", "block", "reroute", "delegate", "amend", "brief", "status",
                      "board", "next", "why", "autonomy"},
             "any": {"status", "board", "next", "why", "brief"}}


def _subcmd(argv):
    i = 0
    while i < len(argv):
        a = argv[i]
        if a in ("--root", "--actor"):
            i += 2
            continue
        if a.startswith("-"):
            i += 1
            continue
        return a, argv[i + 1:]
    return None, []


def _opt(argv, name):
    for i, a in enumerate(argv):
        if a == name and i + 1 < len(argv):
            return argv[i + 1]
        if a.startswith(name + "="):
            return a.split("=", 1)[1]
    return None


def harness_call_problem(root, board, team, actor, call):
    tool, argv = call["tool"], call["argv"]
    sub, rest = _subcmd(argv)
    if tool == "validate":
        return None
    if tool == "guard":
        return "guard.py não é chamado à mão"
    at = actor.get("agent_type")
    if tool == "state":
        if actor["main"]:
            if sub in ("submit", "review", "abstain"):
                return "cs-state %s é ato do subagente (o principal não se auto-aprova)" % sub
            return None if sub in STATE_SUB["main"] or sub is None else "cs-state %s desconhecido" % sub
        if sub in STATE_SUB["any"] or sub is None:
            return None
        if sub in ("submit", "abstain"):
            tid = _opt(rest, "--task") or next((x for x in rest if not x.startswith("-")), None)
            t = hcore.find(board, "task", tid or "") or hcore.task_of_deleg(board, tid or "")
            if not t or (t.get("delegations") or [{}])[-1].get("agent") != at:
                return "%s só pode %s a própria task" % (at, sub)
            return None
        if sub == "review":
            if _opt(rest, "--by") != at:
                return "review --by deve ser o próprio agente (%s)" % at
            if at not in hcore.gate_agents(team):
                return "%s não é gate" % at
            return None
        return "subagente não roda cs-state %s (orquestração é do agente principal)" % sub
    if tool == "mem":
        if sub in ("search", "check", "stats", None):
            return None
        if sub in ("add", "correct"):
            if actor["main"]:
                return None
            if _opt(rest, "--agent") != at:
                return "subagente só grava lição na própria memória (--agent %s)" % at
            return None
        return None if actor["main"] else "cs-mem %s é do agente principal" % sub
    if tool == "session":
        return None if actor["main"] else "cs-session é do agente principal"
    if tool == "route":
        if sub in ("recommend", "stats", None):
            return None
        return None if actor["main"] else "cs-route %s é do agente principal" % sub
    return "ferramenta do harness desconhecida"


def decide_bash(root, board, cfg, team, actor, command, cwd):
    s = bashscan.scan(command, cwd or root, root, harness_paths(root))
    if s.unanalyzable:
        return "comando não analisável (%s) — divida em comandos simples, sem $(...), heredoc ou -c" % "; ".join(s.unanalyzable[:3])
    import autonomy
    auto = autonomy.active(root) if board is not None else None
    for sub, args in s.git:
        eff = bashscan.git_effect(sub)
        if not actor["main"] and eff != "read":
            return "subagente não roda git %s (CLAUDE.md: git é do tech-lead)" % sub
        if eff == "tree":
            return "git %s reescreve a árvore de trabalho/produto: bloqueado (delegue ou use kill-switch registrado)" % sub
        if sub == "push" and auto:
            return "modo autônomo: push proibido"
        if sub == "push":
            for b in cfg.get("protected_branches") or []:
                if b in args:
                    return "push direto em branch protegida %s" % b
    for call in s.harness_calls:
        if board is None and not (call["tool"] in ("validate",) or (call["tool"] == "state" and _subcmd(call["argv"])[0] in ("init", "status"))):
            return "estado ausente: só cs-state init/status e validate rodam (fail-closed)"
        if board is not None:
            pr = harness_call_problem(root, board, team, actor, call)
            if pr:
                return pr
    if board is None:
        bad = [p for p in s.programs if p not in bashscan.READONLY and p not in ("python3", "python")]
        if bad or s.writes:
            return "estado ausente (board.json5): só leitura e cs-state init (fail-closed)"
        return None
    for tok, base in s.writes:
        r = decide_write(root, board, cfg, actor, tok, base or root)
        if r:
            return "Bash escreveria: " + r
    return None


# ================================================================ despacho (Agent|Task)
def decide_agent(root, payload, actor):
    import engine
    import cmds
    import router
    ti = payload.get("tool_input") or {}
    st, desc, model = ti.get("subagent_type"), ti.get("description") or "", ti.get("model")
    if not actor["main"]:
        return "subagente não despacha subagente (delegação de nível único)"
    board = hcore.load_board(root)
    ctx = engine.Ctx(root, board)
    ids = engine.DELEG_RE.findall(desc + " " + (ti.get("prompt") or "")[:300])
    found = [(i, hcore.find(board, "deleg", i)) for i in dict.fromkeys(ids)]
    found = [(i, d) for i, d in found if d]
    if not found:
        if st in (ctx.cfg.get("readonly_agents") or []):
            return None if model else "despacho sem model (%s): passe model explicitamente" % st
        briefed = ["%s" % d["id"] for t, d in engine.all_delegs(board) if d["agent"] == st and d["state"] == "BRIEFED"]
        return ("despacho de %s sem id de delegação BRIEFED na description. %s" % (
            st, ("Use description='%s: ...'" % briefed[0]) if briefed else "Crie e prepare: cs-state add task ... --ready"))
    for did, d in found:
        task = hcore.task_of_deleg(board, did)
        if d["state"] == "BRIEFED" and d["agent"] == st:
            try:
                cmds.dispatch(root, "lead", did, model=model, tool_use_id=payload.get("tool_use_id"),
                              procedencia="declarada-no-despacho")
            except hcore.Refused as e:
                return "despacho de %s recusado: %s" % (did, "; ".join(e.problems))
            return None
        if d["state"] in ("VERIFIED", "REVIEWED") and st in hcore.gate_agents(ctx.team) and st != d["agent"]:
            pr = router.review_model_problems(ctx, task, d, model)
            return ("revisão de %s: %s" % (did, "; ".join(pr))) if pr else None
    return "nenhuma delegação citada está BRIEFED para %s (estados: %s)" % (st, ", ".join("%s=%s/%s" % (i, d["state"], d["agent"]) for i, d in found))


# ================================================================ modos
def mode_pre(mode, root, payload):
    actor = actor_of(payload)
    try:
        cfg = hcore.load_config(root)
    except Exception as e:
        raise Block("config.json5 ilegível: %s" % e)
    board = None
    try:
        board = hcore.load_board(root)
    except hcore.StateError as e:
        if mode != "pre-bash":
            raise Block("estado ausente/ilegível (%s) — fail-closed" % e)
    team = hcore.load_team(root)
    ti = payload.get("tool_input") or {}
    if mode == "pre-write":
        path = ti.get("file_path") or ti.get("notebook_path") or ti.get("path")
        r = decide_write(root, board, cfg, actor, path, payload.get("cwd") or root)
        return r, path
    if mode == "pre-bash":
        cmd = ti.get("command")
        return decide_bash(root, board, cfg, team, actor, cmd, payload.get("cwd") or root), (cmd or "")[:300]
    if mode == "pre-agent":
        return decide_agent(root, payload, actor), ti.get("description")
    raise Block("modo desconhecido")


def mode_subagent_start(root, payload):
    import engine
    import brief
    at = payload.get("agent_type")
    board = hcore.load_board(root)
    ctx = engine.Ctx(root, board)
    ds = dispatched_for(board, at)
    if len(ds) == 1:
        text = brief.package(ctx, ds[0][0], "implement", at)
    elif at in hcore.gate_agents(ctx.team):
        cands = [(t, d) for t, d in engine.all_delegs(board) if d["state"] in ("VERIFIED", "REVIEWED", "RETURNED") and d["agent"] != at
                 and engine.latest_deleg(t) is d]
        if cands:
            t, d = cands[-1]
            text = brief.package(ctx, t, "review" if d["state"] != "RETURNED" else "verify", at)
            if len(cands) > 1:
                text += "\n(outras em revisão: %s — cs-state brief <task> --phase review)" % ", ".join(x[0]["id"] for x in cands[:-1])
        else:
            text = brief.no_task_package(at)
    else:
        text = brief.no_task_package(at)
    out_json({"hookSpecificOutput": {"hookEventName": "SubagentStart", "additionalContext": text[:10000]}})


def _measure_model(payload):
    p = payload.get("agent_transcript_path")
    if not p or not os.path.isfile(p):
        return None
    try:
        with open(p, "rb") as f:
            f.seek(max(0, os.path.getsize(p) - 400000))
            data = f.read().decode("utf-8", "replace")
    except OSError:
        return None
    ms = re.findall(r'"model"\s*:\s*"([^"]+)"', data)
    for m in reversed(ms):
        for tier in ("haiku", "sonnet", "opus"):
            if tier in m:
                return tier
    return None


def mode_subagent_stop(root, payload):
    import cmds
    import engine
    at = payload.get("agent_type")
    board = hcore.load_board(root)
    ds = dispatched_for(board, at)
    if len(ds) != 1:
        return
    t, d = ds[0]
    tier = _measure_model(payload)
    if tier:
        try:
            import router
            router.measured(root, d["id"], tier)
            declared = (d.get("model") or {}).get("name")

            def build(ctx):
                return [engine.Event("delegation.measure_model", d["id"], [
                    ["set", engine.ref("deleg", d["id"]), "model", {"name": tier, "procedencia": "medida",
                                                                     "declared": declared}]])]
            engine.commit(root, "hook", build, post=False)
        except Exception:
            pass
    if payload.get("stop_hook_active"):
        cmds.return_(root, "hook", t["id"], "protocol_failure: subagente %s encerrou sem submission" % at)
        ledger(root, {"kind": "protocol_failure", "task": t["id"], "agent_type": at})
        return
    out_json({"decision": "block", "reason": "Antes de encerrar: cs-state submit --task %s --files-changed ... --check ... --risk ... "
              "--handoff-notes ...  (ou cs-state abstain --task %s --kind spec_ambiguous|test_suspect --reason ...)" % (t["id"], t["id"])})


def mode_stop(root, payload):
    import autonomy
    block, reason = autonomy.stop_decision(root, payload)
    if block:
        out_json({"decision": "block", "reason": reason})


def mode_user_prompt(root, payload):
    msg = payload.get("prompt") or ""
    if CORRECTION_RE.search(msg):
        out_json({"hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext":
                  "[cs-harness advisory] A mensagem parece uma CORREÇÃO da saída de um agente. Registre antes de seguir: "
                  "cs-mem correct --agent <agente> --wrong '...' --right '...' --why '...' [--paths '<glob>']"}})


def mode_session_start(root, payload):
    parts = []
    orch = os.path.join(root, ".claude", "orchestrator.md")
    if os.path.isfile(orch):
        with open(orch, "r", encoding="utf-8") as f:
            parts.append(f.read()[:7000])
    try:
        import session
        text, _ = session.load(root)
        parts.append("<<DADO sessão (cs-session load)>>\n" + text + "\n<</DADO>>")
    except Exception as e:
        parts.append("(cs-session load indisponível: %s)" % str(e)[:120])
    out_json({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": "\n\n".join(parts)[:10000]}})


def mode_post_edit(root, payload):
    import subprocess
    cfg = hcore.load_config(root)
    ti = payload.get("tool_input") or {}
    path = ti.get("file_path") or ti.get("notebook_path")
    if not path:
        return
    _, rel = hcore.resolve_target(root, path)
    if rel is None:
        return
    msgs = []
    for chk in cfg.get("post_edit_checks") or []:
        if not hcore.matches_any(rel, chk.get("glob") or ["**"]):
            continue
        argv = [a.replace("{file}", rel) for a in chk.get("argv") or []]
        if not argv:
            continue
        try:
            p = subprocess.run(argv, cwd=root, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=int(chk.get("timeout_s", 60)))
            if p.returncode != 0:
                msgs.append("[%s] exit %d:\n%s" % (chk.get("name", argv[0]), p.returncode, p.stdout.decode("utf-8", "replace")[-2500:]))
        except (OSError, subprocess.TimeoutExpired) as e:
            msgs.append("[%s] não rodou: %s" % (chk.get("name", argv[0]), e))
    if msgs:
        out_json({"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext":
                  "Diagnóstico do check rápido após editar %s (corrija antes de seguir):\n%s" % (rel, "\n".join(msgs))[:9000]}})


def check_diff(root, staged=False):
    import subprocess
    import validate
    cfg = hcore.load_config(root)
    board = hcore.load_board(root)
    args = ["git", "diff", "--name-only"] + (["--cached"] if staged else ["HEAD"])
    p = subprocess.run(args, cwd=root, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    files = [x for x in p.stdout.decode().splitlines() if x]
    if not staged:
        u = subprocess.run(["git", "ls-files", "--others", "--exclude-standard"], cwd=root, stdout=subprocess.PIPE)
        files += [x for x in u.stdout.decode().splitlines() if x]
    allowed = list(cfg.get("lead_write_allow") or [])
    for t in board["tasks"]:
        d = (t.get("delegations") or [{}])[-1]
        if d.get("state") in ("DISPATCHED", "RETURNED", "VERIFIED", "REVIEWED"):
            allowed += t["allowed_paths"]
    ok_state = validate.run(root, strict=False)[0]
    bad = []
    for f in files:
        if f.startswith(".specialists/state/") or f.startswith(".specialists/memory/"):
            if not ok_state:
                bad.append("%s (estado não valida)" % f)
            continue
        if hcore.matches_any(f, cfg.get("protected") or []):
            bad.append("%s (área protegida)" % f)
        elif not hcore.matches_any(f, allowed):
            bad.append("%s (fora de qualquer allowed_paths em voo)" % f)
    return bad


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    mode = argv[0] if argv else ""
    if mode == "check-diff":
        root = hcore.resolve_root(argv[argv.index("--root") + 1] if "--root" in argv else None)
        bad = check_diff(root, "--staged" in argv)
        for b in bad:
            print("FORA: " + b)
        if bad:
            ledger(root, {"kind": "block", "mode": "check-diff", "files": bad[:50]})
        return 1 if bad else 0
    root_env = os.environ.get("CLAUDE_PROJECT_DIR")
    raw = sys.stdin.read() if not sys.stdin.isatty() else ""
    try:
        payload = json.loads(raw) if raw.strip() else {}
        if not isinstance(payload, dict):
            raise ValueError("payload não é objeto")
    except ValueError as e:
        payload, perr = {}, "payload ilegível: %s" % e
    else:
        perr = None
    if not root_env:
        if mode in PRE_MODES:
            sys.stderr.write("cs-guard: CLAUDE_PROJECT_DIR ausente — bloqueado (fail-closed)\n")
            return 2
        return 0
    root = os.path.realpath(root_env)
    actor = actor_of(payload)
    base = {"mode": mode, "tool": payload.get("tool_name"), "tool_use_id": payload.get("tool_use_id"),
            "session_id": payload.get("session_id"), "agent_type": actor.get("agent_type"), "agent_id": actor.get("agent_id")}
    if mode in PRE_MODES:
        if perr:
            ledger(root, dict(base, kind="block", reason=perr))
            sys.stderr.write("cs-guard: %s — bloqueado\n" % perr)
            return 2
        if os.environ.get("CS_GUARD_OFF") == "1":
            auto = None
            try:
                import autonomy
                auto = autonomy.active(root)
            except Exception:
                auto = None
            who = dict(base, kind="killswitch_ignored" if auto else "killswitch", user=os.environ.get("USER"),
                       target=str((payload.get("tool_input") or {}))[:300])
            if not ledger(root, who):
                sys.stderr.write("cs-guard: kill-switch exige ledger gravável — bloqueado\n")
                return 2
            if not auto:
                return 0
        try:
            reason, target = mode_pre(mode, root, payload)
        except Block as e:
            reason, target = str(e), None
        except Exception as e:  # fail-closed em qualquer erro inesperado
            reason, target = "erro interno do guard (%s: %s) — fail-closed" % (type(e).__name__, e), None
        if reason:
            logged = ledger(root, dict(base, kind="block", reason=reason[:600], target=(str(target) if target else None)))
            sys.stderr.write("cs-guard BLOQUEOU: %s%s\n" % (reason, "" if logged else " [ledger indisponível]"))
            return 2
        return 0
    handlers = {"subagent-start": mode_subagent_start, "subagent-stop": mode_subagent_stop, "stop": mode_stop,
                "user-prompt": mode_user_prompt, "session-start": mode_session_start, "post-edit": mode_post_edit}
    h = handlers.get(mode)
    if not h:
        sys.stderr.write("cs-guard: modo desconhecido %r\n" % mode)
        return 2
    try:
        h(root, payload)
    except Exception as e:  # modos não-bloqueantes: registram e seguem
        ledger(root, dict(base, kind="error", reason="%s: %s" % (type(e).__name__, e)))
        if mode == "subagent-start":
            out_json({"hookSpecificOutput": {"hookEventName": "SubagentStart", "additionalContext":
                      "<<DADO cs-harness>>estado indisponível (%s): escritas serão bloqueadas.<</DADO>>" % type(e).__name__}})
    return 0


if __name__ == "__main__":
    sys.exit(main())
