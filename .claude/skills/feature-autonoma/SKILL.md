---
name: feature-autonoma
description: "Inicia o modo autônomo de uma feature: aprovação única de spec, testes de aceite, classe e orçamento; depois `.specialists/bin/cs-state next` até o relatório."
disable-model-invocation: true
argument-hint: "<feature-id> <arquivo-spec>"
arguments: [feature, spec]
---
<!-- codebase-specialists:generated; não edite: altere .specialists/team.json5 e rode `cs.py emit` -->

Conduz o toque único de aprovação do modo autônomo para a feature `$0` (spec em `$1`).

1. Leia a spec `$1` e os testes de aceite que ela cita; rode-os e mostre que falham hoje.
2. Classifique a feature (pequena, feature, risco). Classe `risco` não entra no autônomo: pare e diga por quê.
3. Proponha o orçamento: `tasks=N,attempts=2,minutes=M`.
4. Mostre ao usuário, numa mensagem só: spec resumida, testes de aceite (comando + estado atual), classe e
   orçamento. Peça uma única aprovação.
5. Aprovado: `.specialists/bin/cs-state autonomy start --feature $0 --spec $1 --budget <orçamento aprovado>`.
   Recusado ou com ressalva: ajuste e pergunte de novo, ou fique no modo assistido.
6. Com o mandato gravado, siga `.specialists/bin/cs-state next` até REPORTING sem novas perguntas, salvo condição de
   escalada do kernel do orquestrador.
