COMPOSE_ENV_FILES := .envs/.env.compose,.envs/.env.vault

export COMPOSE_ENV_FILES

up:
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f

restart:
	docker compose restart

clean:
	docker compose down -v --remove-orphans

re: clean up

.PHONY: up down test-waf logs restart clean re
