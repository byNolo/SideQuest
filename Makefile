up:
	docker compose up -d

down:
	docker compose down

restart:
	docker compose restart api web

build:
	docker compose build api web

logs:
	docker compose logs -f api

ps:
	docker compose ps

reset:
	docker compose down
	docker volume rm sidequest_dbdata || true
	docker compose up -d --build

api-health:
	curl -sS -H "X-Debug-User: tester" http://localhost:8001/api/health | jq .

onboarding-status:
	curl -sS -H "X-Debug-User: tester" http://localhost:8001/api/me/onboarding/status | jq .

web-dev:
	cd web && npm install && npm run dev
