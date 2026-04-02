#!/bin/bash
# ╔══════════════════════════════════════════════════════════╗
# ║     HERMES OS — Deploy Script                            ║
# ║     Wipe + Setup limpio desde cero                      ║
# ╚══════════════════════════════════════════════════════════╝

set -euo pipefail

REPO_DIR="/home/mystic/hermes-os"
COMPOSE="docker compose -f $REPO_DIR/docker-compose.yml"

log() { echo "[$(date '+%H:%M:%S')] $*"; }
err() { echo "[ERROR] $*" >&2; exit 1; }

# ── 1. VERIFICAR .env ────────────────────────────────────────
log "Verificando configuración..."
[ ! -f "$REPO_DIR/.env" ] && err "Falta .env — copia .env.example y configura las variables"

required_vars=(DB_PASSWORD REDIS_PASSWORD JWT_SECRET OPENROUTER_API_KEY EVOLUTION_API_KEY
               TELEGRAM_TOKEN_CEO TELEGRAM_TOKEN_PUBLIC TELEGRAM_TOKEN_HERMES TELEGRAM_TOKEN_MYSTIC
               N8N_PASSWORD N8N_ENCRYPTION_KEY CEO_CHAT_ID)

source "$REPO_DIR/.env"
for var in "${required_vars[@]}"; do
    [ -z "${!var:-}" ] && err "Variable $var no configurada en .env"
done
log "Variables de entorno OK"

# ── 2. WIPE LIMPIO (opcional) ────────────────────────────────
if [ "${1:-}" = "--fresh" ]; then
    log "WIPE COMPLETO — eliminando contenedores y volúmenes anteriores..."
    $COMPOSE down -v --remove-orphans 2>/dev/null || true
    docker system prune -f 2>/dev/null || true
    log "Wipe completo"
fi

# ── 3. BUILD ──────────────────────────────────────────────────
log "Construyendo imágenes..."
$COMPOSE build --no-cache

# ── 4. LEVANTAR CAPA 0 y ESPERAR ─────────────────────────────
log "Levantando base de datos y Redis..."
$COMPOSE up -d postgres redis
sleep 8

# ── 5. VERIFICAR DB ───────────────────────────────────────────
log "Verificando PostgreSQL..."
docker exec hermes_postgres pg_isready -U "${DB_USER:-hermes}" -d "${DB_NAME:-hermes_db}" \
    || err "PostgreSQL no responde"
log "PostgreSQL OK"

# ── 6. LEVANTAR TODO ──────────────────────────────────────────
log "Levantando stack completo..."
$COMPOSE up -d

# ── 7. NGINX ──────────────────────────────────────────────────
log "Configurando Nginx..."
cp "$REPO_DIR/infra/nginx/hermes.conf" /etc/nginx/sites-available/hermes
ln -sf /etc/nginx/sites-available/hermes /etc/nginx/sites-enabled/hermes
nginx -t && systemctl reload nginx
log "Nginx OK"

# ── 8. STATUS FINAL ───────────────────────────────────────────
sleep 5
log "═══════════════════════════════════════"
log "HERMES OS — Deploy completado"
log "═══════════════════════════════════════"
$COMPOSE ps
echo ""
echo "  Frontend:  https://sonoradigitalcorp.com"
echo "  API:       https://sonoradigitalcorp.com/api/"
echo "  N8N:       https://sonoradigitalcorp.com/n8n/"
echo "  WhatsApp:  https://sonoradigitalcorp.com/wa/"
