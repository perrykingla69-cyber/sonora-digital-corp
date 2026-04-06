# agent:hermes — Orquestador HERMES
> Carga solo este archivo. Para contexto cross-dominio: `mem_search "hermes agent rag"` en Engram.

## Dominio
Agente IA principal. Polling Telegram. Consulta RAG en Qdrant antes de responder.
Modelo: `google/gemini-2.0-flash-001` vía OpenRouter.

## Archivo clave
- `agent.py` — polling loop, consulta RAG, llama OpenRouter, responde

## Reglas críticas
- **Nunca** responde sin pasar por RAG — siempre citar fuente: `(Fuente: NOM-251, 2024)`
- Nunca inventa artículos, leyes, montos ni fechas
- Usa `delete_webhook()` antes de iniciar polling (evita conflicto 409)
- Modelo: `OPENROUTER_API_KEY` → `google/gemini-2.0-flash-001`
- RAG: Qdrant colección `hermes_knowledge`, tenant-aware por `tenant_id`

## Flujo RAG
```
mensaje_usuario
  → embed con nomic-embed-text (Ollama :11434)
  → búsqueda Qdrant híbrida (dense 768 + BM25)
  → contexto → OpenRouter → respuesta con fuente
```
