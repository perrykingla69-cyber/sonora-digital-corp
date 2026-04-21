#!/usr/bin/env python3
"""
seed_architecture_patterns.py — Seed Qdrant colección 'architecture-patterns'

Cubre: Design patterns (MVC, event-driven, CQRS), SOLID principles, refactoring catalogs.
Colección: architecture-patterns (Dense 768-dim + BM25 sparse híbrido)

Uso:
    cd /home/mystic/hermes-os
    python3 scripts/seed_architecture_patterns.py
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
QDRANT_COLLECTION = "architecture-patterns"
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
EMBED_MODEL = "nomic-embed-text"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── Documentos de patrones y principios de arquitectura ──────────────────────

ARCHITECTURE_PATTERNS = [
    {
        "title": "MVC — Model-View-Controller Architecture",
        "source": "Gang of Four / Martin Fowler",
        "content": """MVC = Modelo-Vista-Controlador. Separación de responsabilidades en 3 capas.

CAPAS:

1. MODEL (Modelo)
   Responsabilidad: lógica de negocio, acceso datos, validaciones
   - Contiene clases que representan entidades (User, Order, Product)
   - Métodos de negocio (calcular descuento, validar stock)
   - Acceso BD (queries, inserts, updates)
   - NO debe conocer Vista o Controlador
   Ejemplo:
     class User:
         def __init__(self, name, email):
             self.name = name
             self.email = email
         def validate_email(self):
             return '@' in self.email
         def save(self):  # Persistencia
             db.insert('users', self)

2. VIEW (Vista)
   Responsabilidad: presentación datos al usuario
   - Interfaz gráfica (HTML, formularios, reportes)
   - Formateo datos para visualizar
   - NO contiene lógica negocio
   - NO accede directo BD (siempre via Modelo)
   Ejemplo:
     <table>
       <tr><td>Name: {{user.name}}</td></tr>
       <tr><td>Email: {{user.email}}</td></tr>
     </table>

3. CONTROLLER (Controlador)
   Responsabilidad: orquestar entrada usuario, invocar modelo, seleccionar vista
   - Recibe input usuario (formulario, click, request HTTP)
   - Llama método Modelo apropiado
   - Pasa resultado a Vista
   - Manejo excepciones y redirecciones
   Ejemplo:
     def create_user(request):
         name = request.form['name']
         email = request.form['email']
         user = User(name, email)
         if user.validate_email():
             user.save()
             return render('user_created.html', user)
         else:
             return render('error.html', 'Invalid email')

FLUJO:
Usuario input (formulario)
  ↓
Controller recibe input
  ↓
Controller llama Model.create_user(data)
  ↓
Model valida, guarda BD
  ↓
Controller pasa resultado a View
  ↓
View renderiza HTML
  ↓
Usuario ve resultado

VENTAJAS:
- Separación clara responsabilidades
- Reusabilidad: Model puede usarse en Web, Mobile, API
- Testeable: cada capa se testa independiente
- Mantenibilidad: cambio Vista no afecta Modelo

DESVENTAJAS:
- Más archivos, más complejidad inicial
- Si lógica está entre Controller/Model, spaghetti code
- Para apps pequeñas, overkill

HERMES OS usa MVC:
- Model: /apps/api/app/models/ (User, Tenant, Order)
- View: /frontend (Next.js components)
- Controller: /apps/api/app/routes/ (FastAPI routers)""",
    },
    {
        "title": "Event-Driven Architecture — Publicador-Suscriptor",
        "source": "CQRS Pattern / Chris Richardson",
        "content": """Event-Driven = sistemas basados en eventos que disparadores acciones desacopladas.

CONCEPTO BÁSICO:
En lugar de: A llama B → B llama C → C llama D (acoplamiento fuerte)
En Event-Driven: A publica evento → B, C, D se suscriben y actúan independiente (desacoplamiento)

COMPONENTES:

1. EVENT (Evento)
   - Representa algo que ocurrió en el pasado
   - Inmutable (no cambia)
   - Contiene datos del suceso
   Ejemplo:
     class UserCreatedEvent:
         def __init__(self, user_id, email, timestamp):
             self.user_id = user_id
             self.email = email
             self.timestamp = timestamp  # Cuándo ocurrió

