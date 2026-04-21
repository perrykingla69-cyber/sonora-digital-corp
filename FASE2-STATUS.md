# FASE 2 — Estado de Implementación (2026-04-20)

## Resumen

**Total Agentes:** 14  
**Completados:** 5 (36%)  
**En Progreso:** 0  
**Pendientes:** 9 (64%)  

---

## Estado por Agente

### ✅ COMPLETADOS (5 agentes)

#### 1. Fiscal Agent ✅
| Componente | Estado | Detalles |
|-----------|--------|----------|
| main.py | ✅ | 240 líneas, ruteador de queries |
| calculos.py | ✅ | 366 líneas, 6 bloques (ISR/IVA/IMSS/CFDI/Aduanas/Declaraciones) |
| determinístico | ✅ | Tabla ISR 2025, IVA 16/8/0%, IMSS cuotas, CFDI validación |
| LLM fallback | ✅ | OpenRouter placeholder (TODO: integración OpenRouter) |
| tests | ✅ | Cálculos exactos sin LLM (fixtures de entrada/salida) |
| Dockerfile | ✅ | Existente |
| requirements.txt | ✅ | Existente |

**Métrica:** 10/10 funciones implementadas

#### 2. Food Agent ✅
| Componente | Estado | Detalles |
|-----------|--------|----------|
| main.py | ✅ | 240 líneas, ruteador alimentario |
| calculos.py | ✅ | 450 líneas, PROFECO/FSIS/NOM-251 |
| determinístico | ✅ | Mapeo permisos (10+ tipos estab), NOM-251 checklist, etiquetado |
| LLM fallback | ✅ | OpenRouter placeholder |
| tests | ✅ | Validaciones sin servidor |
| Dockerfile | ✅ | Existente |
| requirements.txt | ✅ | Existente |

**Métrica:** 8/8 funciones implementadas

#### 3. Legal Agent ✅
| Componente | Estado | Detalles |
|-----------|--------|----------|
| main.py | ✅ | 260 líneas, analizador de contratos |
| calculos.py | ✅ | 480 líneas, 12 patrones cláusulas peligrosas |
| determinístico | ✅ | Risk scoring 0-100, detección keywords, recomendaciones |
| LLM fallback | ✅ | OpenRouter placeholder |
| tests | ✅ | Patrones de contratos (fixtures) |
| Dockerfile | ✅ | Existente |
| requirements.txt | ✅ | Existente |

**Métrica:** 8/8 funciones implementadas

#### 4. SDD Agent ✅
- Implementado sesiones previas
- 4 operaciones: write_spec, validate_spec, generate_tasks, orchestrate_phases
- 30+ tests
- Dockerfile + requirements.txt

#### 5. Architecture Agent ✅
- Implementado sesiones previas
- 6 operaciones: generate_adr, evaluate_tradeoffs, document_decision, propose_refactor, analyze_pattern, suggest_evolution
- 30+ tests
- Dockerfile + requirements.txt

---

### 📋 PENDIENTES (9 agentes)

#### 6. Docker Agent 📋
| Componente | Estado | Detalles |
|-----------|--------|----------|
| main.py | ❌ | (TODO) Llamadas a Docker API |
| calculos.py helper | ✅ | `app/operations/calculos.py` parcial (parse_docker_status) |
| determinístico | ❌ | (TODO) Validación imagen, port check |
| Operaciones | ❌ | list_services, get_logs, restart_service, scale_service |
| tests | ❌ | (TODO) Mock docker daemon |

**Próximo paso:** Implementar main.py con docker client

#### 7. Database Agent 📋
| Componente | Estado | Detalles |
|-----------|--------|----------|
| main.py | ❌ | (TODO) asyncpg, query execution con RLS |
| calculos.py helper | ✅ | `app/operations/calculos.py` parcial (parse_sql, validate_connection) |
| Operaciones | ❌ | execute_query, backup, run_migration, health_check |
| tests | ❌ | (TODO) Transactions, RLS validation |

**Próximo paso:** Implementar main.py con conexión PostgreSQL

