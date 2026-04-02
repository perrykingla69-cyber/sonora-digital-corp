#!/bin/bash
# SSL Renewal — reemplaza el cron roto que apuntaba a mystic-platform/
# Cron: 0 3 * * 1 /home/mystic/hermes-os/infra/scripts/renew_ssl.sh

set -euo pipefail

LOG="/var/log/hermes_ssl_renew.log"
COMPOSE="docker compose -f /home/mystic/hermes-os/docker-compose.yml"

echo "[$(date)] Renovando SSL..." >> "$LOG"
certbot renew --quiet --nginx >> "$LOG" 2>&1
systemctl reload nginx >> "$LOG" 2>&1
echo "[$(date)] SSL OK" >> "$LOG"
