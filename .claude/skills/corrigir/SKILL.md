---
name: corrigir
description: "Registra a correção do usuário como lição do agente que errou (`.specialists/bin/cs-mem correct`)."
disable-model-invocation: true
argument-hint: "<agente> <o que estava errado> -> <o certo>, porque <porquê>"
allowed-tools: "Bash(.specialists/bin/cs-mem correct *)"
---
<!-- codebase-specialists:generated; não edite: altere .specialists/team.json5 e rode `cs.py emit` -->

Registra a correção do usuário como lição do agente que errou; não edite arquivos de memória.

1. Identifique o agente, o que ele fez de errado, o certo e o porquê (1 linha cada), a partir de: $ARGUMENTS
2. Rode exatamente: `.specialists/bin/cs-mem correct --agent <agente> --wrong "<errado>" --right "<certo>" --why "<porquê>" [--paths "<glob>"]`
3. Mostre a saída (lição nova ou `count+1` de uma existente) e só então siga com o trabalho.
