# HERMES OS — Makefile
COMPOSE = docker compose -f docker-compose.yml
VPS     = ssh -i ~/.ssh/hostinger_openclaw mystic@2a02:4780:4:eca4::1

.PHONY: up down build logs ps wipe deploy vps-wipe vps-deploy vps-logs vps-ps

# ── Local ─────────────────────────────────────────────────────
up:
	$(COMPOSE) up -d

down:
	$(COMPOSE) down

build:
	$(COMPOSE) build --no-cache

logs:
	$(COMPOSE) logs -f --tail=50

ps:
	$(COMPOSE) ps

wipe:
	$(COMPOSE) down -v --remove-orphans
	docker system prune -f

# ── VPS ───────────────────────────────────────────────────────
vps-wipe:
	$(VPS) "bash /home/mystic/hermes-os/infra/scripts/wipe_vps.sh"

vps-deploy:
	$(VPS) "cd /home/mystic/hermes-os && git pull && bash infra/scripts/deploy.sh"

vps-deploy-fresh:
	$(VPS) "cd /home/mystic/hermes-os && git pull && bash infra/scripts/deploy.sh --fresh"

vps-logs:
	$(VPS) "docker compose -f /home/mystic/hermes-os/docker-compose.yml logs -f --tail=50"

vps-ps:
	$(VPS) "docker compose -f /home/mystic/hermes-os/docker-compose.yml ps"

vps-shell:
	$(VPS)

# ── API shortcuts ─────────────────────────────────────────────
api-logs:
	$(COMPOSE) logs hermes-api -f --tail=50

clawbot-logs:
	$(COMPOSE) logs clawbot -f --tail=50

hermes-logs:
	$(COMPOSE) logs hermes-agent -f --tail=50

mystic-logs:
	$(COMPOSE) logs mystic-agent -f --tail=50
