# agent:rag — RAG & AutoSeeder
> Carga solo este archivo. Para contexto cross-dominio: `mem_search "qdrant seeder niche"` en Engram.

## Dominio
Pipeline de conocimiento: seed por nicho, embeddings, upsert a Qdrant.
Se activa automáticamente en onboarding de nuevo tenant.

## Archivos clave
- `seeders/auto_seeder.py` — orquesta seed por nicho
- `seeders/niche_registry.py` — registry de nichos y fuentes
- `mystic/hostinger_monitor.py` — monitor de hosting

## Nichos registrados
`pastelero`, `restaurante`, `proveedor_alimentos`, `contador`, `abogado`,
`bombero`, `medico`, `constructor`, `general`

## Pipeline AutoSeeder
```
classify_niche(desc) → niche
  → fetch fuentes (URL/RSS/NOM)
  → chunk_text(500 words, 50 overlap)
  → embed nomic-embed-text (Ollama :11434, 768-dim)
  → upsert Qdrant: colección hermes_knowledge
    payload: {tenant_id, niche, source, chunk_id}
```

## Qdrant
- URL: `http://qdrant:6333`
- Colección: `hermes_knowledge`
- Vectores: dense 768 + BM25 sparse (híbrido)
- Tenant activo CEO: `72202fe3-e2e1-4896-a4cb-69acf0d1666c`

## Reglas
- Siempre upsert (no insert) — evitar duplicados por `chunk_id`
- Verificar Ollama disponible antes de embed: `GET http://ollama:11434/api/tags`
