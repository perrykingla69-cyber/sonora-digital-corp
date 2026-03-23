#!/usr/bin/env bash
# mystic_monitor.sh — Health check completo + auto-repair + Telegram report
# Uso: ./mystic_monitor.sh [--silent]   (--silent omite el reporte si todo OK)

set -euo pipefail

SILENT="${1:-}"
DC_CMD="docker compose -f /home/mystic/sonora-digital-corp/infra/docker-compose.vps.yml --env-file /home/mystic/sonora-digital-corp/infra/.env.vps --project-name mystic"
CONTAINERS=(mystic_postgres mystic_redis mystic_api mystic_n8n mystic-ollama mystic_qdrant mystic_frontend mystic_bot mystic_wa)
API_URL="http://localhost:8000/status"
ISSUES=()
REPAIRED=()

# ── Telegram helper ──────────────────────────────────────────────────────────
send_telegram() {
  local msg="$1"
  if [[ -z "${TELEGRAM_TOKEN:-}" || -z "${TELEGRAM_CHAT_ID:-}" ]]; then
    # Leer desde .env.vps si no están en el entorno
    if [[ -f /home/mystic/sonora-digital-corp/infra/.env.vps ]]; then
      TELEGRAM_TOKEN=$(grep '^TELEGRAM_TOKEN=' /home/mystic/sonora-digital-corp/infra/.env.vps | cut -d= -f2- | tr -d '"')
      TELEGRAM_CHAT_ID=$(grep '^TELEGRAM_CHAT_ID=' /home/mystic/sonora-digital-corp/infra/.env.vps | cut -d= -f2- | tr -d '"')
    fi
  fi
  [[ -z "${TELEGRAM_TOKEN:-}" ]] && return 0
  python3 -c "
import urllib.request, json, sys
data = json.dumps({
  'chat_id': '${TELEGRAM_CHAT_ID}',
  'text': sys.stdin.read(),
  'parse_mode': 'HTML'
}).encode()
req = urllib.request.Request(
  'https://api.telegram.org/bot${TELEGRAM_TOKEN}/sendMessage',
  data=data, headers={'Content-Type': 'application/json'}
)
urllib.request.urlopen(req, timeout=10)
" <<< "$msg" 2>/dev/null || echo "[warn] Telegram no disponible"
}

# ── 1. Contenedores ──────────────────────────────────────────────────────────
echo "==> Revisando contenedores..."
CONTAINER_STATUS=""
ALL_UP=true
for c in "${CONTAINERS[@]}"; do
  STATUS=$(docker inspect --format='{{.State.Status}}' "$c" 2>/dev/null || echo "missing")
  if [[ "$STATUS" == "running" ]]; then
    CONTAINER_STATUS+="  ✅ $c\n"
  else
    CONTAINER_STATUS+="  ❌ $c ($STATUS)\n"
    ISSUES+=("Contenedor $c está $STATUS")
    ALL_UP=false
    echo "==> Auto-repair: reiniciando $c..."
    $DC_CMD up -d "$c" 2>/dev/null && REPAIRED+=("$c reiniciado") || true
  fi
done