2. EVENT PUBLISHER (Publicador)
   - Genera eventos cuando ocurre acción
   - No conoce quién suscrito
   - Emite a través broker/bus
   Ejemplo:
     class UserService:
         def create_user(self, email):
             user = User(email)
             db.save(user)
             event_bus.publish(UserCreatedEvent(user.id, email, now()))
             # UserService no sabe quién recibirá evento

3. EVENT SUBSCRIBER (Suscriptor)
   - Escucha eventos de interés
   - Ejecuta lógica cuando evento ocurre
   - Actúa independiente, sin conocer publisher
   Ejemplo:
     class WelcomeEmailService:
         @subscribe(UserCreatedEvent)
         def send_welcome_email(self, event):
             send_email(event.email, "Bienvenido!")

     class NotificationService:
         @subscribe(UserCreatedEvent)
         def log_new_user(self, event):
             logger.info(f"New user: {event.user_id}")

4. EVENT BUS (Bus/Broker)
   - Intermediario que entrega eventos a suscriptores
   - Puede ser: RabbitMQ, Redis, Kafka, simple pub-sub en memoria
   Ejemplo:
     class EventBus:
         def publish(self, event):
             subscribers = self.registry.get(event.__class__)
             for subscriber in subscribers:
                 subscriber(event)
         def subscribe(self, event_class, handler):
             self.registry[event_class].append(handler)

FLUJO:
UserService.create_user()
  ↓
Crea User en BD
  ↓
Publica UserCreatedEvent("jane@example.com")
  ↓
EventBus enruta evento a todos suscriptores
  ├─→ WelcomeEmailService.send_welcome_email()
  ├─→ NotificationService.log_new_user()
  └─→ AnalyticsService.track_signup()
  ↓
Todos ejecutan PARALELO, ASINCRÓNICO

VENTAJAS:
- Desacoplamiento: services no conocen entre sí
- Escalabilidad: fácil agregar nuevo subscriber sin tocar existentes
- Resiliencia: si email falla, rest continúa (con retry)
- Auditoría: todos eventos quedan registrados

DESVENTAJAS:
- Debugging difícil (flujo no secuencial)
- Si falla evento, propagación incierta
- Requiere broker (Redis, RabbitMQ) = complejidad operativa
- Order eventos puede ser crítico (si A antes B)

HERMES OS usa Event-Driven:
- EventBus: /apps/api/app/events/
- UserCreatedEvent → triggers auto-seed Qdrant por nicho
- OrderPaidEvent → triggers facturación CFDI""",
    },
    {
        "title": "CQRS — Command Query Responsibility Segregation",
        "source": "Greg Young / Microsoft",
        "content": """CQRS = separación lectura (Query) de escritura (Command) en dos modelos distintos.

PROBLEMA QUE RESUELVE:
En CRUD normal: Reader requiere índices, Writer requiere normalizacion
Compromise = performance deficiente en ambas direcciones

SOLUCIÓN CQRS:
Modelo de lectura optimizado para queries (denormalizado, índices)
Modelo de escritura optimizado para comandos (normalizado, consistencia)

COMPONENTES:

1. COMMAND (Comando)
   - Acción que CAMBIA estado
   - Create, Update, Delete
   - Validación obligatoria
   - Transaccional
   Ejemplo:
     class CreateOrderCommand:
         user_id: str
         items: List[Item]
         delivery_address: str

     def execute(cmd):
         order = Order(cmd.user_id, cmd.items, cmd.delivery_address)
         order.validate()  # Debe ser válido
         db_write.save(order)
         eventbus.publish(OrderCreatedEvent(...))

2. QUERY (Consulta)
   - Acción que LEE estado
   - Read-only, sin mutación
   - Optimizada para velocidad
   - Puede ser eventual consistent
   Ejemplo:
     class GetOrderByIdQuery:
         order_id: str

     def execute(query):
         return db_read.query("SELECT * FROM orders_view WHERE id = ?", query.order_id)

ARQUITECTURA SEPARADA:

ESCRITURA (Command Side):
┌─ Normalized DB ─────────────┐
│ Table: orders               │
│ Table: order_items          │
│ Table: order_events         │
└─────────────────────────────┘
      ↓
  EventBus (OrderCreatedEvent, OrderPaidEvent, etc.)
      ↓
┌─ Read Model Generator ──────┐
│ Consume events              │
│ Update denormalized views   │
└─────────────────────────────┘

