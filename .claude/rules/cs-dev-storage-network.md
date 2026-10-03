---
paths:
  - "maestro/storage_proof.py"
  - "maestro/shard_manager.py"
  - "maestro/shard_registry.py"
  - "maestro/shard_utils.py"
  - "maestro/api_storage.py"
  - "maestro/node_server.py"
  - "maestro/node_cli.py"
  - "maestro/lan_discovery.py"
  - "maestro/cluster.py"
  - "maestro/api_cluster.py"
  - "maestro/instances.py"
  - "maestro/api_instances.py"
  - "maestro/state_bus.py"
  - "maestro/agents/shard.py"
  - "maestro/agents/mock_shard_node.py"
---
<!-- codebase-specialists:generated; não edite: altere .specialists/team.json5 e rode `cs.py emit` -->

# Território de `dev-storage-network`

Dono de escrita destes arquivos: `dev-storage-network` (dev). Mudança aqui respeita o que segue; o cartão do dono tem missão e recusas.

## Invariantes

- Limite DEFAULT_CHALLENGE_WINDOW_SECONDS = 60 (business) em maestro/storage_proof.py; coberto por tests/test_storage_proof.py (o teste chama `StorageProofEngine` e confere o resultado — valor ou exceção esperados, derivados da regra)
- Limite DEFAULT_MAX_LATENCY_MS = 5000 (business) em maestro/storage_proof.py; citado em teste tests/test_storage_proof.py (`DEFAULT_MAX_LATENCY_MS`)
- Limite EVICTION_THRESHOLD = 0.3 (business) em maestro/storage_proof.py; coberto por tests/test_storage_proof.py (o teste chama `StorageProofEngine` e confere o resultado — valor ou exceção esperados, derivados da regra)
- Limite HANDSHAKE_TIMEOUT = 5.0 (technical) em maestro/lan_discovery.py; nenhum caso de teste alcança esta regra mecanicamente (o módulo é importado por tests/test_lan_discovery.py, mas nenhum caso confere a mensagem nem chama o símbolo no corpo do teste; chamadas via setUp/helpers não são rastreadas)
- Limite PROBATION_THRESHOLD = 0.7 (business) em maestro/storage_proof.py; coberto por tests/test_storage_proof.py (o teste chama `StorageProofEngine` e confere o resultado — valor ou exceção esperados, derivados da regra)
- Limite STALE_TIMEOUT = 15.0 (technical) em maestro/lan_discovery.py; coberto por tests/test_lan_discovery.py (o teste chama `is_alive` e confere o resultado — valor ou exceção esperados, derivados da regra)
- Estados de AdjacencyState (maestro/lan_discovery.py): DISCOVERED, HANDSHAKE_SENT, HANDSHAKE_ACKED, CONFIRMED, STALE; citado em teste tests/test_lan_discovery.py (`AdjacencyState`)
- Regra (validação) em maestro/instances.py: quando `if not _is_port_available(SHARED_REDIS_PORT):` (linha 244) → RuntimeError("Port {SHARED_REDIS_PORT} is already in use by another process. ") (linha 245); coberto por tests/test_instances.py (o teste confere a mensagem)
- Regra (validação) em maestro/shard_manager.py: → ImportError("huggingface_hub is required for downloading shards.\n"); alcançável por teste: tests/test_shard_manager.py chama `ShardManager` (se o teste isola esta regra não é determinável mecanicamente — confira antes de afirmar)
- Regra (validação) em maestro/shard_utils.py: quando `if len(header_size_bytes) < 8:` (linha 44) → ValueError("File too small to be safetensors: {filepath}") (linha 45); coberto por tests/test_shard_utils.py (o teste confere a mensagem)
- Entrevista protected-areas: Há áreas que exigem aprovação humana antes de mudar (ex.: limiares QUORUM_THRESHOLD/SIMILARITY_THRESHOLD, storage_proof, self_improvement/code_injection, updater, licença)? — resposta do dono (literal): Limiares de consenso, Self-improvement, Storage proof / rede
- Invariante: except: sem tipo tem 0 ocorrências em 65 arquivos python de produto (não introduzir)
- Invariante: eval() tem 0 ocorrências em 65 arquivos python de produto (não introduzir)
- Invariante: exec() tem 0 ocorrências em 65 arquivos python de produto (não introduzir)
- Invariante: os.system() tem 0 ocorrências em 65 arquivos python de produto (não introduzir)
- Invariante: pickle.load(s) tem 0 ocorrências em 65 arquivos python de produto (não introduzir)
- Invariante: subprocess com shell=True tem 0 ocorrências em 65 arquivos python de produto (não introduzir)
- Invariante: import * tem 0 ocorrências em 65 arquivos python de produto (não introduzir)
- Invariante: yaml.load sem Loader tem 0 ocorrências em 65 arquivos python de produto (não introduzir)

