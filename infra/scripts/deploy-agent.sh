#!/bin/bash
# Script auxiliar para deploy manual de agentes en VPS
# Uso: ./deploy-agent.sh <agent_id> <image_tag>
#
# Normalmente esto lo hace Agent Factory automáticamente.
# Este script es solo para debug/recovery.

set -e

AGENT_ID=${1:?"Uso: $0 <agent_id> [image_tag]"}
IMAGE_TAG=${2:-"hermes-agent-${AGENT_ID:0:8}:latest"}
CONTAINER_NAME="agent-${AGENT_ID:0:8}"

echo "Deploy agente: $AGENT_ID"
echo "Imagen: $IMAGE_TAG"
echo "Container: $CONTAINER_NAME"

# Parar container existente si hay
docker stop "$CONTAINER_NAME" 2>/dev/null || true
docker rm "$CONTAINER_NAME" 2>/dev/null || true

# Levantar container
docker run -d \
  --name "$CONTAINER_NAME" \
  --network hermes_network \
  --restart unless-stopped \
  --label "hermes.agent_id=$AGENT_ID" \
  --label "hermes.managed=true" \
  -e "AGENT_ID=$AGENT_ID" \
  -e "OPENROUTER_API_KEY=${OPENROUTER_API_KEY}" \
  "$IMAGE_TAG"

echo "Container levantado: $(docker inspect $CONTAINER_NAME --format '{{.Id}}' | head -c 12)"
