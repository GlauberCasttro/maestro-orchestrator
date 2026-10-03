---
paths:
  - "frontend/**"
---
<!-- codebase-specialists:generated; não edite: altere .specialists/team.json5 e rode `cs.py emit` -->

# Território de `dev-frontend`

Dono de escrita destes arquivos: `dev-frontend` (dev). Mudança aqui respeita o que segue; o cartão do dono tem missão e recusas.

## Invariantes

- Entrevista ui-primary: Qual interface é a principal e mantida: TUI Textual (maestro/tui/) ou web (frontend/ React + backend/main.py)? — resposta do dono (literal): Ambas
- TypeScript em modo strict (frontend/tsconfig.json)
- Invariante: tipo any tem 0 ocorrências em 5 arquivos typescript de produto (não introduzir)
- Invariante: eval() tem 0 ocorrências em 5 arquivos typescript de produto (não introduzir)
- Invariante: non-null assertion (!.) tem 0 ocorrências em 5 arquivos typescript de produto (não introduzir)
- Invariante: @ts-ignore tem 0 ocorrências em 5 arquivos typescript de produto (não introduzir)

## Convenções e regras técnicas

- TypeScript em modo strict em frontend/tsconfig.json; não afrouxar. — prova: `grep -n '"strict": true' frontend/tsconfig.json`
- Zero tipo any em frontend/src. — prova: `rg -n ":\s*any\b|<any>|as\s+any\b" "frontend/src"`
- Zero @ts-ignore em frontend/src. — prova: `rg -n "@ts-ignore" "frontend/src"`
- Zero non-null assertion (!.) em frontend/src. — prova: `rg -n "\w!\." "frontend/src"`
- Zero eval() em frontend/src. — prova: `rg -nP "(?<![\w.])eval\(" "frontend/src"`
- frontend/package.json e frontend/package-lock.json mudam juntos. — prova: `git diff --name-only | grep frontend/package`
- Build de produção declarado em frontend/package.json; não executado no scan por falta do vite. — prova: `npm --prefix frontend run build`

## Armadilhas registradas

- A tela de histórico de sessões ficou em branco porque o objeto inteiro da resposta de /api/sessions foi posto no estado de lista e o .map quebrou; o array está em data.sessions.
- O painel de update exibiu ao mesmo tempo o card de erro e o card de 'up to date' ou 'Update available'; cards de sucesso devem sumir quando há erro.
- A UI já prefixa a mensagem com 'Update failed:'; o backend deixou de prefixar para não duplicar. Não reintroduza o prefixo dos dois lados.
- Com versão local desconhecida, o updater mostrava '0 new commits' porque 'unknown' não é ref git válida; a UI precisa tratar versão indeterminada como caso próprio.
- O badge de versão em maestroUI.tsx desalinhou de frontend/package.json e do lockfile mais de uma vez e exigiu commits só de correção de versão.
- Glifos emoji (aviso, check) renderizavam coloridos em alguns terminais e foram trocados por ASCII ([!!], [ok]); não reintroduza emoji na UI.
- URL truncada no painel Storage Network foi corrigida com copy-to-clipboard, mexendo em maestroUI.tsx, style.css e docs/ui-guide.md juntos.
- Erros de agente chegam estruturados (rate_limit, not_found, auth, server, timeout); a UI mostra banner por agente e escurece o card em vez de exibir a string crua.

## Notas por caminho

- `frontend/**`: TS/TSX: indentação de 2 espaços, ponto-e-vírgula em todo import, aspas simples na maioria dos imports, interfaces em PascalCase, nomes de arquivo em kebab-case na maioria (exceção: maestroUI.tsx).
- `frontend/src/style.css`, `frontend/src/maestroUI.tsx`: style.css nunca mudou sem maestroUI.tsx; mude os dois no mesmo commit.
- `frontend/package.json`, `frontend/package-lock.json`: Manifesto e lockfile mudam juntos; docs/roadmap.md costuma acompanhar mudanças de versão em frontend/package.json.

## Termos do domínio (além do cartão do dono)

- `ShardModel` (em `frontend/src/maestroUI.tsx`)
- `R2Data` (em `frontend/src/maestroUI.tsx`)
- `DissentData` (em `frontend/src/maestroUI.tsx`)
- `DepCheck` (em `frontend/src/maestroUI.tsx`)
- `NodeContribution` (em `frontend/src/maestroUI.tsx`)
- `UpdateInfo` (em `frontend/src/maestroUI.tsx`)
- `DiscoveryPeer` (em `frontend/src/maestroUI.tsx`)
- `OrchestratorResponse` (em `frontend/src/maestroUI.tsx`)
- `AutoUpdateStatus` (em `frontend/src/maestroUI.tsx`)
- `DiscoverySnapshot` (em `frontend/src/maestroUI.tsx`)
- `NetworkModel` (em `frontend/src/maestroUI.tsx`)
- `StreamStage` (em `frontend/src/maestroUI.tsx`)
- `KeyInfo` (em `frontend/src/maestroUI.tsx`)
- `NcgPerAgent` (em `frontend/src/maestroUI.tsx`)
- `StorageNodeInfo` (em `frontend/src/maestroUI.tsx`)
- `AgentProfile` (em `frontend/src/maestroUI.tsx`)
- `DepReport` (em `frontend/src/maestroUI.tsx`)
- `InstanceListResponse` (em `frontend/src/maestroUI.tsx`)
- `PairwiseEntry` (em `frontend/src/maestroUI.tsx`)
- `SessionSummary` (em `frontend/src/maestroUI.tsx`)
