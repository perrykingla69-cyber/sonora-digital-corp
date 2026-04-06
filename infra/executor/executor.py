"""
HERMES Executor — Puente OpenClaw → Claude Code / OpenCode
Corre en el HOST (no en Docker) en puerto 9001
ClawBot lo llama via host.docker.internal:9001
"""
from fastapi import FastAPI, BackgroundTasks
import subprocess, os, httpx, asyncio

app = FastAPI(title="HERMES Executor", version="1.0")

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN_CEO", "")
CEO_CHAT_ID    = os.environ.get("CEO_CHAT_ID", "")
OPENCODE       = os.environ.get("OPENCODE_BIN", "/home/mystic/.opencode/bin/opencode")
WORKSPACE      = os.environ.get("WORKSPACE", "/home/mystic/hermes-os")
TIMEOUT        = int(os.environ.get("EXEC_TIMEOUT", "300"))  # 5 min


async def telegram(msg: str):
    if not TELEGRAM_TOKEN or not CEO_CHAT_ID:
        return
    async with httpx.AsyncClient() as c:
        await c.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            json={"chat_id": CEO_CHAT_ID, "text": msg, "parse_mode": "Markdown"},
            timeout=10,
        )


async def run_task(task: str):
    await telegram(f"⚡ *Claude Code ejecutando:*\n`{task[:120]}`")
    try:
        proc = subprocess.run(
            [OPENCODE, "run", task],
            capture_output=True, text=True,
            timeout=TIMEOUT, cwd=WORKSPACE,
        )
        output = (proc.stdout or proc.stderr or "Sin output").strip()
        # Truncar para Telegram (max 4096 chars)
        if len(output) > 3500:
            output = output[-3500:] + "\n...(truncado)"
        status = "✅" if proc.returncode == 0 else "⚠️"
        await telegram(f"{status} *Completado:*\n```\n{output}\n```")
    except subprocess.TimeoutExpired:
        await telegram(f"⏱ *Timeout* ({TIMEOUT}s)\nTarea: `{task[:80]}`")
    except FileNotFoundError:
        await telegram(f"🔴 OpenCode no encontrado en `{OPENCODE}`")
    except Exception as e:
        await telegram(f"🔴 *Error executor:* `{str(e)[:200]}`")


@app.post("/run")
async def run(body: dict, bg: BackgroundTasks):
    task = (body.get("task") or "").strip()
    if not task:
        return {"error": "campo 'task' requerido"}
    bg.add_task(run_task, task)
    return {"ok": True, "queued": task[:60]}


@app.post("/run-sync")
async def run_sync(body: dict):
    """Para uso interno — responde cuando termina (max 60s)"""
    task = (body.get("task") or "").strip()
    if not task:
        return {"error": "campo 'task' requerido"}
    try:
        proc = subprocess.run(
            [OPENCODE, "run", task],
            capture_output=True, text=True, timeout=60, cwd=WORKSPACE,
        )
        return {"ok": True, "output": (proc.stdout or proc.stderr or "")[-2000:]}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@app.get("/health")
async def health():
    opencode_ok = os.path.exists(OPENCODE)
    return {"ok": True, "opencode": opencode_ok, "workspace": WORKSPACE}
