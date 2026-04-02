#!/bin/sh
# =============================================================================
# agent.sh — Script de arranque del agente OpenClaw persistente
# Proyecto: MYSTIC AI OS — Sonora Digital Corp
#
# Responsabilidades:
#   1. Instalar OpenClaw globalmente si no está instalado
#   2. Iniciar engram (servidor de memoria vectorial) en background
#   3. Configurar OpenClaw con credenciales de entorno
#   4. Arrancar OpenClaw en modo escucha (headless / daemon)
#
# Variables de entorno requeridas (provistas por docker-compose.openclaw.yml):
#   ANTHROPIC_API_KEY     — Clave de API Anthropic
#   TELEGRAM_BOT_TOKEN    — Token del bot de Telegram para OpenClaw
#   OPENCLAW_MODEL        — Modelo Claude a utilizar
#   OPENCLAW_WORKSPACE    — Ruta del workspace dentro del contenedor
#   OPENCLAW_CONFIG_DIR   — Directorio de configuración persistente
#
# SEGURIDAD: Este script NO debe imprimir secretos en stdout/stderr.
#            Redirige logs sensibles a /dev/null cuando sea necesario.
# =============================================================================

set -e  # Salir inmediatamente si un comando falla

# ---------------------------------------------------------------------------
# 0. Validación de variables de entorno obligatorias
# ---------------------------------------------------------------------------
echo "[openclaw] Validando variables de entorno..."

if [ -z "${ANTHROPIC_API_KEY}" ]; then
  echo "[openclaw] ERROR: ANTHROPIC_API_KEY no está definida. Abortando." >&2
  exit 1
fi

if [ -z "${TELEGRAM_BOT_TOKEN}" ]; then
  echo "[openclaw] ERROR: TELEGRAM_BOT_TOKEN no está definida. Abortando." >&2
  exit 1
fi

OPENCLAW_MODEL="${OPENCLAW_MODEL:-claude-haiku-4-5-20251001}"
OPENCLAW_WORKSPACE="${OPENCLAW_WORKSPACE:-/workspace}"
OPENCLAW_CONFIG_DIR="${OPENCLAW_CONFIG_DIR:-/root/.openclaw}"

echo "[openclaw] Modelo: ${OPENCLAW_MODEL}"
echo "[openclaw] Workspace: ${OPENCLAW_WORKSPACE}"
echo "[openclaw] Config dir: ${OPENCLAW_CONFIG_DIR}"

# ---------------------------------------------------------------------------
# 1. Instalar dependencias del sistema (Alpine)
# ---------------------------------------------------------------------------
echo "[openclaw] Instalando dependencias del sistema..."
apk add --no-cache \
  bash \
  curl \
  git \
  python3 \
  py3-pip \
  2>/dev/null

# ---------------------------------------------------------------------------
# 2. Instalar OpenClaw globalmente si no existe
# ---------------------------------------------------------------------------
if ! command -v openclaw > /dev/null 2>&1; then
  echo "[openclaw] Instalando openclaw via npm..."
  npm install -g openclaw --silent
  echo "[openclaw] OpenClaw instalado: $(openclaw --version 2>/dev/null || echo 'version desconocida')"
else
  echo "[openclaw] OpenClaw ya instalado: $(openclaw --version 2>/dev/null || echo 'version desconocida')"
fi

# ---------------------------------------------------------------------------
# 3. Crear directorios de configuración y logs
# ---------------------------------------------------------------------------
mkdir -p "${OPENCLAW_CONFIG_DIR}"
mkdir -p "${OPENCLAW_CONFIG_DIR}/logs"
mkdir -p "${OPENCLAW_CONFIG_DIR}/memory"

# ---------------------------------------------------------------------------
# 4. Generar archivo de configuración de OpenClaw
#    Los secretos se leen de variables de entorno, nunca hardcodeados aquí.
# ---------------------------------------------------------------------------
echo "[openclaw] Escribiendo configuración..."

