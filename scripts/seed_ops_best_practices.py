#!/usr/bin/env python3
"""
seed_ops_best_practices.py — Seed Qdrant colección 'ops-best-practices'

Cubre: Docker optimization, PostgreSQL tuning, Kubernetes patterns, monitoring setup.
Colección: ops-best-practices (Dense 768-dim + BM25 sparse híbrido)

Uso:
    cd /home/mystic/hermes-os
    python3 scripts/seed_ops_best_practices.py
"""

import asyncio
import hashlib
import httpx
import logging
import os
from uuid import uuid4

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, SparseVectorParams, SparseIndexParams

# ── Config ────────────────────────────────────────────────────────────────────
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_COLLECTION = "ops-best-practices"
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
EMBED_MODEL = "nomic-embed-text"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── Documentos de best practices operacionales ────────────────────────────────

OPS_BEST_PRACTICES = [
    {
        "title": "Docker Best Practices — Optimización Imágenes y Containers",
        "source": "Docker Official / Best Practices Guide",
        "content": """Docker = containerización de aplicaciones. Best practices para producción.

1. CONSTRUIR IMÁGENES EFICIENTES:

Multi-stage builds:
Problema: Dockerfile que compila + tests genera imagen gigante (500MB+)
Solución: usar múltiples FROM para separar compile vs runtime

❌ MAL:
FROM python:3.11
RUN apt-get install -y build-essential gcc
COPY . /app
RUN pip install -r requirements.txt
RUN pytest tests/  # Tests no necesarios en producción
CMD ["python", "main.py"]
# Imagen final: 800MB (incluye dev tools, tests, compilador)

✅ BIEN:
FROM python:3.11 AS builder
RUN apt-get install -y build-essential gcc
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
RUN pytest tests/

FROM python:3.11-slim  # Imagen más pequeña
COPY --from=builder /app /app
WORKDIR /app
CMD ["python", "main.py"]
# Imagen final: 200MB (solo runtime, sin build tools)

2. TAMAÑO IMÁGENES:

Usar image base apropiada:
- python:3.11 = 900MB (full Python environment)
- python:3.11-slim = 150MB (Python sin dev tools)
- python:3.11-alpine = 50MB (muy minimal, cuidado con compatibilidad)

Usar .dockerignore:
.dockerignore (excluye del COPY):
    .git
    .pytest_cache
    __pycache__
    *.log
    node_modules
    venv

Limpiar después instalar:
❌ MAL:
RUN apt-get install -y build-essential
RUN pip install -r requirements.txt
# Deja archivos temporales en imagen

✅ BIEN:
RUN apt-get install -y build-essential && \
    pip install -r requirements.txt && \
    apt-get purge -y build-essential && \
    rm -rf /var/lib/apt/lists/*
# Una capa, sin archivos temporales

3. SEGURIDAD IMÁGENES:

No ejecutar como root:
❌ MAL:
FROM python:3.11
COPY . /app
RUN pip install -r requirements.txt
CMD ["python", "main.py"]
# Corre como root → si app hackeada, acceso total

✅ BIEN:
FROM python:3.11
RUN useradd -m appuser
COPY . /app
RUN chown -R appuser:appuser /app
USER appuser
CMD ["python", "main.py"]
# Corre como appuser → acceso limitado

4. HEALTH CHECKS:

Monitorear si container está vivo:
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

Docker verifica cada 30 segundos:
- Si endpoint /health retorna 200 → healthy
- Si 3 intentos fallan → unhealthy
- Docker reinicia si unhealthy

5. VOLUMENES Y DATOS:

VOLUMES para persistencia:
docker run -v my_data:/data my_container
# /data en container → guarda en /var/lib/docker/volumes/my_data/_data en host

Nombrados vs anónimos:
✅ Nombrados (persistente): -v postgres_data:/var/lib/postgresql/data
❌ Anónimos (se elimina si rm container): -v /var/lib/postgresql/data

Backups:
docker run --rm -v postgres_data:/data -v /backups:/backup \
  postgres:15 pg_dump -U postgres > /backup/dump.sql

HERMES OS Docker optimizations:
- Multi-stage: hermes-api builder vs runtime
- Base: python:3.11-slim (150MB vs 900MB)
- Health checks: todos servicios (postgres, redis, qdrant)
- User: appuser en FastAPI container
- Volumes: postgres_data, redis_data, qdrant_data (persistentes)""",
    },
    {
        "title": "PostgreSQL Tuning — Optimización Queries y Configuración",
        "source": "PostgreSQL Documentation / Performance Tuning",
        "content": """PostgreSQL = BD relacional. Tuning para producción.

1. ÍNDICES ESTRATÉGICOS:

Problema: SELECT * FROM orders WHERE user_id = ? → full table scan (lento)
Solución: índice en user_id

CREATE INDEX idx_orders_user_id ON orders(user_id);
# Búsqueda: O(log n) vs O(n)

Tipos índices:
- B-tree (default): búsquedas exactas, rangos. Úsa 90% casos
- Hash: solo igualdad, muy rápido pero sin rangos
- GiST/GIN: búsquedas texto completo, geometría
- BRIN: datos muy grandes (millones filas), índice minúsculo

Evitar índices no usados:
ANALYZE TABLE para ver si índice se usa:
SELECT schemaname, tablename, indexname, idx_scan
FROM pg_stat_user_indexes
WHERE idx_scan = 0;  # No se usa este índice, eliminar

2. EXECUTION PLANS:

Analizar query lenta:
EXPLAIN ANALYZE SELECT * FROM orders o
  JOIN order_items oi ON o.id = oi.order_id
  WHERE o.user_id = 123;

Output: muestra plan y estadísticas reales
- Seq Scan = full table scan (rojo, malo)
- Index Scan = usa índice (verde, bueno)
- Hash Join = unión eficiente
- Loop Join = unión lenta (N² complejidad)

Si ves Seq Scan donde no debería:
1. Crear índice: CREATE INDEX idx_user_id ON orders(user_id);
2. Actualizar estadísticas: ANALYZE orders;
3. Re-ejecutar EXPLAIN ANALYZE

3. CONNECTION POOLING (PgBouncer):

Problema: cada conexión consume RAM (5-10MB). 1000 clientes = 5-10GB
Solución: PgBouncer pooling

[databases]
mydb = host=localhost port=5432 dbname=mydb

[pgbouncer]
pool_mode = transaction  # conexión devuelta después query
max_client_conn = 1000
default_pool_size = 25   # máx 25 conexiones reales a PG
max_db_connections = 100

Resultado: 1000 clientes → 25 conexiones reales a DB (economía RAM)

4. CONFIGURACIÓN postgresql.conf (Servidor):

shared_buffers = 256MB  # Caché memoria compartida
# Regla: 25% RAM. VPS 1GB → 256MB
effective_cache_size = 1GB  # Total cache (RAM + OS)
work_mem = 16MB  # Memoria por query (sorting, hash join)
maintenance_work_mem = 64MB  # VACUUM, CREATE INDEX
random_page_cost = 1.1  # SSD (1.1 vs HDD 4.0)

max_connections = 100  # Conexiones simultáneas (default 100)
max_prepared_transactions = 0  # Si no usa prepared txn, 0 ahorra RAM

5. VACUUM & AUTOVACUUM:

Problema: UPDATE/DELETE deja "dead tuples". Tabla crece sin datos reales.
Solución: VACUUM limpia tuples muertas

VACUUM manual: VACUUM ANALYZE orders;
Autovacuum (cron PostgreSQL):
autovacuum = on
autovacuum_max_workers = 3  # Procesos vacuum en paralelo
autovacuum_naptime = 30s  # Verificar cada 30s

6. REPLICACIÓN (master-replica):

Alta disponibilidad: si master falla, replica toma control

master.conf:
wal_level = replica
max_wal_senders = 5
hot_standby = on

replica.conf:
standby_mode = on
primary_conninfo = 'host=master_ip port=5432'

Uso:
- Escrituras → master
- Lecturas → replica (distribuir carga)
- Si master cae → promover replica a master

7. HERMES OS PostgreSQL:

RLS (Row-Level Security):
CREATE POLICY tenant_isolation ON orders
  USING (tenant_id = current_setting('app.current_tenant_id')::uuid);

Multitenancy: cada query automáticamente filtra por tenant.
Ejemplo: SELECT * FROM orders; → devuelve solo órdenes del tenant actual

Índices críticos:
- idx_orders_user_id(user_id)
- idx_tenants_id(id)
- idx_cfdi_tenant_id(tenant_id)
- idx_cfdi_folio_tenant(folio, tenant_id)  # Multicolumn para CFDI únicas por tenant

Sharding futuro:
Si tabla > 10GB, considerar sharding horizontal (particionar por tenant_id)""",
    },
    {
        "title": "Kubernetes Patterns — Despliegue Escalable y Resiliente",
        "source": "Kubernetes Official / Cloud Native Patterns",
        "content": """Kubernetes (K8s) = orquestador containers para producción escalable.

1. PODS vs DEPLOYMENTS:

Pod = unidad mínima en K8s (un container o varios acoplados)
Deployment = "cómo quiero que se vea": N replicas, actualización, rollback

❌ MAL (manual):
kubectl run myapp --image=myapp:1.0
# Crea pod, si muere no se recupera

✅ BIEN (declarativo):
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
spec:
  replicas: 3  # 3 pods siempre corriendo
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1  # Máx 1 pod down durante actualización
      maxSurge: 1  # Máx 1 pod extra durante actualización
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
      - name: myapp
        image: myapp:2.0  # Cambio versión
        ports:
        - containerPort: 8000
        livenessProbe:  # ¿Container vivo?
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:  # ¿Listo recibir tráfico?
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5

K8s automáticamente:
- Mantiene 3 replicas (si pod muere, crea otro)
- Rolling update (para en 1, levanta nuevo, repite)
- Health checks (si liveness falla, reinicia)

2. SERVICES (Networking):

Pod IPs cambian. Service = stable endpoint

apiVersion: v1
kind: Service
metadata:
  name: myapp-service
spec:
  type: ClusterIP  # Interno al cluster (default)
  selector:
    app: myapp
  ports:
  - port: 80
    targetPort: 8000  # pods corren en 8000
---
apiVersion: v1
kind: Service
metadata:
  name: myapp-lb
spec:
  type: LoadBalancer  # Externo (asigna IP pública)
  selector:
    app: myapp
  ports:
  - port: 80
    targetPort: 8000

Tipos:
- ClusterIP: interno, para comunicación entre pods
- NodePort: puerto en cada nodo, acceso externo
- LoadBalancer: IP pública (si cloud provider)

3. CONFIGMAPS & SECRETS:

ConfigMaps = configuración no-sensitiva
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  LOG_LEVEL: INFO
  DATABASE_HOST: postgres.default.svc.cluster.local
  QDRANT_URL: http://qdrant:6333

Secrets = credenciales (cifradas)
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
type: Opaque
data:
  POSTGRES_PASSWORD: cGFzc3dvcmQxMjM=  # Base64
  OPENROUTER_API_KEY: YWJjZGVmZ2hpamtsbW4=

Uso en Deployment:
env:
- name: LOG_LEVEL
  valueFrom:
    configMapKeyRef:
      name: app-config
      key: LOG_LEVEL
- name: POSTGRES_PASSWORD
  valueFrom:
    secretKeyRef:
      name: app-secrets
      key: POSTGRES_PASSWORD

4. STATEFULSETS (Para BD y colas):

Deployment = stateless (pods intercambiables)
StatefulSet = stateful (pod 0, pod 1, … mantienen identidad)

apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
spec:
  replicas: 1  # Master
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15
        ports:
        - containerPort: 5432
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
        livenessProbe:
          exec:
            command:
            - /bin/sh
            - -c
            - pg_isready -U postgres
          initialDelaySeconds: 30
          periodSeconds: 10
  volumeClaimTemplates:  # PVC por replica
  - metadata:
      name: postgres-storage
    spec:
      accessModes: [ "ReadWriteOnce" ]
      resources:
        requests:
          storage: 10Gi

K8s crea: postgres-0 (con volumen postgres-storage-0)
Si postgres-0 muere, se recrea con MISMO volumen (data persist)

5. INGRESS (Punto entrada HTTP):

En lugar de exponer cada Service como LoadBalancer (costoso):
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: myapp-ingress
spec:
  ingressClassName: nginx
  rules:
  - host: myapp.example.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: myapp-service
            port:
              number: 80
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend-service
            port:
              number: 80

Un Ingress + un LoadBalancer = múltiples rutas HTTP a servicios internos

6. HERMES OS en Kubernetes (futuro):

Deployments:
- hermes-api (3 replicas, rolling update)
- hermes-agent (1 replica, secrets para Telegram tokens)
- mystic-agent (1 replica)
- clawbot (2 replicas)
- frontend (2 replicas)

StatefulSet:
- postgres (1 master + replica standby)

Services:
- postgres-service (ClusterIP, interno)
- qdrant-service (ClusterIP, interno)
- hermes-api-service (ClusterIP, interno)
- frontend-lb (LoadBalancer, externo)

Ingress:
- hermes.example.com → frontend
- api.hermes.example.com → hermes-api
- admin.hermes.example.com → admin dashboard""",
    },
    {
        "title": "Monitoring & Alerting — Observabilidad en Producción",
        "source": "Prometheus / Grafana / ELK Stack",
        "content": """Monitoring = recopilar métricas. Alerting = notificar si algo malo ocurre.

1. MÉTRICAS CLAVE (The 4 Golden Signals):

Latency (Latencia):
- Tiempo respuesta API: GET /api/orders → 150ms (bueno) vs 5s (malo)
- SLO típico: p95 < 200ms, p99 < 500ms
- Herramientas: Prometheus, Datadog

Traffic (Tráfico):
- Requests por segundo: 100 req/s (normal) vs 1000 req/s (spike)
- Bytes transferidos: detectar ataques DDoS
- Usuarios activos: load forecast

Errors (Errores):
- Rate: 500 errors / total requests
- SLO típico: < 0.1% errors (99.9% uptime)
- Por tipo: DB connection error, auth error, timeout

Saturation (Saturación):
- CPU: 80% = ok, 95%+ = problema inminente
- RAM: 90%+ = memoria agotándose
- Disk: 85%+ = espacio crítico
- DB connections: 95/100 = casi full

2. PROMETHEUS (Recopilación métricas):

Scrape = lectura periódica de métricas (cada 15s)

prometheus.yml:
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'hermes-api'
    static_configs:
      - targets: ['localhost:8000']

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']

Hermes-api expone /metrics:
# HELP request_duration_seconds Duration of HTTP requests
# TYPE request_duration_seconds histogram
request_duration_seconds_bucket{method="GET",path="/api/orders",le="0.1"} 100
request_duration_seconds_bucket{method="GET",path="/api/orders",le="0.5"} 150
request_duration_seconds_bucket{method="GET",path="/api/orders",le="1.0"} 160
request_duration_seconds_sum{method="GET",path="/api/orders"} 18500
request_duration_seconds_count{method="GET",path="/api/orders"} 160

3. GRAFANA (Visualización):

Dashboard muestra gráficas Prometheus en tiempo real:
- CPU/RAM nodos K8s
- Request latency (p50, p95, p99)
- Error rate por servicio
- Database connection pool utilization

Alertas:
alert:
  - name: HighErrorRate
    expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
    for: 5m
    annotations:
      summary: "High error rate on {{ $labels.job }}"
      description: "{{ $value }}% of requests failing"

Si error rate > 5% por 5 minutos, trigger alerta (email, Slack, PagerDuty)

4. LOGGING (ELK Stack - Elasticsearch + Logstash + Kibana):

Problema: Si servicio falla, ¿por qué? Logs en stdout/files no escalables.
Solución: Centralizar logs

Logstash recolecta:
input {
  beats {
    port => 5000
  }
}

filter {
  if [type] == "app-log" {
    grok {
      match => { "message" => "%{TIMESTAMP_ISO8601:timestamp} %{LOGLEVEL:level} %{DATA:message}" }
    }
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "logs-%{+YYYY.MM.dd}"
  }
}

Kibana permite buscar logs:
- Filtrar por nivel (ERROR, WARN, INFO)
- Rango fechas
- Búsqueda texto: "database connection failed"
- Gráfico: errores por hora

5. DISTRIBUTED TRACING (Jaeger, Zipkin):

Problema: Request pasa por API → Auth → DB → Caché. ¿Dónde latencia?
Solución: Rastrear request completo

Cada paso emite span:
span_auth: 10ms
span_db_query: 80ms
span_cache_write: 5ms
Total: 95ms

Jaeger visualiza como:
GET /api/orders
├── auth (10ms)
├── validate_tenant (5ms)
├── db_query (80ms)
│   ├── connection_pool (2ms)
│   ├── prepare (3ms)
│   └── execute (75ms)
└── serialize_response (0.5ms)

Identifica bottleneck: DB query tarda 80ms

6. HERMES OS Monitoring:

Prometheus targets:
- hermes-api:8000/metrics (FastAPI)
- postgres-exporter:9187 (PostgreSQL)
- redis-exporter:9121 (Redis)
- qdrant:6333/metrics (Qdrant, si expone)
- node-exporter:9100 (HW: CPU, RAM, Disk)

Grafana dashboards:
- API Performance (latency, error rate, RPS)
- Database Health (connections, slow queries, cache hit rate)
- System Resources (CPU, RAM, Disk, Network)

Alertas críticas:
- API error rate > 1% por 5 min → Page on-call
- Database replication lag > 10s → Warning
- Disk usage > 90% → Warning
- CPU > 80% sustained → Scale or investigate""",
    },
]