# ── 2. API Health ────────────────────────────────────────────────────────────
echo "==> Revisando API..."
API_RESP=$(python3 -c "
import urllib.request, json
try:
  r = urllib.request.urlopen('${API_URL}', timeout=5)
  print(r.read().decode())
except Exception as e:
  print('{\"api\":\"error\",\"detail\":\"' + str(e) + '\"}')
" 2>/dev/null)
API_OK=$(echo "$API_RESP" | python3 -c "import sys,json; d=json.load(sys.stdin); print('ok' if d.get('api')=='ok' else 'fail')" 2>/dev/null || echo "fail")

if [[ "$API_OK" == "ok" ]]; then
  API_LINE="✅ API respondiendo"
else
  API_LINE="❌ API sin respuesta"
  ISSUES+=("API no responde en $API_URL")
fi

# ── 3. Disco y RAM ───────────────────────────────────────────────────────────
DISK_USED=$(df -h / | awk 'NR==2{print $5}')
DISK_AVAIL=$(df -h / | awk 'NR==2{print $4}')
RAM_TOTAL=$(free -m | awk '/^Mem/{print $2}')
RAM_USED=$(free -m | awk '/^Mem/{print $3}')
RAM_PCT=$(( RAM_USED * 100 / RAM_TOTAL ))

DISK_PCT=$(echo "$DISK_USED" | tr -d '%')
[[ "$DISK_PCT" -gt 85 ]] && ISSUES+=("Disco al ${DISK_USED} — quedan solo ${DISK_AVAIL}")
[[ "$RAM_PCT" -gt 90 ]] && ISSUES+=("RAM al ${RAM_PCT}% — ${RAM_USED}/${RAM_TOTAL} MB")

# ── 4. Git — verificar que main esté actualizado ────────────────────────────
echo "==> Revisando repo..."
cd /home/mystic/sonora-digital-corp
git fetch origin main --quiet 2>/dev/null || true
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main)
if [[ "$LOCAL" != "$REMOTE" ]]; then
  GIT_LINE="⚠️ Repo desactualizado (hay commits nuevos en origin/main)"
  ISSUES+=("Repo local desactualizado")
else
  GIT_LINE="✅ Repo al día ($(git rev-parse --short HEAD))"
fi

# ── 5. Frontend accesible ───────────────────────────────────────────────────
FRONT_CODE=$(python3 -c "
import urllib.request
try:
  r = urllib.request.urlopen('http://localhost:3000', timeout=5)
  print(r.status)
except Exception: print(0)
" 2>/dev/null)
if [[ "$FRONT_CODE" == "200" ]]; then
  FRONT_LINE="✅ Frontend :3000 OK"
else
  FRONT_LINE="❌ Frontend :3000 no responde (código: ${FRONT_CODE})"
  ISSUES+=("Frontend no responde")
fi

# ── 6. Construir reporte ─────────────────────────────────────────────────────
NOW=$(date '+%Y-%m-%d %H:%M')
ISSUE_COUNT=${#ISSUES[@]}
REPAIR_COUNT=${#REPAIRED[@]}

if [[ "$ISSUE_COUNT" -eq 0 ]]; then
  HEADER="🟢 <b>Mystic — Todo operativo</b>"
else
  HEADER="🔴 <b>Mystic — ${ISSUE_COUNT} problema(s) detectado(s)</b>"
fi

MSG="${HEADER}
📅 ${NOW}

<b>Contenedores (${#CONTAINERS[@]}):</b>
$(echo -e "$CONTAINER_STATUS")
${API_LINE}
${FRONT_LINE}
${GIT_LINE}

<b>Recursos:</b>
  💾 Disco: ${DISK_USED} usado (${DISK_AVAIL} libre)
  🧠 RAM: ${RAM_USED}/${RAM_TOTAL} MB (${RAM_PCT}%)"

if [[ "$REPAIR_COUNT" -gt 0 ]]; then
  MSG+="

<b>Auto-reparado:</b>"
  for r in "${REPAIRED[@]}"; do
    MSG+="
  🔧 $r"
  done
fi

if [[ "$ISSUE_COUNT" -gt 0 ]]; then
  MSG+="

<b>Problemas activos:</b>"
  for issue in "${ISSUES[@]}"; do
    MSG+="
  ⚠️ $issue"
  done
fi

MSG+="

🔗 sonoradigitalcorp.com"

echo "==> Reporte:"
echo -e "$MSG" | sed 's/<[^>]*>//g'

# Enviar si hay problemas, o si no es modo silencioso
if [[ "$ISSUE_COUNT" -gt 0 || "$SILENT" != "--silent" ]]; then
  echo "==> Enviando a Telegram..."
  send_telegram "$MSG"
fi

# Exit code no-zero si hay problemas sin reparar
exit $ISSUE_COUNT
