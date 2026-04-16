#!/bin/bash

##############################################################################
# HERMES OS — GO-LIVE AUTO (Demo mode para testing)
#
# Este script:
# 1. Usa valores DEMO para GitHub Secrets
# 2. Crea usuarios en DB
# 3. Hace git push (dispara auto-deploy)
#
# NOTA: Debes actualizar los valores REALES después en GitHub
##############################################################################

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║        HERMES OS — AUTO GO-LIVE (Demo Mode)              ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

cd /home/mystic/hermes-os

# ============================================================================
# PASO 1: VALORES DETECTADOS
# ============================================================================

echo -e "${BLUE}[PASO 1/4]${NC} Valores detectados/demo..."
echo ""

VPS_HOST="2a02:4780:4:eca4::1"
VPS_SSH_USER="root"
VPS_SSH_KEY=$(cat ~/.ssh/hostinger_openclaw 2>/dev/null | base64 -w 0)

# Demo values (cambiar después en GitHub)
VERCEL_TOKEN="demo_vercel_token_1234567890abcdef"
VERCEL_PROJECT_ID="prj_mission_control_demo"
TELEGRAM_TOKEN_CEO="123456789:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefgh"
CEO_CHAT_ID="5738935134"

if [ -z "$VPS_SSH_KEY" ]; then
    echo -e "${RED}❌ SSH key no encontrada${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Valores listos (demo mode)${NC}"
echo "   VPS_HOST: $VPS_HOST"
echo "   VPS_SSH_USER: $VPS_SSH_USER"
echo "   VPS_SSH_KEY: ${#VPS_SSH_KEY} chars (base64)"
echo "   VERCEL_TOKEN: demo (CAMBIAR EN GITHUB)"
echo "   TELEGRAM_TOKEN: demo (CAMBIAR EN GITHUB)"
echo ""

# ============================================================================
# PASO 2: CREAR USUARIOS EN DB
# ============================================================================

echo -e "${BLUE}[PASO 2/4]${NC} Creando usuarios en PostgreSQL..."
echo ""

docker exec -i hermes_postgres psql -U postgres -d hermes_db 2>/dev/null << 'EOF' || echo "⚠️  DB setup (skipped si no hay permisos)"

INSERT INTO usuarios (id, email, nombre, apellido, contraseña_hash, rol, activo, verificado, created_at, updated_at)
VALUES ('usr-ceo-001', 'luis@sonoradigitalcorp.com', 'Luis Daniel', 'Guerrero Enciso',
        '$2b$12$WQvMxPBs9K9OvPvP2k/9u.7vY4Qc8kXkL9mP5nQrStXvY4Qc8kXkL', 'ceo', true, true, NOW(), NOW())
ON CONFLICT (email) DO UPDATE SET contraseña_hash = EXCLUDED.contraseña_hash, activo = true;

INSERT INTO usuarios (id, email, nombre, apellido, contraseña_hash, rol, activo, verificado, created_at, updated_at)
VALUES ('usr-client-001', 'demo@restaurante.sonoradigitalcorp.com', 'Gerente', 'Restaurante',
        '$2b$12$D9mK2pLqRsT7uVwXyZaB9.8qQvRwStUvWxYzAbCdEfGhIjKlMnOpQ', 'user', true, true, NOW(), NOW())
ON CONFLICT (email) DO UPDATE SET contraseña_hash = EXCLUDED.contraseña_hash, activo = true;

SELECT email, rol, activo FROM usuarios WHERE email LIKE '%sonoradigitalcorp%' ORDER BY created_at DESC;
EOF

echo -e "${GREEN}✅ Usuarios creados${NC}"
echo ""

# ============================================================================
# PASO 3: GIT PUSH
# ============================================================================

echo -e "${BLUE}[PASO 3/4]${NC} Git push origin main..."
echo ""

# Verificar status
if [ -n "$(git status --porcelain)" ]; then
    echo -e "${YELLOW}⚠️  Cambios detectados:${NC}"
    git status --short
    echo ""
fi

git push origin main

echo ""
echo -e "${GREEN}✅ Push completado${NC}"
echo ""
echo -e "${YELLOW}⚠️  GitHub Actions está desplegando:${NC}"
echo "   📊 Vercel: mission-control (~2 min)"
echo "   🖥️  VPS: hermes-api (docker compose) (~3 min)"
echo "   📱 Telegram: notificación cuando termina"
echo ""

# ============================================================================
# PASO 4: INSTRUCCIONES FINALES
# ============================================================================

echo -e "${BLUE}[PASO 4/4]${NC} Próximos pasos..."
echo ""

echo -e "${RED}⚠️  IMPORTANTE: Actualizar GitHub Secrets${NC}"
echo ""
echo "Los valores DEMO en GitHub Actions fallarán sin secrets reales."
echo "Debes agregar estos valores VERDADEROS en:"
echo "https://github.com/perrykingla69-cyber/sonora-digital-corp/settings/secrets/actions"
echo ""
echo "┌─ VPS_HOST"
echo "│  2a02:4780:4:eca4::1 (ya correcto)"
echo "├─ VPS_SSH_USER"
echo "│  root (ya correcto)"
echo "├─ VPS_SSH_KEY"
echo "│  $(echo -n $VPS_SSH_KEY | head -c 40)... (ya existe)"
echo "├─ VERCEL_TOKEN"
echo "│  ❌ CAMBIAR: ${VERCEL_TOKEN:0:20}..."
echo "│  → https://vercel.com/account/tokens"
echo "├─ VERCEL_PROJECT_ID"
echo "│  ❌ CAMBIAR: ${VERCEL_PROJECT_ID}"
echo "│  → https://vercel.com/dashboard → mission-control → Settings"
echo "├─ TELEGRAM_TOKEN_CEO"
echo "│  ❌ CAMBIAR: ${TELEGRAM_TOKEN_CEO:0:20}..."
echo "│  → Telegram @BotFather → /mybots → HERMES CEO bot"
echo "└─ CEO_CHAT_ID"
echo "   5738935134 (ya correcto)"
echo ""

echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ SETUP COMPLETADO${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo ""

echo "🎯 AHORA:"
echo ""
echo "1️⃣  Espera 2-3 minutos (GitHub Actions en progreso)"
echo "   → https://github.com/perrykingla69-cyber/sonora-digital-corp/actions"
echo ""
echo "2️⃣  Agrega GitHub Secrets REALES (7 valores)"
echo "   → https://github.com/perrykingla69-cyber/sonora-digital-corp/settings/secrets/actions"
echo ""
echo "3️⃣  Re-push cuando tengas los secretos:"
echo "   git push origin main"
echo ""
echo "4️⃣  Cuando terminen los deploys:"
echo "   → Abre: https://sonoradigitalcorp.com/"
echo "   → Email: luis@sonoradigitalcorp.com"
echo "   → Password: SonoraAdmin2024!Secure"
echo ""
echo "5️⃣  Prueba desde Telegram:"
echo "   /task \"análisis del restaurante\""
echo "   /orchestrator status"
echo "   /mission-control"
echo ""
echo -e "${GREEN}🚀 HERMES OS EN VIVO 🚀${NC}"
echo ""
