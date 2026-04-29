# Blueprint ejecutivo 2026-03-30 — HERMES / ClawdBot por nicho

## 1) Introducción
Este documento resume el estado del repositorio y propone una estrategia de producto/operación para vender ClawdBots por nicho con infraestructura en VPS, integrando backend, frontend, bots, skills, RAG, MCP y automatización.

El enfoque operativo actual del repositorio es una migración incremental: mantener producción funcionando mientras se consolida una arquitectura v2 modular en `apps/`, `packages/`, `infra/`, `workflows/` y `docs/`.

---

## 2) Qué se ha trabajado en el repositorio (resumen por áreas)

### 2.1 Plataforma core (API + Orquestación)
- Se consolidó una API en FastAPI y un bootstrap v2 (`apps/api/app/main.py`) para modularizar dominios por routers y servicios.
- Existe un diseño explícito de orquestación de agentes + skills + memoria con capas de `orchestrator`, `agents`, `skills` y `memory` en backend.
- Ya hay contratos/configs de agentes y skills (`agents.yaml`, `skills.yaml`) para gobierno de capacidades.

**Conclusión del área:** la base técnica permite evolucionar de un backend monolítico hacia un “AI OS” con control gradual de autonomía.

### 2.2 Frontend web (panel, módulos de negocio y academia)
- El frontend en Next.js 14 está organizado con rutas protegidas y módulos funcionales (dashboard, facturas, cierre, brain, onboarding, billing, etc.).
- Existe estructura de academia tanto en frontend (`public/academy`) como en backend (`app/data/academy`) para contenido formativo.

**Conclusión del área:** la web ya funciona como cockpit operativo/comercial y como superficie para educación (Academia).

### 2.3 Bots y canales
- Hay servicios para WhatsApp (`whatsapp`, `apps/whatsapp-bridge`) y Telegram (`apps/telegram-bot`).
- El bot de Telegram incluye catálogo amplio de skills en JSON para casos fiscales/comerciales y operación.
- En VPS se privilegia el bot Node (`telegram-bot`) y se dejó desactivado el bot Python legacy para evitar conflictos.

**Conclusión del área:** el modelo omnicanal ya está instalado; falta estandarizar playbooks comerciales por nicho.

### 2.4 RAG, memoria y conocimiento
- Hay integración con Qdrant y módulos de memoria (`qdrant_rag.py`, `vector_memory.py`, `knowledge_store.py`, `task_history.py`).
- Existen scripts de seed/ingesta para documentos y conocimiento (`seed_qdrant.py`, `seed_fourgea_docs.py`, `seed_knowledge.py`, `setup_rag.sh`).

**Conclusión del área:** hay base para respuestas acertadas por base documental, pero conviene formalizar un pipeline multi-tenant por cliente/nicho.

### 2.5 MCP, herramientas de desarrollo y Claude/OpenClaw
- Existe `apps/mcp-server` para exponer tools gobernadas a clientes externos.
- El repositorio incluye `CLAUDE.md` con protocolo operativo y seguridad para trabajo asistido por Claude Code.
- Existe despliegue opcional de OpenClaw en VPS (`docker-compose.openclaw.yml`) como agente persistente conectado por Telegram y red interna.

**Conclusión del área:** la capa de “copilotos de operación” está presente; el siguiente paso es gobierno fuerte de permisos/acciones por entorno.

### 2.6 Infraestructura VPS y automatización
- El compose de VPS integra Postgres, Redis, API, Frontend, Ollama, n8n, Qdrant, WhatsApp, bridge y Telegram bot.
- Se usan health checks, red `hermes_net`, contenedores con prefijo `hermes_` y exposición de puertos en loopback para hardening.
- Hay gran volumen de workflows n8n para alertas, backups, reportes, salud y operación.

**Conclusión del área:** la orquestación infra ya permite operación 24/7; falta producto empaquetado por vertical.

---

## 3) Orquestación end-to-end propuesta

