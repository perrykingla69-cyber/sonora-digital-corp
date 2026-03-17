"""Analysis skill — text analysis, keyword extraction, summarization via Ollama."""

from __future__ import annotations

import re
import json
import urllib.request
from collections import Counter
from typing import Any

from skills.base_skill import BaseSkill

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "phi3:mini"


class Skill(BaseSkill):
    name = "analysis"
    description = "Analyze text: stats, keywords, summarize (local Ollama or extractive fallback)."

    def execute(self, action: str = "stats", **kwargs: Any) -> Any:
        """
        Actions:
            stats      — word/sentence/char counts + avg word length (text)
            keywords   — top N keywords by TF (text, top_n=10)
            summarize  — summarize text via Ollama or extractive fallback (text, sentences=3)
            classify   — classify text into a category (text, categories=list[str])
            ask        — ask Ollama a free-form question (prompt, model=phi3:mini)
        """
        action = action.lower()

        if action == "stats":
            return self._stats(kwargs["text"])

        if action == "keywords":
            return self._keywords(kwargs["text"], int(kwargs.get("top_n", 10)))

        if action == "summarize":
            return self._summarize(kwargs["text"], int(kwargs.get("sentences", 3)))

        if action == "classify":
            return self._classify(kwargs["text"], kwargs.get("categories", []))

        if action == "ask":
            return self._ollama(kwargs["prompt"], kwargs.get("model", OLLAMA_MODEL))

        raise ValueError(f"Unknown action '{action}'. Valid: stats, keywords, summarize, classify, ask")

    # ------------------------------------------------------------------

    def _stats(self, text: str) -> dict:
        words = re.findall(r"\b\w+\b", text)
        sentences = re.split(r"[.!?]+", text)
        sentences = [s.strip() for s in sentences if s.strip()]
        return {
            "chars": len(text),
            "words": len(words),
            "sentences": len(sentences),
            "paragraphs": len([p for p in text.split("\n\n") if p.strip()]),
            "avg_word_length": round(sum(len(w) for w in words) / max(len(words), 1), 2),
            "unique_words": len(set(w.lower() for w in words)),
        }

    def _keywords(self, text: str, top_n: int = 10) -> list[dict]:
        STOPWORDS = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
            "of", "with", "by", "from", "is", "was", "are", "were", "be", "been",
            "that", "this", "it", "he", "she", "they", "we", "you", "i", "my",
            "de", "la", "el", "en", "los", "las", "un", "una", "que", "es", "se",
            "no", "si", "por", "con", "del", "al", "su", "sus",
        }
        words = re.findall(r"\b[a-zA-ZáéíóúüñÁÉÍÓÚÜÑ]{3,}\b", text.lower())
        filtered = [w for w in words if w not in STOPWORDS]
        counter = Counter(filtered)
        return [{"keyword": kw, "count": count} for kw, count in counter.most_common(top_n)]

    def _summarize(self, text: str, sentences: int = 3) -> dict:
        # Try Ollama first
        try:
            prompt = (
                f"Summarize the following text in {sentences} sentences. "
                f"Be concise and factual.\n\nText:\n{text[:3000]}"
            )
            summary = self._ollama(prompt)
            return {"method": "ollama", "summary": summary, "model": OLLAMA_MODEL}
        except Exception:
            pass

        # Extractive fallback: score sentences by keyword density
        sents = re.split(r"[.!?]+", text)
        sents = [s.strip() for s in sents if len(s.strip()) > 30]
        if not sents:
            return {"method": "extractive", "summary": text[:500]}

        keywords = {item["keyword"] for item in self._keywords(text, top_n=15)}
        scored = []
        for i, sent in enumerate(sents):
            words = set(re.findall(r"\b\w+\b", sent.lower()))
            score = len(words & keywords) + (1 if i < 3 else 0)  # favor early sentences
            scored.append((score, i, sent))

        top = sorted(scored, reverse=True)[:sentences]
        top_sorted = sorted(top, key=lambda x: x[1])  # restore original order
        summary = ". ".join(t[2] for t in top_sorted) + "."
        return {"method": "extractive", "summary": summary}

    def _classify(self, text: str, categories: list[str]) -> dict:
        if not categories:
            raise ValueError("Provide at least one category")
        try:
            prompt = (
                f"Classify the following text into exactly one of these categories: "
                f"{', '.join(categories)}.\n"
                f"Reply with only the category name.\n\nText:\n{text[:2000]}"
            )
            category = self._ollama(prompt).strip()
            return {"category": category, "method": "ollama"}
        except Exception:
            # Fallback: keyword match
            text_lower = text.lower()
            for cat in categories:
                if cat.lower() in text_lower:
                    return {"category": cat, "method": "keyword_match"}
            return {"category": categories[0], "method": "default_fallback"}

    def _ollama(self, prompt: str, model: str = OLLAMA_MODEL) -> str:
        payload = json.dumps({"model": model, "prompt": prompt, "stream": False}).encode()
        req = urllib.request.Request(
            OLLAMA_URL,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read())
        return data.get("response", "").strip()
