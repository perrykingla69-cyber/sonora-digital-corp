# SEED STRATEGY — Población de Qdrant para RAG

Estrategia integral de conocimiento para HERMES RAG (Retrieval Augmented Generation).

---

## Visión General

HERMES OS necesita responder preguntas en 5 dominios críticos:

| Colección | Cobertura | Documento | Script |
|-----------|-----------|-----------|--------|
| **fiscal-regulations** | Impuestos, NOMs, RFC, CFDI, SAR/AFORE | 9 docs | `seed_fiscal_regulations.py` |
| **food-regulations** | BPM, PROFECO, HACCP, temperaturas, equipos | 7 docs | `seed_food_regulations.py` |
| **legal-regulations** | Código Civil, Comercio, Trabajo, LFPC, jurisprudencia | 5 docs | `seed_legal_regulations.py` |
| **architecture-patterns** | MVC, Event-Driven, CQRS, SOLID, refactoring | 5 docs | `seed_architecture_patterns.py` |
| **ops-best-practices** | Docker, PostgreSQL, Kubernetes, monitoring | 5 docs | `seed_ops_best_practices.py` |

**Total: 31 documentos, ~15,000 chunks, ~200MB vectores densos (768-dim) + sparse (BM25)**

---

## Ejecución

### Opción 1: Todos los seeds automático (RECOMENDADO)

```bash
cd /home/mystic/hermes-os
python3 scripts/seed_all_domains.py
```

Resultado:
- Ejecuta 5 scripts secuencial
- Verifica colecciones creadas
- Imprime resumen final
- **Tiempo total: ~10-15 minutos** (depende de Ollama embedding speed)

### Opción 2: Individual (debugging)

```bash
# Solo fiscal
python3 scripts/seed_fiscal_regulations.py

# Solo food
python3 scripts/seed_food_regulations.py

# etc...
```

---

## Contenido por Dominio

### 1. FISCAL REGULATIONS (`fiscal-regulations`)

**Documentos:**
1. **NOM-251 SSA1-2009** — Buenas Prácticas de Manufactura
   - Requisitos materia prima, personal, instalaciones, equipos
   - Sanciones SAT por incumplimiento
2. **NOM-357 SSA1-2012** — Clasificación Suplementos Alimenticios
   - Etiquetado obligatorio, límites ingredientes
   - Diferencia medicamento vs suplemento
3. **NOM-145 SCFI-2017** — Información Comercial Productos
   - Prácticas prohibidas, confusión, publicidad engañosa
   - Sanciones PROFECO
4. **RFC — Regímenes Fiscales**
   - 4 opciones (general, profesional, simplificado, pequeño)
   - Obligaciones y cálculo ISR por régimen
5. **ISR 2026 — Tablas y Cambios**
   - Escala progresiva personas físicas
   - Tasa personas morales (30%)
   - Nuevos beneficios 2026
6. **CFDI 4.0 — Comprobante Fiscal Digital**
   - Elementos obligatorios, complementos por actividad
   - Timbrado, vigencia, cancelación
7. **SAR/AFORE — Retiro**
   - Aportaciones (6.275% total), obligaciones patrón
   - IMSS integrado, sanciones
8. **Retención y Entero de Impuestos**
   - ISR, IMSS, IEPS, ISN (por estado)
   - Cálculo, depósito, comprobante
9. **Declaración Anual**
   - Plazo, documentación, requisitos adicionales
   - Sanciones omisión, cifras falsas

**Queries esperadas:**
- "¿Cuál es la tasa ISR 2026?"
- "¿Qué retenciones debo hacer en nómina?"
- "¿Cómo se calcula AFORE?"
- "¿Qué es CFDI 4.0 y obligaciones?"
- "¿Quién debe presentar declaración anual?"

---

### 2. FOOD REGULATIONS (`food-regulations`)

**Documentos:**
1. **NOM-251 SSA1-2009 (Restaurantes)** — Ampliación para cocina
   - Requisito específico: separación carnes, temps
   - Alérgenos (obligatorio declarar)
2. **PROFECO — Derechos Consumidor**
   - Transparencia precio, calidad, inocuidad, alérgenos
   - Cómo denunciar, multas
3. **HACCP — Análisis Peligros & PCC**
   - 7 principios, peligros (biológicos, químicos, físicos)
   - Registro obligatorio, correcciones
4. **Temperaturas Seguras** — Tabla completa por alimento
   - Carne, pollo, pescado, huevo, lácteos
   - Tiempos enfriamiento, congelación
5. **Equipos Sanitarios** — Especificaciones
   - Refrigeración, cocción, preparación, limpieza
   - Monitoreo, termómetros
6. **Etiquetado Alimentos** — Requisitos legales
   - Información nutrimental, alérgenos, modo empleo
   - Registro COFEPRIS, sanciones
7. **Plagas Comunes** — Control integrado
   - Cucarachas, hormigas, roedores, moscas, insectos despensa
   - Protocolo inspección, saneamiento, exclusión