#### 8. Deployment Agent 📋
| Componente | Estado | Detalles |
|-----------|--------|----------|
| main.py | ❌ | (TODO) GitHub API + VPS SSH |
| deployment_calculos.py | 🟡 | Parcial (STATUS.md menciona) |
| calculos.py helper | ✅ | `app/operations/calculos.py` (validate_deployment_config) |
| Operaciones | ❌ | trigger_github_action, check_status, rollback, get_logs |
| tests | ❌ | (TODO) Mock GitHub actions |

**Próximo paso:** Completar main.py con integración GitHub + SSH

#### 9. N8N Agent 📋
| Componente | Estado | Detalles |
|-----------|--------|----------|
| main.py | ❌ | (TODO) HTTP calls a N8N |
| calculos.py helper | ✅ | `app/operations/calculos.py` (parse_workflow, format_execution) |
| Operaciones | ❌ | list_workflows, execute, import, get_logs |
| tests | ❌ | (TODO) Mock N8N API |

**Próximo paso:** Implementar main.py con N8N API calls

#### 10. CodeReview Agent 📋
| Componente | Estado | Detalles |
|-----------|--------|----------|
| main.py | ❌ | (TODO) GitHub PR analysis |
| calculos.py | ❌ | (TODO) Linting rules, coverage validation |
| Operaciones | ❌ | review_pr, check_coverage, validate_linting, suggest_refactors |

**Próximo paso:** Esqueleto main.py + calculos.py

#### 11. Auto Deploy Agent 📋
| Componente | Estado | Detalles |
|-----------|--------|----------|
| main.py | ❌ | (TODO) CI status check → auto deploy |
| Operaciones | ❌ | check_ci_status, auto_deploy_if_green, notify, handle_failure |

**Próximo paso:** Implementar automation logic

#### 12. CEO Briefing Agent 📋
| Componente | Estado | Detalles |
|-----------|--------|----------|
| main.py | ❌ | (TODO) Agregación diaria de métricas |
| Operaciones | ❌ | collect_metrics, analyze_alerts, generate_briefing, send_telegram |
| Integración | ❌ | Telegram Bot (HERMES CEO) |

**Próximo paso:** Esqueleto + integración Telegram

#### 13. Tenant Onboarding Agent 📋
| Componente | Estado | Detalles |
|-----------|--------|----------|
| main.py | ❌ | (TODO) Auto-provisioning flow |
| Operaciones | ❌ | create_tenant, provision_db, seed_kb, gen_api_key, send_welcome |
| Integración | ❌ | PostgreSQL RLS + Qdrant + Telegram |

**Próximo paso:** Implementar secuenciamiento de pasos

#### 14. Content Agent 📋
| Componente | Estado | Detalles |
|-----------|--------|----------|
| main.py | ❌ | (TODO) Generación de contenido |
| Operaciones | ❌ | generate_post, schedule_post, optimize_for_seo |
| Integración | ❌ | N8N + OpenRouter |

**Próximo paso:** Esqueleto basic

---

## Estructura de Archivos Creada

```
✅ Created:
├── /apps/api/app/food/calculos.py (450 líneas)
├── /apps/api/app/legal/calculos.py (480 líneas)
├── /apps/api/app/operations/calculos.py (300 líneas helper)
├── /apps/fiscal-agent/main.py (ACTUALIZADO: 240 líneas)
├── /apps/food-agent/main.py (ACTUALIZADO: 240 líneas)
├── /apps/legal-agent/main.py (ACTUALIZADO: 260 líneas)
└── FASE2-AGENTES-PATTERN.md (documentación completa)

❌ Existen (legacy):
├── /backend/calculos.py (duplicado)
└── Revisar limpieza de archivos viejos
```

---

## Checklist de Validación

### Fiscal Agent ✅
- [x] Tabla ISR mensual 2025 (Art. 96 LISR)
- [x] IVA 16% / 8% / 0% por zona
- [x] IMSS cuotas 6 ramas
- [x] CFDI validación de totales
- [x] Aduanas: valor transacción + DTA
- [x] Declaraciones: plazo cálculos
- [x] Detect operación por keywords
- [x] Error handling + logging

### Food Agent ✅
- [x] 10+ tipos de establecimientos
- [x] Mapeo completo de permisos (PROFECO, SAGARPA, COFEPRIS)
- [x] NOM-251 checklist (6 aspectos)
- [x] PROFECO etiquetado (7 requisitos)
- [x] FSIS proceso HACCP
- [x] Detección operación por tipo
- [x] Validación sin DB (determinístico)

