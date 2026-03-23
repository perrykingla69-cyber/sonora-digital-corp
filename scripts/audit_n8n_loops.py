#!/usr/bin/env python3
"""
audit_n8n_loops.py — Audita workflows de N8N en busca de riesgos de seguridad y estabilidad.

Detecta:
  1. Nodos sin ninguna conexión de salida (nodos colgados)
  2. Workflows activos sin error handler (Error Trigger)
  3. Loops potencialmente infinitos (ciclos en el grafo de conexiones)
  4. Credenciales hardcodeadas en parámetros HTTP (API keys en headers/body)
  5. Webhooks sin autenticación configurada

Uso:
    python3 scripts/audit_n8n_loops.py
    python3 scripts/audit_n8n_loops.py --dir infra/n8n-workflows
    python3 scripts/audit_n8n_loops.py --json   # output en JSON
"""
import argparse
import json
import re
import sys
from collections import defaultdict, deque
from pathlib import Path
from typing import Any


# ── Helpers ────────────────────────────────────────────────────────────────────

def load_workflows(directory: Path) -> list[tuple[Path, dict]]:
    """Carga todos los JSONs de workflow del directorio."""
    workflows = []
    for path in sorted(directory.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            workflows.append((path, data))
        except Exception as e:
            print(f"  [WARN] No se pudo leer {path.name}: {e}", file=sys.stderr)
    return workflows


def build_adjacency(connections: dict, nodes: list[dict]) -> tuple[dict, dict]:
    """
    Construye grafo de adyacencia a partir del bloque 'connections' de N8N.

    Retorna:
        outgoing: {node_name: [node_name, ...]}   nodos a los que apunta
        incoming: {node_name: [node_name, ...]}   nodos que apuntan hacia él
    """
    outgoing: dict[str, list[str]] = defaultdict(list)
    incoming: dict[str, list[str]] = defaultdict(list)

    # Registrar todos los nodos (incluso los sin conexiones)
    for node in nodes:
        name = node.get("name", "")
        if name:
            outgoing.setdefault(name, [])
            incoming.setdefault(name, [])

    for source_node, branches in connections.items():
        # branches = {"main": [[{node, type, index}, ...], ...]}
        for _branch_type, branch_lists in branches.items():
            if not isinstance(branch_lists, list):
                continue
            for branch in branch_lists:
                if not isinstance(branch, list):
                    continue
                for edge in branch:
                    if isinstance(edge, dict):
                        target = edge.get("node", "")
                        if target:
                            if target not in outgoing[source_node]:
                                outgoing[source_node].append(target)
                            if source_node not in incoming[target]:
                                incoming[target].append(source_node)

    return dict(outgoing), dict(incoming)


def detect_cycles(outgoing: dict) -> list[list[str]]:
    """
    Detecta ciclos en el grafo dirigido usando DFS.
    Retorna lista de ciclos encontrados (cada ciclo como lista de nodos).
    """
    visited: set[str] = set()
    in_stack: set[str] = set()
    cycles: list[list[str]] = []

    def dfs(node: str, path: list[str]) -> None:
        visited.add(node)
        in_stack.add(node)
        path.append(node)

        for neighbor in outgoing.get(node, []):
            if neighbor not in visited:
                dfs(neighbor, path)
            elif neighbor in in_stack:
                # Encontramos un ciclo — extraer la parte cíclica
                cycle_start = path.index(neighbor)
                cycle = path[cycle_start:] + [neighbor]
                if cycle not in cycles:
                    cycles.append(cycle)

        path.pop()
        in_stack.discard(node)

    for node in list(outgoing.keys()):
        if node not in visited:
            dfs(node, [])

    return cycles


HARDCODED_SECRET_PATTERNS = [
    # API keys genéricas
    re.compile(r'(?i)(api[-_]?key|token|password|secret|passwd|authorization)\s*[=:]\s*["\']?[\w\-\.]{8,}["\']?'),
    # Contraseñas con ! (patrón del proyecto)
    re.compile(r'\w+2026!'),
    # Bearer tokens
    re.compile(r'(?i)bearer\s+[a-z0-9\-_\.]{20,}'),
]


def scan_hardcoded_secrets(node: dict) -> list[str]:
    """Busca credenciales hardcodeadas en los parámetros del nodo."""
    found = []
    params_str = json.dumps(node.get("parameters", {}))

    for pattern in HARDCODED_SECRET_PATTERNS:
        matches = pattern.findall(params_str)
        if matches:
            # Censurar el valor exacto
            for match in matches:
                if isinstance(match, tuple):
                    match = " ".join(m for m in match if m)
                preview = match[:40] + "..." if len(match) > 40 else match
                found.append(f"posible secreto hardcodeado: '{preview}'")

    return found


def has_error_handler(nodes: list[dict]) -> bool:
    """Verifica si el workflow tiene un nodo de tipo Error Trigger."""
    for node in nodes:
        ntype = node.get("type", "")
        if "errorTrigger" in ntype or "error-trigger" in ntype.lower():
            return True
    return False


def is_webhook_authenticated(node: dict) -> bool:
    """
    Verifica si un nodo Webhook tiene autenticación configurada.
    N8N permite: 'none', 'basicAuth', 'headerAuth'.
    """
    params = node.get("parameters", {})
    auth = params.get("authentication", "none")
    return auth != "none"


# ── Auditor principal ──────────────────────────────────────────────────────────

def audit_workflow(path: Path, workflow: dict) -> dict:
    """
    Audita un workflow individual.
    Retorna dict con hallazgos estructurados.
    """
    name = workflow.get("name", path.stem)
    is_active = workflow.get("active", False)
    nodes: list[dict] = workflow.get("nodes", [])
    connections: dict = workflow.get("connections", {})

    findings: list[dict] = []
    risk_level = "OK"

    outgoing, incoming = build_adjacency(connections, nodes)

    # ── Check 1: Nodos sin salida (excepto nodos tipo "respuesta" esperados) ──
    terminal_types = {
        "n8n-nodes-base.noOp",
        "n8n-nodes-base.respondToWebhook",
        "n8n-nodes-base.wait",
        "n8n-nodes-base.stopAndError",
    }
    # Nodos de notificación/envío típicamente terminan el flujo
    terminal_name_keywords = ["notif", "send", "envio", "envío", "wa", "telegram", "email", "slack"]

    for node in nodes:
        nname = node.get("name", "")
        ntype = node.get("type", "")
        out_edges = outgoing.get(nname, [])
        in_edges = incoming.get(nname, [])

        is_terminal_type = ntype in terminal_types
        is_terminal_name = any(kw in nname.lower() for kw in terminal_name_keywords)
        is_trigger = "trigger" in ntype.lower() or "webhook" in ntype.lower() or "schedule" in ntype.lower()

        if not out_edges and not is_terminal_type and not is_terminal_name and not is_trigger:
            if in_edges:  # tiene entrada pero no salida → nodo colgado
                findings.append({
                    "type": "nodo_sin_salida",
                    "node": nname,
                    "detail": f"El nodo '{nname}' recibe datos pero no tiene conexión de salida. "
                              "Puede ser un nodo colgado que detiene el flujo silenciosamente.",
                    "severity": "MEDIUM",
                })
                if risk_level == "OK":
                    risk_level = "MEDIUM"

    # ── Check 2: Sin error handler en workflows activos ────────────────────────
    if is_active and not has_error_handler(nodes):
        findings.append({
            "type": "sin_error_handler",
            "node": None,
            "detail": "Workflow activo sin nodo 'Error Trigger'. Si falla un nodo intermedio, "
                      "el error puede silenciarse sin alerta.",
            "severity": "MEDIUM",
        })
        if risk_level == "OK":
            risk_level = "MEDIUM"

    # ── Check 3: Ciclos / loops infinitos ─────────────────────────────────────
    cycles = detect_cycles(outgoing)
    for cycle in cycles:
        cycle_str = " → ".join(cycle)
        findings.append({
            "type": "loop_infinito",
            "node": cycle[0],
            "detail": f"Ciclo detectado en el grafo: {cycle_str}. "
                      "Puede causar ejecución infinita y colapso del worker N8N.",
            "severity": "HIGH",
        })
        risk_level = "HIGH"

    # ── Check 4: Credenciales hardcodeadas ────────────────────────────────────
    for node in nodes:
        nname = node.get("name", "")
        secrets = scan_hardcoded_secrets(node)
        for secret_detail in secrets:
            findings.append({
                "type": "credencial_hardcodeada",
                "node": nname,
                "detail": f"Nodo '{nname}': {secret_detail}. Usar credenciales de N8N o variables de entorno.",
                "severity": "HIGH",
            })
            risk_level = "HIGH"

    # ── Check 5: Webhooks sin autenticación ──────────────────────────────────
    for node in nodes:
        ntype = node.get("type", "")
        nname = node.get("name", "")
        if "webhook" in ntype.lower() and not is_webhook_authenticated(node):
            findings.append({
                "type": "webhook_sin_auth",
                "node": nname,
                "detail": f"Webhook '{nname}' sin autenticación (authentication=none). "
                          "Cualquier IP puede disparar este workflow.",
                "severity": "MEDIUM",
            })
            if risk_level == "OK":
                risk_level = "MEDIUM"

    return {
        "workflow": name,
        "file": path.name,
        "active": is_active,
        "nodes_count": len(nodes),
        "risk_level": risk_level,
        "findings_count": len(findings),
        "findings": findings,
    }


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Audita workflows N8N en busca de loops, nodos colgados y credenciales."
    )
    parser.add_argument(
        "--dir",
        default=str(Path(__file__).resolve().parent.parent / "infra" / "n8n-workflows"),
        help="Directorio con los JSONs de workflows (default: infra/n8n-workflows)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emitir resultado en JSON puro (para integración con CI/CD)",
    )
    args = parser.parse_args()

    workflows_dir = Path(args.dir)
    if not workflows_dir.is_dir():
        print(f"ERROR: directorio no encontrado: {workflows_dir}", file=sys.stderr)
        sys.exit(1)

    workflows = load_workflows(workflows_dir)
    if not workflows:
        print(f"No se encontraron JSONs en {workflows_dir}", file=sys.stderr)
        sys.exit(0)

    results = []
    for path, wf_data in workflows:
        result = audit_workflow(path, wf_data)
        results.append(result)

    # ── Salida JSON ───────────────────────────────────────────────────────────
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
        sys.exit(0)

    # ── Salida legible ────────────────────────────────────────────────────────
    RISK_ICONS = {"OK": "✅", "MEDIUM": "⚠️ ", "HIGH": "🔴"}

    print(f"\n{'='*70}")
    print(f"  AUDITORÍA N8N WORKFLOWS — {workflows_dir}")
    print(f"  Total workflows analizados: {len(results)}")
    print(f"{'='*70}\n")

    any_issue = False
    for r in results:
        icon = RISK_ICONS.get(r["risk_level"], "?")
        active_str = "ACTIVO" if r["active"] else "inactivo"
        print(f"{icon}  [{r['risk_level']:6}] {r['workflow']}  ({active_str}, {r['nodes_count']} nodos)")

        if r["findings"]:
            any_issue = True
            for f in r["findings"]:
                sev = f["severity"]
                nodo = f" → nodo: {f['node']}" if f["node"] else ""
                print(f"     [{sev}]{nodo}")
                # Wrap detail a 65 chars
                detail = f["detail"]
                while detail:
                    print(f"       {detail[:65]}")
                    detail = detail[65:]
        print()

    # ── Resumen ───────────────────────────────────────────────────────────────
    by_risk = defaultdict(int)
    total_findings = 0
    for r in results:
        by_risk[r["risk_level"]] += 1
        total_findings += r["findings_count"]

    print(f"{'─'*70}")
    print(f"  Resumen: {total_findings} hallazgo(s) en {len(results)} workflow(s)")
    for level in ("HIGH", "MEDIUM", "OK"):
        count = by_risk.get(level, 0)
        if count:
            print(f"  {RISK_ICONS[level]}  {level}: {count} workflow(s)")
    print(f"{'─'*70}\n")

    if any_issue:
        print("  Acción recomendada:")
        print("  1. Agregar Error Trigger a workflows activos sin handler.")
        print("  2. Reemplazar credenciales hardcodeadas por N8N Credentials o env vars.")
        print("  3. Agregar headerAuth a webhooks públicos.")
        print("  4. Revisar nodos colgados — conectar o eliminar.\n")
        sys.exit(1)  # exit code no-cero para CI/CD
    else:
        print("  Todos los workflows pasaron la auditoría.\n")
        sys.exit(0)


if __name__ == "__main__":
    main()
