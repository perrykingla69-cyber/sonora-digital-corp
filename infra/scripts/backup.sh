#!/bin/sh
# backup.sh — Backup automático PostgreSQL (corre dentro del contenedor mystic_backup)
DB_HOST="${DB_HOST:-postgres}"
DB_USER="${DB_USER:-mystic}"
DB_NAME="${DB_NAME:-mystic_unified}"
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
FILE="${BACKUP_DIR}/mystic_${DATE}.sql.gz"
KEEP_DAYS="${KEEP_DAYS:-7}"

mkdir -p "$BACKUP_DIR"
echo "[backup] Dump de $DB_NAME@$DB_HOST ..."

if pg_dump -h "$DB_HOST" -U "$DB_USER" "$DB_NAME" | gzip > "$FILE"; then
    echo "[backup] OK — $FILE ($(du -sh "$FILE" | cut -f1))"
else
    echo "[backup] ERROR — pg_dump falló"; rm -f "$FILE"; exit 1
fi

find "$BACKUP_DIR" -name "mystic_*.sql.gz" -mtime +"$KEEP_DAYS" -exec rm -f {} \;
echo "[backup] Backups retenidos: $(find "$BACKUP_DIR" -name "mystic_*.sql.gz" | wc -l)"