# ── Funciones auxiliares ──────────────────────────────────────────────────────


def chunk_text(text: str, source: str) -> list[dict]:
    """Divide texto en chunks de 500 palabras con overlap."""
    words = text.split()
    chunks = []
    for i in range(0, len(words), CHUNK_SIZE - CHUNK_OVERLAP):
        chunk = " ".join(words[i : i + CHUNK_SIZE])
        if len(chunk.strip()) < 50:
            continue
        chunk_id = hashlib.md5(f"{source}:{i}".encode()).hexdigest()
        chunks.append(
            {
                "text": chunk,
                "source": source,
                "chunk_index": i // (CHUNK_SIZE - CHUNK_OVERLAP),
                "id": chunk_id,
            }
        )
    return chunks


async def embed_text(text: str) -> list[float]:
    """Genera embedding con nomic-embed-text vía Ollama."""
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(
                f"{OLLAMA_URL}/api/embeddings",
                json={"model": EMBED_MODEL, "prompt": text},
            )
            r.raise_for_status()
            return r.json()["embedding"]
    except Exception as e:
        logger.error(f"Error embedding: {e}")
        raise


async def ensure_collection(client: AsyncQdrantClient):
    """Crea colección si no existe."""
    try:
        collections = await client.get_collections()
        names = [c.name for c in collections.collections]
        if QDRANT_COLLECTION not in names:
            await client.create_collection(
                collection_name=QDRANT_COLLECTION,
                vectors_config=VectorParams(size=768, distance=Distance.COSINE),
                sparse_vectors_config={
                    "bm25": SparseVectorParams(
                        index=SparseIndexParams(on_disk=False)
                    )
                },
            )
            logger.info(f"✓ Colección '{QDRANT_COLLECTION}' creada")
        else:
            logger.info(f"✓ Colección '{QDRANT_COLLECTION}' ya existe")
    except Exception as e:
        logger.error(f"Error ensuring collection: {e}")
        raise


