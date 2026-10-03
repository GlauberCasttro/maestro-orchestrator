---
name: reviewer-playbooks
description: "Procedimentos passo a passo de reviewer neste repo. Use quando reviewer for executar: Revisao de diff; Bump de versao"
---
<!-- codebase-specialists:generated; não edite: altere .specialists/team.json5 e rode `cs.py emit` -->

# Playbooks de `reviewer`

Procedimentos do território de `reviewer`, extraídos de `.specialists/team.json`.

## Revisao de diff

1. Listar arquivos do diff com git diff --name-only e mapear cada um ao dono: maestro/orchestrator.py, maestro/aggregator.py, maestro/deliberation.py -> dev-consensus; maestro/storage_proof.py, maestro/instances.py, maestro/lan_discovery.py -> dev-storage-network; backend/main.py, maestro/updater.py, maestro/tui/app.py -> dev-platform; frontend/src/maestroUI.tsx -> dev-frontend; maestros/** -> dev-maestros; tests/** -> qa; docs/** -> architect; Dockerfile, docker-compose.yml, Makefile -> ops.
2. Rodar cada check de invariante de rules (rg -nP ...) e exigir exit 1 (sem ocorrencia); qualquer ocorrencia nova = FAIL.
3. Se o diff toca maestro/aggregator.py (limiares), maestro/storage_proof.py ou o pipeline de self-improvement: NEEDS_SPECIALIST com o dev dono e pedido de aprovacao humana.
4. Rodar pytest tests/ quando disponivel e relatar o resultado; se pytest nao estiver instalado, dizer isso no veredito em vez de presumir verde.
5. Comparar os arquivos do diff com as armadilhas de footguns (updater x frontend/dist, IDs de widget Textual, portas Redis, imports circulares, strings de versao) e checar o par co-alterado.

## Bump de versao

1. Conferir que a nova versao aparece de forma consistente em maestro/__init__.py, frontend/package.json, RELEASE.md, changelog.md e docs/roadmap.md; divergencia = FAIL com encaminhamento ao dono do arquivo.
2. Rodar rg -n "v[0-9]+\.[0-9]+\.[0-9]+" readme.md docs maestro/__init__.py frontend/package.json e procurar a versao antiga remanescente.