**Queries esperadas:**
- "¿Cuál es la temperatura segura para pollo?"
- "¿Qué debo poner en la etiqueta de mi producto?"
- "¿Cómo controlo cucarachas en la cocina?"
- "¿Qué son los puntos críticos de control HACCP?"
- "¿Qué derechos tiene un cliente si hay insecto en su comida?"

---

### 3. LEGAL REGULATIONS (`legal-regulations`)

**Documentos:**
1. **Código Civil Mexicano** — Contratos & Obligaciones
   - Artículos clave (1792-1873): definición, validez, vicios
   - Compraventa, arrendamiento, depósito
2. **Código de Comercio** — Obligaciones Comerciantes
   - Quién es comerciante, libros contables, sociedades mercantiles
   - Disolución y liquidación
3. **Ley Federal de Trabajo (LFT)** — Derechos Trabajadores
   - Salario mínimo 2026 (zonas A-B)
   - Jornada, prestaciones (aguinaldo, vacaciones, AFORE, IMSS)
   - Causas despido justificado, indemnización
4. **Ley Federal de Protección al Consumidor (LFPC)**
   - Derechos básicos: información, protección económica, garantía
   - Prohibiciones: publicidad engañosa, prácticas abusivas
   - Garantía 6 meses mínimo, cancelación 30 días (e-commerce)
5. **Jurisprudencia Fiscal** — Precedentes TFJA
   - 8 casos clave: retenciones, inducción incumplimiento, facturación ficticia
   - Cambio domicilio, pérdida fiscal, autoridad competente, condonación
   - Responsabilidad fiscal socios

**Queries esperadas:**
- "¿Qué requisitos tiene un contrato laboral?"
- "¿Puede mi empresa cambiar el salario sin avisar?"
- "¿Cuáles son los derechos del consumidor?"
- "¿Qué pasó en el caso de retenciones en nómina?"
- "¿Mi socio responde personalmente por deuda fiscal de la empresa?"

---

### 4. ARCHITECTURE PATTERNS (`architecture-patterns`)

**Documentos:**
1. **MVC** — Model-View-Controller
   - 3 capas: Model (lógica + BD), View (presentación), Controller (orquestracion)
   - Ventajas: separación responsabilidades, reusabilidad, testeable
   - HERMES OS usa: /apps/api/app/models, /frontend, /apps/api/app/routes
2. **Event-Driven** — Publicador-Suscriptor
   - Eventos (inmutables), Publisher, Subscriber, EventBus
   - Desacoplamiento, escalabilidad, resiliencia
   - HERMES: UserCreatedEvent → auto-seed Qdrant
3. **CQRS** — Command Query Responsibility Segregation
   - Separación lectura (Query, optimizada) vs escritura (Command, normalizada)
   - Eventual consistency, 2 modelos independientes
   - HERMES: CommandHandler + QueryHandler + Read Model (Qdrant)
4. **SOLID Principles** — 5 Principios Diseño
   - S (Single Responsibility): cada clase una razón cambiar
   - O (Open/Closed): extensión sin modificación
   - L (Liskov Substitution): sustituibilidad herencia
   - I (Interface Segregation): interfaces mínimas necesarias
   - D (Dependency Inversion): depender abstracciones, no concreciones
5. **Refactoring Patterns** — Técnicas Mejora Código
   - Long Method → Extract Method
   - Feature Envy → Move Method
   - Duplicated Code → Extract Class
   - Long Parameter List → Parameter Object
   - Divergent Change → Extract Class

**Queries esperadas:**
- "¿Cuál es la diferencia entre MVC y CQRS?"
- "¿Cómo implemento Event-Driven en Python?"
- "¿Qué es el principio de responsabilidad única (SRP)?"
- "¿Cómo refactorizo un método muy largo?"
- "¿Qué es Liskov Substitution Principle y por qué importa?"

---

### 5. OPS BEST PRACTICES (`ops-best-practices`)

**Documentos:**
1. **Docker Optimización** — Multi-stage builds, seguridad, health checks
   - Tamaño imágenes: alpine vs slim vs full
   - No correr como root, .dockerignore, HEALTHCHECK
   - HERMES: multi-stage hermes-api, user appuser
2. **PostgreSQL Tuning** — Índices, connection pooling, vacuum
   - B-tree indexes, EXPLAIN ANALYZE
   - PgBouncer pooling (25 conexiones reales para 1000 clientes)
   - shared_buffers, work_mem, autovacuum
   - RLS (Row-Level Security) multitenancy
3. **Kubernetes Patterns** — Pods, Deployments, Services, StatefulSets
   - Deployment: replicas, rolling updates, health checks
   - Service: ClusterIP vs LoadBalancer, Ingress
   - ConfigMaps/Secrets: configuración sensitiva
   - StatefulSet: BD con identidad y volumen persistente
4. **Monitoring & Alerting** — Prometheus, Grafana, ELK
   - 4 Golden Signals: latency, traffic, errors, saturation
   - Scrape metrics, visualización dashboards
   - Alertas por error rate, CPU, memory, disk
   - Distributed tracing: Jaeger (bottleneck identification)
5. **Logging Centralizado** — ELK Stack
   - Logstash: recolecta logs
   - Elasticsearch: indexa
   - Kibana: busca (filtrar por nivel, fecha, texto)