async def upsert_documents(client: AsyncQdrantClient, documents: list[dict]):
    """Chunk, embed y upsert documentos a Qdrant."""
    await ensure_collection(client)

    total_chunks = 0
    for doc in documents:
        chunks = chunk_text(doc["content"], doc["title"])
        logger.info(f"  → {doc['title']}: {len(chunks)} chunks")

        # Embed todos los chunks
        texts = [c["text"] for c in chunks]
        vectors = []
        for text in texts:
            vec = await embed_text(text)
            vectors.append(vec)

        # Upsert a Qdrant
        points = []
        for chunk, vector in zip(chunks, vectors):
            point_id = int(
                hashlib.md5(chunk["id"].encode()).hexdigest(), 16
            ) % (2**63)
            points.append(
                PointStruct(
                    id=point_id,
                    vector={"default": vector},
                    payload={
                        "text": chunk["text"],
                        "source": chunk["source"],
                        "chunk_index": chunk["chunk_index"],
                        "document_id": str(uuid4()),
                        "domain": "ops",
                        "type": "best_practice",
                    },
                )
            )

        await client.upsert(collection_name=QDRANT_COLLECTION, points=points)
        total_chunks += len(points)

    logger.info(f"\n✓ Total chunks insertados: {total_chunks}")


async def main():
    logger.info(f"=== Seed Ops Best Practices → {QDRANT_COLLECTION} ===\n")

    client = AsyncQdrantClient(url=QDRANT_URL)

    try:
        await upsert_documents(client, OPS_BEST_PRACTICES)
        logger.info(f"\n✓ Seed completado exitosamente")
    except Exception as e:
        logger.error(f"✗ Error: {e}")
        raise
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
