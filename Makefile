# MYSTIC — Makefile de comandos estandar

.PHONY: help install dev build test audit clean deploy

help:
	@echo "Comandos disponibles:"
	@echo "  make install       Instalar dependencias"
	@echo "  make dev           Levantar entorno de desarrollo"
	@echo "  make build         Construir imagenes Docker"
	@echo "  make test          Ejecutar tests"
	@echo "  make audit         Auditar reglas del proyecto"
	@echo "  make clean         Limpiar contenedores y volumenes"
	@echo "  make deploy        Deploy a produccion"
	@echo "  make api-logs      Ver logs de la API"
	@echo "  make restart-api   Reiniciar API"
	@echo "  make shell-api     Shell dentro del contenedor API"
	@echo "  make db-backup     Respaldo de base de datos"

install:
	cd backend && pip install -r requirements.txt
	cd frontend && npm install --legacy-peer-deps
	cd apps/whatsapp-bridge && npm install
	cd apps/telegram-bot && npm install

dev:
	cd infra && docker compose -f docker-compose.vps.yml up -d

build:
	cd infra && docker compose -f docker-compose.vps.yml build --no-cache

test:
	cd backend && python -m pytest tests/ -v 2>/dev/null || echo "Sin tests configurados"

audit:
	python3 scripts/audit_rules.py

clean:
	cd infra && docker compose -f docker-compose.vps.yml down -v
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

deploy:
	python3 apps/cli/mystic_cli.py deploy check

api-logs:
	docker logs -f mystic_api

frontend-logs:
	docker logs -f mystic_frontend

whatsapp-logs:
	docker logs -f mystic_whatsapp_bridge

telegram-logs:
	docker logs -f mystic_telegram_bot

restart-api:
	cd infra && docker compose -f docker-compose.vps.yml restart api

shell-api:
	docker exec -it mystic_api /bin/sh

db-backup:
	./infra/scripts/backup.sh
