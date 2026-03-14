#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "[1/4] Initializing memory subsystem..."
python - <<'PY'
from memory.task_history import TaskHistory
from memory.knowledge_store import KnowledgeStore
from memory.vector_memory import VectorMemory

TaskHistory()
KnowledgeStore()
VectorMemory()
print("Memory initialized")
PY

echo "[2/4] Loading skills config..."
python - <<'PY'
from pathlib import Path


def count_named_items(path: Path) -> int:
    return sum(1 for line in path.read_text().splitlines() if line.strip().startswith('- name:'))

print(f"Loaded {count_named_items(Path('configs/skills.yaml'))} skills")
PY

echo "[3/4] Loading agents config..."
python - <<'PY'
from pathlib import Path


def count_named_items(path: Path) -> int:
    return sum(1 for line in path.read_text().splitlines() if line.strip().startswith('- name:'))

print(f"Loaded {count_named_items(Path('configs/agents.yaml'))} agents")
PY

echo "[4/4] Starting orchestrator..."
python - <<'PY'
from orchestrator.orchestrator import Orchestrator

orchestrator = Orchestrator()
print("Orchestrator started:", orchestrator.__class__.__name__)
PY
