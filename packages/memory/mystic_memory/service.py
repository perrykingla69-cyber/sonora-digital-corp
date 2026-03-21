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

    def ingest(
        self,
        key: str,
        text: str,
        metadata: dict[str, Any] | None = None,
        *,
        tenant_id: str | None = None,
        kind: str | None = None,
    ) -> MemoryDocument:
        clean_metadata = dict(metadata or {})
        if tenant_id and "tenant_id" not in clean_metadata:
            clean_metadata["tenant_id"] = tenant_id
        if kind and "kind" not in clean_metadata:
            clean_metadata["kind"] = kind

        document = MemoryDocument(
            key=key,
            text=text,
            tenant_id=tenant_id or clean_metadata.get("tenant_id"),
            kind=kind or clean_metadata.get("kind"),
            metadata=clean_metadata,
        )
        self.documents.put(key, document.model_dump())
        self.vectors.add(key, text, metadata=document.metadata)
        return document

    def get_document(self, key: str) -> MemoryDocument | None:
        value = self.documents.get(key)
        if not value:
            return None
        return MemoryDocument(**value)

    def list_documents(self, *, tenant_id: str | None = None, kind: str | None = None, source: str | None = None) -> list[MemoryDocument]:
        docs: list[MemoryDocument] = []
        for key in self.documents.keys():
            value = self.documents.get(key)
            if not value:
                continue
            document = MemoryDocument(**value)
            if not self._matches_filters(document, tenant_id=tenant_id, kind=kind, source=source):
                continue
            docs.append(document)
        docs.sort(key=lambda document: document.created_at, reverse=True)
        return docs

    def delete_document(self, key: str) -> bool:
        deleted_doc = self.documents.delete(key)
        deleted_vector = self.vectors.delete(key)
        return deleted_doc or deleted_vector

    def search(
        self,
        query: str,
        limit: int = 5,
        *,
        tenant_id: str | None = None,
        kind: str | None = None,
        source: str | None = None,
    ) -> list[MemorySearchResult]:
        results = self.vectors.similarity_search(query, limit=max(limit * 5, limit))
        needle = query.strip().lower()
        filtered: list[MemorySearchResult] = []
        for record in results:
            document = self.get_document(record.key)
            metadata = document.metadata if document else record.metadata
            result = MemorySearchResult(
                key=record.key,
                text=record.text,
                tenant_id=document.tenant_id if document else metadata.get("tenant_id"),
                kind=document.kind if document else metadata.get("kind"),
                metadata=metadata,
                score=1.0 if needle and needle in record.text.lower() else None,
            )
            if not self._matches_filters(result, tenant_id=tenant_id, kind=kind, source=source):
                continue
            filtered.append(result)
            if len(filtered) >= limit:
                break
        return filtered

    def save_feedback(self, key: str, rating: int, comment: str | None = None) -> MemoryFeedback:
        feedback = MemoryFeedback(key=key, rating=rating, comment=comment)
        bucket = self.feedback.get(key, []) or []
        bucket.append(feedback.model_dump())
        self.feedback.put(key, bucket)
        return feedback

    def get_feedback(self, key: str) -> list[MemoryFeedback]:
        bucket = self.feedback.get(key, []) or []
        return [MemoryFeedback(**item) for item in bucket]

    def stats(self, *, tenant_id: str | None = None) -> MemoryStats:
        documents = self.list_documents(tenant_id=tenant_id)
        doc_keys = {document.key for document in documents}
        feedback_count = 0
        ratings: list[int] = []
        for key in self.feedback.keys():
            if tenant_id and key not in doc_keys:
                continue
            bucket = self.feedback.get(key, []) or []
            feedback_count += len(bucket)
            ratings.extend(item["rating"] for item in bucket if isinstance(item, dict) and "rating" in item)

        avg_rating = round(sum(ratings) / len(ratings), 2) if ratings else None
        vectors_count = len(doc_keys)

        return MemoryStats(
            documents=len(documents),
            feedback_items=feedback_count,
            vectors=vectors_count,
            avg_feedback_rating=avg_rating,
        )

    @staticmethod
    def _matches_filters(item: MemoryDocument | MemorySearchResult, *, tenant_id: str | None, kind: str | None, source: str | None) -> bool:
        if tenant_id and item.tenant_id != tenant_id and item.metadata.get("tenant_id") != tenant_id:
            return False
        if kind and item.kind != kind and item.metadata.get("kind") != kind:
            return False
        if source and item.metadata.get("source") != source:
            return False
        return True
