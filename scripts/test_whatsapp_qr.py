#!/usr/bin/env python3
"""
test_whatsapp_qr.py — Verifica que el endpoint /whatsapp/qr responde correctamente.
Uso: python3 scripts/test_whatsapp_qr.py
"""

import urllib.request
import urllib.error
import json
import logging
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

BASE_LOCAL  = "http://localhost:3001"
BASE_PUBLIC = "https://sonoradigitalcorp.com/whatsapp"
API_KEY     = "MysticWA2026!"
API_KEY_ENC = "MysticWA2026%21"

def check(label, url, headers=None):
    try:
        req = urllib.request.Request(url, headers=headers or {})
        with urllib.request.urlopen(req, timeout=10) as r:
            code = r.getcode()
            ct   = r.headers.get("Content-Type", "")
            body = r.read(200)
            ok = code == 200
            logging.info(f"  {'✅' if ok else '❌'} {label}: HTTP {code} | {ct[:30]}")
            return ok
    except urllib.error.HTTPError as e:
        logging.error(f"  ❌ {label}: HTTP {e.code} — {e.reason}")
        return False
    except Exception as e:
        logging.error(f"  ❌ {label}: {e}")
        return False

def check_json(label, url, headers=None):
    try:
        req = urllib.request.Request(url, headers=headers or {})
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
            state = data.get("state", "?")
            has_qr = data.get("hasQR", False)
            ok = r.getcode() == 200
            logging.info(f"  {'✅' if ok else '❌'} {label}: state={state} hasQR={has_qr}")
            return ok
    except Exception as e:
        logging.error(f"  ❌ {label}: {e}")
        return False


logging.info("\n=== TEST: mystic-wa WhatsApp QR ===\n")

logging.info("[ Local :3001 ]")
check("QR con ! literal",   f"{BASE_LOCAL}/qr?apikey={API_KEY}")
check("QR con %21 encoded", f"{BASE_LOCAL}/qr?apikey={API_KEY_ENC}")
check("QR via x-api-key",   f"{BASE_LOCAL}/qr", {"x-api-key": API_KEY})
check_json("Status",        f"{BASE_LOCAL}/status?apikey={API_KEY_ENC}")

logging.info("\n[ HTTPS sonoradigitalcorp.com ]")
check("QR %21 encoded",   f"{BASE_PUBLIC}/qr?apikey={API_KEY_ENC}")
check("QR ! literal",     f"{BASE_PUBLIC}/qr?apikey={API_KEY}")
check("QR x-api-key",     f"{BASE_PUBLIC}/qr", {"x-api-key": API_KEY})
check_json("Status",      f"{BASE_PUBLIC}/status?apikey={API_KEY_ENC}")

logging.info("\n[ Health check sin auth ]")
check("Root /",  f"{BASE_LOCAL}/")

logging.info(
    "\n=== URL FINAL PARA ESCANEAR QR ===\n\n"
    "  https://sonoradigitalcorp.com/whatsapp/qr?apikey=MysticWA2026%21\n\n"
    "  (Ábrela en el navegador — muestra el QR directamente)\n"
    "  Se auto-actualiza cada 30 segundos.\n"
)
