COMPOSE_ENV_FILES := .envs/.env.compose

export COMPOSE_ENV_FILES



up:
	docker compose up -d --build

rebuild:
	docker compose build --no-cache
	docker compose up -d

down:
	docker compose down

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

re: clean prune rebuild

ai-pull:
	docker compose exec ollama ollama pull qwen3:4b

ai-test:
	python3 scripts/test_recipe_ai.py
	docker compose exec ollama ollama ps

.PHONY: up rebuild down test-waf logs restart clean prune re insert-secrets
.PHONY: ai-up ai-pull ai-test ai-stop