LECTURA (Query Side):
┌─ Denormalized DB ───────────┐
│ View: orders_summary        │
│  - id, user_id, total,      │
│    status, created_at       │
│ View: orders_with_items     │
│  - id, user_id, item_count, │
│    total, paid              │
│ View: orders_by_user        │
│  - user_id, order_count,    │
│    total_spent              │
└─────────────────────────────┘
      ↓
  Fast queries (índices, denormalizado)
      ↓
  API /api/orders (instant response)

FLUJO:

User crea Order:
  POST /api/orders {items: [...]
       ↓
  CommandHandler.CreateOrderCommand()
       ↓
  Guarda en normalized DB (ACID)
       ↓
  Publica OrderCreatedEvent
       ↓
  Event handler consume evento
       ↓
  Actualiza Read Model (vistas denormalizadas)
       ↓
  Usuario consulta: GET /api/orders/123
       ↓
  Query contra Read Model (rápido)

EVENTUAL CONSISTENCY:
Hay lag entre escritura (command) y disponibilidad lectura (read model).
Ejemplo: Order se crea en 100ms, pero view se actualiza en 200ms = 100ms delay.
Para apps tiempo-real: aceptable. Para transacciones críticas: problema.

VENTAJAS:
- Optimización independiente: read y write sin compromiso
- Escalabilidad: read model puede replicarse en caché (Redis)
- CQRS + Event Sourcing: auditoria completa de cambios
- Performance: queries contra índices denormalizados (muy rápido)

DESVENTAJAS:
- Eventual consistency: datos pueden estar atrasados
- Complejidad: más código, más sincronización
- Debugging: bifurcación lógica (command vs query)
- Sincronización Read Model: si cae, eventos se pierden

HERMES OS implementa CQRS parcial:
- CommandHandler: /apps/api/app/commands/ (crear factura, auditar)
- QueryHandler: /apps/api/app/queries/ (listar órdenes, reportes)
- Read Model: Qdrant (búsqueda RAG), Redis (caché)""",
    },
    {
        "title": "SOLID Principles — Principios de Diseño Software",
        "source": "Robert C. Martin (Uncle Bob)",
        "content": """SOLID = 5 principios para código mantenible, flexible, extensible.

1. SINGLE RESPONSIBILITY PRINCIPLE (SRP)
   "Una clase debe tener una sola razón para cambiar"

   ❌ MAL:
   class User:
       def __init__(self, name, email):
           self.name = name
           self.email = email

       def save(self):  # Responsabilidad BD
           db.insert('users', self)

       def send_email(self):  # Responsabilidad email
           email_service.send(self.email)

       def generate_report(self):  # Responsabilidad reporting
           return f"User: {self.name}, Email: {self.email}"
   # 3 razones para cambiar: BD, email API, formato report

   ✅ BIEN:
   class User:
       def __init__(self, name, email):
           self.name = name
           self.email = email

   class UserRepository:  # Responsabilidad: persistencia
       def save(self, user):
           db.insert('users', user)

   class UserEmailService:  # Responsabilidad: emails
       def send_welcome(self, user):
           email_service.send(user.email, "Bienvenido")

   class UserReporter:  # Responsabilidad: reportes
       def generate_report(self, user):
           return f"User: {user.name}, Email: {user.email}"

2. OPEN/CLOSED PRINCIPLE (OCP)
   "Abierto para extensión, cerrado para modificación"

   ❌ MAL:
   class PaymentProcessor:
       def process(self, payment):
           if payment.method == 'credit_card':
               # Procesar tarjeta
           elif payment.method == 'paypal':
               # Procesar PayPal
           elif payment.method == 'bitcoin':
               # Procesar Bitcoin
           # Cada nuevo método = modificar clase

   ✅ BIEN:
   class PaymentMethod:
       def process(self, amount):
           raise NotImplementedError

   class CreditCardPayment(PaymentMethod):
       def process(self, amount):
           # Procesar tarjeta

   class PayPalPayment(PaymentMethod):
       def process(self, amount):
           # Procesar PayPal

   class PaymentProcessor:
       def process(self, payment: PaymentMethod, amount):
           payment.process(amount)  # Funciona con cualquier tipo
   # Agregar Bitcoin: crear clase nueva, NO modificar PaymentProcessor

3. LISKOV SUBSTITUTION PRINCIPLE (LSP)
   "Subclases deben ser sustituibles por su clase base"

   ❌ MAL:
   class Bird:
       def fly(self):
           return "Flying"

   class Penguin(Bird):  # Penguin hereda Bird pero NO vuela
       def fly(self):
           raise Exception("Penguins can't fly!")
   # Código que espera Bird.fly() falla si recibe Penguin

   ✅ BIEN:
   class Bird:
       def move(self):
           raise NotImplementedError

   class FlyingBird(Bird):
       def move(self):
           return "Flying"

   class SwimmingBird(Bird):
       def move(self):
           return "Swimming"

   class Penguin(SwimmingBird):
       pass

4. INTERFACE SEGREGATION PRINCIPLE (ISP)
   "No obligues cliente a depender de interfaces que no usa"

   ❌ MAL:
   class Animal:
       def walk(self): pass
       def fly(self): pass
       def swim(self): pass

   class Dog(Animal):
       def walk(self): ...
       def fly(self): raise Exception("Dogs don't fly")  # Forzado
       def swim(self): ...

   ✅ BIEN:
   class Walkable:
       def walk(self): pass

   class Flyable:
       def fly(self): pass

   class Swimmable:
       def swim(self): pass

   class Dog(Walkable, Swimmable):
       pass  # Solo lo que necesita

5. DEPENDENCY INVERSION PRINCIPLE (DIP)
   "Depende de abstracciones, no de concreciones"

   ❌ MAL:
   class UserService:
       def __init__(self):
           self.db = MySQLDatabase()  # Depende de concreción
       def get_user(self, id):
           return self.db.query(id)
   # Si cambio a PostgreSQL, modifico UserService

   ✅ BIEN:
   class Database:  # Abstracción
       def query(self, id): pass

   class UserService:
       def __init__(self, db: Database):  # Inyecta dependencia
           self.db = db
       def get_user(self, id):
           return self.db.query(id)

   # Uso:
   db = MySQLDatabase()  # o PostgreSQL sin cambiar UserService
   service = UserService(db)

RESUMEN SOLID:
S = cada clase una responsabilidad
O = extender sin modificar
L = sustituibilidad (herencia correcta)
I = interfaces mínimas necesarias
D = depender de abstracciones

HERMES OS sigue SOLID:
- SRP: UserService, OrderService, TenantService (separados)
- OCP: PaymentMethods (extensible)
- LSP: BaseAgent → HermesAgent, MysticAgent
- ISP: RagRetriever (solo métodos search, embed)
- DIP: qdrant_client inyectado, no hardcoded""",
    },
    {
        "title": "Refactoring Patterns — Técnicas para Mejorar Código",
        "source": "Martin Fowler / Refactoring Catalog",
        "content": """Refactoring = mejorar estructura código sin cambiar comportamiento.

PROBLEMAS COMUNES Y SOLUCIONES:

1. LONG METHOD (Método muy largo)
   Problema: método con 100+ líneas, difícil seguir lógica
   Síntoma: necesitas 10 comentarios para entender qué hace

   Solución: Extract Method
   ❌ ANTES:
   def process_order(order):
       # Validar orden (10 líneas)
       if not order.items:
           raise ValueError("Empty")
       total = 0
       for item in order.items:
           # Calcular precio (15 líneas)
           base_price = item.price * item.qty
           discount = calculate_discount(item)
           tax = calculate_tax(base_price - discount)
           total += base_price - discount + tax
       # Guardar orden (5 líneas)
       db.save(order)
       return total

   ✅ DESPUÉS:
   def process_order(order):
       validate_order(order)
       total = calculate_total(order)
       save_order(order)
       return total

   def validate_order(order):
       if not order.items:
           raise ValueError("Empty")

   def calculate_total(order):
       total = 0
       for item in order.items:
           item_total = calculate_item_total(item)
           total += item_total
       return total

   def calculate_item_total(item):
       base = item.price * item.qty
       discount = calculate_discount(item)
       tax = calculate_tax(base - discount)
       return base - discount + tax

2. FEATURE ENVY (Un método usa muchos campos de otro objeto)
   Problema: método en A que accesa 5+ campos de B
   Síntoma: order.user.name, order.user.email, order.user.address (¿por qué no en Order?)

   Solución: Move Method
   ❌ ANTES:
   class Order:
       def __init__(self, user, items):
           self.user = user
           self.items = items

       def send_confirmation_email(self):
           email = self.user.email  # Feature Envy
           name = self.user.name
           address = self.user.address
           phone = self.user.phone
           return f"Dear {name}, your order at {address}..."

   ✅ DESPUÉS:
   class Order:
       def send_confirmation_email(self):
           message = self.user.get_confirmation_message()
           return message

   class User:
       def get_confirmation_message(self):
           return f"Dear {self.name}, your order at {self.address}..."

3. DUPLICATED CODE (Código repetido en múltiples lugares)
   Problema: mismo lógica en 3 métodos
   Síntoma: si cambio lógica, debo hacerlo 3 veces

   Solución: Extract Method o Extract Class
   ❌ ANTES:
   class ReportService:
       def generate_sales_report(self):
           data = db.query("SELECT * FROM orders WHERE status='paid'")
           total = 0
           for order in data:
               total += order.amount
           return f"Total sales: ${total}"

       def generate_revenue_report(self):
           data = db.query("SELECT * FROM orders WHERE status='paid'")
           total = 0
           for order in data:
               total += order.amount
           return f"Revenue: ${total}"

   ✅ DESPUÉS:
   class ReportService:
       def generate_sales_report(self):
           total = self.calculate_paid_total()
           return f"Total sales: ${total}"

       def generate_revenue_report(self):
           total = self.calculate_paid_total()
           return f"Revenue: ${total}"

       def calculate_paid_total(self):
           data = db.query("SELECT * FROM orders WHERE status='paid'")
           return sum(order.amount for order in data)

4. LONG PARAMETER LIST (Método con 5+ parámetros)
   Problema: función(a, b, c, d, e, f) — fácil confundir orden
   Síntoma: create_order(user_id, items, discount, tax, shipping, promo_code)

   Solución: Introduce Parameter Object
   ❌ ANTES:
   def create_order(user_id, items, discount, tax, shipping, promo_code, date, notes):
       order = Order(user_id, items)
       order.apply_discount(discount)
       order.add_tax(tax)
       order.set_shipping(shipping)
       ...

   ✅ DESPUÉS:
   class OrderRequest:
       def __init__(self, user_id, items, discount, tax, shipping, promo_code, date, notes):
           self.user_id = user_id
           self.items = items
           self.discount = discount
           self.tax = tax
           self.shipping = shipping
           self.promo_code = promo_code
           self.date = date
           self.notes = notes

   def create_order(request: OrderRequest):
       order = Order(request.user_id, request.items)
       order.apply_discount(request.discount)
       ...

5. DIVERGENT CHANGE (Clase que cambia por muchas razones)
   Problema: clase que hace BD, email, validación, reporting
   Síntoma: modifiquei OrderProcessor y rompí emails (no debería estar acoplado)

   Solución: Extract Class
   ❌ ANTES:
   class Order:
       def process(self):  # 100 líneas: validación, BD, email, logging
           self.validate()
           self.save_to_db()
           self.send_email()
           self.log_event()

   ✅ DESPUÉS:
   class Order:
       def __init__(self, validator, persister, emailer, logger):
           self.validator = validator
           self.persister = persister
           self.emailer = emailer
           self.logger = logger

       def process(self):
           self.validator.validate(self)
           self.persister.save(self)
           self.emailer.notify(self)
           self.logger.log(f"Order processed: {self.id}")

REFACTORING EN HERMES OS:
- Extract Method: separar lógica RAG de búsqueda fiscal
- Move Method: mover validación CFDI a CFDIValidator
- Remove Duplication: consolidar seed scripts (fiscal, food, legal) en clase base
- Introduce Parameter Object: OrderRequest para crear órdenes""",
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
                        "domain": "architecture",
                        "type": "pattern",
                    },
                )
            )

        await client.upsert(collection_name=QDRANT_COLLECTION, points=points)
        total_chunks += len(points)

    logger.info(f"\n✓ Total chunks insertados: {total_chunks}")


async def main():
    logger.info(f"=== Seed Architecture Patterns → {QDRANT_COLLECTION} ===\n")

    client = AsyncQdrantClient(url=QDRANT_URL)

    try:
        await upsert_documents(client, ARCHITECTURE_PATTERNS)
        logger.info(f"\n✓ Seed completado exitosamente")
    except Exception as e:
        logger.error(f"✗ Error: {e}")
        raise
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
