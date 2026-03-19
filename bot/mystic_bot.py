"""
Mystic Bot — Telegram Bot para Sonora Digital Corp
Conecta con la API del VPS (localhost:8000)
"""

import os
import json
import logging
import urllib.request
import urllib.parse
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ── Config ────────────────────────────────────────────────────────────────────
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
API_URL = os.environ.get("API_URL", "http://localhost:8000")
ALLOWED_USERS = set(
    u.strip() for u in os.environ.get("ALLOWED_USERS", "").split(",") if u.strip()
)

# Tokens JWT por usuario (en memoria, se pierden al reiniciar)
_user_tokens: dict[int, str] = {}


# ── Helpers ──────────────────────────────────────────────────────────────────

def _api(method: str, path: str, data: dict = None, token: str = None) -> dict:
    url = f"{API_URL}{path}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        try:
            return json.loads(body)
        except Exception:
            return {"error": f"HTTP {e.code}: {body[:200]}"}
    except Exception as e:
        return {"error": str(e)}


def _fmt_mxn(val: float) -> str:
    return f"${val:,.2f} MXN"


def _check_auth(user_id: int) -> str | None:
    """Devuelve token JWT si el usuario está autenticado."""
    return _user_tokens.get(user_id)


# ── /start ────────────────────────────────────────────────────────────────────

async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    kb = [
        [InlineKeyboardButton("📊 Dashboard", callback_data="dashboard"),
         InlineKeyboardButton("📋 Status API", callback_data="status")],
        [InlineKeyboardButton("🔑 Login", callback_data="login_prompt"),
         InlineKeyboardButton("❓ Ayuda", callback_data="help")],
    ]
    await update.message.reply_text(
        "👋 *Mystic Bot* listo.\n\nUsa los botones o escribe un comando:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(kb),
    )


# ── /status ──────────────────────────────────────────────────────────────────

