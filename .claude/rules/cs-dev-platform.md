---
paths:
  - "backend/**"
  - "entrypoint.py"
  - "maestro/cli.py"
  - "maestro/cli_keys.py"
  - "maestro/keyring.py"
  - "maestro/api_keys.py"
  - "maestro/selector.py"
  - "maestro/tui/**"
  - "maestro/plugins/**"
  - "maestro/api_plugins.py"
  - "maestro/updater.py"
  - "maestro/api_update.py"
  - "maestro/dependency_resolver.py"
  - "data/**"
---
<!-- codebase-specialists:generated; não edite: altere .specialists/team.json5 e rode `cs.py emit` -->

# Território de `dev-platform`

Dono de escrita destes arquivos: `dev-platform` (dev). Mudança aqui respeita o que segue; o cartão do dono tem missão e recusas.

## Invariantes

- Estados de PluginState (maestro/plugins/base.py): DISCOVERED, VALIDATED, LOADED, ENABLED, DISABLED, ERROR, UNLOADED; citado em teste tests/test_mod_manager.py (`PluginState`)
- Entrevista protected-areas: Há áreas que exigem aprovação humana antes de mudar (ex.: limiares QUORUM_THRESHOLD/SIMILARITY_THRESHOLD, storage_proof, self_improvement/code_injection, updater, licença)? — resposta do dono (literal): Limiares de consenso, Self-improvement, Storage proof / rede
- Entrevista ui-primary: Qual interface é a principal e mantida: TUI Textual (maestro/tui/) ou web (frontend/ React + backend/main.py)? — resposta do dono (literal): Ambas
- Invariante: except: sem tipo tem 0 ocorrências em 65 arquivos python de produto (não introduzir)
- Invariante: eval() tem 0 ocorrências em 65 arquivos python de produto (não introduzir)
- Invariante: exec() tem 0 ocorrências em 65 arquivos python de produto (não introduzir)
- Invariante: os.system() tem 0 ocorrências em 65 arquivos python de produto (não introduzir)
- Invariante: pickle.load(s) tem 0 ocorrências em 65 arquivos python de produto (não introduzir)
- Invariante: subprocess com shell=True tem 0 ocorrências em 65 arquivos python de produto (não introduzir)
- Invariante: import * tem 0 ocorrências em 65 arquivos python de produto (não introduzir)
- Invariante: yaml.load sem Loader tem 0 ocorrências em 65 arquivos python de produto (não introduzir)

## Convenções e regras técnicas

- Não introduzir `except:` sem tipo (0 ocorrências hoje no Python de produto). — prova: `rg -n "^\s*except\s*:" backend data entrypoint.py maestro setup.py`
- Não introduzir eval() nem `exec()`. — prova: `rg -nP "(?<![\w.])(eval|exec)\(" backend data entrypoint.py maestro setup.py`
- Não usar `subprocess` com `shell=True` nem `os.system()` (o updater e o dependency_resolver chamam processos externos). — prova: `rg -n "shell\s*=\s*True|\bos\.system\(" backend data entrypoint.py maestro setup.py`
- Não usar `pickle.load(s)` nem `yaml.load` sem Loader (manifestos e snapshots de plugin incluídos). — prova: `rg -nP "pickle\.loads?\(|\byaml\.load\((?![^)]*Loader)" backend data entrypoint.py maestro setup.py`
- Não usar `from x import *`. — prova: `rg -n "^\s*from\s+\S+\s+import\s+\*" backend data entrypoint.py maestro setup.py`
- Os estados de PluginState são contrato: adicionar/renomear exige atualizar `tests/test_mod_manager.py`. — prova: `rg -n "PluginState" maestro/plugins/base.py tests/test_mod_manager.py`
- Gate de merge declarado pelo dono: a suíte inteira passa (não há config pytest nem CI no repo). — prova: `pytest tests/`

## Armadilhas registradas

- O updater apagou frontend/dist (só existe na imagem Docker) e o container passou a dar 404 após restart.
- Update sobrescreveu as chaves de API do usuário; a correção passou a preservar .env na sincronização.
- Chaves de API se perdiam em restart do container.
- Versão local 'unknown' usada como ref git fazia o painel mostrar 0 commits novos.
- Método _render em widget colidiu com o Textual e derrubou o ClusterDashboard; `self._nodes` derrubou a tela Nodes.
- Nome de agente usado cru como ID de widget gerou BadIdentifier na TUI.
- Uma única correção na TUI/updater consertou seis bugs juntos: sentinel de restart, corrida de DOM, API de loop depreciada, vazamento de tmp, corrupção da TUI e churn de thread pool.
- Import de `maestro` no topo de `entrypoint.py` quebrou o startup e foi removido.
- Chaves configuradas apareciam como não configuradas (dependency_resolver + tui/backend) e status ficava velho após o wizard.
- O seletor de modo deixava artefatos de renderização até limpar cada linha e encurtar as opções.

## Notas por caminho

- `data/**`: Docs citam caminhos em data/ que não existem (`data/runtime_config.json`, `data/rollbacks/log.json`, `data/node_shards.json`, `data/storage_proofs/reputations.json`); não os trate como contrato sem conferir o código.
- `backend/**`: `backend/main.py` é hotspot (20 commits, 5 correções) e só depende de `maestro`; `backend/orchestrator_foundry.py` é o arquivo mais central da pasta.
- `entrypoint.py`, `maestro/cli.py`: `entrypoint.py`, `maestro/cli.py` e `tests/test_startup.py` formam uma comunidade de imports isolada: mudança no startup se confere em `tests/test_startup.py`.

## Termos do domínio (além do cartão do dono)

- `stream` (em `backend/main.py`)
- `validate` (em `maestro/api_keys.py`)
- `ask` (em `backend/main.py`)
- `Prompt` (em `backend/main.py`)
- `config` (em `maestro/api_plugins.py`)
- `check` (em `maestro/api_update.py`)
- `Mod Manager` — Central lifecycle manager — discover, validate, load, enable, disable, unload, hot-reload. Manages pipeline hooks, event bus, weight state snapshots. (em `maestro/plugins/manager.py`)
- `apply` (em `maestro/api_update.py`)
- `Severity` (em `maestro/dependency_resolver.py`)
- `AutoUpdater` (em `maestro/updater.py`)
- `MaestroTUI` (em `maestro/tui/app.py`)
- `Response Viewer` — Scrollable RichLog showing streaming agent responses and consensus output with syntax highlighting (em `maestro/tui/widgets.py`)
- `enable` (em `maestro/api_plugins.py`)
- `diff` (em `maestro/api_plugins.py`)
- `restore` (em `maestro/api_plugins.py`)
- `discover` (em `maestro/api_plugins.py`)
- `reload` (em `maestro/api_plugins.py`)
- `PluginState` (em `maestro/plugins/base.py`)
- `restart` (em `maestro/api_update.py`)
- `disable` (em `maestro/api_plugins.py`)

- Mais 40 termo(s)/regra(s): `.specialists/bin/cs-mem search "<consulta>" --kind term|rule --paths "backend/**,entrypoint.py,maestro/cli.py,maestro/cli_keys.py,maestro/keyring.py,maestro/api_keys.py,maestro/selector.py,maestro/tui/**,maestro/plugins/**,maestro/api_plugins.py,maestro/updater.py,maestro/api_update.py,maestro/dependency_resolver.py,data/**"`.
