<!-- cs-report acceptance=4eaa09912af1157cd8dbb249c4f3c35ac452a87b771556e65a57779a6122c629 -->
# Relatório codebase-specialists

Decisão: GO — gates GO; decidido por GlauberCasttro em 2026-10-03T21:03:33+00:00

Modo: --fast (padrão: sem mesa redonda e/ou sem refino; 4 sub-etapa(s) pulada(s))

## Pulos (caminho --fast)

Modo --fast: sem mesa redonda e/ou com sondas reduzidas — time NÃO certificado como especialista.

- `rt.1` (round-table-deep-specialize): --fast (padrão)
- `rt.2` (round-table-deep-specialize): --fast (padrão)
- `rt.3` (round-table-deep-specialize): --fast (padrão)
- `rt.4` (round-table-deep-specialize): --fast (padrão)

## Time

| agente | kind | território | território (sonda) | cross | alucinações | delta | status | modo fechado (sinal) |
|---|---|---|---|---|---|---|---|---|
| dev-consensus | dev | `maestro/orchestrator.py`, `maestro/aggregator.py`, `maestro/deliberation.py`, `maestro/dissent.py`, `maestro/session.py`, `maestro/api_sessions.py`, `maestro/r2.py`, `maestro/ncg/**`, `maestro/agents/__init__.py`, `maestro/agents/base.py`, `maestro/agents/aria.py`, `maestro/agents/sol.py`, `maestro/agents/prism.py`, `maestro/agents/tempagent.py`, `maestro/agents/mock.py`, `maestro/__init__.py` | 0.8889 | 1.0 | 0 | 0.7 | especialista | - |
| dev-self-improve | dev | `maestro/magi.py`, `maestro/magi_vir.py`, `maestro/api_magi.py`, `maestro/introspect.py`, `maestro/optimization.py`, `maestro/applicator.py`, `maestro/rollback.py`, `maestro/injection_guard.py`, `maestro/self_improve.py`, `maestro/api_self_improve.py` | 1.0 | 1.0 | 0 | 0.85 | especialista | - |
| dev-storage-network | dev | `maestro/storage_proof.py`, `maestro/shard_manager.py`, `maestro/shard_registry.py`, `maestro/shard_utils.py`, `maestro/api_storage.py`, `maestro/node_server.py`, `maestro/node_cli.py`, `maestro/lan_discovery.py`, `maestro/cluster.py`, `maestro/api_cluster.py`, `maestro/instances.py`, `maestro/api_instances.py`, `maestro/state_bus.py`, `maestro/agents/shard.py`, `maestro/agents/mock_shard_node.py` | 0.875 | 1.0 | 0 | 0.7 | especialista | - |
| dev-platform | dev | `backend/**`, `entrypoint.py`, `maestro/cli.py`, `maestro/cli_keys.py`, `maestro/keyring.py`, `maestro/api_keys.py`, `maestro/selector.py`, `maestro/tui/**`, `maestro/plugins/**`, `maestro/api_plugins.py`, `maestro/updater.py`, `maestro/api_update.py`, `maestro/dependency_resolver.py`, `data/**` | 1.0 | 1.0 | 0 | 0.7 | especialista | - |
| dev-frontend | dev | `frontend/**` | 0.9 | 1.0 | 0 | 0.8 | especialista | - |
| dev-maestros | dev | `maestros/**` | 1.0 | 1.0 | 0 | 0.85 | especialista | - |
| qa | dev | `tests/**` | 1.0 | 1.0 | 0 | 0.8 | especialista | - |
| architect | design | `docs/**` | 1.0 | 1.0 | 0 | 0.85 | especialista | - |
| ops | ops | `.github/**`, `setup.py`, `setup.sh`, `.dockerignore`, `.env.example`, `.gitignore`, `ARCHITECTURE.md`, `CLUSTERING.md`, `CONTRIBUTING.md`, `Dockerfile`, `LICENSE.md`, `Makefile`, `ORCHESTRA.md`, `PROJECT_EXPLAINED.md`, `RELEASE.md`, `ROADMAP.md`, `changelog.md`, `commercial_license.md`, `dashboard.html`, `docker-compose.yml`, `readme.md`, `requirements.txt`, `use_policy.md` | 1.0 | 0.8571 | 0 | 0.8 | especialista | - |
| reviewer | gate | sem escrita | 1.0 | 1.0 | 0 | 0.85 | especialista | - |
| security | gate | sem escrita | 1.0 | 1.0 | 0 | 0.8 | especialista | - |
| po | product | sem escrita | 1.0 | 1.0 | 0 | 0.7 | especialista | - |

## Garantia por plataforma

| plataforma | enforcement | o que garante |
|---|---|---|
| claude-code | hook | hook: bloqueia ANTES da escrita/despacho (guards cs-guard.sh); programa arbitrário só é pego depois (verify) |

## Lacunas declaradas (o dono não soube responder)

- nenhuma

## Como usar

`.specialists/bin/cs-state next` · `.specialists/bin/cs-mem search "<assunto>"` · `.specialists/bin/cs-session save|load`
