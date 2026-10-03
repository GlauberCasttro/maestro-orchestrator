---
paths:
  - ".github/**"
  - "setup.py"
  - "setup.sh"
  - ".dockerignore"
  - ".env.example"
  - ".gitignore"
  - "ARCHITECTURE.md"
  - "CLUSTERING.md"
  - "CONTRIBUTING.md"
  - "Dockerfile"
  - "LICENSE.md"
  - "Makefile"
  - "ORCHESTRA.md"
  - "PROJECT_EXPLAINED.md"
  - "RELEASE.md"
  - "ROADMAP.md"
  - "changelog.md"
  - "commercial_license.md"
  - "dashboard.html"
  - "docker-compose.yml"
  - "readme.md"
  - "requirements.txt"
  - "use_policy.md"
---
<!-- codebase-specialists:generated; não edite: altere .specialists/team.json5 e rode `cs.py emit` -->

# Território de `ops`

Dono de escrita destes arquivos: `ops` (ops). Mudança aqui respeita o que segue; o cartão do dono tem missão e recusas.

## Invariantes

- Limite HEALTH_RETRIES = 30 (technical) em setup.py; nenhum teste importa este módulo nem cita a mensagem (cobertura indireta — CLI/HTTP/subprocess — não verificada)
- Invariante: except: sem tipo tem 0 ocorrências em 65 arquivos python de produto (não introduzir)
- Invariante: eval() tem 0 ocorrências em 65 arquivos python de produto (não introduzir)
- Invariante: exec() tem 0 ocorrências em 65 arquivos python de produto (não introduzir)
- Invariante: os.system() tem 0 ocorrências em 65 arquivos python de produto (não introduzir)
- Invariante: pickle.load(s) tem 0 ocorrências em 65 arquivos python de produto (não introduzir)
- Invariante: subprocess com shell=True tem 0 ocorrências em 65 arquivos python de produto (não introduzir)
- Invariante: import * tem 0 ocorrências em 65 arquivos python de produto (não introduzir)
- Invariante: yaml.load sem Loader tem 0 ocorrências em 65 arquivos python de produto (não introduzir)

## Convenções e regras técnicas

- `setup.py` não introduz subprocess com shell=True, os.system(), eval(), exec(), except sem tipo, import *, pickle.load(s) nem yaml.load sem Loader (0 ocorrências hoje no Python de produto). — prova: `rg -n "shell=True|os\.system\(|\beval\(|\bexec\(|except:|import \*|pickle\.loads?\(|yaml\.load\(" setup.py`
- Os alvos do Makefile citados nos docs (setup, up, down, build, logs, status, clean, update, dev, help) não são renomeados nem removidos. — prova: `grep -cE "^(help|setup|up|down|build|logs|status|clean|update|dev):" Makefile`
- A imagem continua buildando após mudança em Dockerfile, docker-compose.yml, .dockerignore ou requirements.txt. — prova: `make build`
- Versão de readme.md, RELEASE.md e changelog.md sobe junto. — prova: `rg -n "version-v|^# Maestro-Orchestrator v" readme.md RELEASE.md`

## Armadilhas registradas

- setup.py falhava com 'no configuration file provided' quando não era executado a partir da raiz do projeto.
- setup.py quebrava no Windows por saída não UTF-8; e a instalação das dependências da TUI falhava em ambientes PEP 668 (Debian/Ubuntu/Raspbian).
- setup.py confundia socket Docker sem permissão com daemon parado.
- O build Docker quebrava por containers e processos antigos; a limpeza foi parar em setup.sh e depois em setup.py, que é o entry point real.
- O env_file do docker-compose.yml precisou voltar a um formato compatível com Compose legado, com mudança casada em setup.py e setup.sh.
- Chaves de API se perdiam ao reiniciar o container, e um .env.template ignorado pelo .gitignore deixava o onboarding sem configuração.
- O updater dentro do Docker só funcionou depois de passar a ler o arquivo VERSION gravado no build (sem .git na imagem).
- Rede Docker ambígua impedia subir o 4º nó do cluster em diante; porta do Redis compartilhado colidia com o Redis por stack.
- Versões divergentes entre changelog.md, readme.md, docs/roadmap.md e frontend/package.json exigiram correção dedicada.

## Notas por caminho

- `changelog.md`: Entradas antigas citam caminhos que não existem mais (backend/Dockerfile, frontend/Dockerfile, node_shards.json, data/prompt_templates.json); são registro histórico, não referência atual.
- `readme.md`: readme.md cita node_shards.json, e as linhas 147-148 citam IDs de modelo que o scan marcou como caminho inexistente; confira antes de copiar para outros docs.
- `CLUSTERING.md`: CLUSTERING.md muda junto com correções de spawn de cluster e da TUI (maestro/tui/app.py, maestro/instances.py); atualize-o quando o comportamento de cluster mudar.

## Termos do domínio (além do cartão do dono)

