---
name: dev-frontend-playbooks
description: "Procedimentos passo a passo de dev-frontend neste repo. Use quando dev-frontend for executar: Exibir dados de uma rota /api nova ou alterada; Alinhar a versão exibida pela Web UI"
---
<!-- codebase-specialists:generated; não edite: altere .specialists/team.json5 e rode `cs.py emit` -->

# Playbooks de `dev-frontend`

Procedimentos do território de `dev-frontend`, extraídos de `.specialists/team.json`.

## Exibir dados de uma rota /api nova ou alterada

1. Leia a rota na fonte (backend/main.py ou o maestro/api_*.py correspondente) e anote o envelope exato do JSON; não assuma que o corpo é uma lista (ex.: /api/sessions devolve um objeto com sessions e total).
2. Declare a interface da resposta em PascalCase em frontend/src/maestroUI.tsx, ao lado das existentes (AgentError, DissentData, NcgBenchmark, R2Data, ShardModel, NetworkTopology, InstanceInfo).
3. Desembrulhe o campo com fallback vazio antes de chamar .map, e trate erro HTTP mostrando mensagem ao usuário em vez de esconder o painel.
4. Se houver estilo novo, edite frontend/src/style.css no mesmo commit que frontend/src/maestroUI.tsx.
5. Rode as buscas de invariantes listadas em rules sobre `frontend/src` e confirme saída vazia.
6. Se a mudança afeta o que a TUI mostra, avise o orquestrador para checar paridade em maestro/tui/ e se docs/ui-guide.md precisa de ajuste (leitura apenas para este agente).

## Alinhar a versão exibida pela Web UI

1. Atualize o campo version de frontend/package.json e o version correspondente em frontend/package-lock.json no mesmo commit.
2. Atualize o badge de versão renderizado em frontend/src/maestroUI.tsx (span com className version) para o mesmo valor.
3. Confirme com grep -n "className=\"version\"" frontend/src/maestroUI.tsx e grep -n '"version"' frontend/package.json que os valores coincidem.
