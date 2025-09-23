# SideQuest Makefile - common dev/ops commands

up:
	docker compose up -d

down:
	docker compose down

restart:
	docker compose restart api web proxy

build:
	docker compose build api web proxy

logs:
	docker compose logs -f proxy

ps:
	docker compose ps

rebuild-web:
	docker compose stop proxy web
	docker volume rm sidequest_webdist || true
	docker compose build --no-cache web
	docker compose up -d web proxy

reset-all:
	docker compose down
	docker volume rm sidequest_dbdata sidequest_minio sidequest_webdist || true
	docker compose up -d --build

health:
	curl -sS http://localhost:8080/api/health

login-url:
	curl -sS http://localhost:8080/api/auth/login-url | jq -r .url

me:
	curl -sS http://localhost:8080/api/auth/me | jq

# Progress tracking
status:
	@echo "=== SideQuest Development Status ==="
	@echo ""
	@grep -A 2 "Last Updated:" PROGRESS.md
	@grep -A 2 "Current Phase:" PROGRESS.md
	@echo ""
	@echo "=== Service Status ==="
	@docker compose ps
	@echo ""
	@echo "=== Quick Health Check ==="
	@curl -sS http://localhost:8080/api/health 2>/dev/null && echo " ✅ API Health OK" || echo " ❌ API Health Failed"

# Quest testing
test-quest:
	@echo "Testing quest generation..."
	@curl -sS -H "X-Debug-User: testuser" http://localhost:8080/api/quests/today | jq '{title: .title, rarity: .rarity, weather: .weather.description}'

# Template management  
templates:
	curl -sS http://localhost:8080/api/templates | jq '.templates | length'
	@echo " quest templates available"

seed-templates:
	curl -X POST http://localhost:8080/api/admin/seed-templates

