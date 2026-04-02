#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "========================================"
echo "  MYSTIC AI Operating System Bootstrap  "
echo "========================================"

echo ""
echo "[1/5] Checking Python version..."
python3 --version

echo ""
echo "[2/5] Installing dependencies..."
pip install -q -r requirements.txt

echo ""
echo "[3/5] Initializing memory subsystem..."
python3 - <<'PY'
import sys
sys.path.insert(0, '.')
from memory import TaskHistory, KnowledgeStore, VectorMemory

th = TaskHistory()
ks = KnowledgeStore()
vm = VectorMemory()
print(f"  TaskHistory   : OK")
print(f"  KnowledgeStore: OK")
print(f"  VectorMemory  : OK")
PY

echo ""
echo "[4/5] Loading skill + agent configs..."
python3 - <<'PY'
import sys, yaml
sys.path.insert(0, '.')
from pathlib import Path

skills = yaml.safe_load(Path('configs/skills.yaml').read_text())
agents = yaml.safe_load(Path('configs/agents.yaml').read_text())
print(f"  Skills loaded : {[s['name'] for s in skills['skills']]}")
print(f"  Agents loaded : {[a['name'] for a in agents['agents']]}")
PY

echo ""
echo "[5/5] Starting orchestrator..."
python3 - <<'PY'
import sys
sys.path.insert(0, '.')
from orchestrator import Orchestrator

orch = Orchestrator.from_config('configs/agents.yaml', 'configs/skills.yaml')
status = orch.status()
print(f"  Agents  : {status['agents']}")
print(f"  Skills  : {status['skills']}")
print(f"  Status  : READY")
PY

echo ""
echo "========================================"
echo "  System started successfully"
echo "========================================"
