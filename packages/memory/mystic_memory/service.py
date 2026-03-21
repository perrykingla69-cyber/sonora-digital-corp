from __future__ import annotations

from pathlib import Path
from typing import Any

from .contracts import MemoryDocument, MemoryFeedback, MemorySearchResult, MemoryStats
from .stores import DocumentStore, FeedbackStore, JsonDocumentStore, JsonFeedbackStore, JsonVectorStore, VectorStore


class MemoryService:
    def __init__(
        self,
        data_dir: str | Path = ".data",
        *,
        documents: DocumentStore | None = None,
        feedback: FeedbackStore | None = None,
        vectors: VectorStore | None = None,
    ) -> None:
        data_dir = Path(data_dir)
        data_dir.mkdir(parents=True, exist_ok=True)
        self.documents = documents or JsonDocumentStore(data_dir / "v2_memory_documents.json")
        self.feedback = feedback or JsonFeedbackStore(data_dir / "v2_memory_feedback.json")
        self.vectors = vectors or JsonVectorStore(data_dir / "v2_memory_vectors.json")

    def ingest(self, key: str, text: str, metadata: dict[str, Any] | None = None) -> MemoryDocument:
        document = MemoryDocument(key=key, text=text, metadata=metadata or {})
        self.documents.put(key, document.model_dump())
        self.vectors.add(key, text, metadata=document.metadata)
        return document

    def get_document(self, key: str) -> MemoryDocument | None:
        value = self.documents.get(key)
        if not value:
            return None
        return MemoryDocument(**value)

    def list_documents(self) -> list[MemoryDocument]:
        docs: list[MemoryDocument] = []
        for key in self.documents.keys():
            value = self.documents.get(key)
            if value:
                docs.append(MemoryDocument(**value))
        docs.sort(key=lambda document: document.created_at, reverse=True)
        return docs

    def delete_document(self, key: str) -> bool:
        deleted_doc = self.documents.delete(key)
        deleted_vector = self.vectors.delete(key)
        return deleted_doc or deleted_vector

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
        bucket = self.feedback.get(key, []) or []
        bucket.append(feedback.model_dump())
        self.feedback.put(key, bucket)
        return feedback

    def get_feedback(self, key: str) -> list[MemoryFeedback]:
        bucket = self.feedback.get(key, []) or []
        return [MemoryFeedback(**item) for item in bucket]

    def stats(self) -> MemoryStats:
        feedback_count = 0
        ratings: list[int] = []
        for key in self.feedback.keys():
            bucket = self.feedback.get(key, []) or []
            feedback_count += len(bucket)
            ratings.extend(item["rating"] for item in bucket if isinstance(item, dict) and "rating" in item)

        avg_rating = round(sum(ratings) / len(ratings), 2) if ratings else None
        vectors_count = len(self.vectors.similarity_search("", limit=10_000)) if hasattr(self.vectors, 'similarity_search') else 0
        if hasattr(self.vectors, 'all'):
            vectors_count = len(self.vectors.all())

        return MemoryStats(
            documents=len(self.documents.keys()),
            feedback_items=feedback_count,
            vectors=vectors_count,
            avg_feedback_rating=avg_rating,
        )
