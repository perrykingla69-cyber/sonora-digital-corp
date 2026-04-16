#!/bin/bash

################################################################################
# GitHub Secrets Setup Helper — HERMES OS
#
# Uso:
#   bash scripts/setup-github-secrets.sh
#
# Genera los valores necesarios para configurar los secrets en GitHub Actions.
# NO configura los secrets automáticamente (requiere interfaz web de GitHub).
################################################################################

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
  echo -e "${BLUE}════════════════════════════════════════${NC}"
  echo -e "${BLUE}$1${NC}"
  echo -e "${BLUE}════════════════════════════════════════${NC}"
}

print_success() {
  echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
  echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
  echo -e "${RED}❌ $1${NC}"
}

print_section() {
  echo -e "\n${BLUE}▸ $1${NC}"
}

# ============================================================================
print_header "HERMES OS — GitHub Secrets Setup Helper"

echo "Este script te ayuda a generar los valores para configurar secrets en GitHub."
echo "Los valores se generarán aquí, pero debes agregarlos manualmente a GitHub."
echo ""
read -p "¿Continuar? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
  print_error "Abortado"
  exit 1
fi

# ============================================================================
print_section "1. SSH Key (VPS_SSH_KEY)"

if [ -f ~/.ssh/id_rsa ]; then
  print_success "Encontrado: ~/.ssh/id_rsa"
  read -p "¿Usar esta key? (y/n) " -n 1 -r
  echo
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    SSH_KEY_FILE="$HOME/.ssh/id_rsa"
  else
    print_warning "Especifica una key alternativa:"
    read -p "Ruta: " SSH_KEY_FILE
    if [ ! -f "$SSH_KEY_FILE" ]; then
      print_error "Archivo no encontrado: $SSH_KEY_FILE"
      exit 1
    fi
  fi
else
  print_warning "No se encontró ~/.ssh/id_rsa"
  read -p "Ruta a SSH key: " SSH_KEY_FILE
  if [ ! -f "$SSH_KEY_FILE" ]; then
    print_error "Archivo no encontrado"
    exit 1
  fi
fi

# Verificar si la key tiene passphrase
if grep -q "ENCRYPTED" "$SSH_KEY_FILE"; then
  print_warning "La key parece tener passphrase. Para GitHub Actions, se necesita sin passphrase."
  print_warning "Si continúas, se creará una copia sin passphrase en ~/.ssh/hermes_deploy"
  read -p "¿Continuar? (y/n) " -n 1 -r
  echo
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_section "  Removiendo passphrase..."
    read -s -p "  Ingresa la passphrase actual: " CURRENT_PASS
    echo
    ssh-keygen -p -f "$SSH_KEY_FILE" -N "" -P "$CURRENT_PASS" 2>/dev/null && \
      print_success "Passphrase removida" || print_error "Passphrase incorrecta"
  else
    print_error "Abortado"
    exit 1
  fi
fi

