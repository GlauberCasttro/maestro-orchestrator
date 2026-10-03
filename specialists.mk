# specialists.mk — alvos finos do harness: cada alvo chama o script e nada mais (gerado; não editar).
# Compatível com GNU make 3.81+ e BSD make. Variáveis: ID=<task> FEAT=<feature> Q=<consulta> ARGS='<flags>'.
CS_BIN = .specialists/bin

next:
	@$(CS_BIN)/cs-state next

board:
	@$(CS_BIN)/cs-state board

add-epic:
	@$(CS_BIN)/cs-state add epic $(ARGS)

add-feature:
	@$(CS_BIN)/cs-state add feature $(ARGS)

add-story:
	@$(CS_BIN)/cs-state add story $(ARGS)

sprint-plan:
	@$(CS_BIN)/cs-state sprint plan $(ARGS)

sprint-start:
	@$(CS_BIN)/cs-state sprint start $(ARGS)

sprint-review:
	@$(CS_BIN)/cs-state sprint review $(ARGS)

sprint-close:
	@$(CS_BIN)/cs-state sprint close $(ARGS)

brief:
	@$(CS_BIN)/cs-state brief --task $(ID) $(ARGS)

dispatch:
	@$(CS_BIN)/cs-state dispatch --task $(ID) $(ARGS)

verify:
	@$(CS_BIN)/cs-state verify --task $(ID)

review:
	@$(CS_BIN)/cs-state review --task $(ID) $(ARGS)

accept:
	@$(CS_BIN)/cs-state accept --task $(ID)

reject:
	@$(CS_BIN)/cs-state reject --task $(ID) $(ARGS)

abstain:
	@$(CS_BIN)/cs-state abstain --task $(ID) $(ARGS)

session-save:
	@$(CS_BIN)/cs-session save $(ARGS)

session-load:
	@$(CS_BIN)/cs-session load

mem:
	@$(CS_BIN)/cs-mem search "$(Q)"

autonomy-start:
	@$(CS_BIN)/cs-state autonomy start --feature $(FEAT) $(ARGS)

autonomy-status:
	@$(CS_BIN)/cs-state autonomy status

selftest:
	@python3 .specialists/harness/selftest.py --root .

validate:
	@python3 .specialists/harness/validate.py --strict --allow-empty --root .

drift:
	@python3 .specialists/harness/selftest.py --drift --root .

cs-help:
	@echo '  make next             próxima ação permitida'
	@echo '  make board            árvore épico→feature→story→task com rollup'
	@echo '  make add-epic         ARGS=--title .. --objective .. --metric ..'
	@echo '  make add-feature      ARGS=--epic EPIC-n --title .. --spec .. --accept-cmd ..'
	@echo '  make add-story        ARGS=--type us|bug|fix --feature FEAT-n --title ..'
	@echo '  make sprint-plan      ARGS=--goal .. --budget tasks=N,attempts=2,minutes=M --stories US-1,BUG-2'
	@echo '  make sprint-start     '
	@echo '  make sprint-review    '
	@echo '  make sprint-close     '
	@echo '  make brief            ID=<task>'
	@echo '  make dispatch         ID=<task> ARGS=--model sonnet'
	@echo '  make verify           ID=<task>'
	@echo '  make review           ID=<task> ARGS=--by gate --verdict PASS --findings ..'
	@echo '  make accept           ID=<task>'
	@echo '  make reject           ID=<task> ARGS=--reason ..'
	@echo '  make abstain          ID=<task> ARGS=--kind spec_ambiguous --reason ..'
	@echo '  make session-save     ARGS=--did .. --next ..'
	@echo '  make session-load     '
	@echo '  make mem              Q=<consulta>'
	@echo '  make autonomy-start   FEAT=FEAT-n ARGS=--budget tasks=6,attempts=2,minutes=90'
	@echo '  make autonomy-status  '
	@echo '  make selftest         sondas negativas dos guards (G6)'
	@echo '  make validate         validador do estado'
	@echo '  make drift            integridade do motor + revalidação da memória'
	@echo '  make cs-help          esta lista'

.PHONY: next board add-epic add-feature add-story sprint-plan sprint-start sprint-review sprint-close brief dispatch verify review accept reject abstain session-save session-load mem autonomy-start autonomy-status selftest validate drift cs-help
