#!/bin/bash
# Backup PostgreSQL — reemplaza el cron roto (apuntaba al container muerto)
# Cron: 0 3 * * * /home/mystic/hermes-os/infra/scripts/backup.sh

set -euo pipefail

BACKUP_DIR="/home/mystic/hermes-os/backups"
CONTAINER="hermes_postgres"
KEEP_DAYS=14
DATE=$(date +%Y%m%d_%H%M%S)
FILE="$BACKUP_DIR/hermes_db_${DATE}.dump"

source /home/mystic/hermes-os/.env

mkdir -p "$BACKUP_DIR"

docker exec "$CONTAINER" pg_dump \
    -U "$DB_USER" \
    -d "$DB_NAME" \
    -Fc \
    > "$FILE"

# Verificar que no está vacío
SIZE=$(stat -c%s "$FILE" 2>/dev/null || echo 0)
if [ "$SIZE" -lt 1000 ]; then
    echo "[ERROR $(date)] Backup vacío o muy pequeño: $FILE ($SIZE bytes)" >&2
    rm -f "$FILE"
    exit 1
fi

# Limpiar backups viejos
find "$BACKUP_DIR" -name "*.dump" -mtime +$KEEP_DAYS -delete

echo "[$(date)] Backup OK: $FILE ($(du -h "$FILE" | cut -f1))"
