#!/bin/bash
# ╔══════════════════════════════════════════════════════════╗
# ║     HERMES OS — Wipe VPS                                 ║
# ║     Elimina todo lo anterior. IRREVERSIBLE.              ║
# ╚══════════════════════════════════════════════════════════╝
# EJECUTAR EN EL VPS con: bash wipe_vps.sh

set -euo pipefail

echo "⚠️  WIPE VPS — Esto eliminará:"
echo "   - Todos los contenedores Docker"
echo "   - Todos los volúmenes Docker"
echo "   - Todas las imágenes Docker"
echo "   - /home/mystic/sonora-digital-corp"
echo "   - /home/mystic/web"
echo "   - /home/mystic/backups (dumps viejos)"
echo "   - /home/mystic/fourgea_docs"
echo ""
echo "   SE PRESERVA:"
echo "   - /etc/letsencrypt (SSL)"
echo "   - /etc/nginx/sites-enabled"
echo "   - ~/.ssh (keys)"
echo "   - /home/mystic/hermes-os (nuevo proyecto)"
echo ""
read -p "¿Confirmar wipe? (escribe WIPE para confirmar): " confirm

[ "$confirm" != "WIPE" ] && { echo "Cancelado."; exit 0; }

echo "[1/6] Deteniendo contenedores..."
docker stop $(docker ps -q) 2>/dev/null || true
docker rm $(docker ps -aq) 2>/dev/null || true

echo "[2/6] Eliminando volúmenes..."
docker volume rm $(docker volume ls -q) 2>/dev/null || true

echo "[3/6] Limpiando imágenes..."
docker rmi $(docker images -q) 2>/dev/null || true
docker system prune -af 2>/dev/null || true

echo "[4/6] Eliminando directorios obsoletos..."
rm -rf /home/mystic/sonora-digital-corp
rm -rf /home/mystic/web
rm -rf /home/mystic/fourgea_docs
rm -f /home/mystic/backup.env

# Limpiar backups vacíos (mantener el schema si existiera)
find /home/mystic/backups -name "*.dump" -empty -delete 2>/dev/null || true
find /home/mystic/backups -name "*.dump" -size -1k -delete 2>/dev/null || true

echo "[5/6] Removiendo nginx configs viejas..."
rm -f /etc/nginx/sites-enabled/mystic
rm -f /etc/nginx/sites-enabled/bazar-acordeones-hmo
rm -f /etc/nginx/sites-available/mystic
rm -f /etc/nginx/sites-available/bazar-acordeones-hmo
nginx -t && systemctl reload nginx

echo "[6/6] Limpiando .env viejo si existe..."
[ -f /root/.env ] && mv /root/.env /root/.env.backup.$(date +%Y%m%d) && echo "  -> /root/.env respaldado"

echo ""
echo "✅ VPS limpio. Listo para HERMES OS."
echo ""
echo "Siguiente paso:"
echo "  cd /home/mystic/hermes-os"
echo "  cp .env.example .env && nano .env"
echo "  bash infra/scripts/deploy.sh --fresh"
