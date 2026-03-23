#!/usr/bin/env python3
"""MYSTIC CLI — Herramienta operativa para Sonora Digital Corp"""
import argparse, json, os, subprocess, sys, time, urllib.error, urllib.request
from pathlib import Path

API_URL = os.getenv("MYSTIC_API_URL", "http://localhost:8000")
EMAIL = os.getenv("MYSTIC_EMAIL", "")
PASSWORD = os.getenv("MYSTIC_PASSWORD", "")
TOKEN = os.getenv("MYSTIC_TOKEN", "")
REPO_ROOT = Path(__file__).resolve().parent.parent.parent

def _request(method, path, data=None, token=None, timeout=15):
    url = f"{API_URL}{path}"
    body = json.dumps(data).encode() if data else None
    headers = {"Content-Type": "application/json"}
    if token: headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        print(f"[error] HTTP {e.code}: {e.read().decode()[:200]}"); sys.exit(1)
    except Exception as exc:
        print(f"[error] {exc}"); sys.exit(1)

def _get_token():
    global TOKEN
    if TOKEN: return TOKEN
    if not EMAIL or not PASSWORD:
        print("[error] Configura MYSTIC_EMAIL + MYSTIC_PASSWORD o MYSTIC_TOKEN"); sys.exit(1)
    resp = _request("POST", "/auth/login", {"email": EMAIL, "password": PASSWORD})
    TOKEN = resp.get("access_token", ""); return TOKEN

def _ok(m): print(f"  \033[32m✓\033[0m  {m}")
def _err(m): print(f"  \033[31m✗\033[0m  {m}")
def _info(m): print(f"  \033[34m•\033[0m  {m}")
def _h(t): print(f"\n\033[1m{t}\033[0m")

def cmd_status(args):
    _h("Estado del sistema MYSTIC")
    try:
        resp = _request("GET", "/status", timeout=5)
        _ok(f"API  {API_URL}  — {resp.get('status', 'ok')}")
    except SystemExit: _err(f"API  {API_URL}  — sin respuesta")
    services = ["mystic_api","mystic_frontend","mystic_bot","mystic_wa","mystic_postgres","mystic_redis","mystic_ollama","mystic_qdrant","mystic_n8n"]
    try:
        result = subprocess.run(["docker","ps","--format","{{.Names}}\t{{.Status}}"], capture_output=True, text=True, timeout=5)
        running = dict(l.split("\t",1) for l in result.stdout.strip().splitlines() if "\t" in l)
        for svc in services:
            status = running.get(svc)
            if status: _ok(f"Docker  {svc}  — {status[:40]}")
            else: _err(f"Docker  {svc}  — no encontrado")
    except Exception: _info("Docker no disponible en este entorno")

def cmd_brain_ask(args):
    query = " ".join(args.query)
    _h(f"Brain IA — {query[:60]}")
    token = _get_token()
    t0 = time.time()
    resp = _request("POST", "/api/brain/ask", {"query": query}, token=token, timeout=30)
    ms = (time.time() - t0) * 1000
    print(f"\n{resp.get('answer', resp.get('response', ''))}\n")
    sources = resp.get("sources", [])
    if sources: _info(f"Fuentes: {', '.join(str(s) for s in sources[:3])}")
    _info(f"Latencia: {ms:.0f}ms")

def cmd_seed(args):
    seeds = {"fiscal": "scripts/seed_fiscal_completo.py", "dof": "scripts/seed_dof_auto.py", "fourgea": "scripts/seed_fourgea_docs.py", "legal": "scripts/seed_legal_mve.py", "knowledge": "scripts/seed_knowledge.py", "qdrant": "scripts/seed_qdrant.py"}
    tipo = args.tipo
    if tipo == "list":
        _h("Seeds disponibles")
        for k, v in seeds.items():
            exists = (REPO_ROOT / v).exists()
            print(f"  {'✓' if exists else '✗'}  {k:<12} {v}")
        return
    if tipo not in seeds:
        print(f"[error] Tipo desconocido. Usa: {', '.join(seeds)}, list"); sys.exit(1)
    script = REPO_ROOT / seeds[tipo]
    if not script.exists():
        print(f"[error] Script no encontrado: {script}"); sys.exit(1)
    _h(f"Ejecutando seed: {tipo}")
    os.execv(sys.executable, [sys.executable, str(script)])

def cmd_logs(args):
    svc_map = {"api":"mystic_api","bot":"mystic_bot","frontend":"mystic_frontend","whatsapp":"mystic_wa","n8n":"mystic_n8n","qdrant":"mystic_qdrant","ollama":"mystic_ollama"}
    container = svc_map.get(args.servicio or "api", args.servicio or "mystic_api")
    lines = str(getattr(args, "lines", 50) or 50)
    _h(f"Logs — {container} (últimas {lines} líneas)")
    try: subprocess.run(["docker","logs","--tail",lines,"-f",container])
    except KeyboardInterrupt: pass
    except FileNotFoundError: print("[error] docker no disponible"); sys.exit(1)

def cmd_deploy_check(args):
    _h("Validación pre-deploy"); errors = 0
    branch = subprocess.run(["git","branch","--show-current"], capture_output=True,text=True,cwd=REPO_ROOT).stdout.strip()
    (_ok if branch == "main" else _err)(f"Rama: {branch}")
    if branch != "main": errors += 1
    dirty = subprocess.run(["git","status","--porcelain"], capture_output=True,text=True,cwd=REPO_ROOT).stdout.strip()
    if not dirty: _ok("Working tree limpio")
    else: _err("Cambios sin commitear"); errors += 1
    subprocess.run(["git","fetch","origin"],capture_output=True,cwd=REPO_ROOT)
    behind = subprocess.run(["git","rev-list","HEAD..origin/main","--count"], capture_output=True,text=True,cwd=REPO_ROOT).stdout.strip()
    (_ok if behind == "0" else _err)(f"Sync con origin/main: {behind} commits detrás")
    if behind != "0": errors += 1
    print(); 
    if errors == 0: _ok("Listo para deploy")
    else: _err(f"{errors} problema(s) — corrige antes de deploy"); sys.exit(1)

def main():
    global API_URL
    p = argparse.ArgumentParser(prog="mystic", description="MYSTIC CLI")
    p.add_argument("--api-url", default=API_URL)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status")
    seed = sub.add_parser("seed"); seed.add_argument("tipo", nargs="?", default="list")
    logs = sub.add_parser("logs")
    logs.add_argument("servicio", nargs="?")
    logs.add_argument("-n","--lines", type=int, default=50)
    deploy = sub.add_parser("deploy")
    deploy_sub = deploy.add_subparsers(dest="deploy_cmd", required=True)
    deploy_sub.add_parser("check")
    brain = sub.add_parser("brain")
    brain_sub = brain.add_subparsers(dest="brain_cmd", required=True)
    ask = brain_sub.add_parser("ask"); ask.add_argument("query", nargs="+")
    args = p.parse_args()
    if args.api_url != API_URL: API_URL = args.api_url
    if args.cmd == "status": cmd_status(args)
    elif args.cmd == "seed": cmd_seed(args)
    elif args.cmd == "logs": cmd_logs(args)
    elif args.cmd == "deploy": cmd_deploy_check(args)
    elif args.cmd == "brain" and args.brain_cmd == "ask": cmd_brain_ask(args)

if __name__ == "__main__": main()