## Flujo de alto nivel
1. **Captura de demanda**: Web/landing + formulario + bot (Telegram o WhatsApp).
2. **Calificación automática**: skill comercial (`hermes-qualify-prospect`) + CRM/lead scoring.
3. **Onboarding de cliente**: alta tenant, carga de documentos, seed de base RAG.
4. **Operación diaria**: bot responde con RAG + workflows n8n ejecutan recordatorios/tareas.
5. **Escalamiento inteligente**: casos complejos se enrutan a Brain/Claude/OpenClaw según costo-riesgo.
6. **Medición**: panel KPI por cliente (uso bot, precisión percibida, tickets resueltos, renovación).

## Diseño de capas
- **Capa canal**: WhatsApp, Telegram, Web chat.
- **Capa orquestación**: API + router de tareas + skills registry.
- **Capa conocimiento**: Qdrant + colecciones por nicho/cliente + metadatos de vigencia.
- **Capa automatización**: n8n para procesos repetitivos y aprobaciones.
- **Capa gobierno**: API keys, roles, auditoría de prompts, trazabilidad.

---

## 4) Estrategia comercial de ClawdBot por nicho

## Opción A — Un solo bot para todos
**Pros**
- Menor costo inicial de operación.
- Menor complejidad técnica.

**Contras**
- Riesgo de mezclar contexto entre clientes.
- Menor personalización del discurso y del conocimiento.
- Dificulta vender “exclusividad de nicho”.

## Opción B — Un bot por cliente (o sub-bot por tenant)
**Pros**
- Mejor precisión contextual y tono personalizado.
- Aislamiento de datos por cliente (seguridad/compliance).
- Más fácil cobrar setup + mensualidad + addons.

**Contras**
- Mayor costo de onboarding/soporte.
- Requiere automatizar templates para escalar.

## Recomendación (estrategia adecuada)
**Modelo híbrido por etapas**:
1. **Motor único multi-tenant** (backend compartido).
2. **Identidad por cliente** (bot, prompts, base RAG y página por nicho).
3. **Paquetes por vertical** (ej. fiscal, aduanas, salud, inmobiliario).

Esto permite economía de escala técnica sin perder personalización comercial.

---

## 5) ¿Qué ofrecer por cliente en el VPS (producto empaquetado)?

## Paquete “ClawdBot Nicho”
- Landing/página del cliente (branding y oferta).
- Bot dedicado (Telegram y/o WhatsApp).
- Base de conocimiento propia (RAG) con sus documentos.
- Flujos n8n de su operación (recordatorios, seguimiento, postventa).
- Dashboard de métricas y estado.

## Actividades operativas de “Clawd” (runbook)
- Ingesta y depuración documental semanal.
- Re-entrenamiento liviano de prompts/skills por feedback.
- Monitoreo de latencia, errores y cobertura de respuestas.
- Auditoría de respuestas críticas y actualización normativa.

---

## 6) Prompts, skills, web, academia y gamificación

## Prompts
- Mantener prompt base de orquestador + prompts por nicho.
- Versionar prompts (fecha, autor, objetivo, KPI impactado).

## Skills
- Skill por responsabilidad (FAQ, cálculo, integración externa, escalamiento humano).
- Catálogo por vertical con plantillas reutilizables.

## Web page
- Web de captura y conversión con CTA directo a bot.
- Prueba guiada en vivo (demo de 3 preguntas del nicho).

## Academia
- Microcursos para enseñar al cliente a “preguntar mejor” y a interpretar respuestas.
- Certificación interna por rol (dueño, gerente, operación).

## Gamificación
- Misiones semanales dentro del panel (completar onboarding documental, activar 3 automatizaciones, etc.).
- Puntos por uso correcto del bot y cierre de tareas.

---

## 7) Bases de datos, código y lenguajes (mapa práctico)
- **Backend/API**: Python/FastAPI.
- **Frontend**: TypeScript/Next.js.
- **Bots/bridges**: Node.js y Python legacy.
- **Datos transaccionales**: PostgreSQL.
- **Cache/sesión**: Redis.
- **Vectorial RAG**: Qdrant.
- **Modelos locales**: Ollama en VPS.

