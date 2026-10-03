#!/usr/bin/env python3
"""validate — validador do estado do harness. Usa o CÓDIGO DO HARNESS (nunca um script do alvo).

  python3 validate.py [--strict] [--allow-empty] [--root <alvo>]   (raiz = --root ou $CLAUDE_PROJECT_DIR)

Checa: machines.json5 e guardas implementadas; board.json5 (schema, enum de veredito, campos do brief);
events.jsonl (cadeia de hashes, seq); replay board×events com legalidade de cada mudança de estado;
ACCEPTED coerente (verify exit 0 + reviews exigidas); ledgers encadeados; assinatura do mandato autônomo.
--strict: estado vazio (sem nenhuma entidade) é FALHA, salvo --allow-empty explícito.
"""
import argparse
import copy
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
for _p in (HERE, os.path.join(os.path.dirname(os.path.dirname(HERE)), "memory")):
    if os.path.isdir(_p) and _p not in sys.path:
        sys.path.insert(0, _p)

import hcore  # noqa: E402
import j5  # noqa: E402

TASK_REQ = {"id": str, "story": str, "agent": str, "title": str, "status": str, "allowed_paths": list,
            "verification_command": str, "acceptance_criteria": list, "attempts": int, "reviews": list, "created_at": str}


def task_errors(t, i, verdicts):
    E = []
    for k, typ in TASK_REQ.items():
        v = t.get(k)
        if not isinstance(v, typ) or (typ is int and isinstance(v, bool)):
            E.append("task[%d] %s: campo %s ausente/tipo errado" % (i, t.get("id"), k))
    for ac in t.get("acceptance_criteria") or []:
        if not isinstance(ac, dict) or not {"id", "criterion", "verified_by"} <= set(ac):
            E.append("task %s: AC sem id/criterion/verified_by" % t.get("id"))
    for r in t.get("reviews") or []:
        if not isinstance(r, dict) or r.get("verdict") not in verdicts:
            E.append("task %s: veredito fora do enum: %r" % (t.get("id"), (r or {}).get("verdict") if isinstance(r, dict) else r))
        elif not all(k in r for k in ("by", "verdict", "findings", "at")):
            E.append("task %s: review incompleta" % t.get("id"))
    if "status_history" in t:
        E.append("task %s: status_history não fica no board (derivado de events.jsonl)" % t.get("id"))
    return E


def run(root, strict=True, allow_empty=False):
    E, W = [], []
    try:
        M = hcore.machines()
    except Exception as e:
        return False, ["machines.json5: %s" % e], W
    import engine
    miss = engine.check_guards_defined()
    if miss:
        E.append("guardas citadas em machines.json5 sem implementação: %s" % ", ".join(miss))
    p = hcore.state_paths(root)
    try:
        board = hcore.load_board(root)
    except hcore.StateError as e:
        return False, [str(e)], W
    events, cerr, lh = hcore.read_chain(p["events"])
    E += ["events.jsonl: " + x for x in cerr]
    if not events:
        E.append("events.jsonl vazio/ausente (estado sem gênese)")
    elif events[0].get("type") != "init":
        E.append("primeiro evento não é init")
    verdicts = tuple(M["verdict_enum"])
    for i, t in enumerate(board["tasks"]):
        E += task_errors(t, i, verdicts)
    for s in board["sessions"]:
        for r in s.get("reviews") or []:
            if r.get("verdict") not in verdicts:
                E.append("sessão %s: veredito fora do enum" % s["id"])
    total = sum(len(board[l]) for l in hcore.BOARD_LISTS.values())
    if strict and total == 0 and not allow_empty:
        E.append("estado vazio: board sem nenhuma entidade (use --allow-empty só logo após o install)")
    # replay
    replay = hcore.new_board()
    for ev in events[1:] if events and events[0].get("type") == "init" else events:
        try:
            hcore.apply_ops(replay, ev.get("ops") or [], check_legal=True)
        except (hcore.StateError, KeyError, ValueError, TypeError, AttributeError) as e:
            E.append("replay seq %s (%s): %s" % (ev.get("seq"), ev.get("type"), e))
            break
    for lst in hcore.BOARD_LISTS.values():
        if hcore.canonical(replay[lst]) != hcore.canonical(board[lst]):
            E.append("board×events divergem em '%s' (edição manual ou escrita fora do cs-state)" % lst)
    if board.get("event_count") != len(events):
        E.append("event_count=%s ≠ %d linhas em events.jsonl" % (board.get("event_count"), len(events)))
    if board.get("last_event_hash") != lh:
        E.append("last_event_hash do board ≠ hash da última linha de events.jsonl")
    # ACCEPTED coerente
    if not E:
        ctx = engine.Ctx(root, board)
        for t in board["tasks"]:
            if t["status"] != "ACCEPTED":
                continue
            b = (t.get("gate_report") or {}).get("build") or {}
            if b.get("exit_code") != 0 or b.get("attempt") != t["attempts"]:
                E.append("task %s ACCEPTED sem verify exit 0 na tentativa final" % t["id"])
            d = (t.get("delegations") or [{}])[-1]
            pr = engine.GUARDS["reviews_satisfy_class"](ctx, "deleg", d, {}) if d.get("id") else ["sem delegação"]
            if pr:
                E.append("task %s ACCEPTED sem reviews exigidas: %s" % (t["id"], pr[0]))
    for name, path in (("harness-ledger", p["ledger"]), ("model-router", os.path.join(p["state_dir"], "model-router.jsonl"))):
        if os.path.isfile(path):
            _, le, _ = hcore.read_chain(path)
            E += ["%s.jsonl: %s" % (name, x) for x in le]
    if os.path.isfile(p["autonomy"]):
        try:
            import autonomy
            m = j5.load(p["autonomy"])
            if autonomy.signature(m) != m.get("signature"):
                E.append("autonomy.json5: assinatura não confere (mandato editado à mão)")
            starts = [e for e in events if e.get("type") == "autonomy.start"]
            if not starts or ((starts[-1].get("data") or {}).get("args") or {}).get("signature") != m.get("signature"):
                E.append("autonomy.json5: assinatura não corresponde ao último evento autonomy.start")
        except Exception as e:
            E.append("autonomy.json5 ilegível: %s" % e)
    return not E, E, W


def main(argv=None):
    ap = argparse.ArgumentParser(prog="validate")
    ap.add_argument("root_pos", nargs="?")
    ap.add_argument("--root")
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--allow-empty", action="store_true")
    a = ap.parse_args(argv)
    try:
        root = hcore.resolve_root(a.root or a.root_pos)
    except hcore.StateError as e:
        sys.stderr.write("validate: %s\n" % e)
        return 2
    ok, errs, _ = run(root, a.strict, a.allow_empty)
    if ok:
        print("validate: OK (%s)" % ("strict" if a.strict else "básico"))
        return 0
    print("validate: FALHOU")
    for e in errs:
        print("  - " + e)
    return 1


if __name__ == "__main__":
    sys.exit(main())
