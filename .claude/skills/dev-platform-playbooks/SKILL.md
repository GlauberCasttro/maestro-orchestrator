---
name: dev-platform-playbooks
description: "Procedimentos passo a passo de dev-platform neste repo. Use quando dev-platform for executar: Mudar o auto-updater (maestro/updater.py, maestro/api_update.py); Mudar TUI (maestro/tui/app.py, maestro/tui/widgets.py); Mudar o Mod Manager (maestro/plugins/**, maestro/api_plugins.py); Mudar startup e chaves (entrypoint.py, maestro/cli.py, maestro/keyring.py, maestro/dependency_resolver.py)"
---
<!-- codebase-specialists:generated; não edite: altere .specialists/team.json5 e rode `cs.py emit` -->

# Playbooks de `dev-platform`

Procedimentos do território de `dev-platform`, extraídos de `.specialists/team.json`.

## Mudar o auto-updater (maestro/updater.py, maestro/api_update.py)

1. Em `maestro/updater.py`, mantenha .env/`.env.local` e frontend/dist preservados na sincronização de diretório: perder o primeiro apaga as chaves do usuário; perder o segundo derruba a web com 404 após restart do container.
2. Trate versão local desconhecida: 'unknown' não é ref git válida e já fez o updater mostrar 0 commits novos.
3. No modo Docker a detecção usa git ls-remote + arquivo VERSION (não há .git utilizável na imagem); não volte a depender de git log local.
4. Na TUI, check e apply rodam em threads de fundo para não travar a interface (`maestro/tui/app.py`).
5. Se a resposta de `maestro/api_update.py` mudar de forma, descreva o novo contrato para o dono de `frontend/src/maestroUI.tsx`; não edite lá.

## Mudar TUI (maestro/tui/app.py, maestro/tui/widgets.py)

1. Não nomeie método/atributo de widget com nome interno do Textual (_render, `_nodes` já derrubaram ClusterDashboard e a tela Nodes); use nomes como `_refresh_display` e `_node_data`.
2. IDs de widget derivados de nome de agente passam por `_sanitize_id` em `maestro/tui/widgets.py` (senão BadIdentifier).
3. Texto com colchetes renderizado como Rich markup precisa de escape (controles de deliberação já quebraram assim).
4. Glifos: use ASCII; emojis/símbolos como ⚠ e ✔ foram removidos de `maestro/tui/app.py`.
5. Ao fechar o KeySetupWizard, recarregue status de chaves e checagem de dependências.
6. Exercite com python -m maestro.tui e, para o modo cliente, python -m maestro.tui --mode http.

## Mudar o Mod Manager (maestro/plugins/**, maestro/api_plugins.py)

1. Respeite o ciclo PluginState em `maestro/plugins/base.py` (DISCOVERED, VALIDATED, LOADED, ENABLED, DISABLED, ERROR, UNLOADED) e o caso de teste que o referencia em `tests/test_mod_manager.py`.
2. Descoberta ignora manifestos inválidos e hook point inválido levanta erro — comportamentos fixados em `tests/test_mod_manager.py`.
3. Inicialize os callbacks de PluginContext no construtor (bug já corrigido).
4. `maestro/plugins/manager.py` muda junto com `docs/mod-manager.md`, `maestro/node_server.py`, `RELEASE.md`, `changelog.md` e `readme.md`; strings de versão dentro de manager.py já ficaram defasadas — confira-as ao fazer bump.

## Mudar startup e chaves (entrypoint.py, maestro/cli.py, maestro/keyring.py, maestro/dependency_resolver.py)

1. `entrypoint.py` não importa `maestro` no nível de módulo (import tardio, para rodar antes da checagem de dependências).
2. Chaves precisam sobreviver a restart de container e a update: o caminho envolve `Dockerfile`, `backend/orchestrator_foundry.py`, `maestro/cli.py` e `maestro/keyring.py`.
3. Status 'chave não configurada' é lido por `maestro/dependency_resolver.py` e `maestro/tui/backend.py`; mude os dois juntos (falso positivo de 'sem chaves' já ocorreu duas vezes).
4. Nomes de agentes no diagnóstico de `maestro/dependency_resolver.py` devem acompanhar os agentes atuais (nomes depreciados já vazaram).
5. Teste manual: python -m maestro.cli_keys set openai sk-... e depois python -m maestro.tui.