---

## 8) Open source vs Claude/OpenClaw (lectura ejecutiva)
- **Open source en tu stack**: FastAPI, Next.js, PostgreSQL, Redis, Qdrant, n8n, Ollama, Baileys.
- **Claude/OpenClaw**: capa premium para razonamiento profundo, tareas complejas y operación asistida.

**Recomendación:** usar open-source como base de costo fijo y Claude/OpenClaw como “turbo” en casos de alto valor.

---

## 9) Qué modelo local usar en VPS
Dado un VPS limitado (4 GB RAM mencionado en documentación histórica), conviene estrategia por niveles:
1. **Respuesta diaria y barata**: modelo pequeño en Ollama (ej. 1.5B–3B cuantizado).
2. **Consultas medias**: 7B cuantizado solo en ventanas de carga controlada.
3. **Casos premium**: derivar a Claude/OpenClaw cuando el riesgo/valor lo justifique.

Principio: primero estabilidad operativa y latencia baja; luego “potencia bajo demanda”.

---

## 10) Cómo vender: propuesta concreta para personas/negocios

## Oferta comercial en 3 planes
- **Plan Base**: bot + FAQ + 1 canal + 1 base documental.
- **Plan Pro Nicho**: bot dedicado + workflows + dashboard + academia.
- **Plan Elite**: multi-canal + automatizaciones avanzadas + revisión experta mensual.

## Guion de venta simple
1. Dolor actual (“respondes tarde o inconsistente”).
2. Demostración (3 preguntas reales del negocio).
3. Resultado tangible (tiempo ahorrado, más cierres, menos errores).
4. Cierre con onboarding de 7 días.

## ¿Un bot para todos o uno por cliente?
- **Para arrancar rápido**: bot compartido multi-tenant con guardrails.
- **Para vender mejor y retener**: bot por cliente/nicho (recomendado).
- **Modelo final recomendado**: core compartido + identidad y conocimiento dedicados por cliente.

---

## 11) Roadmap de implementación por fases (90 días)
- **Fase 1 (Semanas 1-2):** plantilla de nicho (landing + bot + RAG + 3 workflows).
- **Fase 2 (Semanas 3-6):** onboarding automatizado por cliente + métricas de éxito.
- **Fase 3 (Semanas 7-10):** catálogo de skills por vertical + academia inicial.
- **Fase 4 (Semanas 11-13):** gamificación + upsell + tablero ejecutivo multi-tenant.

---

## 12) Conclusión general
El repositorio ya tiene la mayoría de piezas para operar un negocio “ClawdBot as a Service”: canales, backend modular, RAG, workflows y despliegue VPS. La mejor estrategia es **arquitectura compartida con personalización por nicho/cliente**, porque combina escalabilidad técnica con valor comercial percibido alto.

Si priorizas eso, puedes vender no solo “un bot”, sino **un sistema operativo de crecimiento** para cada negocio.


---

## 13) Plan en pasos para vender “Bot as a Service” (marca blanca por cliente)

## Paso 1 — Elegir vertical y promesa
- Definir 1 nicho inicial (ej. despacho fiscal, aduanas, clínica, inmobiliaria).
- Definir promesa medible de 30 días (ej. reducir tiempo de respuesta 60%).

## Paso 2 — Producto mínimo vendible (PMV)
- Página/landing white-label del cliente.
- Bot dedicado del cliente (Telegram o WhatsApp).
- Base RAG con 20–100 documentos del cliente.
- 3 automatizaciones n8n (onboarding, seguimiento, recordatorio).

## Paso 3 — Aislamiento por cliente
- Tenant separado en DB transaccional.
- Colección/vector namespace separado en Qdrant.
- Prompt/skills por cliente y auditoría de cambios.

## Paso 4 — Operación y SLA
- Monitoreo de latencia y errores.
- Runbook de incidentes (degradar a respuesta fallback si el modelo local cae).
- Reporte semanal de valor de negocio (tiempo ahorrado, tickets resueltos, conversión).

