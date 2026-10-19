COMPOSE_ENV_FILES := .envs/.env.compose

export COMPOSE_ENV_FILES

UID := $(shell id -u)
GID := $(shell id -g)
export UID
export GID

up:
	docker compose up -d --build

rebuild:
	docker compose build --no-cache
	docker compose up -d

down:
	docker compose down

stop:
	docker compose stop

logs:
	docker compose logs -f

insert-secrets:
	docker exec -it vault ./usr/local/src/vault/scripts/vault-secrets.sh

restart:
	docker compose restart

clean:
	docker compose down -v --rmi local --remove-orphans

prune:
	docker system prune -f --volumes

re: rebuild

.PHONY: up rebuild down test-waf logs restart clean prune re insert-secrets
