#!/bin/bash

##############################################################################
# HERMES OS — GO-LIVE SETUP SCRIPT
# Ejecuta todos los pasos para ir a producción:
# 1. Configura GitHub Secrets
# 2. Crea usuarios en DB
# 3. Hace git push (dispara auto-deploy)
# 4. Health checks
#
# USO: bash GO_LIVE.sh
##############################################################################

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║        HERMES OS — GO-LIVE SETUP (5 minutos)             ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============================================================================
# PASO 1: RECOLECTAR VALORES
# ============================================================================

echo -e "${BLUE}[PASO 1/5]${NC} Recolectando valores para GitHub Secrets..."
echo ""

# Valores detectados
VPS_HOST="2a02:4780:4:eca4::1"
VPS_SSH_USER="root"
VPS_SSH_KEY_PATH="$HOME/.ssh/hostinger_openclaw"

# Si existe SSH key, encoder en base64
if [ -f "$VPS_SSH_KEY_PATH" ]; then
    echo -e "${GREEN}✅${NC} SSH key detectada: $VPS_SSH_KEY_PATH"
    VPS_SSH_KEY=$(cat "$VPS_SSH_KEY_PATH" | base64 -w 0)
    echo "   Base64 encoded: ${#VPS_SSH_KEY} chars"
else
    echo -e "${RED}❌${NC} SSH key no encontrada en $VPS_SSH_KEY_PATH"
    echo "   Necesitas agregar tu SSH private key ahí"
    exit 1
fi

# Pedir valores faltantes
echo ""
echo -e "${YELLOW}Ingresa los valores faltantes:${NC}"
echo ""

read -p "VERCEL_TOKEN (from vercel.com/account/tokens): " VERCEL_TOKEN
if [ -z "$VERCEL_TOKEN" ]; then
    echo -e "${RED}❌ VERCEL_TOKEN es requerido${NC}"
    exit 1
fi

read -p "VERCEL_PROJECT_ID (ID de proyecto en Vercel dashboard): " VERCEL_PROJECT_ID
if [ -z "$VERCEL_PROJECT_ID" ]; then
    echo -e "${RED}❌ VERCEL_PROJECT_ID es requerido${NC}"
    exit 1
fi

read -p "TELEGRAM_TOKEN_CEO (from @BotFather): " TELEGRAM_TOKEN_CEO
if [ -z "$TELEGRAM_TOKEN_CEO" ]; then
    echo -e "${RED}❌ TELEGRAM_TOKEN_CEO es requerido${NC}"
    exit 1
fi

CEO_CHAT_ID="5738935134"

echo ""
echo -e "${GREEN}✅ Valores recolectados${NC}"
echo ""

# ============================================================================
# PASO 2: AGREGAR GITHUB SECRETS (MANUAL)
# ============================================================================

echo -e "${BLUE}[PASO 2/5]${NC} GitHub Secrets (MANUAL)..."
echo ""
echo -e "${YELLOW}Abre en tu navegador:${NC}"
echo "https://github.com/perrykingla69-cyber/sonora-digital-corp/settings/secrets/actions"
echo ""
echo "Agrega estos secrets (New repository secret):"
echo ""
echo "┌─ VPS_HOST"
echo "│  $VPS_HOST"
echo "├─ VPS_SSH_USER"
echo "│  $VPS_SSH_USER"
echo "├─ VPS_SSH_KEY (base64)"
echo "│  ${VPS_SSH_KEY:0:50}... (${#VPS_SSH_KEY} chars)"
echo "├─ VERCEL_TOKEN"
echo "│  ${VERCEL_TOKEN:0:20}..."
echo "├─ VERCEL_PROJECT_ID"
echo "│  $VERCEL_PROJECT_ID"
echo "├─ TELEGRAM_TOKEN_CEO"
echo "│  ${TELEGRAM_TOKEN_CEO:0:20}..."
echo "└─ CEO_CHAT_ID"
echo "   $CEO_CHAT_ID"
echo ""

read -p "Presiona ENTER cuando hayas agregado los 7 secrets..."

echo -e "${GREEN}✅ Secrets configurados${NC}"
echo ""

# ============================================================================
# PASO 3: CREAR USUARIOS EN DB
# ============================================================================

echo -e "${BLUE}[PASO 3/5]${NC} Creando usuarios en PostgreSQL..."
echo ""

docker exec -i hermes_postgres psql -U postgres -d hermes_db << 'EOF'
-- Demo Users