# Codificar en base64
SSH_KEY_B64=$(cat "$SSH_KEY_FILE" | base64 -w0)
SSH_KEY_LENGTH=${#SSH_KEY_B64}

print_success "SSH key codificada (base64)"
echo "  Largo: $SSH_KEY_LENGTH caracteres"
echo ""
echo -e "${YELLOW}Valor para GitHub secret VPS_SSH_KEY:${NC}"
echo -e "${BLUE}$SSH_KEY_B64${NC}"
echo ""

# ============================================================================
print_section "2. VPS Host (VPS_HOST)"

print_warning "¿Cuál es la IP o hostname del VPS?"
print_warning "Ejemplo: 192.168.1.100 o vps.tudominio.com"
read -p "VPS_HOST: " VPS_HOST

if [ -z "$VPS_HOST" ]; then
  print_error "VPS_HOST no puede estar vacío"
  exit 1
fi

print_success "VPS_HOST configurado"
echo ""
echo -e "${YELLOW}Valor para GitHub secret VPS_HOST:${NC}"
echo -e "${BLUE}$VPS_HOST${NC}"
echo ""

# ============================================================================
print_section "3. VPS SSH User (VPS_SSH_USER)"

print_warning "¿Cuál es el usuario SSH para el VPS? (usualmente 'root')"
read -p "VPS_SSH_USER [root]: " VPS_SSH_USER
VPS_SSH_USER=${VPS_SSH_USER:-root}

print_success "VPS_SSH_USER configurado"
echo ""
echo -e "${YELLOW}Valor para GitHub secret VPS_SSH_USER:${NC}"
echo -e "${BLUE}$VPS_SSH_USER${NC}"
echo ""

# ============================================================================
print_section "4. Vercel Token (VERCEL_TOKEN)"

print_warning "Para obtener el token de Vercel:"
print_warning "  1. Ve a https://vercel.com/account/tokens"
print_warning "  2. Clic en 'Create Token'"
print_warning "  3. Nombre: 'github-actions'"
print_warning "  4. Copia el token y pégalo aquí"
echo ""
read -p "VERCEL_TOKEN: " VERCEL_TOKEN

if [ -z "$VERCEL_TOKEN" ]; then
  print_error "VERCEL_TOKEN no puede estar vacío"
  exit 1
fi

print_success "VERCEL_TOKEN configurado"
echo ""

# ============================================================================
print_section "5. Vercel Project ID (VERCEL_PROJECT_ID)"

print_warning "Para obtener el project ID:"
print_warning "  1. Ve a https://vercel.com"
print_warning "  2. Abre el proyecto 'mission-control'"
print_warning "  3. Haz clic en 'Settings'"
print_warning "  4. Busca 'Project ID' (comienza con 'prj_')"
print_warning "  5. Cópialo aquí"
echo ""
read -p "VERCEL_PROJECT_ID: " VERCEL_PROJECT_ID

if [ -z "$VERCEL_PROJECT_ID" ]; then
  print_error "VERCEL_PROJECT_ID no puede estar vacío"
  exit 1
fi

print_success "VERCEL_PROJECT_ID configurado"
echo ""

# ============================================================================
print_section "6. Vercel Org ID (VERCEL_ORG_ID) — Opcional"

print_warning "Si usas un equipo en Vercel, ingresa el organization ID."
print_warning "Si no, presiona Enter para omitir."
echo ""
read -p "VERCEL_ORG_ID [omitir]: " VERCEL_ORG_ID

if [ -n "$VERCEL_ORG_ID" ]; then
  print_success "VERCEL_ORG_ID configurado"
else
  print_warning "VERCEL_ORG_ID omitido (recomendado para equipo)"
fi
echo ""

# ============================================================================
print_section "7. Telegram Bot Token (TELEGRAM_TOKEN_CEO)"

print_warning "Para crear un bot de Telegram:"
print_warning "  1. Abre Telegram"
print_warning "  2. Busca @BotFather"
print_warning "  3. Envía /newbot"
print_warning "  4. Sigue las instrucciones (nombre, username)"
print_warning "  5. Te dará un token (ej: 123456:ABC-DEF...)"
print_warning "  6. Cópialo aquí"
echo ""
read -p "TELEGRAM_TOKEN_CEO: " TELEGRAM_TOKEN_CEO

if [ -z "$TELEGRAM_TOKEN_CEO" ]; then
  print_error "TELEGRAM_TOKEN_CEO no puede estar vacío"
  exit 1
fi

print_success "TELEGRAM_TOKEN_CEO configurado"
echo ""

# ============================================================================
print_section "8. Telegram Chat ID (CEO_CHAT_ID)"

print_warning "Para obtener tu Chat ID:"
print_warning "  1. Abre Telegram"
print_warning "  2. Busca @userinfobot"
print_warning "  3. Envía cualquier mensaje"
print_warning "  4. Recibirás tu ID de usuario"
print_warning "  5. Cópialo aquí (es un número largo)"
echo ""
read -p "CEO_CHAT_ID: " CEO_CHAT_ID

if [ -z "$CEO_CHAT_ID" ]; then
  print_error "CEO_CHAT_ID no puede estar vacío"
  exit 1
fi

print_success "CEO_CHAT_ID configurado"
echo ""

# ============================================================================
print_header "📋 RESUMEN DE SECRETS"

echo ""
echo -e "${YELLOW}1. VPS_SSH_KEY${NC} (SSH private key en base64)"
echo "   ${BLUE}[Mostrado arriba — muy largo para repetir]${NC}"
echo ""
echo -e "${YELLOW}2. VPS_HOST${NC}"
echo "   ${BLUE}$VPS_HOST${NC}"
echo ""
echo -e "${YELLOW}3. VPS_SSH_USER${NC}"
echo "   ${BLUE}$VPS_SSH_USER${NC}"
echo ""
echo -e "${YELLOW}4. VERCEL_TOKEN${NC}"
echo "   ${BLUE}${VERCEL_TOKEN:0:15}...${NC}"
echo ""
echo -e "${YELLOW}5. VERCEL_PROJECT_ID${NC}"
echo "   ${BLUE}$VERCEL_PROJECT_ID${NC}"
echo ""
if [ -n "$VERCEL_ORG_ID" ]; then
  echo -e "${YELLOW}6. VERCEL_ORG_ID${NC}"
  echo "   ${BLUE}$VERCEL_ORG_ID${NC}"
  echo ""
fi
echo -e "${YELLOW}7. TELEGRAM_TOKEN_CEO${NC}"
echo "   ${BLUE}${TELEGRAM_TOKEN_CEO:0:15}...${NC}"
echo ""
echo -e "${YELLOW}8. CEO_CHAT_ID${NC}"
echo "   ${BLUE}$CEO_CHAT_ID${NC}"
echo ""

# ============================================================================
print_header "🚀 PRÓXIMOS PASOS"

echo ""
echo "1. Ve a: https://github.com/perrykingla69-cyber/sonora-digital-corp/settings/secrets/actions"
echo ""
echo "2. Haz clic en 'New repository secret' y agrega cada uno:"
echo ""
echo "   • VPS_SSH_KEY = [pega el valor base64 mostrado arriba]"
echo "   • VPS_HOST = $VPS_HOST"
echo "   • VPS_SSH_USER = $VPS_SSH_USER"
echo "   • VERCEL_TOKEN = $VERCEL_TOKEN"
echo "   • VERCEL_PROJECT_ID = $VERCEL_PROJECT_ID"
if [ -n "$VERCEL_ORG_ID" ]; then
  echo "   • VERCEL_ORG_ID = $VERCEL_ORG_ID"
fi
echo "   • TELEGRAM_TOKEN_CEO = $TELEGRAM_TOKEN_CEO"
echo "   • CEO_CHAT_ID = $CEO_CHAT_ID"
echo ""
echo "3. Verifica que todos aparezcan en GitHub → Settings → Secrets"
echo ""
echo "4. Prueba el workflow: Actions → Deploy — Vercel + VPS + Notify → Run workflow"
echo ""

# ============================================================================
print_section "Guardar valores en archivo local (opcional)"

read -p "¿Guardar los valores en un archivo local? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
  SECRETS_FILE="$(pwd)/.github-secrets.env"
  cat > "$SECRETS_FILE" << EOF
# GitHub Secrets — HERMES OS
# Generado: $(date)
# ADVERTENCIA: Este archivo contiene secretos. NO lo commits.

VPS_SSH_KEY="$SSH_KEY_B64"
VPS_HOST="$VPS_HOST"
VPS_SSH_USER="$VPS_SSH_USER"
VERCEL_TOKEN="$VERCEL_TOKEN"
VERCEL_PROJECT_ID="$VERCEL_PROJECT_ID"
VERCEL_ORG_ID="$VERCEL_ORG_ID"
TELEGRAM_TOKEN_CEO="$TELEGRAM_TOKEN_CEO"
CEO_CHAT_ID="$CEO_CHAT_ID"
EOF

  print_success "Guardado en: $SECRETS_FILE"
  print_warning "⚠️  IMPORTANTE: Este archivo contiene secretos. No lo commits."
  print_warning "    Añádelo a .gitignore si no está ya"
fi

echo ""
print_success "¡Listo! Continúa con los pasos en GitHub."
