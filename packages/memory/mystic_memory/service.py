from __future__ import annotations

from pathlib import Path
from typing import Any

from backend.app.ai.memory import KnowledgeStore, VectorMemory

from .contracts import MemoryDocument, MemoryFeedback, MemorySearchResult


class MemoryService:
    def __init__(self, data_dir: str | Path = ".data") -> None:
        data_dir = Path(data_dir)
        data_dir.mkdir(parents=True, exist_ok=True)
        self.documents = KnowledgeStore(str(data_dir / "v2_memory_documents.json"))
        self.feedback = KnowledgeStore(str(data_dir / "v2_memory_feedback.json"))
        self.vectors = VectorMemory(str(data_dir / "v2_memory_vectors.json"))

    def ingest(self, key: str, text: str, metadata: dict[str, Any] | None = None) -> MemoryDocument:
        document = MemoryDocument(key=key, text=text, metadata=metadata or {})
        self.documents.put(key, document.model_dump())
        self.vectors.add(key, text, metadata=document.metadata)
        return document

    def list_documents(self) -> list[MemoryDocument]:
        docs: list[MemoryDocument] = []
        for key in self.documents.keys():
            value = self.documents.get(key)
            if value:
                docs.append(MemoryDocument(**value))
        docs.sort(key=lambda document: document.created_at, reverse=True)
        return docs

    def search(self, query: str, limit: int = 5) -> list[MemorySearchResult]:
        results = self.vectors.similarity_search(query, limit=limit)
        needle = query.strip().lower()
        return [
            MemorySearchResult(
                key=record.key,
                text=record.text,
                metadata=record.metadata,
                score=1.0 if needle and needle in record.text.lower() else None,
            )
            for record in results
        ]

    def save_feedback(self, key: str, rating: int, comment: str | None = None) -> MemoryFeedback:
        feedback = MemoryFeedback(key=key, rating=rating, comment=comment)
        bucket = self.feedback.get(key, [])
        bucket.append(feedback.model_dump())
        self.feedback.put(key, bucket)
        return feedback

    def get_feedback(self, key: str) -> list[MemoryFeedback]:
        bucket = self.feedback.get(key, [])
        return [MemoryFeedback(**item) for item in bucket]
