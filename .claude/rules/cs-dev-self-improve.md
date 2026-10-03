---
paths:
  - "maestro/magi.py"
  - "maestro/magi_vir.py"
  - "maestro/api_magi.py"
  - "maestro/introspect.py"
  - "maestro/optimization.py"
  - "maestro/applicator.py"
  - "maestro/rollback.py"
  - "maestro/injection_guard.py"
  - "maestro/self_improve.py"
  - "maestro/api_self_improve.py"
---
<!-- codebase-specialists:generated; não edite: altere .specialists/team.json5 e rode `cs.py emit` -->

# Território de `dev-self-improve`

Dono de escrita destes arquivos: `dev-self-improve` (dev). Mudança aqui respeita o que segue; o cartão do dono tem missão e recusas.

## Invariantes

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

- Não introduzir eval(), exec(), os.system(), subprocess com shell=True, pickle.load(s) nem yaml.load sem Loader — o pipeline aplica código gerado e o repo tem zero ocorrências. — prova: `rg -nP '(?<![\w.])(eval|exec)\(|\bos\.system\(|shell\s*=\s*True|pickle\.loads?\(|\byaml\.load\((?![^)]*Loader)' maestro/ # esperado: sem saída, exit 1`
- Não introduzir except: sem tipo nem import *. — prova: `rg -nP '^\s*except\s*:|^\s*from\s+\S+\s+import\s+\*' maestro/ # esperado: sem saída, exit 1`
- Gate de teste antes de merge é a suíte inteira com pytest (declarado pelo dono; nenhum comando de teste declarado em ferramenta). — prova: `pytest tests/`
- Não usar from __future__ import annotations nos arquivos do território (lei do repo: 94% sem). — prova: `rg -l 'from __future__ import annotations' maestro/magi.py maestro/magi_vir.py maestro/api_magi.py maestro/introspect.py maestro/optimization.py maestro/applicator.py maestro/rollback.py maestro/injection_guard.py maestro/self_improve.py maestro/api_self_improve.py # esperado: exit 1`
- Regra de negócio/limite só existe se aparecer como fato brule.* (ex.: brule.limit.*) ou termo canônico do glossário; nome perguntado que não é termo canônico → responder NENHUM e, no máximo, citar como observação o identificador real mais próximo (ex.: parâmetro de função), sem afirmar que a regra existe. — prova: `.specialists/bin/cs-mem search '<nome perguntado>' # sem fato brule/gloss com esse nome => NENHUM`
- Termo técnico: o local de definição canônico é o do fato gloss.* (pode estar fora do território); símbolo com nome ou assinatura mascarada: listar todos os candidatos com rg e nomear a ambiguidade quando houver mais de um, citando só arquivo:linha aberto. — prova: `rg -n 'def _\w*_targets\(' maestro/optimization.py # >1 resultado => ambíguo, listar todos`

## Armadilhas registradas

- Uma correção de code review do pipeline precisou mexer de uma vez em maestro/self_improve.py, maestro/api_self_improve.py, maestro/introspect.py, maestro/magi.py, maestro/magi_vir.py, maestro/optimization.py, maestro/r2.py, tests/test_self_improvement.py e em docs/magi.md, docs/r2-engine.md, docs/self-improvement-pipeline.md e docs/architecture.md: mudança de contrato entre etapas do pipeline arrasta o R2 (fora do território), os testes e a documentação.

## Notas por caminho

- `docs/self-improvement-pipeline.md`, `docs/architecture.md`: Estes docs citam data/runtime_config.json e data/rollbacks/log.json, que não existem no repositório; não trate a ausência como bug nem crie esses arquivos como fixture versionada.
- `maestro/magi_vir.py`: Concentra as exceções à regra de classes em PascalCase do repo; não renomeie em massa sem pedido.

## Termos do domínio (além do cartão do dono)

- `ComputeNode` (em `maestro/magi_vir.py`)
- `inject` (em `maestro/api_self_improve.py`)
- `MAGI_VIR` — Virtual Instance Runtime — sandboxed testing environment that runs benchmark prompts through baseline and optimized configurations, compares results, and produces promotion/rejection recommendations (em `maestro/magi_vir.py`)
- `Injection Guard` — Safety rails for the injection system — category whitelist (blocks `architecture` and `pipeline` by default), bounds enforcement at injection time, rate limiting (default 5/hour), and post-injection smoke test with automatic rollback on gra (em `maestro/injection_guard.py`)
- `Recommendation` (em `maestro/magi.py`)
- `SelfImprovementEngine` (em `maestro/self_improve.py`)
- `ImprovementCycle` (em `maestro/self_improve.py`)
- `injections` (em `maestro/api_self_improve.py`)
- `VIRReport` (em `maestro/magi_vir.py`)
- `MagiReport` (em `maestro/magi.py`)
- `introspect` (em `maestro/api_self_improve.py`)
- `OptimizationProposal` — generates concrete code change proposals (threshold tuning, agent config, architecture) (em `maestro/optimization.py`)
- `IntrospectionReport` (em `maestro/introspect.py`)
- `RollbackLog` (em `maestro/rollback.py`)
- `CodeTarget` (em `maestro/introspect.py`)
- `ProposalBatch` (em `maestro/optimization.py`)
- `RollbackEntry` (em `maestro/rollback.py`)
- `CodeInjector` (em `maestro/applicator.py`)
- `Compute Node Registry` — JSON-based registry for distributed validation across multiple Maestro nodes (em `maestro/magi_vir.py`)
- `GuardConfig` (em `maestro/injection_guard.py`)
- `rollback-cycle` (em `maestro/api_self_improve.py`)
- `InjectionResult` (em `maestro/applicator.py`)
- `Optimization Engine` — Translates introspection results into structured `OptimizationProposal` objects with threshold strategies, temperature strategies, and architecture refactoring rules (em `maestro/optimization.py`)
- `CodeIntrospector` (em `maestro/introspect.py`)
- `BenchmarkResult` (em `maestro/magi_vir.py`)
- `VIRComparison` (em `maestro/magi_vir.py`)
