"""
Mystic Bot — Telegram multi-modo
  BOT_MODE=ceo     → Mystic AI Asistente Personal (solo Marco)
  BOT_MODE=public  → Mystic Consulting (todos los clientes)
"""

import os
import json
import logging
import urllib.request
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
API_URL        = os.environ.get("API_URL", "http://athena-cerebro:8000")
BOT_MODE       = os.environ.get("BOT_MODE", "public")   # "ceo" | "public"
CEO_ID         = int(os.environ.get("TELEGRAM_CEO_ID", "0"))

_user_tokens: dict[int, str] = {}


# ── Helpers ───────────────────────────────────────────────────────────────────

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
        txt = e.read().decode()
        try:
            return json.loads(txt)
        except Exception:
            return {"error": f"HTTP {e.code}: {txt[:200]}"}
    except Exception as e:
        return {"error": str(e)}


def _fmt(val: float) -> str:
    return f"${val:,.0f} MXN"


def _token(user_id: int) -> str | None:
    return _user_tokens.get(user_id)


def _is_ceo(user_id: int) -> bool:
    return CEO_ID > 0 and user_id == CEO_ID


def _guard_ceo(user_id: int) -> bool:
    """True si el modo es CEO y el usuario NO es el CEO → bloquear."""
    return BOT_MODE == "ceo" and not _is_ceo(user_id)


# ── /start ────────────────────────────────────────────────────────────────────

async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id

    if _guard_ceo(uid):
        await update.message.reply_text("🔒 Acceso restringido.")
        return

    if BOT_MODE == "ceo":
        now = datetime.now().strftime("%d/%m/%Y %H:%M")
        data = _api("GET", "/status")
        api_ok  = "✅" if data.get("api") == "ok" else "⚠️"
        db_ok   = "✅" if data.get("db") == "ok" else "⚠️"
        kb = [
            [InlineKeyboardButton("📊 Dashboard CEO", callback_data="dashboard"),
             InlineKeyboardButton("💰 Ventas hoy", callback_data="ventas")],
            [InlineKeyboardButton("🖥️ Sistema", callback_data="sistema"),
             InlineKeyboardButton("👥 Clientes", callback_data="clientes_count")],
            [InlineKeyboardButton("⚡ Tareas", callback_data="tasks"),
             InlineKeyboardButton("💵 TC USD/MXN", callback_data="tc")],
        ]
        await update.message.reply_text(
            f"🔮 *Mystic AI — Panel CEO*\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🕐 {now}\n"
            f"API {api_ok}  ·  DB {db_ok}\n\n"
            f"Bienvenido, Marco. ¿Qué revisamos?",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(kb),
        )
    else:
        kb = [
            [InlineKeyboardButton("🔑 Iniciar sesión", callback_data="login_prompt"),
             InlineKeyboardButton("❓ ¿Qué puedo hacer?", callback_data="help")],
            [InlineKeyboardButton("💵 Tipo de cambio", callback_data="tc"),
             InlineKeyboardButton("📋 Estado sistema", callback_data="status")],
        ]
        await update.message.reply_text(
            "👋 Hola, soy *Mystic Consulting* 🔮\n\n"
            "Tu asistente contable inteligente.\n"
            "Consulta facturas, cierres fiscales, tipo de cambio y más — sin abrir el sistema.\n\n"
            "Escríbeme en lenguaje natural o usa los botones:",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(kb),
        )


# ── /login ────────────────────────────────────────────────────────────────────

