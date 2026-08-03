up:
	docker compose up --build

down:
	docker compose down

down-v:
	docker compose down -v

logs:
	docker compose logs -f

re: down-v up

.PHONY: up down down-v logs re
