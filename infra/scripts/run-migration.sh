#!/bin/bash
# Ejecuta migración SQL en la base de datos del VPS
# Uso: ./run-migration.sh 004_saas_tables.sql

set -e

MIGRATION=${1:-004_saas_tables.sql}
MIGRATION_FILE="$(dirname "$0")/../migrations/$MIGRATION"

if [ ! -f "$MIGRATION_FILE" ]; then
  echo "ERROR: Migración no encontrada: $MIGRATION_FILE"
  exit 1
fi

# Leer .env si existe
if [ -f "$(dirname "$0")/../.env" ]; then
  source "$(dirname "$0")/../.env"
fi

DB_URL=${DATABASE_URL:-"postgresql://mystic:${DB_PASSWORD:-mystic_secure_2026}@localhost:5432/mystic_unified"}

echo "Ejecutando migración: $MIGRATION"
echo "DB: $DB_URL (sin password)"

# Ejecutar en el container de postgres
docker compose -f "$(dirname "$0")/../docker-compose.yml" exec -T postgres \
  psql -U mystic -d mystic_unified < "$MIGRATION_FILE"

echo "Migración completada: $MIGRATION"
