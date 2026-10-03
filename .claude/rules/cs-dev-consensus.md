---
paths:
  - "maestro/orchestrator.py"
  - "maestro/aggregator.py"
  - "maestro/deliberation.py"
  - "maestro/dissent.py"
  - "maestro/session.py"
  - "maestro/api_sessions.py"
  - "maestro/r2.py"
  - "maestro/ncg/**"
  - "maestro/agents/__init__.py"
  - "maestro/agents/base.py"
  - "maestro/agents/aria.py"
  - "maestro/agents/sol.py"
  - "maestro/agents/prism.py"
  - "maestro/agents/tempagent.py"
  - "maestro/agents/mock.py"
  - "maestro/__init__.py"
---
<!-- codebase-specialists:generated; não edite: altere .specialists/team.json5 e rode `cs.py emit` -->

# Território de `dev-consensus`

Dono de escrita destes arquivos: `dev-consensus` (dev). Mudança aqui respeita o que segue; o cartão do dono tem missão e recusas.

## Invariantes

- Limite QUORUM_THRESHOLD = 0.66 (business) em maestro/aggregator.py; citado em teste tests/test_orchestration.py (`QUORUM_THRESHOLD`)
- Limite SIMILARITY_THRESHOLD = 0.5 (business) em maestro/aggregator.py; citado em teste tests/test_code_injection.py (`SIMILARITY_THRESHOLD`)
- Regra (validação) em maestro/deliberation.py: quando `if rounds < 1:` (linha 138) → ValueError("rounds must be >= 1, got {rounds}") (linha 139); alcançável por teste: tests/test_orchestration.py chama `run_orchestration_async` (se o teste isola esta regra não é determinável mecanicamente — confira antes de afirmar)
- Entrevista protected-areas: Há áreas que exigem aprovação humana antes de mudar (ex.: limiares QUORUM_THRESHOLD/SIMILARITY_THRESHOLD, storage_proof, self_improvement/code_injection, updater, licença)? — resposta do dono (literal): Limiares de consenso, Self-improvement, Storage proof / rede
- Invariante: except: sem tipo tem 0 ocorrências em 65 arquivos python de produto (não introduzir)
- Invariante: eval() tem 0 ocorrências em 65 arquivos python de produto (não introduzir)
- Invariante: exec() tem 0 ocorrências em 65 arquivos python de produto (não introduzir)
- Invariante: os.system() tem 0 ocorrências em 65 arquivos python de produto (não introduzir)
- Invariante: pickle.load(s) tem 0 ocorrências em 65 arquivos python de produto (não introduzir)
- Invariante: subprocess com shell=True tem 0 ocorrências em 65 arquivos python de produto (não introduzir)
- Invariante: import * tem 0 ocorrências em 65 arquivos python de produto (não introduzir)
- Invariante: yaml.load sem Loader tem 0 ocorrências em 65 arquivos python de produto (não introduzir)

## Convenções e regras técnicas

- Gate antes de merge: suíte inteira de testes. — prova: `pytest tests/`
- Nenhum padrão proibido (eval/exec/os.system/shell=True/pickle.load/import * ou except sem tipo) em código de produto: a busca deve voltar vazia. — prova: `rg -n "\beval\(|\bexec\(|os\.system\(|shell=True|pickle\.loads?\(|^\s*from \S+ import \*|^\s*except\s*:" "maestro/" "backend/"`
- yaml.load só com Loader explícito.
- Limiares de consenso fixos: QUORUM_THRESHOLD = 0.66 e SIMILARITY_THRESHOLD = 0.5. — prova: `rg -n "^(QUORUM|SIMILARITY)_THRESHOLD" "maestro/aggregator.py"`
- DeliberationEngine exige rounds >= 1 (ValueError caso contrário).
- Python: 4 espaços, snake_case em funções e arquivos, PascalCase em classes, sem `from __future__ import annotations`, LF e newline final.
- Pergunta de dependência ('quem importa o módulo X'): `answer` traz SÓ o conjunto de importadores DIRETOS do módulo-alvo (linha `from <pacote>.<modulo> import` ou `import <pacote>.<modulo>`), ou a palavra NENHUM sozinha quando o conjunto é vazio. Não entram em `answer`: quem importa via re-export do pacote (`from maestro.agents import`, servido por `maestro/agents/__init__.py`, que re-exporta Agent, MockAgent, Sol, Aria, Prism, TempAgent e ShardAgent) nem quem importa um submódulo quando o alvo é o `__init__.py` do pacote. Ressalvas e re-exports vão, no máximo, para `evidence` como o comando de busca usado. — prova: `rg -n "from maestro\.agents\.<modulo> import|import maestro\.agents\.<modulo>" "maestro/" "backend/" "tests/" "data/"`
- Formato de toda resposta: `answer` contém só o valor pedido (conjunto, `arquivo:linha` aberto ou NENHUM puro), sem rótulos, comentários nem leituras alternativas. Se a pergunta tem mais de uma leitura (termo definido em vários lugares), responder pela leitura literal e, para termo, usar o ponto de definição canônico do glossário (`.specialists/bin/cs-mem search "<termo>" --kind term`); as outras leituras ficam fora de `answer`.

