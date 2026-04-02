#!/bin/bash
# MYSTIC - Optimización de RAM para Backend y VPS
# Ejecutar en ambos entornos (local + VPS)

set -e

echo "🔧 MYSTIC - Optimizando uso de RAM..."

# ── 1. Limitar memoria de procesos Python ─────────────────────────────────────
export PYTHONMALLOC=malloc
export MALLOC_ARENA_MAX=2

# ── 2. Configurar límites para Ollama (si está corriendo local) ───────────────
if command -v ollama &> /dev/null; then
    echo "⚙️  Configurando Ollama para bajo consumo..."
    # Limitar a 2GB max para modelos pequeños
    export OLLAMA_NUM_PARALLEL=1
    export OLLAMA_MAX_LOADED_MODELS=1
    export OLLAMA_CONTEXT_LENGTH=2048
fi

# ── 3. Redis - limitar memoria ────────────────────────────────────────────────
if command -v redis-cli &> /dev/null; then
    redis-cli CONFIG SET maxmemory 256mb 2>/dev/null || true
    redis-cli CONFIG SET maxmemory-policy allkeys-lru 2>/dev/null || true
    echo "✅ Redis limitado a 256MB"
fi

# ── 4. Qdrant - optimizar ─────────────────────────────────────────────────────
# Qdrant ya es eficiente, pero podemos limpiar puntos antiguos
echo "🧹 Limpiando puntos duplicados en Qdrant..."
python3 << 'EOF'
try:
    from qdrant_client import QdrantClient
    client = QdrantClient(host="localhost", port=6333, timeout=10)
    
    collections = client.get_collections().collections
    for col in collections:
        count = client.count(col.name).count
        print(f"  📊 {col.name}: {count} puntos")
        
        # Si hay más de 10000 puntos, sugerir limpieza
        if count > 10000:
            print(f"     ⚠️  Considera archivar puntos antiguos (>10k)")
except Exception as e:
    print(f"  ⚠️  Qdrant no disponible: {e}")
EOF

# ── 5. PostgreSQL - vacuum y optimización ─────────────────────────────────────
echo "🗄️  Optimizando PostgreSQL..."
psql -h localhost -U mystic -d mystic_db -c "VACUUM ANALYZE;" 2>/dev/null || \
  echo "  ⚠️  No se pudo conectar a PostgreSQL (ejecutar manualmente)"

# ── 6. N8N - limitar memoria ──────────────────────────────────────────────────
if docker ps | grep -q n8n; then
    echo "⚙️  Limitando memoria de N8N..."
    docker update --memory=512m $(docker ps -q -f name=n8n) 2>/dev/null || true
fi

# ── 7. Limpieza de caché ──────────────────────────────────────────────────────
echo "🧹 Limpiando cachés..."
rm -rf ~/.cache/pip/* 2>/dev/null || true
rm -rf __pycache__ **/__pycache__ 2>/dev/null || true
find /tmp -name "*.pyc" -delete 2>/dev/null || true

# ── 8. Verificar procesos pesados ─────────────────────────────────────────────
echo ""
echo "📊 Procesos más pesados:"
ps aux --sort=-%mem | head -10

# ── 9. Sugerencias finales ────────────────────────────────────────────────────
echo ""
echo "✅ Optimización completada!"
echo ""
echo "📋 Recomendaciones adicionales:"
echo "   1. Usar modelos pequeños de Ollama: nomic-embed-text, deepseek-coder:1.3b"
echo "   2. Configurar swap de 4GB mínimo: sudo fallocate -l 4G /swapfile"
echo "   3. Monitorear con: watch -n 5 'free -h && echo --- && docker stats --no-stream'"
echo "   4. Para producción: considerar separar servicios en múltiples servidores"
