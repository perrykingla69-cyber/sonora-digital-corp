#!/usr/bin/env bash
# setup_rag.sh — Inicializa Qdrant + descarga nomic-embed-text en Ollama
set -euo pipefail

echo "=== Setup RAG: Qdrant + Embeddings ==="

# 1. Verificar que Qdrant esté corriendo
echo "[1/3] Verificando Qdrant..."
until curl -sf http://localhost:6333/healthz > /dev/null 2>&1; do
  echo "  Esperando Qdrant..."
  sleep 3
done
echo "  Qdrant OK"

# 2. Descargar modelo de embeddings en Ollama
echo "[2/3] Descargando nomic-embed-text (274MB)..."
docker exec mystic_ollama ollama pull nomic-embed-text
echo "  Modelo OK"

# 3. Crear colecciones iniciales vía API de Qdrant
echo "[3/3] Creando colecciones base..."

create_collection() {
  local name=$1
  curl -sf -X PUT "http://localhost:6333/collections/${name}" \
    -H "Content-Type: application/json" \
    -d '{"vectors": {"size": 768, "distance": "Cosine"}}' > /dev/null
  echo "  Colección creada: ${name}"
}

create_collection "fiscal_mx"    # Leyes SAT, LIVA, ISR, CFDI
create_collection "fourgea_docs" # Documentos específicos de Fourgea
create_collection "tripler_docs" # Documentos de Triple R Oil

echo ""
echo "=== RAG listo ==="
echo "  Qdrant UI: http://localhost:6333/dashboard"
echo "  Colecciones: fiscal_mx, fourgea_docs, tripler_docs"