## Armadilhas registradas

- O import de `_is_agent_error` de orchestrator dentro de deliberation criou um ciclo (o orquestrador importa DeliberationEngine) e quebrou a inicialização com ImportError; a correção duplicou o sentinela localmente.
- O streaming usava `asyncio.as_completed` e buscava o agente pelo objeto devolvido: os wrappers novos não batiam com as chaves do dict e davam KeyError. A correção trocou para `asyncio.wait(FIRST_COMPLETED)`.
- Respostas de erro dos agentes entravam no dissenso, no drift do NCG e na agregação e distorciam as métricas; houve correção para filtrá-las, junto com a troca do modelo do Prism, que dava 404.
- Agentes sem system prompt respondiam com ressalvas de data de corte; a correção alterou os cinco arquivos de agente juntos (base, aria, sol, prism, tempagent).
- Mudanças em `maestro/deliberation.py` vieram junto com bump de versão e atualização de `maestro/__init__.py`, docs e changelog nos mesmos commits de correção; quem mexe na deliberação costuma ter de atualizar a versão e os docs junto.

## Notas por caminho

- `maestro/deliberation.py`, `maestro/orchestrator.py`: O detector de sentinela de erro de agente existe em duas cópias de propósito (orchestrator e deliberation); deliberation não pode importar de orchestrator, porque isso cria um ciclo de import.
- `maestro/agents/**`: Todo agente de provedor envia um system prompt com a data atual; mudança no contrato de `maestro/agents/base.py` afeta as 7 importações dele. `maestro/agents/__init__.py` re-exporta as classes de agente: quem faz `from maestro.agents import` depende do pacote, não do módulo do agente, e por isso não conta como importador direto do módulo.

## Termos do domínio (além do cartão do dono)

- `R2 Engine` — - Scores each session in real time, detects dissent and improvement signals (em `maestro/r2.py`)
- `Sol` (em `maestro/agents/sol.py`)
- `R2Score` (em `maestro/r2.py`)
- `Aria` (em `maestro/agents/aria.py`)
- `Prism` (em `maestro/agents/prism.py`)
- `MockAgent` (em `maestro/agents/mock.py`)
- `MockHeadlessGenerator` (em `maestro/ncg/generator.py`)
- `DeliberationRound` — Each completed round flips agent indicators to "done", (em `maestro/deliberation.py`)
- `DissentAnalyzer` (em `maestro/dissent.py`)
- `SessionRecord` (em `maestro/session.py`)
- `DriftDetector` (em `maestro/ncg/drift.py`)
- `Deliberation Engine` — After collecting initial responses from all agents, each agent now reads what its peers said and produces a refined reply before any analysis runs. This transforms the parallel-collect pattern into an actual multi-round debate. (em `maestro/deliberation.py`)
- `ImprovementSignal` (em `maestro/r2.py`)
- `DeliberationReport` — Full history of every round (round 0 = initial responses, rounds 1..N = deliberation turns), final deliberated responses, participating agents, and skip reason if fewer than 2 healthy agents are available. (em `maestro/deliberation.py`)
- `TempAgent` (em `maestro/agents/tempagent.py`)
- `AnthropicHeadlessGenerator` (em `maestro/ncg/generator.py`)
- `OpenAIHeadlessGenerator` (em `maestro/ncg/generator.py`)
- `PairwiseDissent` (em `maestro/dissent.py`)
- `R2LedgerEntry` (em `maestro/r2.py`)
- `DriftSignal` (em `maestro/ncg/drift.py`)
- `AgentDissentProfile` (em `maestro/dissent.py`)
