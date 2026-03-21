"""Thin WhatsApp client used by the modular auth service."""
from __future__ import annotations

import json
import os
import urllib.request


class WhatsAppClient:
    def __init__(self, base_url: str | None = None, api_key: str | None = None):
        self.base_url = base_url or os.getenv("WHATSAPP_BASE_URL", "http://localhost:3001")
        self.api_key = api_key or os.getenv("WA_API_KEY", "MysticWA2026!")

    def send_text(self, to: str, message: str, timeout: int = 5) -> bool:
        payload = json.dumps({"to": to, "message": message}).encode()
        req = urllib.request.Request(
            f"{self.base_url}/send",
            data=payload,
            headers={"Content-Type": "application/json", "x-api-key": self.api_key},
        )
        urllib.request.urlopen(req, timeout=timeout)
        return True
