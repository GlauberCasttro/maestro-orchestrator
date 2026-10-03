---
name: po-playbooks
description: "Procedimentos passo a passo de po neste repo. Use quando po for executar: Classificar um pedido de feature; Conferir caminho citado por doc antes de usá-lo num critério"
---
<!-- codebase-specialists:generated; não edite: altere .specialists/team.json5 e rode `cs.py emit` -->

# Playbooks de `po`

Procedimentos do território de `po`, extraídos de `.specialists/team.json`.

## Classificar um pedido de feature

1. Localizar o item em `ROADMAP.md` e em `docs/roadmap.md`; se só existir no da raiz (Fases 5–9), marcar como fora da fase corrente.
2. Conferir se o item está marcado [x] (entregue) ou [ ] (aberto) e em qual fase; Fase 2 aberta tem precedência sobre Fases 3–9.
3. Confrontar o escopo com os Guiding Principles de `docs/roadmap.md` e com `docs/vision.md`; conflito com 'Preserve dissent' ou humano no laço vira recusa ou ressalva.
4. Redigir critérios de aceite a partir da regra do módulo afetado: `docs/quorum_logic.md` (agreement_ratio ≥ 0.66), `docs/r2-engine.md` (grade e confidence), `docs/self-improvement-pipeline.md` (opt-in, 5/hora, rollback), `docs/deliberation.md` (1–5 rodadas, não-fatal).

## Conferir caminho citado por doc antes de usá-lo num critério

1. Para todo arquivo citado num doc, confirmar que existe com `ls <caminho>`; os docs citam arquivos que não existem, como o runtime_config (JSON em data, criado em runtime) em `docs/self-improvement-pipeline.md` e `docs/architecture.md`, e o node_shards (JSON em data, criado em runtime) em `docs/storage-network.md`.
2. Se não existir, não usar como critério de aceite; registrar como divergência doc×repo.
