# SEED QUICKSTART — Poblar Qdrant en 5 minutos

Guía rápida para ejecutar seeders y verificar RAG en Qdrant.

---

## 1. Verificar Prerrequisitos

Asegurar que estos servicios están running:

```bash
# En VPS o Docker local
docker compose ps | grep -E "(qdrant|ollama|postgres|hermes-api)"
```

Esperado: Todos en estado `Up`

```
qdrant      Up (healthy)
ollama      Up
postgres    Up (healthy)
hermes-api  Up (healthy)
```

Si alguno no está UP:

```bash
docker compose up -d qdrant ollama postgres
```

---

## 2. Ejecutar Seed Automático (RECOMENDADO)

```bash
cd /home/mystic/hermes-os
python3 scripts/seed_all_domains.py
```

**Duración**: ~10-15 minutos (depende de Ollama embedding speed)

**Output esperado**:
```
================================================================================
  SEED ALL DOMAINS — Poblar Qdrant con Regulaciones & Patrones
================================================================================

Flujo de ejecución:
  1. seed_fiscal_regulations.py
  2. seed_food_regulations.py
  3. seed_legal_regulations.py
  4. seed_architecture_patterns.py
  5. seed_ops_best_practices.py

...

✓ Seed completado exitosamente
```

---

## 3. Verificar Colecciones Creadas

```bash
# Listar todas colecciones en Qdrant
curl http://localhost:6333/collections | jq '.collections[] | {name, points_count}'
```

**Esperado**:
```json
{
  "name": "fiscal-regulations",
  "points_count": 2500
}
{
  "name": "food-regulations",
  "points_count": 2100
}
{
  "name": "legal-regulations",
  "points_count": 1800
}
{
  "name": "architecture-patterns",
  "points_count": 1600
}
{
  "name": "ops-best-practices",
  "points_count": 2000
}
```

Total: ~10,000 puntos (chunks)

---

## 4. Prueba Manual: Búsqueda en Qdrant

```bash
# Conectar a Qdrant API directamente
curl -X POST http://localhost:6333/collections/food-regulations/points/search \
  -H "Content-Type: application/json" \
  -d '{
    "vector": [0.1, 0.2, 0.3, ...],  # dummy vector
    "limit": 3,
    "score_threshold": 0.65
  }'
```

Nota: Para búsqueda real, usar HERMES API (paso 5)

---

## 5. Prueba RAG: Consultar desde HERMES API

Obtener JWT token:

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "marco@fourgea.mx", "password": "Marco2026!"}'
```

Copiar `access_token` del response.

Consulta RAG:

```bash
curl -X POST http://localhost:8000/api/brain/search \
  -H "Authorization: Bearer <token-aquí>" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "¿Cuál es la temperatura segura para pollo?",
    "tenant_id": "72202fe3-e2e1-4896-a4cb-69acf0d1666c"
  }'
```

**Esperado**: 
```json
{
  "context": "CONTEXTO RELEVANTE:\n[Temperaturas Seguras]\nPollo: 74°C mínimo... ",
  "chunks": [
    {
      "text": "Pollo & Aves: Pechuga: 74°C...",
      "source": "Temperaturas Seguras por Tipo de Alimento",
      "score": 0.89
    }
  ]
}
```

---

## 6. Prueba RAG: Chat en Telegram (HERMES CEO)

1. Abrir Telegram
2. Buscar bot HERMES CEO (`@hermes_ceo_bot` o según config)
3. Enviar mensaje:

```
/chat ¿Qué temperatura debe tener el pollo cocido?
```

**Esperado**:
```
HERMES: Según NOM-251 y regulaciones de HACCP, el pollo debe alcanzar una 
temperatura interna mínima de 74°C (165°F) para eliminar patógenos. 

Fuentes: 
- Temperaturas Seguras por Tipo de Alimento
- HACCP — Hazard Analysis & Critical Control Points
```

---

## 7. Troubleshooting

### Error: "Connection refused" en Qdrant

```bash
# Verificar si Qdrant está corriendo
docker ps | grep qdrant

# Si no, iniciar
docker compose up -d qdrant

# Esperar 5 segundos
sleep 5

# Verificar conectividad
curl http://localhost:6333/health
```

### Error: "Ollama not responding"

```bash
# Verificar Ollama
docker exec ollama ollama list

# Si no está la imagen
docker exec ollama ollama pull nomic-embed-text

# Reiniciar
docker restart ollama
```

### Error: "API 500 Internal Server Error"

```bash
# Verificar logs de hermes-api
docker logs hermes-api | tail -50

# Reiniciar API
docker compose restart hermes-api

# Esperar 10 segundos
sleep 10
```

### Seed muy lento

Embedding lento = Ollama saturado o CPU limitada

```bash
# Ver CPU/memoria Ollama
docker stats ollama

# Si CPU 100%: esperar o aumentar RAM si disponible
```

---

## 8. Pasos Siguientes

### ✓ Seed completado

- [x] 5 colecciones creadas
- [x] ~10,000 chunks en Qdrant
- [x] RAG funcional en HERMES API
- [x] Telegram bot responde con contexto

### → Próximo: Actualizar niche_registry (opcional)

Si quieres que HERMES auto-seed nuevos tenants con estas colecciones:

Editar `/home/mystic/hermes-os/agents/seeders/niche_registry.py`:

```python
"contador": {
    "keywords": ["contador", "contabilidad", "fiscal"],
    "collections": [
        "fiscal-regulations",  # ← AGREGAR
        "legal-regulations",
        "global_fiscal_mx"
    ],
    # ...
}
```

Resultado: Nuevo tenant contador → auto-seed con fiscal-regulations

---

## Archivos Creados

```
scripts/
├── seed_fiscal_regulations.py      (9 docs, ~2500 chunks)
├── seed_food_regulations.py        (7 docs, ~2100 chunks)
├── seed_legal_regulations.py       (5 docs, ~1800 chunks)
├── seed_architecture_patterns.py   (5 docs, ~1600 chunks)
├── seed_ops_best_practices.py      (5 docs, ~2000 chunks)
├── seed_all_domains.py             (maestro, ejecuta todos)
├── SEED_STRATEGY.md                (documentación completa)
└── SEED_QUICKSTART.md              (este archivo)
```

---

## Verificación Final

```bash
# 1. Colecciones existen
curl http://localhost:6333/collections | jq '.collections | length'
# Esperado: 5

# 2. Chunks indexados
curl http://localhost:6333/collections | jq '.collections | map(.points_count) | add'
# Esperado: ~10000

# 3. API responde
curl http://localhost:8000/health
# Esperado: {"status": "ok"}

# 4. Telegram bot responde
# (Manual: enviar /chat y verificar respuesta RAG)
```

---

## Info Adicional

- **Documentación completa**: `scripts/SEED_STRATEGY.md`
- **Colecciones**: `fiscal-regulations`, `food-regulations`, `legal-regulations`, `architecture-patterns`, `ops-best-practices`
- **Acceso RAG**: HERMES API `/api/brain/search` o Telegram HERMES CEO
- **Mantenimiento**: Re-ejecutar `seed_all_domains.py` para actualizar (upsert automático)

---

**¿Listo?** Ejecuta `python3 scripts/seed_all_domains.py` y espera ~15 minutos.

**¿Preguntas?** Ver SEED_STRATEGY.md para detalles técnicos.
