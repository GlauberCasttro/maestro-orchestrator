---
name: ops-playbooks
description: "Procedimentos passo a passo de ops neste repo. Use quando ops for executar: Bump de versão / release; Mudar setup.py; Mudar imagem ou compose"
---
<!-- codebase-specialists:generated; não edite: altere .specialists/team.json5 e rode `cs.py emit` -->

# Playbooks de `ops`

Procedimentos do território de `ops`, extraídos de `.specialists/team.json`.

## Bump de versão / release

1. Atualizar o badge de versão em readme.md e o título/seção What's New em RELEASE.md para a nova versão.
2. Adicionar a entrada correspondente no topo de changelog.md.
3. Conferir que a versão nova aparece nos três: rg -n "v7\.4\.0" readme.md RELEASE.md changelog.md (trocar pela versão nova; a antiga só deve sobrar em changelog.md).
4. Repassar ao agente dono de docs/** e maestro/** a atualização de docs/roadmap.md, docs/agents.md, maestro/__init__.py e frontend/package.json, que historicamente mudam no mesmo bump.

## Mudar setup.py

1. Preservar em setup.py: o reconfigure UTF-8 de stdout/stderr (Windows), o fallback para PEP 668 externally-managed-environment, a distinção socket Docker sem permissão vs daemon parado, a limpeza de containers/processos antigos e a resolução do caminho do compose independente do diretório de onde o script é chamado.
2. Checar invariantes: rg -n "shell=True|os\.system\(|eval\(|exec\(|except:" setup.py deve sair vazio.
3. Executar via make setup (declarado; requer daemon Docker) e conferir que a espera de saúde (HEALTH_RETRIES) termina.

## Mudar imagem ou compose

1. Editar Dockerfile mantendo o ARG GIT_COMMIT e a escrita do arquivo VERSION usados pelo auto-updater.
2. Editar docker-compose.yml mantendo o env_file no formato compatível com Compose legado e o .env opcional.
3. Se um novo arquivo de ambiente for introduzido, ajustar as exceções em .gitignore (!.env.example) e .dockerignore (!.env.example, !.env.template).
4. Rebuild via make build (docker compose build --no-cache) e subir com make up; conferir saúde com make status.
