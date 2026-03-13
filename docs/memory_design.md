# Memory Design

## Components
- `TaskHistory`: append-only execution trace.
- `KnowledgeStore`: lightweight key-value facts and artifacts.
- `VectorMemory`: embedding-ready semantic memory abstraction.

## Data Flow
1. Task enters orchestrator and is assigned.
2. Agent execution result is recorded in task history.
3. Important outputs are persisted to knowledge store.
4. Textual artifacts are indexed in vector memory for retrieval.

## Future Work
- Pluggable vector backend (FAISS/pgvector/etc.).
- Memory TTL and compaction policy.
- Cross-agent memory permissions.
