---
name: dev-self-improve-playbooks
description: "Procedimentos passo a passo de dev-self-improve neste repo. Use quando dev-self-improve for executar: Adicionar ou ajustar uma categoria/estratégia de OptimizationProposal; Mudar o ciclo ou a API de auto-melhoria"
---
<!-- codebase-specialists:generated; não edite: altere .specialists/team.json5 e rode `cs.py emit` -->

# Playbooks de `dev-self-improve`

Procedimentos do território de `dev-self-improve`, extraídos de `.specialists/team.json`.

## Adicionar ou ajustar uma categoria/estratégia de OptimizationProposal

1. Editar a estratégia e o tipo de proposta em maestro/optimization.py (OptimizationProposal, ProposalBatch).
2. Conferir em maestro/injection_guard.py que a categoria nova cai na whitelist ou na lista bloqueada e que os limites min/max da estratégia são reexportados para a checagem de bounds; mudar a whitelist exige aprovação humana.
3. Cobrir em tests/test_code_injection.py no padrão de test_injectable_unknown_category_blocked e test_blocked_category_skipped.
4. Rodar a suíte declarada pelo dono restrita a tests/test_code_injection.py e tests/test_self_improvement.py, depois a suíte inteira.
5. Atualizar docs/self-improvement-pipeline.md na mesma mudança.

## Mudar o ciclo ou a API de auto-melhoria

1. Alterar ImprovementCycle/SelfImprovementEngine em maestro/self_improve.py e a rota correspondente em maestro/api_self_improve.py.
2. Se tocar aplicação ou reversão, manter maestro/applicator.py e maestro/rollback.py coerentes: toda injeção registrada no RollbackLog.
3. Cobrir em tests/test_self_improvement.py (ex.: test_analysis_only_mode).
4. Revisar docs/self-improvement-pipeline.md, docs/magi.md e docs/architecture.md para a mudança.
