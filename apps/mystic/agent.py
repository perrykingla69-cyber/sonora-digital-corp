"""
MYSTIC Agent — La Sombra
Analiza en background, alerta proactivamente al CEO.
Ejecuta shadow_scan periódico en todos los tenants.
"""

import asyncio
import httpx
import os
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='🌑 MYSTIC | %(asctime)s | %(message)s')
logger = logging.getLogger(__name__)

API_URL = os.environ["API_URL"]
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
CEO_CHAT_ID = os.environ.get("CEO_CHAT_ID", "")
SCAN_INTERVAL = int(os.environ.get("SCAN_INTERVAL_SECONDS", "3600"))  # cada hora


async def get_system_token() -> str:
    """Token de sistema para operaciones internas."""
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{API_URL}/api/v1/auth/login", json={
            "email": os.environ.get("SYSTEM_EMAIL"),
            "password": os.environ.get("SYSTEM_PASSWORD"),
            "tenant_slug": os.environ.get("SYSTEM_TENANT", "sonora"),
        })
        return r.json()["access_token"]


async def send_alert(message: str):
    """Envía alerta al CEO via Telegram."""
    async with httpx.AsyncClient() as client:
        await client.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            json={
                "chat_id": CEO_CHAT_ID,
                "text": f"🌑 *MYSTIC ALERT*\n\n{message}",
                "parse_mode": "Markdown",
            },
        )


async def shadow_scan_loop():
    """Loop principal: MYSTIC escanea tenants activos cada hora."""
    logger.info("Shadow scan loop iniciado")

    while True:
        try:
            token = await get_system_token()
            async with httpx.AsyncClient(timeout=60) as client:
                # Analizar estado general del sistema
                r = await client.post(
                    f"{API_URL}/api/v1/agents/mystic/analyze",
                    headers={"Authorization": f"Bearer {token}"},
                    json={
                        "message": (
                            f"Shadow scan automático — {datetime.now().strftime('%Y-%m-%d %H:%M')}.\n"
                            "Analiza el estado del sistema y reporta cualquier anomalía o punto de atención."
                        ),
                        "channel": "system",
                    },
                )

            data = r.json()
            analysis = data.get("response", "")

            # Solo alerta si hay algo crítico (🔴)
            if "🔴" in analysis or "CRÍTICO" in analysis.upper() or "URGENTE" in analysis.upper():
                await send_alert(analysis)
                logger.info("Alerta crítica enviada al CEO")
            else:
                logger.info("Shadow scan completado — sin anomalías críticas")

        except Exception as e:
            logger.error(f"Error en shadow scan: {e}")

        await asyncio.sleep(SCAN_INTERVAL)


async def main():
    logger.info("MYSTIC Agent iniciando — La sombra despierta")
    await shadow_scan_loop()


if __name__ == "__main__":
    asyncio.run(main())