async def cmd_login(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if _guard_ceo(uid):
        await update.message.reply_text("🔒 Acceso restringido.")
        return
    if len(ctx.args) < 2:
        await update.message.reply_text("Uso: `/login <email> <password>`", parse_mode="Markdown")
        return
    email, password = ctx.args[0], ctx.args[1]
    data = _api("POST", "/auth/login", {"email": email, "password": password})
    if "access_token" in data:
        _user_tokens[uid] = data["access_token"]
        u = data.get("usuario", {})
        await update.message.reply_text(
            f"✅ *Sesión iniciada*\n👤 {u.get('nombre', email)}\n"
            f"🏢 {u.get('tenant_id', '-')}",
            parse_mode="Markdown",
        )
    else:
        await update.message.reply_text(
            f"❌ {data.get('detail', data.get('error', 'Credenciales incorrectas'))}"
        )


# ── /status ───────────────────────────────────────────────────────────────────

async def cmd_status(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if _guard_ceo(update.effective_user.id):
        await update.message.reply_text("🔒 Acceso restringido.")
        return
    data = _api("GET", "/status")
    if "error" in data:
        await update.message.reply_text(f"❌ API no responde: {data['error']}")
        return
    ts = data.get("timestamp", "")[:19].replace("T", " ")
    await update.message.reply_text(
        f"*Estado del Sistema*\n\n"
        f"{'✅' if data.get('api')=='ok' else '❌'} API\n"
        f"{'✅' if data.get('db')=='ok' else '❌'} PostgreSQL\n"
        f"{'✅' if data.get('redis')=='ok' else '❌'} Redis\n\n"
        f"🕐 {ts}",
        parse_mode="Markdown",
    )


# ── /dashboard ────────────────────────────────────────────────────────────────

async def cmd_dashboard(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if _guard_ceo(uid):
        await update.message.reply_text("🔒 Acceso restringido.")
        return
    tok = _token(uid)
    if not tok:
        await update.message.reply_text("🔑 Usa `/login email password` primero.", parse_mode="Markdown")
        return
    data = _api("GET", "/dashboard", token=tok)
    if "error" in data:
        await update.message.reply_text(f"❌ {data['error']}")
        return
    r = data.get("resumen", data)
    kpis = data.get("kpis", {})
    salud = {"verde": "💚 ÓPTIMO", "amarillo": "🟡 ATENCIÓN", "rojo": "🔴 ALERTA"}.get(kpis.get("salud", ""), "—")
    await update.message.reply_text(
        f"📊 *Dashboard — {data.get('periodo','Hoy')}*\n\n"
        f"💚 Ingresos: {_fmt(r.get('ingresos_mes',0))}\n"
        f"🔴 Gastos: {_fmt(r.get('gastos_mes',0))}\n"
        f"📈 Utilidad: {_fmt(r.get('utilidad_mes',0))}\n"
        f"📄 Facturas mes: {r.get('facturas_mes',0)}\n"
        f"⏳ Por cobrar: {_fmt(r.get('por_cobrar',0))}\n\n"
        f"Salud: {salud}",
        parse_mode="Markdown",
    )


# ── /facturas ─────────────────────────────────────────────────────────────────

async def cmd_facturas(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if _guard_ceo(uid):
        await update.message.reply_text("🔒 Acceso restringido.")
        return
    tok = _token(uid)
    if not tok:
        await update.message.reply_text("🔑 Usa `/login` primero.", parse_mode="Markdown")
        return
    data = _api("GET", "/facturas?limit=10", token=tok)
    facturas = data if isinstance(data, list) else data.get("items", [])
    if not facturas:
        await update.message.reply_text("No hay facturas registradas.")
        return
    lines = ["📄 *Últimas facturas*\n"]
    for f in facturas[:8]:
        e = f.get("estado", "?")
        emoji = "✅" if e == "pagada" else "⏳" if e == "pendiente" else "❌"
        lines.append(f"{emoji} {f.get('folio','?')} — {_fmt(f.get('total',0))} — {f.get('receptor_nombre','?')[:18]}")
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


# ── /cierre ───────────────────────────────────────────────────────────────────

async def cmd_cierre(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if _guard_ceo(uid):
        await update.message.reply_text("🔒 Acceso restringido.")
        return
    tok = _token(uid)
    if not tok:
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
    data = _api("GET", f"/cierre/{ano}/{mes}", token=tok)
    if "error" in data or "detail" in data:
        await update.message.reply_text(f"❌ {data.get('error', data.get('detail'))}")
        return
    await update.message.reply_text(
        f"📅 *Cierre {mes:02d}/{ano}*\n\n"
        f"💚 Ingresos: {_fmt(data.get('ingresos',0))}\n"
        f"🔴 Egresos: {_fmt(data.get('egresos',0))}\n"
        f"📊 Utilidad: {_fmt(data.get('utilidad_neta',0))}\n"
        f"🏛 ISR estimado: {_fmt(data.get('isr_estimado',0))}\n"
        f"🧾 IVA a pagar: {_fmt(data.get('iva_a_pagar',0))}",
        parse_mode="Markdown",
    )


# ── /tc ───────────────────────────────────────────────────────────────────────

async def cmd_tc(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if _guard_ceo(update.effective_user.id):
        await update.message.reply_text("🔒 Acceso restringido.")
        return
    data = _api("GET", "/tipo-cambio/hoy")
    if "error" in data:
        await update.message.reply_text(f"❌ {data['error']}")
        return
    tc  = data.get("tipo_cambio", data.get("value", 0))
    fec = data.get("fecha", data.get("date", datetime.now().strftime("%Y-%m-%d")))
    await update.message.reply_text(
        f"💵 *USD/MXN*\n\n${tc:.4f} MXN\n📅 {fec}",
        parse_mode="Markdown",
    )


# ── /tasks ────────────────────────────────────────────────────────────────────

async def cmd_tasks(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if _guard_ceo(uid):
        await update.message.reply_text("🔒 Acceso restringido.")
        return
    tok = _token(uid)
    if not tok:
        await update.message.reply_text("🔑 Usa `/login` primero.", parse_mode="Markdown")
        return
    data = _api("GET", "/gsd/tasks", token=tok)
    if not isinstance(data, list):
        await update.message.reply_text(f"❌ {data.get('error', data)}")
        return
    pend = [t for t in data if not t.get("completada")]
    if not pend:
        await update.message.reply_text("✅ Sin tareas pendientes.")
        return
    lines = [f"📋 *Tareas pendientes ({len(pend)})*\n"]
    for t in pend[:8]:
        p = {"alta": "🔴", "media": "🟡", "baja": "🟢"}.get(t.get("prioridad", ""), "⚪")
        lines.append(f"{p} {t.get('titulo','?')[:40]}")
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


# ── /mve ──────────────────────────────────────────────────────────────────────

async def cmd_mve(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if _guard_ceo(uid):
        await update.message.reply_text("🔒 Acceso restringido.")
        return
    tok = _token(uid)
    if not tok:
        await update.message.reply_text("🔑 Usa `/login` primero.", parse_mode="Markdown")
        return
    data = _api("GET", "/mve?limit=5", token=tok)
    mves = data if isinstance(data, list) else []
    if not mves:
        await update.message.reply_text("No hay MVEs registradas.")
        return
    lines = ["📦 *Últimas MVEs*\n"]
    for m in mves[:5]:
        e = m.get("estado", "?")
        emoji = "✅" if e == "presentada" else "🔄" if e == "pendiente" else "❌"
        lines.append(f"{emoji} {m.get('numero_pedimento','?')} — {_fmt(m.get('valor_aduana',0))}")
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


# ── CEO exclusivo: /ventas ────────────────────────────────────────────────────

async def cmd_ventas(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if BOT_MODE != "ceo" or not _is_ceo(uid):
        await update.message.reply_text("🔒 Solo disponible en modo CEO.")
        return
    tok = _token(uid)
    if not tok:
        await update.message.reply_text("🔑 Usa `/login` primero.", parse_mode="Markdown")
        return
    data = _api("GET", "/dashboard", token=tok)
    r = data.get("resumen", data)
    now = datetime.now()
    await update.message.reply_text(
        f"💰 *Ventas — {now.strftime('%d/%m/%Y')}*\n\n"
        f"Ingresos mes: {_fmt(r.get('ingresos_mes',0))}\n"
        f"Facturas mes: {r.get('facturas_mes',0)}\n"
        f"Por cobrar: {_fmt(r.get('por_cobrar',0))}\n"
        f"Por pagar: {_fmt(r.get('por_pagar',0))}",
        parse_mode="Markdown",
    )


# ── CEO exclusivo: /sistema ───────────────────────────────────────────────────

async def cmd_sistema(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if BOT_MODE != "ceo" or not _is_ceo(uid):
        await update.message.reply_text("🔒 Solo disponible en modo CEO.")
        return
    data = _api("GET", "/status")
    ts = data.get("timestamp", "")[:19].replace("T", " ")
    uptime = data.get("uptime", "—")
    tenants = data.get("tenants_activos", "—")
    await update.message.reply_text(
        f"🖥️ *Sistema Mystic*\n\n"
        f"{'✅' if data.get('api')=='ok' else '❌'} API  "
        f"{'✅' if data.get('db')=='ok' else '❌'} DB  "
        f"{'✅' if data.get('redis')=='ok' else '❌'} Redis\n\n"
        f"🏢 Tenants activos: {tenants}\n"
        f"⏱ Uptime: {uptime}\n"
        f"🕐 {ts}",
        parse_mode="Markdown",
    )


# ── CEO exclusivo: /clientes_count ────────────────────────────────────────────

async def cmd_clientes_count(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if BOT_MODE != "ceo" or not _is_ceo(uid):
        await update.message.reply_text("🔒 Solo disponible en modo CEO.")
        return
    tok = _token(uid)
    if not tok:
        await update.message.reply_text("🔑 Usa `/login` primero.", parse_mode="Markdown")
        return
    data = _api("GET", "/contactos?tipo=cliente&limit=500", token=tok)
    total = len(data) if isinstance(data, list) else 0
    activos = sum(1 for c in data if c.get("activo")) if isinstance(data, list) else 0
    await update.message.reply_text(
        f"👥 *Clientes*\n\n"
        f"Total: {total}\n"
        f"Activos: {activos}\n"
        f"Inactivos: {total - activos}",
        parse_mode="Markdown",
    )


# ── /ayuda ────────────────────────────────────────────────────────────────────

async def cmd_ayuda(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if _guard_ceo(update.effective_user.id):
        await update.message.reply_text("🔒 Acceso restringido.")
        return
    if BOT_MODE == "ceo":
        msg = (
            "*Comandos CEO — Mystic AI*\n\n"
            "🔑 `/login email pass` — Sesión\n"
            "📊 `/dashboard` — Resumen financiero\n"
            "💰 `/ventas` — Ingresos de hoy\n"
            "🖥️ `/sistema` — Estado completo\n"
            "👥 `/clientes` — Conteo de clientes\n"
            "📄 `/facturas` — Últimas facturas\n"
            "📅 `/cierre [año/mes]` — Cierre fiscal\n"
            "📋 `/tasks` — Tareas pendientes\n"
            "💵 `/tc` — Tipo de cambio\n"
            "📦 `/mve` — Pedimentos aduana"
        )
    else:
        msg = (
            "*Comandos Mystic Consulting* 🔮\n\n"
            "🔑 `/login email pass` — Iniciar sesión\n"
            "📊 `/dashboard` — Tu resumen financiero\n"
            "📄 `/facturas` — Tus últimas facturas\n"
            "📅 `/cierre [año/mes]` — Cierre mensual\n"
            "💵 `/tc` — Tipo de cambio USD/MXN\n"
            "📦 `/mve` — Tus pedimentos\n"
            "📋 `/tasks` — Tus tareas\n\n"
            "_También puedes escribirme en lenguaje natural_ 🤖"
        )
    await update.message.reply_text(msg, parse_mode="Markdown")


# ── Callbacks ─────────────────────────────────────────────────────────────────

async def on_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    fake = type("U", (), {"message": q.message, "effective_user": q.from_user})()

    dispatch = {
        "status": cmd_status,
        "dashboard": cmd_dashboard,
        "help": cmd_ayuda,
        "tc": cmd_tc,
        "tasks": cmd_tasks,
        "ventas": cmd_ventas,
        "sistema": cmd_sistema,
        "clientes_count": cmd_clientes_count,
    }
    if q.data in dispatch:
        await dispatch[q.data](fake, ctx)
    elif q.data == "login_prompt":
        await q.message.reply_text(
            "Envía: `/login tu@email.com tupassword`\n\n"
            "_Tip: escríbelo en un mensaje privado, no en grupos._",
            parse_mode="Markdown",
        )


# ── Texto libre → Brain IA ────────────────────────────────────────────────────

async def on_message(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if _guard_ceo(uid):
        return

    text = update.message.text.strip()
    tl   = text.lower()

    if tl in ("status", "estado"):
        await cmd_status(update, ctx); return
    if tl in ("dashboard", "resumen"):
        await cmd_dashboard(update, ctx); return

    tok = _token(uid)
    context = "fiscal"
    if tok:
        try:
            import base64, json as _j
            pb = tok.split(".")[1]
            pb += "=" * (4 - len(pb) % 4)
            context = _j.loads(base64.b64decode(pb)).get("tenant_id", "fiscal")
        except Exception:
            pass

    await update.message.chat.send_action("typing")
    resp = _api("POST", "/api/brain/ask", {
        "question": text,
        "context": context,
        "session_id": f"telegram:{uid}",
    })

    if "error" in resp:
        await update.message.reply_text(
            f"❌ Brain IA no disponible.\nUsa /ayuda para ver comandos."
        )
        return

    respuesta = resp.get("respuesta", "Sin respuesta")
    fuente    = resp.get("fuente", "")
    cached    = resp.get("cached", False)
    footer    = f"\n\n_Fuente: {fuente}{'  ·  caché' if cached else ''}_" if fuente else ""
    await update.message.reply_text(f"{respuesta}{footer}", parse_mode="Markdown")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    logger.info(f"Mystic Bot iniciando — modo: {BOT_MODE}")
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start",    cmd_start))
    app.add_handler(CommandHandler("login",    cmd_login))
    app.add_handler(CommandHandler("status",   cmd_status))
    app.add_handler(CommandHandler("dashboard",cmd_dashboard))
    app.add_handler(CommandHandler("facturas", cmd_facturas))
    app.add_handler(CommandHandler("cierre",   cmd_cierre))
    app.add_handler(CommandHandler("tc",       cmd_tc))
    app.add_handler(CommandHandler("mve",      cmd_mve))
    app.add_handler(CommandHandler("tasks",    cmd_tasks))
    app.add_handler(CommandHandler("ventas",   cmd_ventas))
    app.add_handler(CommandHandler("sistema",  cmd_sistema))
    app.add_handler(CommandHandler("clientes", cmd_clientes_count))
    app.add_handler(CommandHandler("ayuda",    cmd_ayuda))
    app.add_handler(CommandHandler("help",     cmd_ayuda))
    app.add_handler(CallbackQueryHandler(on_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_message))

    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
