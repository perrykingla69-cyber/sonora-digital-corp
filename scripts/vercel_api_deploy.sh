#!/bin/bash
# Deploy directo a Vercel usando API
# Requiere: VERCEL_TOKEN y jq

set -e

VERCEL_TOKEN="${VERCEL_TOKEN:-}"
if [ -z "$VERCEL_TOKEN" ]; then
  echo "❌ Error: VERCEL_TOKEN no definido"
  exit 1
fi

FRONTEND_DIR="/home/mystic/hermes-os/frontend"
PROJECT_NAME="hermes-landing"
TEAM_ID=""  # Déjalo vacío para personal account

echo "🚀 Deployando a Vercel usando API..."
echo "Token: ${VERCEL_TOKEN:0:10}..."
echo "Proyecto: $PROJECT_NAME"
echo ""

# Verificar que tenemos jq
if ! command -v jq &> /dev/null; then
  echo "📦 Instalando jq..."
  sudo apt-get update && sudo apt-get install -y jq > /dev/null 2>&1
fi

# Paso 1: Crear o actualizar proyecto en Vercel
echo "1️⃣ Verificando/creando proyecto en Vercel..."

PROJECT_CHECK=$(curl -s -X GET \
  "https://api.vercel.com/v9/projects?slug=$PROJECT_NAME" \
  -H "Authorization: Bearer $VERCEL_TOKEN" \
  -H "Content-Type: application/json")

if echo "$PROJECT_CHECK" | jq -e '.projects[0]' > /dev/null 2>&1; then
  PROJECT_ID=$(echo "$PROJECT_CHECK" | jq -r '.projects[0].id')
  echo "✅ Proyecto existente encontrado: $PROJECT_ID"
else
  echo "📝 Creando nuevo proyecto..."
  CREATE_RESPONSE=$(curl -s -X POST \
    "https://api.vercel.com/v9/projects" \
    -H "Authorization: Bearer $VERCEL_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
      "name": "'$PROJECT_NAME'",
      "framework": "nextjs",
      "buildCommand": "npm run build",
      "outputDirectory": ".next"
    }')

  PROJECT_ID=$(echo "$CREATE_RESPONSE" | jq -r '.id // empty')
  if [ -z "$PROJECT_ID" ]; then
    echo "❌ Error al crear proyecto:"
    echo "$CREATE_RESPONSE" | jq '.'
    exit 1
  fi
  echo "✅ Proyecto creado: $PROJECT_ID"
fi

echo ""

# Paso 2: Crear un deployment
echo "2️⃣ Iniciando deployment..."

cd "$FRONTEND_DIR"

# Crear tarball del proyecto
TARBALL=$(mktemp)
tar czf "$TARBALL" \
  .next/ \
  package.json \
  package-lock.json \
  public/ \
  2>/dev/null || true

FILE_SIZE=$(du -h "$TARBALL" | cut -f1)
echo "📦 Tamaño de deployment: $FILE_SIZE"

# Subir files (opcional - Vercel puede hacerlo por git)
echo "⏳ Deployment en progreso... (esto puede tomar 2-5 minutos)"

DEPLOY_RESPONSE=$(curl -s -X POST \
  "https://api.vercel.com/v13/deployments" \
  -H "Authorization: Bearer $VERCEL_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "'$PROJECT_NAME'",
    "files": [],
    "projectSettings": {
      "buildCommand": "npm run build",
      "outputDirectory": ".next",
      "framework": "nextjs"
    },
    "env": {
      "NEXT_PUBLIC_API_URL": "https://api.hermes.app",
      "NEXT_PUBLIC_LOGIN_URL": "/login",
      "NEXT_PUBLIC_DEMO_URL": "/demo"
    },
    "production": true
  }')

DEPLOYMENT_ID=$(echo "$DEPLOY_RESPONSE" | jq -r '.id // empty')
if [ -z "$DEPLOYMENT_ID" ]; then
  echo "⚠️ Nota: Para deployments reales, usa:"
  echo "   vercel --prod --name $PROJECT_NAME"
  echo ""
  echo "Deploy response:"
  echo "$DEPLOY_RESPONSE" | jq '.'

  # Cleanup
  rm -f "$TARBALL"

  echo ""
  echo "💡 Alternativa: GitHub integration"
  echo "   1. Push código a GitHub"
  echo "   2. Conecta repo en: https://vercel.com/new"
  echo "   3. Vercel deploya automáticamente"
  exit 0
fi

echo "✅ Deployment iniciado: $DEPLOYMENT_ID"
echo ""

# Paso 3: Esperar a que se complete
echo "3️⃣ Esperando a que se complete el deployment..."

READY=false
ATTEMPTS=0
MAX_ATTEMPTS=60  # 5 minutos máx

while [ "$READY" = false ] && [ $ATTEMPTS -lt $MAX_ATTEMPTS ]; do
  sleep 5
  ATTEMPTS=$((ATTEMPTS + 1))

  STATUS=$(curl -s -X GET \
    "https://api.vercel.com/v13/deployments/$DEPLOYMENT_ID" \
    -H "Authorization: Bearer $VERCEL_TOKEN" \
    -H "Content-Type: application/json" | jq -r '.state')

  echo "  Estado: $STATUS (intento $ATTEMPTS/$MAX_ATTEMPTS)"

  if [ "$STATUS" = "READY" ] || [ "$STATUS" = "READY_FOR_VERIFICATION" ]; then
    READY=true
  elif [ "$STATUS" = "ERROR" ] || [ "$STATUS" = "FAILED" ]; then
    echo "❌ Deployment falló"
    exit 1
  fi
done

if [ "$READY" = false ]; then
  echo "⏱️ Timeout esperando deployment (5+ minutos). Checkea en:"
  echo "   https://vercel.com/dashboard"
  exit 1
fi

echo "✅ Deployment completado!"
echo ""

# Paso 4: Obtener URL
DEPLOYMENT_URL=$(curl -s -X GET \
  "https://api.vercel.com/v13/deployments/$DEPLOYMENT_ID" \
  -H "Authorization: Bearer $VERCEL_TOKEN" | jq -r '.url')

echo "🎉 URL en vivo:"
echo "   https://$DEPLOYMENT_URL"
echo ""

# Cleanup
rm -f "$TARBALL"

echo "📋 URLs de landings:"
NICHOS=("restaurante" "contador" "pastelero" "abogado" "fontanero" "consultor")
for niche in "${NICHOS[@]}"; do
  echo "   https://$DEPLOYMENT_URL/$niche"
done

echo ""
echo "⏳ Próximos pasos:"
echo "   1. Configura dominios en: https://vercel.com/dashboard"
echo "   2. Para cada niche, agrega CNAME:"
echo "      restaurante.sonoradigitalcorp.com → cname.vercel-dns.com"
echo "      etc."
echo "   3. Espera 10-30 min para DNS propagación"
echo "   4. Verifica: curl -I https://restaurante.sonoradigitalcorp.com"
