#!/bin/bash
# Instala crontabs correctos — elimina los rotos del VPS viejo
# Ejecutar en el VPS como root: bash setup_crons.sh

HERMES_DIR="/home/mystic/hermes-os"

chmod +x "$HERMES_DIR/infra/scripts/backup.sh"
chmod +x "$HERMES_DIR/infra/scripts/renew_ssl.sh"
chmod +x "$HERMES_DIR/infra/scripts/deploy.sh"
chmod +x "$HERMES_DIR/infra/scripts/wipe_vps.sh"

# Eliminar crons rotos y reemplazar
crontab -l 2>/dev/null | grep -v 'mystic-platform\|backup.sh\|renew_ssl' > /tmp/crontab_clean || true

cat >> /tmp/crontab_clean << 'EOF'
# HERMES OS — Backup diario a las 3am
0 3 * * * /home/mystic/hermes-os/infra/scripts/backup.sh >> /var/log/hermes_backup.log 2>&1
# HERMES OS — Renovar SSL cada lunes
0 4 * * 1 /home/mystic/hermes-os/infra/scripts/renew_ssl.sh
EOF

crontab /tmp/crontab_clean
rm /tmp/crontab_clean

echo "✅ Crontabs actualizados:"
crontab -l
