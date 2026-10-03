---
name: dev-storage-network-playbooks
description: "Procedimentos passo a passo de dev-storage-network neste repo. Use quando dev-storage-network for executar: Corrigir falha no spawn de nó de cluster (maestro/instances.py); Mudar desafio ou reputação de storage proof; Adicionar ou alterar endpoint do Node Server"
---
<!-- codebase-specialists:generated; não edite: altere .specialists/team.json5 e rode `cs.py emit` -->

# Playbooks de `dev-storage-network`

Procedimentos do território de `dev-storage-network`, extraídos de `.specialists/team.json`.

## Corrigir falha no spawn de nó de cluster (maestro/instances.py)

1. Leia em maestro/instances.py a limpeza pré-spawn (_ensure_cluster_network, _is_port_available e a remoção da rede compose do slot) antes de mudar a ordem dos passos.
2. Remova redes duplicadas pelo ID, depois de listá-las com docker network ls --filter name=<proj>_maestro-net; remover pelo nome falha quando há duplicatas.
3. Não coloque REDIS_PORT no ambiente do compose da instância: o Redis compartilhado já ocupa SHARED_REDIS_PORT.
4. Cubra o caso em tests/test_instances.py (o teste confere a mensagem do RuntimeError de porta ocupada) e rode pytest tests/test_instances.py.

## Mudar desafio ou reputação de storage proof

1. Pare e peça aprovação humana: storage proof / rede é área protegida.
2. Altere StorageProofEngine em maestro/storage_proof.py; os limiares são atributos de classe (PROBATION_THRESHOLD, EVICTION_THRESHOLD, DEFAULT_CHALLENGE_WINDOW_SECONDS, DEFAULT_MAX_LATENCY_MS).
3. Ajuste tests/test_storage_proof.py, que exercita os limiares e test_validate_wrong_hash_fails, e rode pytest tests/test_storage_proof.py.
4. Como maestro/storage_proof.py é importado por 9 arquivos, rode pytest tests/ antes de entregar.

## Adicionar ou alterar endpoint do Node Server

1. Edite as rotas em maestro/node_server.py (/infer, /challenge, /health, /heartbeat, /shards, /task, /result).
2. Se o commit muda a versão, atualize junto a string de versão do FastAPI em maestro/node_server.py e _MAESTRO_VERSION em maestro/plugins/manager.py; a mudança em maestro/plugins/manager.py fica com o dono desse território.
3. Confira se docs/storage-network.md, changelog.md e docs/roadmap.md precisam acompanhar: eles mudam junto com maestro/node_server.py na maioria dos commits.
