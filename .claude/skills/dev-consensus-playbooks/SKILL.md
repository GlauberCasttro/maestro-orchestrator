---
name: dev-consensus-playbooks
description: "Procedimentos passo a passo de dev-consensus neste repo. Use quando dev-consensus for executar: Mudar a coleta de respostas dos agentes no streaming; Alterar o detector de erro de agente; Mudar o agente de um provedor (Aria/Sol/Prism/TempAgent)"
---
<!-- codebase-specialists:generated; não edite: altere .specialists/team.json5 e rode `cs.py emit` -->

# Playbooks de `dev-consensus`

Procedimentos do território de `dev-consensus`, extraídos de `.specialists/team.json`.

## Mudar a coleta de respostas dos agentes no streaming

1. Em `maestro/orchestrator.py`, na função `run_orchestration_stream`, mantenha o dict tarefa→agente e consuma com `asyncio.wait(..., return_when=asyncio.FIRST_COMPLETED)`, que devolve as tarefas originais; `asyncio.as_completed` devolve wrappers novos que não batem com as chaves do dict.
2. Garanta que a resposta de um agente com erro (sentinela) continue fora do dissenso, do drift do NCG e da agregação.
3. Rode pytest tests/test_orchestration.py (comando não verificado no scan).

## Alterar o detector de erro de agente

1. Edite `_ERROR_PATTERN`/`_is_agent_error` em `maestro/orchestrator.py` e replique a mesma regex em `maestro/deliberation.py`: as cópias são intencionais e evitam o import circular.
2. Confira com `rg -n "_ERROR_PATTERN" "maestro/orchestrator.py" "maestro/deliberation.py"` que as duas definições continuam iguais.
3. Rode pytest tests/test_orchestration.py (comando não verificado no scan).

## Mudar o agente de um provedor (Aria/Sol/Prism/TempAgent)

1. Edite só a subclasse em `maestro/agents/<nome>.py`; o contrato comum está em `maestro/agents/base.py`.
2. Mantenha o system prompt com a data atual que todos os agentes enviam.
3. Se trocar o modelo, atualize os nomes de modelo citados em `docs/agents.md` e `readme.md`, que já estão defasados (área de leitura; peça a quem tem escrita em docs).
