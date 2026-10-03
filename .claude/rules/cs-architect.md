---
paths:
  - "docs/**"
---
<!-- codebase-specialists:generated; não edite: altere .specialists/team.json5 e rode `cs.py emit` -->

# Território de `architect`

Dono de escrita destes arquivos: `architect` (design). Mudança aqui respeita o que segue; o cartão do dono tem missão e recusas.

## Convenções e regras técnicas

- Os cabeçalhos de versão de `docs/agents.md`, `docs/mod-manager.md`, `docs/quorum_logic.md`, `docs/storage-network.md` e `docs/roadmap.md` precisam bater com `maestro/__init__.py`. — prova: `rg -n "^\*\*(Current )?Version:\*\*" docs`
- Os valores 0.66/0.5 em `docs/quorum_logic.md` saem de `maestro/aggregator.py`. — prova: `rg -n "QUORUM_THRESHOLD =|SIMILARITY_THRESHOLD =" maestro/aggregator.py`
- As faixas trusted/probation/evicted em `docs/storage-network.md` saem de PROBATION_THRESHOLD e EVICTION_THRESHOLD em `maestro/storage_proof.py`. — prova: `rg -n "_THRESHOLD =" maestro/storage_proof.py`
- Comandos de operação citados nos docs se limitam aos alvos existentes do Makefile e aos módulos maestro.tui, maestro.cli, maestro.node_cli e maestro.cli_keys.

## Armadilhas registradas

- A cada bump, strings de versão ficaram defasadas nos docs e precisaram de commits só de correção ('Fix version inconsistencies' para v0.4.3 e para v0.6.3, este último tocando também `maestro/plugins/manager.py`, que guarda _MAESTRO_VERSION).
- Os docs mais quentes acumulam muitas correções: `docs/roadmap.md` (41 commits, 22 correções), `docs/quorum_logic.md` (16), `docs/agents.md` (15), `docs/storage-network.md` e `docs/ui-guide.md` (14 cada). Houve passadas inteiras só para consistência doc↔código e links quebrados.
- Mudanças em spawn de cluster e em Redis (porta compartilhada, rede Docker ambígua no 4º nó) vieram junto com reescritas de `docs/troubleshooting.md` e `docs/deployment.md`. Mexer em `maestro/instances.py` costuma deixar esses docs desatualizados.

## Notas por caminho

- `docs/**`: O verificador de docs marca como STALE IDs de modelo (`models/gemini-2.5-flash`, `meta-llama/llama-3.3-70b-instruct`) e arquivos que o código gera em runtime (`data/node_shards.json`, `data/rollbacks/log.json`, `data/runtime_config.json`). Confira em `maestro` antes de apagar.
- `docs/mod-manager.md`: Muda junto com `maestro/plugins/manager.py` (15 commits em conjunto).

## Termos do domínio (além do cartão do dono)

