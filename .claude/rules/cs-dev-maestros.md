---
paths:
  - "maestros/**"
---
<!-- codebase-specialists:generated; não edite: altere .specialists/team.json5 e rode `cs.py emit` -->

# Território de `dev-maestros`

Dono de escrita destes arquivos: `dev-maestros` (dev). Mudança aqui respeita o que segue; o cartão do dono tem missão e recusas.

## Invariantes

- Entrevista rust-maestros: Qual o papel do workspace Rust maestros/ (v0.0.1, 136 LOC) em relação ao Python maestro/: substituto futuro, experimento paralelo ou congelado? Agentes devem escrever nele? — resposta do dono (literal): o que recomenda
- Invariante: bloco unsafe tem 0 ocorrências em 9 arquivos rust de produto (não introduzir)
- Invariante: .unwrap() tem 0 ocorrências em 9 arquivos rust de produto (não introduzir)

## Convenções e regras técnicas

- Proibido `.unwrap()` em código Rust de produto (hoje são 0 ocorrências em 9 arquivos). — prova: `rg -n "\.unwrap\(\)" maestros # esperado: exit 1, sem saída`
- Proibido bloco `unsafe` em código Rust de produto (hoje são 0 ocorrências em 9 arquivos). — prova: `rg -n "\bunsafe\s*\{" maestros # esperado: exit 1, sem saída`
- maestros-core, maestros-proto e maestros-proof continuam `#![no_std]`. — prova: `rg -c "^#!\[no_std\]" maestros/crates/maestros-core/src/lib.rs maestros/crates/maestros-proto/src/lib.rs maestros/crates/maestros-proof/src/lib.rs # esperado: 1 em cada`
- O workspace compila sem warnings (o README declara: "cargo check should succeed with zero warnings"). — prova: `cd maestros && cargo check --workspace`

## Armadilhas registradas

- O nome e a forma do workspace estão espalhados fora do território: o commit que criou o esqueleto e renomeou telOS→MaestrOS mexeu em `maestros/**` e também em `ARCHITECTURE.md`, `ROADMAP.md` e `docs/maestro-whitepaper.md`. Renomear um crate ou mudar o layout deixa esses docs desatualizados, e eles só podem ser atualizados por outro agente.

## Notas por caminho

- `maestros/README.md`: A seção Branch do README diz que o desenvolvimento do MaestrOS vive no branch claude/telos-kernel-exploration-xSEfp; essa referência está desatualizada (o esqueleto já está no repo principal).
- `maestros/crates/maestros-mesh/**`: A referência Python para descoberta LAN fica em `maestro/lan_discovery.py`: STALE_TIMEOUT = 15.0, HANDSHAKE_TIMEOUT = 5.0, estados de AdjacencyState DISCOVERED, HANDSHAKE_SENT, HANDSHAKE_ACKED, CONFIRMED, STALE. Rede é área protegida pelo dono.

## Termos do domínio (além do cartão do dono)

- `Hailo-8L NPU HAT` — deferred to ~month 3. `ort` backend hook (em `maestros/DESIGN.md`)
- `Public internet exposure` — not until v0.3 at the earliest. (em `maestros/DESIGN.md`)