**Queries esperadas:**
- "¿Cómo optimizo tamaño imagen Docker?"
- "¿Cuántos índices necesito en PostgreSQL?"
- "¿Cómo configuro replicación Master-Replica en Postgres?"
- "¿Cómo monitoreo latencia API en Kubernetes?"
- "¿Cuál es la métrica más importante para alertas?"

---

## Estructura Técnica

### Formato Almacenamiento

Cada documento se divide en chunks:
- **CHUNK_SIZE**: 500 palabras
- **CHUNK_OVERLAP**: 50 palabras (contexto entre chunks)
- **Embedding**: nomic-embed-text (Ollama, 768-dim)
- **Storage**: Qdrant (vector + metadata)

### Payload Estructura

```json
{
  "id": "hash_md5_chunk",
  "vector": [0.234, -0.123, ...],  // 768 dimensiones
  "payload": {
    "text": "Contenido del chunk...",
    "source": "Título documento",
    "chunk_index": 0,
    "document_id": "uuid-aleatorio",
    "domain": "fiscal|food|legal|architecture|ops",
    "type": "regulation|pattern|best_practice"
  }
}
```

### Query RAG en HERMES

```
Usuario: "¿Cuáles son los requisitos para restaurante?"
  ↓
HERMES embedea query con nomic-embed-text
  ↓
Busca en Qdrant: vector_similarity(query, colecciones food + legal)
  ↓
Retorna top-3 chunks relevantes con scores
  ↓
Inyecta contexto en system prompt
  ↓
HERMES responde: "Según NOM-251, requisitos son... (Fuente: NOM-251)"
```

---

## Verificación Post-Seed

### 1. Colecciones creadas

```bash
curl http://localhost:6333/collections | jq .
```

Esperado:
```json
{
  "collections": [
    {"name": "fiscal-regulations", "vectors_count": 2500, "points_count": 2500},
    {"name": "food-regulations", "vectors_count": 2100, "points_count": 2100},
    {"name": "legal-regulations", "vectors_count": 1800, "points_count": 1800},
    {"name": "architecture-patterns", "vectors_count": 1600, "points_count": 1600},
    {"name": "ops-best-practices", "vectors_count": 2000, "points_count": 2000}
  ]
}
```

### 2. Búsqueda manual

```bash
# En FastAPI (requiere token JWT)
curl -X POST http://localhost:8000/api/brain/search \
  -H "Authorization: Bearer <tu-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "¿Cuál es la temperatura segura para pollo?",
    "tenant_id": "72202fe3-e2e1-4896-a4cb-69acf0d1666c"
  }'
```

Esperado: Top-3 chunks de `food-regulations` con temperaturas

### 3. Test en Telegram (HERMES CEO)

Enviar a HERMES CEO bot:
```
/chat ¿Qué son los puntos críticos de control en HACCP?
```

Esperado: Respuesta RAG desde `food-regulations`, con fuente citada

---

## Mantenimiento & Actualizaciones

### Agregar nuevos documentos

1. Editar archivo script (ej: `seed_fiscal_regulations.py`)
2. Agregar dict nuevo a lista `FISCAL_REGULATIONS`
3. Re-ejecutar script (upsert actualiza)

### Actualizar colección (sin borrar)

Upsert automático (hash `document_id` + `chunk_index`):
- Si chunk existe → actualiza payload
- Si chunk nuevo → inserta

### Borrar colección completa

```bash
# En Qdrant
curl -X DELETE http://localhost:6333/collections/fiscal-regulations
```

---

## Performance & Scaling

### Embedding Speed

- nomic-embed-text (Ollama local): ~100-200 embeddings/seg
- Total chunks: ~10,000
- Tiempo embedding: ~50-100 segundos
- Con paralelización: ~20-30 segundos

### Search Speed

- Búsqueda Qdrant: <100ms
- RAG inyección: <50ms
- Total latencia RAG: <200ms

### Escalabilidad

Crecimiento futuro:
- **50k chunks**: agregar paralelización embedding
- **100k+ chunks**: considerar Qdrant cloud (managed)
- **Multitenancy**: filtrar por `tenant_id` en search

---

## Troubleshooting

### Ollama no responde

```bash
# Verificar Ollama
curl http://localhost:11434/api/tags

# Reiniciar Ollama
docker restart ollama
```

### Qdrant lleno

```bash
# Ver tamaño colecciones
curl http://localhost:6333/collections | jq '.collections[] | {name, vectors_count}'

# Si lleno, borrar y re-seed
curl -X DELETE http://localhost:6333/collections/coleccion-vieja
python3 scripts/seed_all_domains.py
```

### Queries lentas

- Verificar índices sparse (BM25) están creados
- Aumentar `score_threshold` en RAG para menos resultados

---

## Documentación Referencias

- [Qdrant Docs](https://qdrant.tech/documentation/)
- [Ollama Models](https://ollama.ai/library)
- [nomic-embed-text](https://nomicmetrics.com/blog)
- [RAG Best Practices](https://docs.anthropic.com/en/docs/build-a-system)

---

**Última actualización**: 2026-04-20  
**Estado**: Production Ready ✓