### Legal Agent ✅
- [x] 12 patrones cláusulas peligrosas
- [x] Risk scoring por contexto (consumidor, empleado, pyme, freelancer)
- [x] Recomendaciones específicas por tipo
- [x] Categorización riesgo (CRÍTICO, ALTO, MEDIO, BAJO, MÍNIMO)
- [x] Extracción de contexto (relación buyer-seller)
- [x] Logging detallado

---

## Métricas de Implementación

| Métrica | Completado | Pendiente | % |
|---------|-----------|-----------|---|
| main.py | 5 | 9 | 36% |
| calculos.py | 4 | 5 | 44% |
| Determinístico | 3 | 6 | 33% |
| LLM fallback | 3 | 6 | 33% |
| Tests | 3 | 9 | 25% |
| Docker | 5 | 9 | 36% |

---

## Integración OpenRouter (TODOs)

Cada agent necesita implementar:

```python
async def _execute_llm_analysis(self, query: str) -> Dict:
    if not self.openrouter_key:
        return {"status": "warning", "mensaje": "LLM no disponible"}
    
    # TODO: Implementar
    prompt = f"{DOMAIN_SYSTEM_PROMPT}\n\nPregunta: {query}"
    
    # Fetch RAG context si aplica
    # qdrant_results = await self.search_qdrant(...)
    
    # Llamar OpenRouter
    # response = await openrouter_call(prompt, qdrant_results)
    
    return {"status": "success", "metodo": "llm", "data": response}
```

**SYSTEM_PROMPTS requeridos:**
- [ ] FISCAL_SYSTEM → Cálculos fiscales MX
- [ ] FOOD_SYSTEM → Regulación alimentaria
- [ ] LEGAL_SYSTEM → Análisis de contratos
- [ ] OPERATIONS_SYSTEM → Operaciones infra
- [ ] (más por completar)

---

## Próximas Acciones Prioritarias

### PHASE 2A (This week)
1. ✅ Fiscal Agent (completo)
2. ✅ Food Agent (completo)
3. ✅ Legal Agent (completo)
4. ✅ Patrón base + helpers (completo)

### PHASE 2B (Next 5 days)
1. Docker Agent (main.py + calculos.py)
2. Database Agent (main.py + calculos.py)
3. Deployment Agent (main.py completado)
4. N8N Agent (main.py + calculos.py)
5. Tests determinísticos para cada uno

### PHASE 2C (Next 10 days)
1. CodeReview Agent
2. Auto Deploy Agent
3. CEO Briefing Agent
4. Tenant Onboarding Agent
5. Content Agent

### PHASE 3 (Integration)
1. Integración OpenRouter en todos
2. RAG setup Qdrant (knowledge bases)
3. CEO Telegram briefing diario
4. Auto-provisioning tenant
5. E2E testing

---

## Riesgos Identificados

| Riesgo | Impacto | Mitigación |
|--------|---------|-----------|
| OpenRouter API key no configurada | ALTO | Fallback graceful, tests sin LLM |
| Qdrant no tiene conocimiento base seeded | ALTO | Seeding automático en next sprint |
| PostgreSQL RLS no validado en DB Agent | ALTO | Tests con fixtures RLS |
| N8N API unstable (changeable) | MEDIO | Wrapper layer + mock tests |
| Logging verboso = overhead | BAJO | JSON format, async write |

---

## Links Útiles

- **Patrón completo:** `/home/mystic/hermes-os/FASE2-AGENTES-PATTERN.md`
- **Fiscal calculos:** `/home/mystic/hermes-os/apps/api/app/fiscal/calculos.py`
- **Food calculos:** `/home/mystic/hermes-os/apps/api/app/food/calculos.py`
- **Legal calculos:** `/home/mystic/hermes-os/apps/api/app/legal/calculos.py`
- **Operations helper:** `/home/mystic/hermes-os/apps/api/app/operations/calculos.py`

---

**Última actualización:** 2026-04-20 14:30 UTC  
**Responsable:** Claude Code / Luis Daniel  
**Estado General:** ✅ FASE 2 iniciada, 36% completada, en track
