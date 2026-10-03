---
name: qa-playbooks
description: "Procedimentos passo a passo de qa neste repo. Use quando qa for executar: Cobrir regra de limite sem asserção (ex.: HANDSHAKE_TIMEOUT); Testar maestro/instances.py sem Docker nem porta real; Testar orquestração/deliberação sem chave de provedor"
---
<!-- codebase-specialists:generated; não edite: altere .specialists/team.json5 e rode `cs.py emit` -->

# Playbooks de `qa`

Procedimentos do território de `qa`, extraídos de `.specialists/team.json`.

## Cobrir regra de limite sem asserção (ex.: HANDSHAKE_TIMEOUT)

1. Ler a constante e quem a usa em maestro/lan_discovery.py (HANDSHAKE_TIMEOUT = 5.0, estados de AdjacencyState).
2. Adicionar em tests/test_lan_discovery.py um caso que chame o símbolo no corpo do teste (não só em setUp/helper) e confira o valor ou a transição esperada, para o caso ser rastreável.
3. Rodar o gate do dono restrito ao arquivo e depois sobre tests/ inteiro.

## Testar maestro/instances.py sem Docker nem porta real

1. Seguir o padrão de tests/test_instances.py: aplicar patch em maestro.instances.subprocess.run e em maestro.instances._is_port_available.
2. Para porta ocupada, conferir RuntimeError com a mensagem de porta em uso; para falha do docker run, encadear side_effect com os retornos de inspect, rm e run.
3. Rodar o gate do dono sobre tests/test_instances.py e tests/.

## Testar orquestração/deliberação sem chave de provedor

1. Montar agentes com MockAgent de maestro/agents/mock.py (como tests/test_orchestrator_snapshot.py e tests/test_plugin_hooks.py fazem).
2. Para NCG usar MockHeadlessGenerator de maestro/ncg/generator.py.
3. Para a validação de rounds, chamar run_orchestration_async com rounds < 1 e conferir ValueError com a mensagem 'rounds must be >= 1' em tests/test_orchestration.py.
