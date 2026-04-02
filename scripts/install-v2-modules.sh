#!/bin/bash
set -e

echo "=========================================="
echo "INSTALANDO MÓDULOS V2 - MYSTIC"
echo "=========================================="

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}1. Verificando estructura...${NC}"
cd ~/sonora-digital-corp
ls -la packages/ backend/app/ | grep -E "(agent-swarm|fiscal_reasoning|document_intelligence|predictive|omnichannel)" || echo "Creando estructura..."

echo -e "${BLUE}2. Instalando dependencias Python...${NC}"
pip install -q qdrant-client httpx pydantic "fastapi>=0.100" "uvicorn>=0.23"

echo -e "${BLUE}3. Instalando paquete Agent Swarm...${NC}"
cd packages/agent-swarm-v2
pip install -q -e .
cd ../..

echo -e "${BLUE}4. Verificando imports...${NC}"
python3 -c "
import sys
sys.path.insert(0, 'packages/agent-swarm-v2')
sys.path.insert(0, 'backend/app')
try:
    from fiscal_reasoning.engine import MotorRazonamientoFiscal
    from document_intelligence.validator import DocumentIntelligencePipeline
    from predictive.early_warning import PredictiveFiscalEngine
    from omnichannel.unified_messaging import OmnichannelOrchestrator
    print('✓ Todos los módulos importan correctamente')
except Exception as e:
    print(f'✗ Error: {e}')
    sys.exit(1)
"

echo -e "${BLUE}5. Verificando frontend components...${NC}"
ls -la frontend/components/dashboard-v2/

echo -e "${BLUE}6. Actualizando docker-compose...${NC}"
docker compose -f infra/docker-compose.yml -f infra/docker-compose.override.yml config > /dev/null && echo "✓ Docker compose válido"

echo ""
echo -e "${GREEN}==========================================${NC}"
echo -e "${GREEN}INSTALACIÓN V2 COMPLETADA${NC}"
echo -e "${GREEN}==========================================${NC}"
echo ""
echo "Próximos pasos:"
echo "1. Reiniciar servicios: docker compose up -d --build api"
echo "2. Probar endpoint: curl http://localhost:8000/v2/fiscal/analyze-mve"
echo "3. Verificar logs: docker logs mystic_api -f"
echo ""
echo "Endpoints nuevos disponibles:"
echo "  POST /v2/fiscal/analyze-mve"
echo "  GET  /v2/predictive/alerts/{tenant_id}"
echo "  POST /v2/omnichannel/send"
echo "  POST /v2/content/generate-campaign"
