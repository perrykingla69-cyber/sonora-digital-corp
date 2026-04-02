"""
MYSTIC — Monitor Hostinger VPS
Usa la API de Hostinger para monitorear recursos y alertar al CEO.

Hostinger API: https://developers.hostinger.com
Auth: Bearer token desde hPanel → API → Create Token
"""

import asyncio
import os
import logging
import httpx
from datetime import datetime

logger = logging.getLogger("mystic.hostinger")

HOSTINGER_TOKEN = os.environ.get("HOSTINGER_API_TOKEN", "")
TELEGRAM_TOKEN  = os.environ.get("TELEGRAM_TOKEN_MYSTIC", "")
CEO_CHAT_ID     = os.environ.get("CEO_CHAT_ID", "")
VPS_ID          = os.environ.get("HOSTINGER_VPS_ID", "")

BASE_URL = "https://api.hostinger.com/v1"

# Umbrales de alerta
ALERTA_RAM_PCT   = 85   # % RAM usada → 🔴
ALERTA_CPU_PCT   = 90   # % CPU → 🔴
ALERTA_DISCO_PCT = 80   # % disco → 🟡
WARN_RAM_PCT     = 70   # % RAM → 🟡


async def notificar(texto: str, urgente: bool = False):
    if not TELEGRAM_TOKEN or not CEO_CHAT_ID:
        logger.info(f"[Telegram off] {texto}")
        return
    async with httpx.AsyncClient(timeout=10) as c:
        await c.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            json={
                "chat_id": CEO_CHAT_ID,
                "text": texto,
                "parse_mode": "Markdown",
                "disable_notification": not urgente,
            },
        )


async def get_vps_metrics() -> dict:
    """Obtiene métricas del VPS via Hostinger API."""
    if not HOSTINGER_TOKEN:
        # Fallback: métricas locales con /proc
        return await get_local_metrics()

    headers = {"Authorization": f"Bearer {HOSTINGER_TOKEN}"}
    async with httpx.AsyncClient(timeout=15) as c:
        try:
            # Listar VPS si no tenemos el ID
            if not VPS_ID:
                r = await c.get(f"{BASE_URL}/vps", headers=headers)
                vps_list = r.json()
                if vps_list:
                    vps = vps_list[0]
                    return {
                        "id": vps.get("id"),
                        "hostname": vps.get("hostname"),
                        "status": vps.get("state"),
                        "plan": vps.get("plan", {}).get("name"),
                        "ram_mb": vps.get("plan", {}).get("memory"),
                        "cpu_cores": vps.get("plan", {}).get("cpu"),
                        "disco_gb": vps.get("plan", {}).get("disk"),
                        "ip": vps.get("ipv4", [{}])[0].get("ip"),
                        "source": "hostinger_api",
                    }
        except Exception as e:
            logger.warning(f"Hostinger API error: {e} — usando métricas locales")

    return await get_local_metrics()


async def get_local_metrics() -> dict:
    """Lee métricas directamente del sistema Linux."""
    metrics = {"source": "local_proc"}
    try:
        # RAM
        with open("/proc/meminfo") as f:
            mem = {}
            for line in f:
                parts = line.split()
                if len(parts) >= 2:
                    mem[parts[0].rstrip(":")] = int(parts[1])
            total = mem.get("MemTotal", 0)
            disponible = mem.get("MemAvailable", 0)
            usado = total - disponible
            metrics.update({
                "ram_total_mb": round(total / 1024),
                "ram_usado_mb": round(usado / 1024),
                "ram_pct": round(usado / total * 100, 1) if total else 0,
            })
    except Exception:
        pass

    try:
        # CPU (promedio 1 min)
        with open("/proc/loadavg") as f:
            load = float(f.read().split()[0])
        with open("/proc/cpuinfo") as f:
            cores = f.read().count("processor\t:")
        metrics["cpu_load1"] = load
        metrics["cpu_cores"] = cores
        metrics["cpu_pct"] = round(load / cores * 100, 1) if cores else 0
    except Exception:
        pass

    try:
        # Disco raíz
        import shutil
        d = shutil.disk_usage("/")
        metrics["disco_total_gb"] = round(d.total / 1e9, 1)
        metrics["disco_usado_gb"] = round(d.used / 1e9, 1)
        metrics["disco_pct"] = round(d.used / d.total * 100, 1)
    except Exception:
        pass

    return metrics


async def scan_vps():
    """
    Scan completo del VPS. MYSTIC lo corre cada hora.
    Solo alerta si hay algo relevante.
    """
    m = await get_vps_metrics()
    alertas = []
    nivel = "🟢"

    ram_pct   = m.get("ram_pct", 0)
    cpu_pct   = m.get("cpu_pct", 0)
    disco_pct = m.get("disco_pct", 0)

    if ram_pct >= ALERTA_RAM_PCT:
        alertas.append(f"🔴 RAM crítica: {ram_pct}% ({m.get('ram_usado_mb')}MB / {m.get('ram_total_mb')}MB)")
        nivel = "🔴"
    elif ram_pct >= WARN_RAM_PCT:
        alertas.append(f"🟡 RAM elevada: {ram_pct}%")
        if nivel != "🔴":
            nivel = "🟡"

    if cpu_pct >= ALERTA_CPU_PCT:
        alertas.append(f"🔴 CPU crítico: {cpu_pct}% (load: {m.get('cpu_load1')})")
        nivel = "🔴"

    if disco_pct >= ALERTA_DISCO_PCT:
        alertas.append(f"🟡 Disco: {disco_pct}% — {m.get('disco_usado_gb')}GB / {m.get('disco_total_gb')}GB")
        if nivel != "🔴":
            nivel = "🟡"

    if alertas:
        texto = (
            f"🌑 *MYSTIC VPS ALERT*\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"*Nivel:* {nivel}\n"
            f"*Hora:* {datetime.now().strftime('%H:%M')} UTC\n\n"
            + "\n".join(alertas) +
            f"\n\n*RAM:* {ram_pct}% | *CPU:* {cpu_pct}% | *Disco:* {disco_pct}%"
        )
        await notificar(texto, urgente=(nivel == "🔴"))
        logger.info(f"Alerta enviada: {nivel}")
    else:
        logger.info(f"VPS OK — RAM:{ram_pct}% CPU:{cpu_pct}% Disco:{disco_pct}%")

    return {"nivel": nivel, "alertas": alertas, "metrics": m}


async def get_hostinger_token_instructions() -> str:
    """Instrucciones para obtener el API token de Hostinger."""
    return """
Para conectar MYSTIC con Hostinger API:

1. Ir a hPanel: https://hpanel.hostinger.com
2. Menú → API → Create new token
3. Nombre: "MYSTIC Monitor"
4. Permisos: VPS (read)
5. Copiar el token generado

Agregar al .env del VPS:
  HOSTINGER_API_TOKEN=tu_token_aqui
  HOSTINGER_VPS_ID=tu_vps_id  (opcional, se auto-detecta)

MYSTIC escaneará el VPS cada hora y alertará si:
  - RAM > 85% → alerta inmediata CEO
  - CPU > 90% → alerta inmediata CEO
  - Disco > 80% → alerta diaria
"""


async def main():
    """Entry point — un scan inmediato."""
    result = await scan_vps()
    print(f"Scan completado: {result['nivel']}")
    if not HOSTINGER_TOKEN:
        print(await get_hostinger_token_instructions())


if __name__ == "__main__":
    asyncio.run(main())
