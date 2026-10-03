---
paths:
  - "tests/**"
---
<!-- codebase-specialists:generated; não edite: altere .specialists/team.json5 e rode `cs.py emit` -->

# Território de `qa`

Dono de escrita destes arquivos: `qa` (dev). Mudança aqui respeita o que segue; o cartão do dono tem missão e recusas.

## Invariantes

- Limite DEFAULT_CHALLENGE_WINDOW_SECONDS = 60 (business) em maestro/storage_proof.py; coberto por tests/test_storage_proof.py (o teste chama `StorageProofEngine` e confere o resultado — valor ou exceção esperados, derivados da regra)
- Limite DEFAULT_MAX_LATENCY_MS = 5000 (business) em maestro/storage_proof.py; citado em teste tests/test_storage_proof.py (`DEFAULT_MAX_LATENCY_MS`)
- Limite EVICTION_THRESHOLD = 0.3 (business) em maestro/storage_proof.py; coberto por tests/test_storage_proof.py (o teste chama `StorageProofEngine` e confere o resultado — valor ou exceção esperados, derivados da regra)
- Limite PROBATION_THRESHOLD = 0.7 (business) em maestro/storage_proof.py; coberto por tests/test_storage_proof.py (o teste chama `StorageProofEngine` e confere o resultado — valor ou exceção esperados, derivados da regra)
- Limite QUORUM_THRESHOLD = 0.66 (business) em maestro/aggregator.py; citado em teste tests/test_orchestration.py (`QUORUM_THRESHOLD`)
- Limite SIMILARITY_THRESHOLD = 0.5 (business) em maestro/aggregator.py; citado em teste tests/test_code_injection.py (`SIMILARITY_THRESHOLD`)
- Limite STALE_TIMEOUT = 15.0 (technical) em maestro/lan_discovery.py; coberto por tests/test_lan_discovery.py (o teste chama `is_alive` e confere o resultado — valor ou exceção esperados, derivados da regra)
- Estados de AdjacencyState (maestro/lan_discovery.py): DISCOVERED, HANDSHAKE_SENT, HANDSHAKE_ACKED, CONFIRMED, STALE; citado em teste tests/test_lan_discovery.py (`AdjacencyState`)
- Estados de PluginState (maestro/plugins/base.py): DISCOVERED, VALIDATED, LOADED, ENABLED, DISABLED, ERROR, UNLOADED; citado em teste tests/test_mod_manager.py (`PluginState`)
- Regra expressa em teste test_analysis_only_mode (tests/test_self_improvement.py): analysis only mode
- Regra expressa em teste test_blocked_category_skipped (tests/test_code_injection.py): blocked category skipped
- Regra expressa em teste test_discover_skips_invalid_manifests (tests/test_mod_manager.py): discover skips invalid manifests
- Regra expressa em teste test_injectable_architecture_blocked (tests/test_code_injection.py): injectable architecture blocked
- Regra expressa em teste test_injectable_rejected_status (tests/test_code_injection.py): injectable rejected status
- Regra expressa em teste test_injectable_unknown_category_blocked (tests/test_code_injection.py): injectable unknown category blocked
- Regra expressa em teste test_invalid_hook_point_raises (tests/test_mod_manager.py): invalid hook point raises
- Regra expressa em teste test_is_adjacent_requires_confirmed_and_alive (tests/test_lan_discovery.py): is adjacent requires confirmed and alive
- Regra expressa em teste test_list_sessions_limit_offset (tests/test_orchestration.py): list sessions limit offset
- Regra expressa em teste test_raises_when_docker_run_fails (tests/test_instances.py): raises when docker run fails
- Regra expressa em teste test_rate_limit_allows (tests/test_code_injection.py): rate limit allows
- Regra expressa em teste test_rate_limit_blocks (tests/test_code_injection.py): rate limit blocks
- Regra expressa em teste test_rate_limit_blocks_injection (tests/test_code_injection.py): rate limit blocks injection
- Regra expressa em teste test_restore_nonexistent_fails (tests/test_weight_snapshots.py): restore nonexistent fails
- Regra expressa em teste test_validate_wrong_hash_fails (tests/test_storage_proof.py): validate wrong hash fails
- Regra (validação) em maestro/deliberation.py: quando `if rounds < 1:` (linha 138) → ValueError("rounds must be >= 1, got {rounds}") (linha 139); alcançável por teste: tests/test_orchestration.py chama `run_orchestration_async` (se o teste isola esta regra não é determinável mecanicamente — confira antes de afirmar)
- Regra (validação) em maestro/instances.py: quando `if not _is_port_available(SHARED_REDIS_PORT):` (linha 244) → RuntimeError("Port {SHARED_REDIS_PORT} is already in use by another process. ") (linha 245); coberto por tests/test_instances.py (o teste confere a mensagem)
- Regra (validação) em maestro/shard_manager.py: → ImportError("huggingface_hub is required for downloading shards.\n"); alcançável por teste: tests/test_shard_manager.py chama `ShardManager` (se o teste isola esta regra não é determinável mecanicamente — confira antes de afirmar)
- Regra (validação) em maestro/shard_utils.py: quando `if len(header_size_bytes) < 8:` (linha 44) → ValueError("File too small to be safetensors: {filepath}") (linha 45); coberto por tests/test_shard_utils.py (o teste confere a mensagem)
- Entrevista test-gate: Qual é o comando oficial de teste/gate antes de merge? (não há CI nem config pytest; CONTRIBUTING.md cita pytest tests/ em prosa) — resposta do dono (literal): pytest tests/
- 1 arquivos de teste sem assert detectável: tests/__init__.py
- tests: 18 arquivos de teste (python), 422 casos, 916 asserts; maiores: tests/test_orchestration.py (192), tests/test_self_improvement.py (129), tests/test_code_injection.py (73)

## Convenções e regras técnicas

- Gate antes de merge: rodar pytest sobre tests/ inteiro e exigir sucesso. — prova: `pytest tests/`
- Arquivo de teste novo fica em tests/ com prefixo test_ e contém assert.
- Python com 4 espaços, LF, newline final, funções e arquivos em snake_case, classes em PascalCase, sem from __future__ import annotations.

## Armadilhas registradas

- A colisão da porta do Redis compartilhado com o Redis por stack no spawn de cluster foi corrigida mudando maestro/instances.py e tests/test_instances.py juntos: mudança em instances quebra esses testes.
- A correção do spawn de instâncias como membros shard/node do cluster também reescreveu tests/test_instances.py junto com maestro/instances.py e maestro/node_server.py.
- A entrada do NCG mexeu em maestro/aggregator.py e maestro/orchestrator.py e exigiu ajuste em tests/test_orchestration.py.
- A correção do pipeline de self-improvement tocou oito módulos (r2, magi, magi_vir, optimization, introspect, self_improve, api_self_improve) e tests/test_self_improvement.py na mesma correção.
- O crash da TUI e o seletor de modo interativo alteraram entrypoint.py e tests/test_startup.py juntos.

## Notas por caminho

- `tests/test_storage_proof.py`, `maestro/storage_proof.py`: Limiares de reputação e desafio de storage proof são área protegida pelo dono: valor esperado só muda com aprovação humana.
