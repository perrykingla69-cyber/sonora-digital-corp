"""
TikTok Trends MCP — JSON-RPC server (port 8004)
Tools: get_trending_hashtags, get_trending_sounds, search_content
"""
import os
import httpx
from fastapi import FastAPI, Request

app = FastAPI(title="TikTok Trends MCP", version="1.0.0")

TIKTOK_ACCESS_TOKEN = os.getenv("TIKTOK_ACCESS_TOKEN", "")


async def get_trending_hashtags(region: str = "MX", limit: int = 20) -> dict:
    if not TIKTOK_ACCESS_TOKEN:
        return {"hashtags": _mock_hashtags_mx(), "source": "mock", "region": region}
    async with httpx.AsyncClient() as client:
        r = await client.get(
            "https://open.tiktokapis.com/v2/research/trending/hashtag/",
            params={"region_code": region, "count": limit},
            headers={"Authorization": f"Bearer {TIKTOK_ACCESS_TOKEN}"},
        )
        if r.status_code == 200:
            return {"hashtags": r.json().get("data", {}).get("hashtags", []), "region": region}
    return {"hashtags": _mock_hashtags_mx(), "source": "mock", "region": region}


def _mock_hashtags_mx() -> list:
    return [
        {"name": "norteño", "video_count": 2500000},
        {"name": "grupero", "video_count": 1800000},
        {"name": "corridos", "video_count": 3200000},
        {"name": "sinaloa", "video_count": 950000},
        {"name": "musicamexicana", "video_count": 5100000},
        {"name": "acordeon", "video_count": 720000},
        {"name": "vallenato", "video_count": 440000},
        {"name": "rancheritas", "video_count": 380000},
    ]


async def get_trending_sounds(region: str = "MX", limit: int = 10) -> dict:
    return {
        "sounds": [
            {"id": "sound_001", "title": "Tendencia Norteña 2026", "usage_count": 85000},
            {"id": "sound_002", "title": "Beat Grupero Hit", "usage_count": 62000},
            {"id": "sound_003", "title": "Intro Impacto", "usage_count": 41000},
        ],
        "region": region,
        "source": "mock",
    }


TOOLS_SCHEMA = {
    "tools": [
        {"name": "get_trending_hashtags", "description": "Get trending hashtags on TikTok by region", "inputSchema": {"type": "object", "properties": {"region": {"type": "string", "default": "MX"}, "limit": {"type": "integer", "default": 20}}}},
        {"name": "get_trending_sounds", "description": "Get trending sounds/music on TikTok", "inputSchema": {"type": "object", "properties": {"region": {"type": "string", "default": "MX"}, "limit": {"type": "integer", "default": 10}}}},
    ]
}


@app.post("/mcp")
async def mcp_handler(request: Request):
    body = await request.json()
    method = body.get("method")
    params = body.get("params", {})

    if method == "get_schema":
        return {"jsonrpc": "2.0", "id": body.get("id"), "result": TOOLS_SCHEMA}
    elif method == "get_trending_hashtags":
        result = await get_trending_hashtags(params.get("region", "MX"), params.get("limit", 20))
    elif method == "get_trending_sounds":
        result = await get_trending_sounds(params.get("region", "MX"), params.get("limit", 10))
    else:
        return {"jsonrpc": "2.0", "id": body.get("id"), "error": {"code": -32601, "message": f"Method not found: {method}"}}

    return {"jsonrpc": "2.0", "id": body.get("id"), "result": result}


@app.get("/health")
async def health():
    return {"status": "ok", "service": "tiktok-mcp", "port": 8004}
