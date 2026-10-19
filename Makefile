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

fclean:
	-docker compose down -v --rmi all --remove-orphans 2>/dev/null || true
	@if [ -n "$$(docker ps -q)" ]; then docker stop $$(docker ps -q) 2>/dev/null || true; fi
	-docker system prune -a --volumes -f
	@if [ -n "$$(docker volume ls -q)" ]; then docker volume rm -f $$(docker volume ls -q) 2>/dev/null || true; fi
	@rm -rf src/backend/uploads 2>/dev/null || docker run --rm -v $(PWD)/src/backend:/app alpine rm -rf /app/uploads 2>/dev/null || true

re: fclean rebuild

.PHONY: up rebuild down test-waf logs restart clean prune fclean re insert-secrets
