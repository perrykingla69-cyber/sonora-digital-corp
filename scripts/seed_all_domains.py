#!/usr/bin/env python3
"""
seed_all_domains.py — Maestro que ejecuta todos los seeds en orden

Ejecución: Fiscal → Food → Legal → Architecture → Ops
Resultado: 5 colecciones en Qdrant, listas para RAG

Uso:
    cd /home/mystic/hermes-os
    python3 scripts/seed_all_domains.py

Verificar después:
    curl http://localhost:6333/collections | jq .
"""

import asyncio
import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime

# ── Scripts a ejecutar ────────────────────────────────────────────────────────
SEED_SCRIPTS = [
    "seed_fiscal_regulations.py",
    "seed_food_regulations.py",
    "seed_legal_regulations.py",
    "seed_architecture_patterns.py",
    "seed_ops_best_practices.py",
]

COLLECTIONS = {
    "seed_fiscal_regulations.py": "fiscal-regulations",
    "seed_food_regulations.py": "food-regulations",
    "seed_legal_regulations.py": "legal-regulations",
    "seed_architecture_patterns.py": "architecture-patterns",
    "seed_ops_best_practices.py": "ops-best-practices",
}

def print_header(text: str):
    """Imprime encabezado."""
    print(f"\n{'=' * 80}")
    print(f"  {text}")
    print(f"{'=' * 80}\n")

def run_script(script_name: str) -> bool:
    """Ejecuta un script de seed individual."""
    script_path = Path(__file__).parent / script_name
    collection = COLLECTIONS[script_name]

    print(f"▶ Ejecutando: {script_name}")
    print(f"  Colección: {collection}")
    print(f"  Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    try:
        result = subprocess.run(
            ["python3", str(script_path)],
            capture_output=False,
            text=True,
            timeout=600  # 10 minutos máximo por script
        )

        if result.returncode == 0:
            print(f"\n✓ {script_name} completado exitosamente")
            return True
        else:
            print(f"\n✗ {script_name} falló con código {result.returncode}")
            return False

    except subprocess.TimeoutExpired:
        print(f"\n✗ {script_name} excedió timeout (10 min)")
        return False
    except Exception as e:
        print(f"\n✗ Error ejecutando {script_name}: {e}")
        return False

async def verify_collections(qdrant_url: str = "http://localhost:6333") -> dict:
    """Verifica colecciones creadas en Qdrant."""
    import httpx

    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{qdrant_url}/collections")
            r.raise_for_status()
            data = r.json()

            collections = {}
            for coll in data.get("collections", []):
                collections[coll["name"]] = {
                    "vectors_count": coll["vectors_count"],
                    "points_count": coll["points_count"],
                }
            return collections
    except Exception as e:
        print(f"Error verificando colecciones: {e}")
        return {}

def main():
    print_header("SEED ALL DOMAINS — Poblar Qdrant con Regulaciones & Patrones")

    print("Flujo de ejecución:")
    for i, script in enumerate(SEED_SCRIPTS, 1):
        print(f"  {i}. {script}")

    print("\nInicio:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    start_time = time.time()
    results = {}
    failed_scripts = []

    for i, script in enumerate(SEED_SCRIPTS, 1):
        print_header(f"[{i}/{len(SEED_SCRIPTS)}] {script}")

        success = run_script(script)
        results[script] = success

        if not success:
            failed_scripts.append(script)

        # Sleep 2s entre scripts (dar tiempo a procesamiento)
        if i < len(SEED_SCRIPTS):
            time.sleep(2)

    # Verificar colecciones
    print_header("VERIFICACIÓN FINAL")

    try:
        collections = asyncio.run(verify_collections())

        print(f"Colecciones en Qdrant ({len(collections)} total):\n")
        total_vectors = 0
        total_points = 0

        for script in SEED_SCRIPTS:
            collection = COLLECTIONS[script]
            if collection in collections:
                info = collections[collection]
                status = "✓" if results.get(script) else "?"
                print(f"  {status} {collection}")
                print(f"      Vectores: {info['vectors_count']}")
                print(f"      Puntos: {info['points_count']}\n")
                total_vectors += info["vectors_count"]
                total_points += info["points_count"]
            else:
                print(f"  ✗ {collection} (NO ENCONTRADA)\n")

    except Exception as e:
        print(f"No se pudo verificar colecciones: {e}\n")

    # Resumen
    print_header("RESUMEN EJECUCIÓN")

    total_time = time.time() - start_time
    passed = sum(1 for v in results.values() if v)
    failed = len(results) - passed

    print(f"Scripts ejecutados: {len(results)}")
    print(f"  ✓ Exitosos: {passed}")
    print(f"  ✗ Fallidos: {failed}")

    if failed_scripts:
        print(f"\nScripts con problemas:")
        for script in failed_scripts:
            print(f"  - {script}")

    print(f"\nTiempo total: {total_time:.1f} segundos ({total_time/60:.1f} minutos)")
    print(f"Fin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    print_header("PRÓXIMOS PASOS")

    print("1. Verificar colecciones manualmente:")
    print("   curl http://localhost:6333/collections | jq .\n")

    print("2. Hacer búsqueda de prueba (RAG):")
    print("   curl -X POST http://localhost:8000/api/brain/search \\")
    print("     -H 'Authorization: Bearer <token>' \\")
    print("     -d '{\"query\": \"¿Cuáles son los requisitos NOM-251?\"}'")
    print()

    print("3. Verificar que HERMES puede usar RAG:")
    print("   En Telegram CEO bot: /chat ¿Qué normas aplican a restaurantes?\n")

    return 0 if failed == 0 else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