## Convenções e regras técnicas

- Gate oficial antes de merge, declarado pelo dono; não há CI nem configuração de pytest no repo. — prova: `pytest tests/`
- Mudança em maestro/storage_proof.py mantém tests/test_storage_proof.py verde, incluindo a rejeição de hash errado. — prova: `pytest tests/test_storage_proof.py`
- is_adjacent em maestro/lan_discovery.py exige estado CONFIRMED e peer vivo. — prova: `pytest tests/test_lan_discovery.py`
- Zero subprocess com shell=True e zero os.system em maestro/**. — prova: `rg -n "shell\s*=\s*True|\bos\.system\(" "maestro/"`
- HANDSHAKE_TIMEOUT = 5.0 em maestro/lan_discovery.py não é alcançado por nenhum teste: quem mudar esse valor escreve o teste.

## Armadilhas registradas

- Remover a rede compose do slot pelo nome falha com 'network X is ambiguous' quando sobrou rede duplicada de um teardown parcial, e isso bloqueou o spawn do 4º nó em diante. A correção lista as redes e remove cada uma pelo ID.
- Definir REDIS_PORT no ambiente do compose da instância fez o Redis da stack subir na mesma porta 6399 do Redis compartilhado ('port is already allocated'). A correção também passou a usar compose up --no-deps.
- Sem limpeza pré-spawn, containers órfãos de uma sessão derrubada mantinham a porta 8000 presa. Por isso spawn() derruba o projeto do slot, remove o container que segura a porta e valida a porta antes do compose up.
- asyncio.get_event_loop() gerava avisos de deprecação em maestro/lan_discovery.py e maestro/api_instances.py; o padrão do território é asyncio.get_running_loop().
- maestro/node_server.py é hotspot (21 commits, 12 de correção) e muda junto com maestro/plugins/manager.py em 86% dos commits, por bumps de versão e endpoints que faltavam; esquecer o par deixa versão ou API inconsistente.

## Notas por caminho

- `maestro/instances.py`, `maestro/api_instances.py`: O spawn de instância depende de rede Docker compartilhada (CLUSTER_NETWORK) e de um Redis compartilhado em SHARED_REDIS_PORT. Quem tocar aqui não injeta REDIS_PORT no compose e remove redes duplicadas pelo ID.
- `maestro/node_server.py`: Mudança de versão aqui acompanha _MAESTRO_VERSION em maestro/plugins/manager.py e as entradas em changelog.md e docs/roadmap.md.

## Termos do domínio (além do cartão do dono)

- `node` (em `maestro/api_storage.py`)
- `health` (em `backend/main.py`)
- `proof` (em `maestro/api_cluster.py`)
- `task` (em `maestro/node_server.py`)
- `download-status` (em `frontend/src/maestroUI.tsx`)
- `dispatch` (em `maestro/api_cluster.py`)
- `ChallengeRequest` (em `maestro/api_storage.py`)
- `result` (em `maestro/node_server.py`)
- `info` (em `maestro/node_server.py`)
- `pipeline` (em `maestro/api_storage.py`)
- `cluster` (em `maestro/node_server.py`)
- `network` (em `maestro/api_storage.py`)
- `reputation` (em `maestro/api_storage.py`)
- `register` (em `maestro/api_storage.py`)
- `models` (em `maestro/api_storage.py`)
- `verify` (em `maestro/api_storage.py`)
- `peers` (em `maestro/api_storage.py`)
- `stop` (em `maestro/api_instances.py`)
- `WeightHost` (em `maestro/shard_registry.py`)
- `spawn` (em `maestro/api_instances.py`)

- Mais 40 termo(s)/regra(s): `.specialists/bin/cs-mem search "<consulta>" --kind term|rule --paths "maestro/storage_proof.py,maestro/shard_manager.py,maestro/shard_registry.py,maestro/shard_utils.py,maestro/api_storage.py,maestro/node_server.py,maestro/node_cli.py,maestro/lan_discovery.py,maestro/cluster.py,maestro/api_cluster.py,maestro/instances.py,maestro/api_instances.py,maestro/state_bus.py,maestro/agents/shard.py,maestro/agents/mock_shard_node.py"`.
