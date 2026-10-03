---
name: security-playbooks
description: "Procedimentos passo a passo de security neste repo. Use quando security for executar: Gate de diff no self-improvement (applicator / injection_guard / rollback / aggregator); Gate de diff em updater / chaves de provedor"
---
<!-- codebase-specialists:generated; não edite: altere .specialists/team.json5 e rode `cs.py emit` -->

# Playbooks de `security`

Procedimentos do território de `security`, extraídos de `.specialists/team.json`.

## Gate de diff no self-improvement (applicator / injection_guard / rollback / aggregator)

1. Confirmar se o diff toca `maestro/aggregator.py`, `maestro/applicator.py`, `maestro/injection_guard.py` ou `maestro/rollback.py`; se tocar limiar ou regra de injeção, veredito mínimo NEEDS_SPECIALIST (área protegida).
2. Conferir em `tests/test_code_injection.py` que os testes test_injectable_architecture_blocked, test_injectable_unknown_category_blocked, test_injectable_rejected_status, test_rate_limit_blocks e test_rate_limit_blocks_injection continuam com as mesmas asserções (não foram removidos nem afrouxados).
3. Rodar os checks negativos de Python (eval/exec/shell=True/pickle/os.system) listados em rules; qualquer saída = FAIL.
4. Não confiar em o log de rollbacks (JSON em data/rollbacks, criado em runtime) citado na documentação: o caminho não existe no repo.

## Gate de diff em updater / chaves de provedor

1. Se o diff toca `maestro/updater.py`, `maestro/keyring.py`, `Dockerfile`, `maestro/cli.py` ou `backend/orchestrator_foundry.py`, exigir evidência de que as chaves de API persistem após update e restart do container; sem ela, NEEDS_SPECIALIST.
2. Verificar no diff de `maestro/updater.py` se a versão local desconhecida é tratada antes de usar como git ref (já gerou '0 commits' por ref inválida).
3. Rodar `rg -nP "shell\s*=\s*True" backend maestro data entrypoint.py setup.py` e `rg -nP "\bos\.system\(" backend maestro data entrypoint.py setup.py`; saída = FAIL.