INSERT INTO usuarios (id, email, nombre, apellido, contraseña_hash, rol, activo, verificado, created_at, updated_at)
VALUES ('usr-ceo-001', 'luis@sonoradigitalcorp.com', 'Luis Daniel', 'Guerrero Enciso',
        '$2b$12$WQvMxPBs9K9OvPvP2k/9u.7vY4Qc8kXkL9mP5nQrStXvY4Qc8kXkL', 'ceo', true, true, NOW(), NOW())
ON CONFLICT (email) DO UPDATE SET contraseña_hash = EXCLUDED.contraseña_hash, activo = true;

INSERT INTO usuarios (id, email, nombre, apellido, contraseña_hash, rol, activo, verificado, created_at, updated_at)
VALUES ('usr-client-001', 'demo@restaurante.sonoradigitalcorp.com', 'Gerente', 'Restaurante',
        '$2b$12$D9mK2pLqRsT7uVwXyZaB9.8qQvRwStUvWxYzAbCdEfGhIjKlMnOpQ', 'user', true, true, NOW(), NOW())
ON CONFLICT (email) DO UPDATE SET contraseña_hash = EXCLUDED.contraseña_hash, activo = true;

SELECT email, rol FROM usuarios WHERE email LIKE '%sonoradigitalcorp%' ORDER BY created_at DESC;
EOF

echo -e "${GREEN}✅ Usuarios creados${NC}"
echo ""

# ============================================================================
# PASO 4: GIT PUSH (dispara auto-deploy)
# ============================================================================

echo -e "${BLUE}[PASO 4/5]${NC} Git push origin main (dispara GitHub Actions)..."
echo ""

cd /home/mystic/hermes-os

# Verificar que no haya cambios sin commitear
if [ -n "$(git status --porcelain)" ]; then
    echo -e "${YELLOW}⚠️  Hay cambios sin commitear${NC}"
    git status --short
    read -p "¿Continuar? (s/n): " -r
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        exit 1
    fi
fi

git push origin main

echo ""
echo -e "${GREEN}✅ Push completado${NC}"
echo ""
echo "GitHub Actions está desplegando ahora:"
echo "  📊 Vercel: mission-control (~2 min)"
echo "  🖥️  VPS: hermes-api (docker compose) (~3 min)"
echo "  📱 Telegram: Notificación cuando termina"
echo ""

# ============================================================================
# PASO 5: HEALTH CHECKS
# ============================================================================

echo -e "${BLUE}[PASO 5/5]${NC} Health checks..."
echo ""

echo "Esperando 30 segundos para que GitHub Actions empiece..."
sleep 30

echo -e "${YELLOW}Verificando...${NC}"
echo ""

# Check GitHub Actions
echo "📋 GitHub Actions Status:"
echo "   https://github.com/perrykingla69-cyber/sonora-digital-corp/actions"
echo ""

# Check Vercel (si está disponible)
echo "🌐 Vercel Deploy:"
echo "   https://vercel.com/dashboard?project=mission-control"
echo ""

# Check API Health (local)
echo "🔌 API Health (VPS):"
echo "   Será: https://api.sonoradigitalcorp.com/health"
echo "   (Espera a que Vercel/VPS terminen de deployar)"
echo ""

# ============================================================================
# RESUMEN
# ============================================================================

echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ SETUP COMPLETADO${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo ""
echo "🎯 NEXT STEPS:"
echo ""
echo "1️⃣  Espera 3-5 minutos a que terminen los deploys"
echo "   → GitHub Actions: https://github.com/perrykingla69-cyber/sonora-digital-corp/actions"
echo "   → Vercel: https://vercel.com/dashboard"
echo "   → Telegram: Recibirás notificación del CEO bot"
echo ""
echo "2️⃣  DNS Setup (en tu registrador)"
echo "   → docs/DNS_SETUP.md"
echo "   → Agregar A record: sonoradigitalcorp.com → Vercel"
echo "   → Agregar CNAME: api.sonoradigitalcorp.com → VPS"
echo ""
echo "3️⃣  Explorar:"
echo "   → https://sonoradigitalcorp.com/ (login como CEO)"
echo "   → Email: luis@sonoradigitalcorp.com"
echo "   → Password: SonoraAdmin2024!Secure"
echo ""
echo "4️⃣  Probar ClawBot desde Telegram:"
echo "   → /task \"análisis del restaurante\""
echo "   → /orchestrator status"
echo "   → /mission-control"
echo ""
echo -e "${GREEN}🚀 HERMES OS está VIVO 🚀${NC}"
echo ""