async def cmd_status(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    data = _api("GET", "/status")
    if "error" in data:
        await update.message.reply_text(f"❌ API no responde: {data['error']}")
        return
    api_ok = "✅" if data.get("api") == "ok" else "❌"
    db_ok = "✅" if data.get("db") == "ok" else "❌"
    redis_ok = "✅" if data.get("redis") == "ok" else "❌"
    ts = data.get("timestamp", "")[:19].replace("T", " ")
    await update.message.reply_text(
        f"*Estado del Sistema*\n\n"
        f"{api_ok} API\n{db_ok} PostgreSQL\n{redis_ok} Redis\n\n"
        f"🕐 {ts}",
        parse_mode="Markdown",
    )


# ── /login ────────────────────────────────────────────────────────────────────

async def cmd_login(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if len(ctx.args) < 2:
        await update.message.reply_text(
            "Uso: `/login <email> <password>`", parse_mode="Markdown"
        )
        return
    email, password = ctx.args[0], ctx.args[1]
    data = _api("POST", "/auth/login", {"email": email, "password": password})
    if "access_token" in data:
        _user_tokens[update.effective_user.id] = data["access_token"]
        user_info = data.get("usuario", {})  # API retorna "usuario", no "user"
        await update.message.reply_text(
            f"✅ Login exitoso\n👤 {user_info.get('nombre', email)}\n"
            f"🏢 Tenant: {user_info.get('tenant_id', '-')}",
        )
    else:
        await update.message.reply_text(
            f"❌ {data.get('detail', data.get('error', 'Error de autenticación'))}"
        )


# ── /dashboard ────────────────────────────────────────────────────────────────

async def cmd_dashboard(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    token = _check_auth(update.effective_user.id)
    if not token:
        await update.message.reply_text("🔑 Inicia sesión primero con `/login email password`", parse_mode="Markdown")
        return
    data = _api("GET", "/dashboard", token=token)
    if "error" in data:
        await update.message.reply_text(f"❌ {data['error']}")
        return
    mes = data.get("mes_actual", datetime.now().strftime("%Y-%m"))
    ingresos = data.get("ingresos_mes", 0)
    egresos = data.get("egresos_mes", 0)
    utilidad = data.get("utilidad_neta", 0)
    facturas_pend = data.get("facturas_pendientes", 0)
    await update.message.reply_text(
        f"📊 *Dashboard — {mes}*\n\n"
        f"💚 Ingresos: {_fmt_mxn(ingresos)}\n"
        f"🔴 Egresos: {_fmt_mxn(egresos)}\n"
        f"📈 Utilidad: {_fmt_mxn(utilidad)}\n"
        f"📄 Facturas pendientes: {facturas_pend}",
        parse_mode="Markdown",
    )


# ── /facturas ────────────────────────────────────────────────────────────────

async def cmd_facturas(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    token = _check_auth(update.effective_user.id)
    if not token:
        await update.message.reply_text("🔑 Usa `/login` primero.", parse_mode="Markdown")
        return
    data = _api("GET", "/facturas?limit=10", token=token)
    if isinstance(data, list):
        facturas = data
    elif isinstance(data, dict) and "items" in data:
        facturas = data["items"]
    else:
        await update.message.reply_text(f"❌ {data.get('error', data)}")
        return
    if not facturas:
        await update.message.reply_text("No hay facturas registradas.")
        return
    lines = ["📄 *Últimas facturas*\n"]
    for f in facturas[:8]:
        estado = f.get("estado", "?")
        emoji = "✅" if estado == "pagada" else "⏳" if estado == "pendiente" else "❌"
        lines.append(
            f"{emoji} {f.get('folio','?')} — {_fmt_mxn(f.get('total',0))} — {f.get('emisor_nombre','?')[:20]}"
        )
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


# ── /cierre ───────────────────────────────────────────────────────────────────

async def cmd_cierre(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    token = _check_auth(update.effective_user.id)
    if not token:
        await update.message.reply_text("🔑 Usa `/login` primero.", parse_mode="Markdown")
        return
    now = datetime.now()
    ano, mes = now.year, now.month
    if ctx.args:
        try:
            parts = ctx.args[0].split("/")
            ano, mes = int(parts[0]), int(parts[1])
        except Exception:
            pass
    data = _api("GET", f"/cierre/{ano}/{mes}", token=token)
    if "error" in data or "detail" in data:
        await update.message.reply_text(f"❌ {data.get('error', data.get('detail'))}")
        return
    ingresos = data.get("ingresos", 0)
    egresos = data.get("egresos", 0)
    isr = data.get("isr_estimado", 0)
    iva = data.get("iva_a_pagar", 0)
    utilidad = data.get("utilidad_neta", 0)
    await update.message.reply_text(
        f"📅 *Cierre {mes:02d}/{ano}*\n\n"
        f"💚 Ingresos: {_fmt_mxn(ingresos)}\n"
        f"🔴 Egresos: {_fmt_mxn(egresos)}\n"
        f"📊 Utilidad: {_fmt_mxn(utilidad)}\n"
        f"🏛 ISR estimado: {_fmt_mxn(isr)}\n"
        f"🧾 IVA a pagar: {_fmt_mxn(iva)}",
        parse_mode="Markdown",
    )


# ── /tc (tipo de cambio) ──────────────────────────────────────────────────────

async def cmd_tc(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    data = _api("GET", "/tipo-cambio/hoy")
    if "error" in data:
        await update.message.reply_text(f"❌ {data['error']}")
        return
    tc = data.get("tipo_cambio", data.get("value", 0))
    fecha = data.get("fecha", data.get("date", datetime.now().strftime("%Y-%m-%d")))
    fuente = data.get("fuente", data.get("source", "Banxico"))
    await update.message.reply_text(
        f"💵 *Tipo de cambio USD/MXN*\n\n"
        f"${tc:.4f} MXN\n📅 {fecha}\n🏦 {fuente}",
        parse_mode="Markdown",
    )


# ── /mve ─────────────────────────────────────────────────────────────────────

async def cmd_mve(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    token = _check_auth(update.effective_user.id)
    if not token:
        await update.message.reply_text("🔑 Usa `/login` primero.", parse_mode="Markdown")
        return
    data = _api("GET", "/mve?limit=5", token=token)
    if isinstance(data, list):
        mves = data
    else:
        await update.message.reply_text(f"❌ {data.get('error', data)}")
        return
    if not mves:
        await update.message.reply_text("No hay MVEs registradas.")
        return
    lines = ["📦 *Últimas MVEs*\n"]
    for m in mves[:5]:
        estado = m.get("estado", "?")
        emoji = "✅" if estado == "presentada" else "🔄" if estado == "pendiente" else "❌"
        lines.append(
            f"{emoji} {m.get('numero_pedimento','?')} — {_fmt_mxn(m.get('valor_aduana',0))} — {estado}"
        )
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


# ── /tasks ────────────────────────────────────────────────────────────────────

async def cmd_tasks(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    token = _check_auth(update.effective_user.id)
    if not token:
        await update.message.reply_text("🔑 Usa `/login` primero.", parse_mode="Markdown")
        return
    data = _api("GET", "/gsd/tasks", token=token)
    if not isinstance(data, list):
        await update.message.reply_text(f"❌ {data.get('error', data)}")
        return
    pendientes = [t for t in data if not t.get("completada")]
    if not pendientes:
        await update.message.reply_text("✅ No hay tareas pendientes.")
        return
    lines = [f"📋 *Tareas pendientes ({len(pendientes)})*\n"]
    for t in pendientes[:8]:
        prior = {"alta": "🔴", "media": "🟡", "baja": "🟢"}.get(t.get("prioridad", ""), "⚪")
        lines.append(f"{prior} {t.get('titulo', '?')[:40]}")
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


# ── /ayuda ────────────────────────────────────────────────────────────────────

async def cmd_ayuda(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "*Comandos disponibles:*\n\n"
        "🔑 `/login email pass` — Iniciar sesión\n"
        "📊 `/dashboard` — Resumen financiero\n"
        "📄 `/facturas` — Últimas facturas\n"
        "📅 `/cierre [año/mes]` — Cierre mensual\n"
        "💵 `/tc` — Tipo de cambio USD/MXN\n"
        "📦 `/mve` — Manifestaciones de valor\n"
        "📋 `/tasks` — Tareas pendientes\n"
        "🔍 `/status` — Estado del sistema",
        parse_mode="Markdown",
    )


# ── Callback buttons ──────────────────────────────────────────────────────────

async def on_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "status":
        await cmd_status(query, ctx)
    elif query.data == "dashboard":
        await cmd_dashboard(query, ctx)
    elif query.data == "help":
        await cmd_ayuda(query, ctx)
    elif query.data == "login_prompt":
        await query.message.reply_text(
            "Envía: `/login tu@email.com tupassword`", parse_mode="Markdown"
        )


# ── Mensajes de texto → Brain IA ─────────────────────────────────────────────

async def on_message(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    text_lower = text.lower()
    user_id = update.effective_user.id

    # Atajos rápidos sin brain
    if text_lower in ("status", "estado"):
        await cmd_status(update, ctx)
        return
    if text_lower in ("dashboard", "resumen"):
        await cmd_dashboard(update, ctx)
        return

    # Todo lo demás → Brain IA
    token = _check_auth(user_id)
    # Determinar contexto del tenant a partir del token si existe
    context = "fiscal"
    if token:
        try:
            import base64, json as _json
            payload_b64 = token.split(".")[1]
            payload_b64 += "=" * (4 - len(payload_b64) % 4)
            payload = _json.loads(base64.b64decode(payload_b64))
            context = payload.get("tenant_id", "fiscal")
        except Exception:
            pass

    session_id = f"telegram:{user_id}"
    await update.message.chat.send_action("typing")

    resp = _api("POST", "/api/brain/ask", {
        "question": text,
        "context": context,
        "session_id": session_id,
    })

    if "error" in resp:
        await update.message.reply_text(f"❌ Brain IA no disponible: {resp['error']}\nUsa /ayuda para ver comandos.")
        return

    respuesta = resp.get("respuesta", "Sin respuesta")
    fuente = resp.get("fuente", "")
    cached = resp.get("cached", False)

    footer = f"\n\n_Fuente: {fuente}{'  ·  caché' if cached else ''}_"
    await update.message.reply_text(
        f"{respuesta}{footer}",
        parse_mode="Markdown",
    )


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("login", cmd_login))
    app.add_handler(CommandHandler("dashboard", cmd_dashboard))
    app.add_handler(CommandHandler("facturas", cmd_facturas))
    app.add_handler(CommandHandler("cierre", cmd_cierre))
    app.add_handler(CommandHandler("tc", cmd_tc))
    app.add_handler(CommandHandler("mve", cmd_mve))
    app.add_handler(CommandHandler("tasks", cmd_tasks))
    app.add_handler(CommandHandler("ayuda", cmd_ayuda))
    app.add_handler(CommandHandler("help", cmd_ayuda))
    app.add_handler(CallbackQueryHandler(on_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_message))

    logger.info("Mystic Bot iniciando (polling)...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