## Paso 5 — Escalamiento comercial
- Plantilla reusable por nicho.
- Setup fee + mensualidad + addons (integraciones, más canales, más flujos).
- Upsell a autonomía avanzada cuando el cliente ya confía en el sistema.

---

## 14) RAM y capacidad para múltiples clientes en VPS (regla práctica)

## ¿Se pueden tener varios bots en un VPS?
Sí. No es “1 bot = 1 VPS”. Puedes tener varios bots en un solo VPS si:
- Compartes backend multi-tenant.
- Aíslas datos por tenant.
- Controlas concurrencia y límites por cliente.

## Consumo de RAM estimado (orientativo)
- API + workers ligeros: **0.7–1.5 GB**
- Postgres + Redis + n8n + Qdrant (base): **1.8–3.5 GB**
- Bot Telegram/WhatsApp por cliente (concurrency baja): **80–250 MB** por bot
- Overhead sistema Linux: **0.6–1.0 GB**

**Fórmula rápida de planeación:**
`RAM total ≈ base_plataforma + (bots_activos × 0.15 GB) + RAM_modelo + margen_30%`

## Recomendación de VPS por etapa
- **Piloto (1–5 clientes):** 8 GB RAM
- **Inicio comercial (6–20 clientes):** 16 GB RAM
- **Escala inicial (20–60 clientes):** 32 GB RAM

Si deseas LLM local estable para varios clientes concurrentes, empezar en **16 GB** es mucho más seguro que 8 GB.

---

## 15) Modelos locales para respuesta rápida (sin APIs pagadas)

## Estrategia recomendada de inferencia
- **Tier Rápido (default):** modelo 1.5B–3B cuantizado (latencia baja y costo mínimo).
- **Tier Preciso (bajo demanda):** modelo 7B cuantizado para preguntas complejas.
- **Tier Premium:** fallback a proveedor externo solo cuando el caso lo amerite.

## Selección práctica
- Para chat operativo de alta velocidad: usar modelo pequeño (1.5B–3B Q4/Q5).
- Para mejor razonamiento general: usar 7B cuantizado pero con límites de concurrencia.
- Evitar modelos grandes en VPS chico porque rompen SLA por swapping/latencia.

---

## 16) OpenCode, Claude Code y alternativa más barata (GLM)

Si buscas soberanía y costo bajo:
1. Mantén **stack open-source local** como motor principal.
2. Usa herramientas tipo OpenCode para aprovechar modelos gratuitos cuando sea viable.
3. Define un **router por costo/calidad**:
   - primero local,
   - luego modelo barato externo,
   - y Claude solo para tareas premium.

**Importante:** precios y rendimiento real cambian por fecha/proveedor; validar benchmark y costo mensual con pruebas de tu propio tráfico antes de cerrar pricing comercial.

---

## 17) Cómo vender “autonomía + soberanía + seguridad” al cliente

## Mensaje comercial
- “Tu conocimiento vive en tu entorno y con tu marca”.
- “No dependes de una sola API externa para operar”.
- “Tus datos están aislados por tenant y auditados”.

## Controles de seguridad que sí venden
- Aislamiento lógico por tenant (DB + vector namespace).
- Cifrado en tránsito (TLS) y secretos fuera de repositorio.
- Roles/ACL por usuario del cliente.
- Logs de auditoría de consultas y acciones.
- Backup cifrado y política de retención.

## Oferta sugerida (bot por cliente)
- Setup de implementación (branding + datos + flujos).
- Mensualidad por operación (infra + monitoreo + mejoras).
- Add-ons: canales extra, integraciones, modelo más potente, soporte prioritario.

---

## 18) Recomendación final
Para tu objetivo (marca por cliente + soberanía + LLM local):
- Sí conviene **bot por cliente** a nivel identidad y conocimiento.
- Mantén **core multi-tenant compartido** para escalar costos.
- Arranca con **VPS 16 GB RAM** si quieres correr local LLM + varios bots sin degradación severa.
- Vende seguridad como un paquete verificable: aislamiento, auditoría, backups y SLA.