- `CLI` — Type `/nodes` to see registered storage nodes (em `docs/storage-network.md`)
- `R2 Engine` — - Scores each session in real time, detects dissent and improvement signals (em `maestro/r2.py`)
- `suspicious` — silent collapse detected, or very high agreement paired with high NCG drift (em `docs/r2-engine.md`)
- `strong` — quorum met, low drift, no collapse, no outliers, no flags (em `docs/r2-engine.md`)
- `Node Server` — Standalone FastAPI server for storage nodes. Endpoints: `/infer`, `/challenge`, `/health`, `/heartbeat`, `/shards` (em `RELEASE.md`)
- `MAGI_VIR` — Virtual Instance Runtime — sandboxed testing environment that runs benchmark prompts through baseline and optimized configurations, compares results, and produces promotion/rejection recommendations (em `maestro/magi_vir.py`)
- `Injection Guard` — Safety rails for the injection system — category whitelist (blocks `architecture` and `pipeline` by default), bounds enforcement at injection time, rate limiting (default 5/hour), and post-injection smoke test with automatic rollback on gra (em `maestro/injection_guard.py`)
- `ShardAgent` — Distributed inference agent with the same `fetch(prompt) -> str` interface as centralized agents (em `maestro/agents/shard.py`)
- `GPT-4o` — OpenAI (`gpt-4o`) (em `docs/architecture.md`)
- `Claude Sonnet 4.6` — Anthropic (`claude-sonnet-4-6`) (em `docs/architecture.md`)
- `Storage Node Registry` — Shard-aware topology, pipeline construction, redundancy mapping, heartbeat tracking, reputation integration (em `RELEASE.md`)
- `Storage Proof Engine` — Three proof types: Proof-of-Replication (byte-range hash), Proof-of-Residency (latency probe), Proof-of-Inference (canary inference) (em `maestro/storage_proof.py`)
- `Gemini 2.5 Flash` — Google (`models/gemini-2.5-flash`) (em `docs/architecture.md`)
- `Llama 3.3 70B` — OpenRouter (`meta-llama/llama-3.3-70b-instruct`) (em `docs/architecture.md`)
- `Smoke test` — After injection, runs a benchmark prompt through the full pipeline. If the R2 grade drops below `acceptable`, the guard signals automatic rollback. (em `docs/self-improvement-pipeline.md`)
- `weak` — quorum not met or high internal dissent (em `docs/r2-engine.md`)
- `acceptable` — quorum met with some concerns (outliers, compression alerts) (em `docs/r2-engine.md`)
- ``setup.py`` — Cross-platform setup script (Docker check, Python package verification and auto-install, build, health wait, browser open). Works on Windows, macOS, and Linux (em `docs/deployment.md`)
- `Verification` — Introduce layers of human and analog verification to test synthetic claims against the physical world. (em `docs/maestro-whitepaper.md`)
- `ShardDescriptor` — Build `ShardDescriptor` objects from actual files on disk (em `maestro/storage_proof.py`)
- `Weight State Snapshots` — Save, restore, diff, and delete system configuration snapshots. Captures plugin states, configs, active agents, runtime config overlay. (em `changelog.md`)
- `Compute Node Registry` — JSON-based registry for distributed validation across multiple Maestro nodes (em `maestro/magi_vir.py`)
- `Confidence trend` — is confidence improving or declining across recent sessions? (em `docs/r2-engine.md`)
- `Grade distribution` — how many sessions are strong vs. weak vs. suspicious? (em `docs/r2-engine.md`)
- `Recurring signals` — which signal types appear repeatedly? (em `docs/r2-engine.md`)
- `ShardNet` — Distributed proof-of-storage inference across storage nodes (em `docs/architecture.md`)
- `HTTP client` — connects to a running Maestro server via SSE, supports multi-device clusters (em `docs/architecture.md`)
- `Pipeline construction` — because a single WeightNode rarely holds a complete model; inference requires composing WeightNodes (em `ARCHITECTURE.md`)
- ``docker-compose.yml`` — - `.env` file is optional (`required: false`) -- keys can be set via the Web-UI (em `docs/deployment.md`)
- `Direct import` — imports orchestrator modules in-process, lowest latency (em `docs/architecture.md`)
- `Rate limiting` — Maximum 5 injections per hour (configurable). Prevents runaway self-modification. (em `docs/self-improvement-pipeline.md`)
- `Auto-registration` — If `MAESTRO_ORCHESTRATOR_URL` is set, the node automatically registers on startup and sends periodic heartbeats (em `docs/storage-network.md`)
- ``Dockerfile`` — - Multi-stage build: Stage 1 builds the Vite frontend, Stage 2 sets up the Python backend and copies the built frontend as static assets (em `docs/deployment.md`)
- `Default on` — deliberation runs automatically with 1 round unless you opt out via `deliberation_enabled: false` in the API request. (em `RELEASE.md`)
- `Non-fatal` — if any agent errors during deliberation, it keeps its previous response and the pipeline continues. (em `RELEASE.md`)
- `Optimization Engine` — Translates introspection results into structured `OptimizationProposal` objects with threshold strategies, temperature strategies, and architecture refactoring rules (em `maestro/optimization.py`)
- `Contested tokens` — Where the chosen token barely beat its top alternative (em `docs/ncg.md`)
- `Plugin Protocol` — `MaestroPlugin` ABC with `activate()`, `deactivate()`, `health_check()`, and `on_config_change()` (em `RELEASE.md`)
- `Transparency` — Every session is logged. Every choice can be traced and evaluated. (em `docs/index.md`)
- `Configurable rounds` — set `deliberation_rounds` (1–5) to run multiple passes of cross-agent debate. Each round costs one additional API call per agent. (em `RELEASE.md`)
- `Pipeline Hooks` — 8 hook points in the orchestration pipeline (`pre_orchestration`, `post_agent_response`, `pre_aggregation`, `post_aggregation`, `pre_r2_scoring`, `post_r2_scoring`, `pre_session_save`, `post_session_save`). Hooks run in registration order, (em `changelog.md`)
- `Code Injection Engine` — Applies validated proposals to the running system via three paths — runtime parameter mutation (in-memory `setattr`), AST-based source patching (persistent across restarts), and config overlay writes (`data/runtime_config.json`). Every inje (em `docs/architecture.md`)
- `Code Introspection Engine` — Three-tier source analysis — static AST parsing with complexity metrics, signal-to-code mapping rules, and token-level behavior analysis from R2 ledger data (em `docs/architecture.md`)

- Mais 67 termo(s)/regra(s): `.specialists/bin/cs-mem search "<consulta>" --kind term|rule --paths "docs/**"`.
