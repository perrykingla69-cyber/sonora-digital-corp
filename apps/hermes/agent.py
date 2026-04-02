"""
HERMES Agent — Proceso independiente
Escucha Telegram, coordina con MYSTIC, reporta al CEO.
"""

import asyncio
import httpx
import os
from telegram import Update, Bot
from telegram.ext import Application, MessageHandler, CommandHandler, filters

API_URL = os.environ["API_URL"]
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
CEO_EMAIL = os.environ.get("CEO_EMAIL", "")
CEO_PASSWORD = os.environ.get("CEO_PASSWORD", "")
CEO_TENANT = os.environ.get("CEO_TENANT_SLUG", "sonora")


class HermesProcess:
    def __init__(self):
        self._token: str | None = None
        self.app = Application.builder().token(TELEGRAM_TOKEN).build()
        self._setup_handlers()

    def _setup_handlers(self):
        self.app.add_handler(CommandHandler("start", self.cmd_start))
        self.app.add_handler(CommandHandler("mystic", self.cmd_mystic))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

    async def get_token(self) -> str:
        if self._token:
            return self._token
        async with httpx.AsyncClient() as client:
            r = await client.post(f"{API_URL}/api/v1/auth/login", json={
                "email": CEO_EMAIL,
                "password": CEO_PASSWORD,
                "tenant_slug": CEO_TENANT,
            })
            self._token = r.json()["access_token"]
        return self._token

    async def cmd_start(self, update: Update, _):
        await update.message.reply_text(
            "☀️ HERMES activo.\n\nSoy tu orquestador. Pregúntame cualquier cosa."
        )

    async def cmd_mystic(self, update: Update, _):
        await update.message.reply_text("🌑 Delegando a MYSTIC para análisis profundo...")

    async def handle_message(self, update: Update, _):
        text = update.message.text
        token = await self.get_token()

        await update.message.chat.send_action("typing")

        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(
                f"{API_URL}/api/v1/agents/hermes/chat",
                headers={"Authorization": f"Bearer {token}"},
                json={"message": text, "channel": "telegram"},
            )

        data = r.json()
        await update.message.reply_text(f"☀️ {data['response']}")

    async def run(self):
        print("☀️ HERMES Agent iniciado")
        await self.app.initialize()
        # Borrar webhook activo antes de polling (evita Conflict)
        await self.app.bot.delete_webhook(drop_pending_updates=True)
        await self.app.start()
        await self.app.updater.start_polling()
        await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(HermesProcess().run())
