---
name: architect-playbooks
description: "Procedimentos passo a passo de architect neste repo. Use quando architect for executar: Alinhar versão nos docs após bump; Tratar um aviso STALE de caminho em doc; Documentar limiar ou estado de domínio"
---
<!-- codebase-specialists:generated; não edite: altere .specialists/team.json5 e rode `cs.py emit` -->

# Playbooks de `architect`

Procedimentos do território de `architect`, extraídos de `.specialists/team.json`.

## Alinhar versão nos docs após bump

1. Ler a versão em `maestro/__init__.py` (o bump de v7.4.0 tocou esse arquivo junto com os docs).
2. Rodar `rg -n "^\*\*(Current )?Version:\*\*" docs` e comparar: `docs/agents.md`, `docs/mod-manager.md`, `docs/quorum_logic.md` e `docs/storage-network.md` ainda dizem v7.3.0, e `docs/roadmap.md` diz v7.4.0.
3. Atualizar cabeçalho e **Last Updated:** nos quatro docs em conjunto, porque eles mudam juntos no histórico.
4. Listar para o dono os arquivos fora do território que costumam acompanhar o bump: `readme.md`, `changelog.md`, `RELEASE.md`.

## Tratar um aviso STALE de caminho em doc

1. Antes de remover a referência, procurar o nome no código: `rg -n "node_shards.json" maestro` (ele é o default de MAESTRO_SHARD_CONFIG em `maestro/node_server.py` e `maestro/node_cli.py`) e `rg -n "rollbacks" maestro/rollback.py`.
2. Se o código cria o arquivo em runtime, manter a referência no doc e deixar claro que o arquivo é gerado.
3. Se o aviso for um ID de modelo de provedor (models/gemini-2.5-flash, meta-llama/llama-3.3-70b-instruct), não tratar como caminho.
4. Só remover a referência quando o `rg` em `maestro` vier vazio.

## Documentar limiar ou estado de domínio

1. Ler a constante na fonte: `rg -n "_THRESHOLD =" maestro/aggregator.py maestro/storage_proof.py`, e as enums em `maestro/lan_discovery.py` e `maestro/plugins/base.py`.
2. Comparar com o doc: `docs/quorum_logic.md` (66%, similaridade), `docs/storage-network.md` (faixas 0.7/0.3), `docs/mod-manager.md` (PluginState).
3. Se for preciso mudar o valor, e não só a redação, parar e pedir aprovação humana (área protegida).
