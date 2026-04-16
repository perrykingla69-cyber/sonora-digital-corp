# HERMES & MYSTIC Endpoints

## Overview
Dos endpoints completamente funcionales para Mission Control y Dashboards:
- **HERMES** (Orquestador): responde preguntas contables/empresariales con RAG + OpenRouter
- **MYSTIC** (Estratega): analiza datos para detectar riesgos y oportunidades

## Endpoint 1: POST /api/v1/agents/hermes/chat

**Propósito**: Orquestador de luz — responde con contexto RAG e integración OpenRouter

### Request
```json
{
  "tenant_id": "uuid",
  "message": "¿Cuál es la tasa de IVA?",
  "context": "opcional",
  "use_rag": true
}
```

### Response (200 OK)
```json
{
  "response": "La tasa de IVA en México es del 16%...",
  "sources": ["qdrant_rag"],
  "confidence": 0.95,
  "processing_time_ms": 245,
  "used_mock": false
}
```

### Error Responses
- **400**: Request inválido (tenant_id o message faltante)
- **401**: No autorizado
- **500**: Error de servidor (usado mock como fallback)

### Features
- ✅ RLS: SET LOCAL app.current_tenant_id (transaction-scoped)
- ✅ RAG: búsqueda en Qdrant si use_rag=true
- ✅ OpenRouter: Gemini Flash (timeout 5s, fallback a mock)
- ✅ Cache: Redis TTL 1 hora
- ✅ Confidence score: 0.95 (OpenRouter) o 0.6 (mock)

### Implementation Details
**File**: `/apps/api/app/services/agents.py` → `HermesService.chat()`
- Timeout: 5 segundos a OpenRouter API
- Si timeout: retorna mock realista
- RAG context inyectado en system prompt
- Response cacheada en Redis con tenant_id + message hash

---

## Endpoint 2: GET /api/v1/agents/mystic/analyze

**Propósito**: Estratega de sombra — análisis fiscal/food/business con alertas clasificadas

### Query Parameters
```
GET /api/v1/agents/mystic/analyze?tenant_id=uuid&analysis_type=fiscal
```

### Response (200 OK)
```json
{
  "analysis": "Análisis profundo: detecté oportunidades en deducciones...",
  "alerts": [
    {
      "level": "info",
      "message": "Revisa deducciones de nómina",
      "code": "NOM-001"
    },
    {
      "level": "warning",
      "message": "Declaraciones próximas a vencer",
      "code": "DEC-001"
    }
  ],
  "recommendations": [
    "Revisar reporte mensual",
    "Coordinar con equipo de operaciones"
  ],
  "generated_at": "2026-04-16T16:20:00Z",
  "used_mock": false
}
```

### Query Parameters
- **tenant_id** (required): UUID del tenant
- **analysis_type** (required): `fiscal` | `food` | `business`

### Error Responses
- **400**: Parámetros inválidos
- **401**: No autorizado
- **404**: Tenant no encontrado
- **500**: Error de servidor

### Features
- ✅ RLS: SET LOCAL para tenant
- ✅ Alertas clasificadas: critical, warning, info
- ✅ Recomendaciones accionables
- ✅ Cache Redis (TTL 1 hora)
- ✅ Tipos especializados: fiscal MX, restaurante, business general

### Implementation Details
**File**: `/apps/api/app/services/agents.py` → `MysticService.analyze()`
- Contexto del tenant inyectado automáticamente
- Alertas predefinidas por tipo (extensibles)
- Mock listo en MVP (integración futura con GLM Z1 vía OpenRouter)
- Cache por tenant + analysis_type

---

## Endpoint 3: GET /api/v1/agents/status

**Propósito**: Health check — estado de HERMES, MYSTIC y RAG

### Query Parameters
```
GET /api/v1/agents/status?tenant_id=uuid
```

### Response (200 OK)
```json
{
  "hermes": {
    "status": "active",
    "model": "google/gemini-2.0-flash-001 (OpenRouter)",
    "role": "orchestrator",
    "description": "Orquestador de luz"
  },
  "mystic": {
    "status": "active",
    "model": "thudm/glm-z1-rumination (OpenRouter)",
    "role": "shadow_analyst",
    "description": "Estratega de sombra"
  },
  "rag": {
    "status": "active",
    "backend": "qdrant+ollama",
    "embeddings": "nomic-embed-text (768-dim)"
  },
  "tenant_id": "uuid"
}
```

---

## Testing

### Unit Tests
```bash
pytest tests/api/test_agents.py -v
```

### Test Coverage
- ✅ HERMES: validación request, RAG, mock fallback, cache
- ✅ MYSTIC: alertas, recomendaciones, tipos especializados
- ✅ Status: health check
- ✅ Error handling: 400, 401, 404, 422, 500

### Mock Data
Si OpenRouter no responde (timeout 5s), automáticamente usa respuestas mock realistas:
- HERMES: respuesta genérica inteligente
- MYSTIC: análisis especializado por tipo

---

## Architecture

### Request Flow
```
Request → RLS (SET LOCAL) → Service Layer → OpenRouter/RAG → Redis Cache → Response
                            ↓ (timeout)
                           Mock Fallback
```

### Files Modified/Created
- **schemas**: `/apps/api/app/schemas/agents.py` (nuevo)
- **services**: `/apps/api/app/services/agents.py` (nuevo)
- **endpoints**: `/apps/api/app/api/v1/agents.py` (actualizado)
- **tests**: `/tests/api/test_agents.py` (nuevo)
- **imports**: `/apps/api/app/schemas/__init__.py` (actualizado)

---

## Configuration

### Environment Variables Required
```bash
OPENROUTER_API_KEY=sk-xxx  # Para HERMES (Gemini Flash)
QDRANT_HOST=qdrant         # RAG backend
QDRANT_PORT=6333
OLLAMA_URL=http://ollama:11434  # Embeddings (nomic-embed-text)
REDIS_URL=redis://redis:6379    # Cache
```

### Performance
- HERMES timeout: 5 segundos (ajustable vía config)
- Cache TTL: 3600 segundos (1 hora, por type/tenant)
- RAG score_threshold: 0.65 (cosine similarity)
- Processing time típico: 200-400ms con OpenRouter

---

## Future Enhancements
- [ ] Integración GLM Z1 para MYSTIC (OpenRouter)
- [ ] RAG con BM25 híbrido (dense + sparse vectors)
- [ ] Métricas Prometheus (request latency, cache hit rate)
- [ ] Rate limiting por tenant
- [ ] Streaming responses (Server-Sent Events)
- [ ] Conversation history (per user + tenant)
