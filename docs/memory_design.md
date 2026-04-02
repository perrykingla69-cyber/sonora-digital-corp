# Diseño de Memoria

## Componentes

### TaskHistory
Registro append-only de todas las tareas ejecutadas.

```python
th = TaskHistory(persist_path="memory/tasks.json")
record = th.store("task-001", task_dict, result_dict)
recent = th.recent(limit=10)
```

- Persiste en JSON automáticamente si se provee `persist_path`
- Útil para auditoría, debugging y aprendizaje

### KnowledgeStore
Almacén clave-valor para hechos, artefactos y resultados importantes.

```python
ks = KnowledgeStore(persist_path="memory/knowledge.json")
ks.put("fourgea_rfc", "E080820LC2")
ks.get("fourgea_rfc")
ks.search("fourgea")  # búsqueda por substring en clave
```

- Persistencia JSON automática
- Búsqueda por substring en claves

### VectorMemory
Memoria semántica lista para embeddings. Hoy: búsqueda léxica. Mañana: cosine similarity.

```python
vm = VectorMemory(persist_path="memory/vectors.json")
vm.add("doc1", "Filtración de aceite industrial", embedding=[...])
results = vm.similarity_search("aceite", limit=5)
# Con embedding: ranking cosine
# Sin embedding: fallback léxico
```

## Flujo de Datos

```
Tarea entra al Orquestador
        │
        ▼
Agente ejecuta skill
        │
        ▼
Resultado → TaskHistory.store()
        │
        ▼ (si es conocimiento relevante)
KnowledgeStore.put() o VectorMemory.add()
        │
        ▼ (próxima tarea similar)
Orchestrator consulta KnowledgeStore antes de ejecutar
```

## Persistencia

Por defecto la memoria es **en RAM** (sin persist_path).
Para persistir en disco, pasar la ruta al constructor:

```python
# En Orchestrator.from_config() se puede configurar:
self.task_history = TaskHistory(persist_path=".data/tasks.json")
self.knowledge_store = KnowledgeStore(persist_path=".data/knowledge.json")
```

## Roadmap

| Fase | Memoria | Backend |
|---|---|---|
| Actual | TaskHistory + KnowledgeStore + VectorMemory léxico | JSON en disco |
| Fase 2 | Embeddings reales con sentence-transformers | pgvector (ya instalado) |
| Fase 3 | Permisos por agente, TTL, compactación | PostgreSQL 15 |
