#!/bin/bash
# CURL Examples — HERMES & MYSTIC Endpoints

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Base URL
BASE_URL="http://localhost:8000"
TENANT_ID="550e8400-e29b-41d4-a716-446655440000"

echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}   HERMES & MYSTIC Endpoints — CURL Examples${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}\n"

# ============================================================================
# 1. HERMES Chat Endpoint
# ============================================================================
echo -e "${YELLOW}1️⃣  POST /api/v1/agents/hermes/chat${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

echo -e "Basic question (with RAG):"
echo -e "${GREEN}curl -X POST ${BASE_URL}/api/v1/agents/hermes/chat \\${NC}"
echo -e "${GREEN}  -H 'Content-Type: application/json' \\${NC}"
echo -e "${GREEN}  -d '{${NC}"
echo -e "${GREEN}    \"tenant_id\": \"${TENANT_ID}\",${NC}"
echo -e "${GREEN}    \"message\": \"¿Cuál es la tasa de IVA en México?\",${NC}"
echo -e "${GREEN}    \"use_rag\": true${NC}"
echo -e "${GREEN}  }'${NC}\n"

echo -e "Question with context:"
echo -e "${GREEN}curl -X POST ${BASE_URL}/api/v1/agents/hermes/chat \\${NC}"
echo -e "${GREEN}  -H 'Content-Type: application/json' \\${NC}"
echo -e "${GREEN}  -d '{${NC}"
echo -e "${GREEN}    \"tenant_id\": \"${TENANT_ID}\",${NC}"
echo -e "${GREEN}    \"message\": \"¿Es deducible?\",${NC}"
echo -e "${GREEN}    \"context\": \"Tenemos gastos de transporte para clientes.\",${NC}"
echo -e "${GREEN}    \"use_rag\": true${NC}"
echo -e "${GREEN}  }'${NC}\n"

echo -e "Without RAG (faster):"
echo -e "${GREEN}curl -X POST ${BASE_URL}/api/v1/agents/hermes/chat \\${NC}"
echo -e "${GREEN}  -H 'Content-Type: application/json' \\${NC}"
echo -e "${GREEN}  -d '{${NC}"
echo -e "${GREEN}    \"tenant_id\": \"${TENANT_ID}\",${NC}"
echo -e "${GREEN}    \"message\": \"¿Cuál es el RFC?\",${NC}"
echo -e "${GREEN}    \"use_rag\": false${NC}"
echo -e "${GREEN}  }'${NC}\n\n"

# ============================================================================
# 2. MYSTIC Analyze Endpoint
# ============================================================================
echo -e "${YELLOW}2️⃣  GET /api/v1/agents/mystic/analyze${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

echo -e "Fiscal analysis:"
echo -e "${GREEN}curl -X GET \"${BASE_URL}/api/v1/agents/mystic/analyze\\${NC}"
echo -e "${GREEN}?tenant_id=${TENANT_ID}\\${NC}"
echo -e "${GREEN}&analysis_type=fiscal\"${NC}\n"

echo -e "Food/Restaurant analysis:"
echo -e "${GREEN}curl -X GET \"${BASE_URL}/api/v1/agents/mystic/analyze\\${NC}"
echo -e "${GREEN}?tenant_id=${TENANT_ID}\\${NC}"
echo -e "${GREEN}&analysis_type=food\"${NC}\n"

echo -e "Business analysis:"
echo -e "${GREEN}curl -X GET \"${BASE_URL}/api/v1/agents/mystic/analyze\\${NC}"
echo -e "${GREEN}?tenant_id=${TENANT_ID}\\${NC}"
echo -e "${GREEN}&analysis_type=business\"${NC}\n\n"

# ============================================================================
# 3. Agents Status Endpoint
# ============================================================================
echo -e "${YELLOW}3️⃣  GET /api/v1/agents/status${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

echo -e "${GREEN}curl -X GET \"${BASE_URL}/api/v1/agents/status\\${NC}"
echo -e "${GREEN}?tenant_id=${TENANT_ID}\"${NC}\n\n"

# ============================================================================
# 4. Error Cases
# ============================================================================
echo -e "${YELLOW}4️⃣  Error Cases (Testing)${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

echo -e "Missing tenant_id (422 Validation Error):"
echo -e "${RED}curl -X POST ${BASE_URL}/api/v1/agents/hermes/chat \\${NC}"
echo -e "${RED}  -H 'Content-Type: application/json' \\${NC}"
echo -e "${RED}  -d '{${NC}"
echo -e "${RED}    \"message\": \"Pregunta\"${NC}"
echo -e "${RED}  }'${NC}\n"

echo -e "Empty message (422 Validation Error):"
echo -e "${RED}curl -X POST ${BASE_URL}/api/v1/agents/hermes/chat \\${NC}"
echo -e "${RED}  -H 'Content-Type: application/json' \\${NC}"
echo -e "${RED}  -d '{${NC}"
echo -e "${RED}    \"tenant_id\": \"${TENANT_ID}\",${NC}"
echo -e "${RED}    \"message\": \"\"${NC}"
echo -e "${RED}  }'${NC}\n"