cat > "${OPENCLAW_CONFIG_DIR}/config.json" <<EOF
{
  "model": "${OPENCLAW_MODEL}",
  "workspace": "${OPENCLAW_WORKSPACE}",
  "configDir": "${OPENCLAW_CONFIG_DIR}",
  "telegram": {
    "enabled": true,
    "listenMode": "polling"
  },
  "memory": {
    "enabled": true,
    "provider": "engram",
    "endpoint": "http://localhost:3333"
  },
  "agent": {
    "headless": true,
    "autoApprove": false,
    "maxTokensPerTurn": 8192,
    "logLevel": "info"
  },
  "permissions": {
    "allowRead": true,
    "allowWrite": false,
    "allowNetwork": true,
    "allowShell": false
  }
}
EOF

echo "[openclaw] Configuración escrita en ${OPENCLAW_CONFIG_DIR}/config.json"

# ---------------------------------------------------------------------------
# 5. Iniciar engram (servidor de memoria) en background
#    engram es el servidor de contexto/memoria vectorial de OpenClaw.
#    Se levanta en segundo plano y se guarda su PID para monitoreo.
# ---------------------------------------------------------------------------
echo "[openclaw] Iniciando engram serve en background..."

if command -v engram > /dev/null 2>&1; then
  engram serve \
    --port 3333 \
    --data-dir "${OPENCLAW_CONFIG_DIR}/memory" \
    >> "${OPENCLAW_CONFIG_DIR}/logs/engram.log" 2>&1 &

  ENGRAM_PID=$!
  echo $ENGRAM_PID > "${OPENCLAW_CONFIG_DIR}/engram.pid"
  echo "[openclaw] engram iniciado con PID ${ENGRAM_PID}"

  # Esperar a que engram esté listo (máximo 15 segundos)
  ENGRAM_READY=false
  for i in $(seq 1 15); do
    if curl -sf "http://localhost:3333/health" > /dev/null 2>&1; then
      ENGRAM_READY=true
      break
    fi
    echo "[openclaw] Esperando engram... (${i}/15)"
    sleep 1
  done

  if [ "${ENGRAM_READY}" = "false" ]; then
    echo "[openclaw] ADVERTENCIA: engram no respondió en 15s. Continuando sin memoria vectorial."
  else
    echo "[openclaw] engram listo en http://localhost:3333"
  fi
else
  echo "[openclaw] ADVERTENCIA: engram no encontrado. Continuando sin servidor de memoria."
  echo "[openclaw] Para habilitar memoria: npm install -g @openclaw/engram"
fi

# ---------------------------------------------------------------------------
# 6. Exportar credenciales como variables de entorno para OpenClaw
#    OpenClaw las lee de process.env en tiempo de ejecución.
# ---------------------------------------------------------------------------
export ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY}"
export TELEGRAM_BOT_TOKEN="${TELEGRAM_BOT_TOKEN}"

# ---------------------------------------------------------------------------
# 7. Función de limpieza al recibir señal de parada
# ---------------------------------------------------------------------------
cleanup() {
  echo "[openclaw] Señal de parada recibida. Cerrando procesos..."

  # Detener engram si está corriendo
  if [ -f "${OPENCLAW_CONFIG_DIR}/engram.pid" ]; then
    ENGRAM_PID=$(cat "${OPENCLAW_CONFIG_DIR}/engram.pid")
    if kill -0 "${ENGRAM_PID}" 2>/dev/null; then
      echo "[openclaw] Deteniendo engram (PID ${ENGRAM_PID})..."
      kill "${ENGRAM_PID}" 2>/dev/null || true
    fi
    rm -f "${OPENCLAW_CONFIG_DIR}/engram.pid"
  fi

  echo "[openclaw] Apagado limpio completado."
  exit 0
}

trap cleanup INT TERM

# ---------------------------------------------------------------------------
# 8. Iniciar OpenClaw en modo escucha (listen/daemon)
#    --telegram          Activa la integración con Telegram
#    --listen            Modo daemon: no interactivo, espera mensajes
#    --config            Ruta al archivo de configuración generado
#    --workspace         Directorio raíz del proyecto
#    --no-auto-approve   Requiere confirmación explícita para cambios
# ---------------------------------------------------------------------------
echo "[openclaw] Iniciando OpenClaw en modo listen..."
echo "[openclaw] Listo para recibir instrucciones via Telegram."

exec openclaw \
  --telegram \
  --listen \
  --config "${OPENCLAW_CONFIG_DIR}/config.json" \
  --workspace "${OPENCLAW_WORKSPACE}" \
  --no-auto-approve \
  >> "${OPENCLAW_CONFIG_DIR}/logs/openclaw.log" 2>&1
