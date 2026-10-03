---
name: planejar-sprint
description: "Planeja a próxima sprint com stories que passam no DoR, via `.specialists/bin/cs-state sprint plan`."
disable-model-invocation: true
argument-hint: "[--dry-run]"
---
<!-- codebase-specialists:generated; não edite: altere .specialists/team.json5 e rode `cs.py emit` -->

Planeja a próxima sprint chamando só o script; não leia nem edite o board à mão.

1. Rode `.specialists/bin/cs-state board` e liste as stories com DoR (READY) por feature.
2. Proponha ao usuário, numa mensagem: meta da sprint (1 linha), orçamento e as stories comprometidas.
3. Aprovado: `.specialists/bin/cs-state sprint plan --goal "<meta>" --budget <orçamento> --stories <US-1,BUG-2,...> $ARGUMENTS`.
4. Se o script recusar uma story por DoR, mostre o motivo e devolva-a ao PO; não contorne.
5. Mostre a saída do script e pare. Início: `.specialists/bin/cs-state sprint start`.