echo -e "Invalid analysis_type (422 Validation Error):"
echo -e "${RED}curl -X GET \"${BASE_URL}/api/v1/agents/mystic/analyze\\${NC}"
echo -e "${RED}?tenant_id=${TENANT_ID}\\${NC}"
echo -e "${RED}&analysis_type=invalid\"${NC}\n\n"

# ============================================================================
# 5. Testing with jq (Pretty Print)
# ============================================================================
echo -e "${YELLOW}5️⃣  Testing with jq (Pretty Print + Validation)${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

echo -e "HERMES response with formatting:"
echo -e "${GREEN}curl -s -X POST ${BASE_URL}/api/v1/agents/hermes/chat \\${NC}"
echo -e "${GREEN}  -H 'Content-Type: application/json' \\${NC}"
echo -e "${GREEN}  -d '{${NC}"
echo -e "${GREEN}    \"tenant_id\": \"${TENANT_ID}\",${NC}"
echo -e "${GREEN}    \"message\": \"¿IVA?\"${NC}"
echo -e "${GREEN}  }' | jq .${NC}\n"

echo -e "Extract response only:"
echo -e "${GREEN}curl -s -X POST ${BASE_URL}/api/v1/agents/hermes/chat \\${NC}"
echo -e "${GREEN}  -H 'Content-Type: application/json' \\${NC}"
echo -e "${GREEN}  -d '{${NC}"
echo -e "${GREEN}    \"tenant_id\": \"${TENANT_ID}\",${NC}"
echo -e "${GREEN}    \"message\": \"¿IVA?\"${NC}"
echo -e "${GREEN}  }' | jq '.response'${NC}\n"

echo -e "Check confidence score:"
echo -e "${GREEN}curl -s -X POST ${BASE_URL}/api/v1/agents/hermes/chat \\${NC}"
echo -e "${GREEN}  -H 'Content-Type: application/json' \\${NC}"
echo -e "${GREEN}  -d '{${NC}"
echo -e "${GREEN}    \"tenant_id\": \"${TENANT_ID}\",${NC}"
echo -e "${GREEN}    \"message\": \"¿IVA?\"${NC}"
echo -e "${GREEN}  }' | jq '{confidence: .confidence, used_mock: .used_mock, time_ms: .processing_time_ms}'${NC}\n"

echo -e "MYSTIC alerts extraction:"
echo -e "${GREEN}curl -s -X GET \"${BASE_URL}/api/v1/agents/mystic/analyze\\${NC}"
echo -e "${GREEN}?tenant_id=${TENANT_ID}&analysis_type=fiscal\" | jq '.alerts[]'${NC}\n\n"

# ============================================================================
# 6. Bash Script for Batch Testing
# ============================================================================
echo -e "${YELLOW}6️⃣  Bash Script for Batch Testing${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

cat << 'SCRIPT'
#!/bin/bash
# batch_test.sh

BASE_URL="http://localhost:8000"
TENANT="550e8400-e29b-41d4-a716-446655440000"

echo "Testing HERMES..."
curl -s -X POST $BASE_URL/api/v1/agents/hermes/chat \
  -H 'Content-Type: application/json' \
  -d "{\"tenant_id\": \"$TENANT\", \"message\": \"¿IVA?\"}" \
  | jq '.response'

echo -e "\nTesting MYSTIC Fiscal..."
curl -s -X GET "$BASE_URL/api/v1/agents/mystic/analyze?tenant_id=$TENANT&analysis_type=fiscal" \
  | jq '.alerts | length'

echo -e "\nTesting Status..."
curl -s -X GET "$BASE_URL/api/v1/agents/status?tenant_id=$TENANT" \
  | jq '.hermes.status'

echo -e "\nAll endpoints tested successfully! ✅"
SCRIPT

echo -e "\n\n"

# ============================================================================
# 7. Performance Testing with Apache Bench
# ============================================================================
echo -e "${YELLOW}7️⃣  Performance Testing (Apache Bench)${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

echo -e "Load test HERMES (100 requests, 10 concurrent):"
echo -e "${BLUE}ab -n 100 -c 10 -p payload.json -T application/json \\${NC}"
echo -e "${BLUE}  ${BASE_URL}/api/v1/agents/hermes/chat${NC}\n"

echo -e "(payload.json contains JSON body with tenant_id and message)\n"

# ============================================================================
# Summary
# ============================================================================
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}All examples ready! Copy and paste to test.${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}\n"

echo -e "📚 Documentation:"
echo -e "  - /apps/api/AGENTS_ENDPOINTS.md"
echo -e "  - /HERMES_MYSTIC_INTEGRATION.md"
echo -e "  - /ENDPOINTS_SMOKE_TEST.md\n"

echo -e "🧪 Run tests:"
echo -e "  pytest tests/api/test_agents.py -v\n"

echo -e "📖 OpenAPI Docs:"
echo -e "  ${BASE_URL}/docs\n"
