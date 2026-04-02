#!/usr/bin/env python3
"""
seed_qdrant.py — Migra knowledge_base de PostgreSQL a Qdrant.
Indexa todos los docs existentes en la colección fiscal_mx.

Uso:
    python3 scripts/seed_qdrant.py
    python3 scripts/seed_qdrant.py --api-url http://localhost:8000 --token <jwt>
"""

import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.error

# ── Config ────────────────────────────────────────────────────────────────────
DEFAULT_API = os.getenv("API_URL", "http://localhost:8000")
DEFAULT_EMAIL = os.getenv("SEED_EMAIL", "marco@fourgea.mx")
DEFAULT_PASS = os.getenv("SEED_PASSWORD", "Marco2026!")
BATCH_SIZE = 10   # docs por batch (limita latencia de embeddings)


def login(api_url: str, email: str, password: str) -> str:
    payload = json.dumps({"email": email, "password": password}).encode()
    req = urllib.request.Request(
        f"{api_url}/auth/login",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())["access_token"]


def get_knowledge_base(api_url: str, token: str) -> list[dict]:
    """Lee todos los docs de la knowledge_base vía endpoint existente."""
    req = urllib.request.Request(
        f"{api_url}/ai/memory/knowledge",
        headers={"Authorization": f"Bearer {token}"},
    )
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())


def index_batch(api_url: str, token: str, docs: list[dict], context: str) -> dict:
    payload = json.dumps({"docs": docs, "context": context}).encode()
    req = urllib.request.Request(
        f"{api_url}/api/brain/index/batch",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())


def main():
    parser = argparse.ArgumentParser(description="Seed Qdrant desde knowledge_base")
    parser.add_argument("--api-url", default=DEFAULT_API)
    parser.add_argument("--email", default=DEFAULT_EMAIL)
    parser.add_argument("--password", default=DEFAULT_PASS)
    args = parser.parse_args()

    print(f"=== Seed Qdrant — {args.api_url} ===\n")

    # 1. Login
    print("[1/4] Autenticando...")
    try:
        token = login(args.api_url, args.email, args.password)
        print("      Token OK\n")
    except Exception as e:
        print(f"      ERROR login: {e}")
        sys.exit(1)

    # 2. Leer knowledge_base desde PostgreSQL vía API
    print("[2/4] Leyendo knowledge_base...")
    try:
        kb = get_knowledge_base(args.api_url, token)
        print(f"      {len(kb)} docs encontrados\n")
    except Exception as e:
        # Fallback: leer directamente de PostgreSQL si la API no tiene ese endpoint
        print(f"      API endpoint no disponible ({e}), leyendo de PostgreSQL...")
        kb = read_from_postgres()
        if not kb:
            print("      ERROR: no se pudo obtener datos")
            sys.exit(1)
        print(f"      {len(kb)} docs encontrados\n")

    # 3. Preparar docs para Qdrant
    print("[3/4] Preparando documentos...")
    # Mapeo topic → contexto Qdrant (todos van a fiscal_mx por ahora)
    qdrant_docs = []
    for item in kb:
        doc_id = str(item.get("key", item.get("id", "")))
        text = item.get("content", item.get("text", ""))
        title = item.get("title", "")
        topic = item.get("topic", "general")
        source = item.get("source", "knowledge_base")

        if not text or not doc_id:
            continue

        # Enriquecer el texto con el título para mejor retrieval
        full_text = f"{title}\n\n{text}" if title else text

        qdrant_docs.append({
            "id": doc_id,
            "text": full_text,
            "metadata": {
                "topic": topic,
                "title": title,
                "fuente": source,
            },
        })

    print(f"      {len(qdrant_docs)} docs preparados\n")

    # 4. Indexar en batches
    print(f"[4/4] Indexando en Qdrant (batches de {BATCH_SIZE})...")
    total = 0
    errors = 0
    for i in range(0, len(qdrant_docs), BATCH_SIZE):
        batch = qdrant_docs[i:i + BATCH_SIZE]
        batch_num = i // BATCH_SIZE + 1
        total_batches = (len(qdrant_docs) + BATCH_SIZE - 1) // BATCH_SIZE
        print(f"      Batch {batch_num}/{total_batches} ({len(batch)} docs)...", end=" ", flush=True)
        try:
            result = index_batch(args.api_url, token, batch, "fiscal_mx")
            total += result.get("indexed", len(batch))
            print(f"OK ({result.get('indexed', len(batch))} indexados)")
        except urllib.error.HTTPError as e:
            body = e.read().decode()
            print(f"ERROR {e.code}: {body[:100]}")
            errors += 1
        except Exception as e:
            print(f"ERROR: {e}")
            errors += 1
        # Pausa entre batches para no saturar Ollama con embeddings
        if i + BATCH_SIZE < len(qdrant_docs):
            time.sleep(2)

    print(f"\n=== Resultado ===")
    print(f"  Indexados: {total}")
    print(f"  Errores:   {errors}")
    print(f"  Colección: fiscal_mx")
    if errors == 0:
        print("\n✅ Seed completado — Qdrant RAG listo para consultas semánticas")
    else:
        print(f"\n⚠️  Completado con {errors} errores — revisar logs")


def read_from_postgres() -> list[dict]:
    """Fallback: lee directo de PostgreSQL con psycopg2."""
    try:
        import psycopg2
        db_url = os.getenv("DATABASE_URL", "postgresql://mystic_user:MysticSecure2026!@localhost:5433/mystic_db")
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        cur.execute("SELECT id, topic, title, content, source, keywords FROM knowledge_base")
        rows = cur.fetchall()
        conn.close()
        return [
            {"key": str(r[0]), "topic": r[1], "title": r[2], "content": r[3], "source": r[4]}
            for r in rows
        ]
    except Exception as e:
        print(f"      psycopg2 error: {e}")
        return []


if __name__ == "__main__":
    main()
