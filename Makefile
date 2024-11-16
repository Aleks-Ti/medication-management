ifeq (revision,$(firstword $(MAKECMDGOALS)))
	# use the rest as arguments for run
	RUN_ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
	# ... and turn them into do-nothing targets
	$(eval $(RUN_ARGS):;@:)
endif

.PHONY: start revision migrate

start:
	python src/main.py

revision:
	poetry run alembic revision --autogenerate -m "$(RUN_ARGS)"

migrate:
	poetry run alembic upgrade head

st:
	ruff . --fix

startd:
	docker compose down && docker compose up -d

redis:
	docker run --name redis -p 6388:6379 -d --rm redis --requirepass 123425
