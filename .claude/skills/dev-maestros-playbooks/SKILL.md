---
name: dev-maestros-playbooks
description: "Procedimentos passo a passo de dev-maestros neste repo. Use quando dev-maestros for executar: Portar um módulo Python para um crate (ex.: storage_proof → maestros-proof); Ligar a primeira dependência real de um crate"
---
<!-- codebase-specialists:generated; não edite: altere .specialists/team.json5 e rode `cs.py emit` -->

# Playbooks de `dev-maestros`

Procedimentos do território de `dev-maestros`, extraídos de `.specialists/team.json`.

## Portar um módulo Python para um crate (ex.: storage_proof → maestros-proof)

1. Ler a referência Python e seus testes: `maestro/storage_proof.py` (constantes PROBATION_THRESHOLD, EVICTION_THRESHOLD, DEFAULT_CHALLENGE_WINDOW_SECONDS, DEFAULT_MAX_LATENCY_MS) e `tests/test_storage_proof.py`, que define o comportamento esperado para a paridade.
2. Implementar dentro dos módulos stub já existentes em `maestros/crates/maestros-proof/src/lib.rs` (porep, pores, poi, sign, manifest), mantendo `#![no_std]` e `extern crate alloc`.
3. Copiar os valores numéricos do Python sem alterar; se a paridade pedir valor diferente, parar e perguntar ao dono (área protegida).
4. Rodar `rg -n "\.unwrap\(\)" maestros` e `rg -n "\bunsafe\s*\{" maestros`; os dois têm de sair sem resultado (exit 1).
5. Rodar `rg -c "^#!\[no_std\]" maestros/crates/maestros-core/src/lib.rs maestros/crates/maestros-proto/src/lib.rs maestros/crates/maestros-proof/src/lib.rs` e confirmar contagem 1 em cada arquivo.

## Ligar a primeira dependência real de um crate

1. Conferir em `maestros/Cargo.toml` o bloco [workspace.dependencies]: hoje só tem comentários que registram a intenção (ciborium, ed25519-dalek no_std, tokio, quinn, foca, lancedb, candle), sem nenhuma dependência real.
2. Escolher o crate pela fronteira: dependência std-only só em maestros-embed, maestros-lance, maestros-mesh, maestros-quorum ou maestros-host; em maestros-core, maestros-proto ou maestros-proof só entra dependência compatível com no_std.
3. Declarar a versão no [workspace.dependencies] de `maestros/Cargo.toml` e referenciar no `Cargo.toml` do crate, em `maestros/crates/<crate>/Cargo.toml`.
4. Repetir as checagens com rg de unwrap, unsafe e no_std do playbook anterior.
