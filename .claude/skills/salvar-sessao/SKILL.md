---
name: salvar-sessao
description: "Salva a sessão via `.specialists/bin/cs-session save` (feito/próximo/bloqueio em 1 linha cada)."
disable-model-invocation: true
argument-hint: "[--commit]"
allowed-tools: "Bash(.specialists/bin/cs-session save *)"
---
<!-- codebase-specialists:generated; não edite: altere .specialists/team.json5 e rode `cs.py emit` -->

Salve a sessão chamando só o script; não leia nem edite arquivos de estado.

1. Escreva 1 linha para cada campo a partir desta conversa: feito, próximo passo, bloqueio (se houver).
2. Rode exatamente: `.specialists/bin/cs-session save --did "<feito>" --next "<próximo>" [--blocked "<bloqueio>"] $ARGUMENTS`
3. Mostre a saída do script e pare. O script coleta board, eventos, git, gates e memória sozinho.