- `PluginContext` — Controlled access to Maestro internals (registry, R2, session logger, agent registration, hooks, events) (em `maestro/plugins/base.py`)
- `Deliberation Engine` — After collecting initial responses from all agents, each agent now reads what its peers said and produces a refined reply before any analysis runs. This transforms the parallel-collect pattern into an actual multi-round debate. (em `maestro/deliberation.py`)
- `Node CLI` — `python -m maestro.node_cli` for storage node operators (setup, start, status, verify, shards) (em `RELEASE.md`)
- `Weight State Snapshots` — Save, restore, diff, and delete system configuration snapshots. Captures plugin states, configs, active agents, runtime config overlay. (em `changelog.md`)
- `Interactive CLI` — Command-line REPL with full pipeline access (em `RELEASE.md`)
- `Event Bus` — Inter-plugin pub/sub with error isolation (em `RELEASE.md`)
- `Interactive Mode Selector` — Arrow-key terminal selector with colored highlights, replacing the plain numbered prompt and static command suggestions. Users can now pick TUI, CLI, or Web-UI mode without memorizing commands. Falls back to a numbered prompt when raw termi (em `changelog.md`)
- `Restart server button` — One-click restart after a successful update (em `RELEASE.md`)
- `Network tab` — Per-model mirror status, layer coverage bars, inference pipeline visualization, redundancy map, gap detection (em `RELEASE.md`)
- `Modular Plugin Architecture (Mod Manager)` — Full plugin lifecycle: discover, validate, load, enable, disable, unload, hot-reload. Plugin protocol (`MaestroPlugin` ABC), manifest validation, version compatibility checks, dependency resolution, and permission system. (em `changelog.md`)
- `Shard Map tab` — Visual grid of nodes × layer blocks with color-coded coverage and redundancy indicators (em `RELEASE.md`)
- `Shard Utilities` — Header parsing, layer index extraction, byte-range SHA-256 proofs, and shard descriptor generation for safetensors weight files (em `RELEASE.md`)
- `Update progress bar` — Visual feedback while updates are applied (em `RELEASE.md`)
- `Automatic Background Updater` — New `AutoUpdater` class runs as a background asyncio task, periodically polling the git remote for new commits at a configurable interval (10s–3600s). Supports auto-apply mode for seamless iterative development where the developer is active (em `changelog.md`)
- `Cluster-Aware Instance Spawning` — Pressing `+` in the TUI Instance screen now spawns fully functional shard/node cluster members instead of isolated Docker Compose stacks. The first instance becomes the **orchestrator**; every subsequent instance spawns as a **shard worker* (em `changelog.md`)
- `New Environment Variables` — `MAESTRO_UPDATE_INTERVAL` (poll interval in seconds, default 60), `MAESTRO_AUTO_APPLY_UPDATES` (auto-apply without confirmation). (em `changelog.md`)
- `Real byte-range proof challenges` — Node server hashes actual file bytes when shards are on disk (em `RELEASE.md`)
- `Default remote URL` — Auto-updater now defaults to the canonical GitHub repo (em `RELEASE.md`)
- `Dual Backend Modes` — Direct import (in-process, lowest latency) and HTTP client (connects to running server via SSE, supports multi-device clusters). (em `RELEASE.md`)
- `Live Cluster Dashboard` — New always-visible `ClusterDashboard` widget on the main TUI screen shows running cluster instances with BTOP-style spinning health indicators, color-coded roles (cyan orchestrator, yellow shards), port/IP info, and a cluster summary line. (em `changelog.md`)
- `New dependencies` — `textual>=0.85.0` and `rich>=13.0.0` added to `backend/requirements.txt` (em `changelog.md`)
- `Node auto-registration` — Node server registers with the orchestrator and sends heartbeats automatically (em `RELEASE.md`)
- `Roadmap updated` — "Storage Network Dashboard" moved from v0.7 goals to completed milestones. (em `changelog.md`)
- `SSE Response Streaming` — New `POST /api/ask/stream` endpoint returns Server-Sent Events as each pipeline stage completes (agent responses, dissent, NCG, consensus, R2). The frontend now renders results progressively instead of waiting for the full pipeline to finis (em `changelog.md`)
- `Switch styling` — deliberation toggle switch uses transparent background (em `RELEASE.md`)
- `TUI mode in startup wrapper` — `entrypoint.py` now offers TUI as a third option alongside Web-UI and CLI. Selectable via dialog menu or `MAESTRO_MODE=tui`. (em `RELEASE.md`)

- Mais 230 termo(s)/regra(s): `.specialists/bin/cs-mem search "<consulta>" --kind term|rule --paths ".github/**,setup.py,setup.sh,.dockerignore,.env.example,.gitignore,ARCHITECTURE.md,CLUSTERING.md,CONTRIBUTING.md,Dockerfile,LICENSE.md,Makefile,ORCHESTRA.md,PROJECT_EXPLAINED.md,RELEASE.md,ROADMAP.md,changelog.md,commercial_license.md,dashboard.html,docker-compose.yml,readme.md,requirements.txt,use_policy.md"`.
