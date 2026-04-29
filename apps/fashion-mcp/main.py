"""
Fashion MCP — JSON-RPC server (port 8005)
Tools: get_style_posts, analyze_outfit, trending_styles
"""
import os
import httpx
from fastapi import FastAPI, Request

app = FastAPI(title="Fashion MCP", version="1.0.0")

PINTEREST_TOKEN = os.getenv("PINTEREST_ACCESS_TOKEN", "")


async def get_style_posts(query: str, limit: int = 12) -> dict:
    return {
        "posts": [
            {"id": f"post_{i}", "title": f"Estilo norteño {i+1}", "tags": ["norteño", "vaquero", "regional"], "engagement": 1200 + i * 300, "platform": "pinterest"}
            for i in range(min(limit, 6))
        ],
        "query": query,
        "source": "mock",
    }


async def analyze_outfit(description: str) -> dict:
    keywords = description.lower()
    style = "norteño_clásico"
    if "urbano" in keywords or "streetwear" in keywords:
        style = "norteño_urbano"
    elif "formal" in keywords or "gala" in keywords:
        style = "norteño_formal"
    return {
        "style_category": style,
        "color_palette": ["café silla", "negro", "crema", "azul índigo"],
        "recommended_items": ["sombrero vaquero", "bota punta fina", "hebilla grabada", "camisa bordada"],
        "trend_score": 0.82,
    }


async def trending_styles(region: str = "MX") -> dict:
    return {
        "trends": [
            {"name": "Norteño Urbano", "growth": "+34%", "key_items": ["snapback", "tenis blancos", "camisa cuadros"]},
            {"name": "Vaquero Clásico", "growth": "+18%", "key_items": ["sombrero Texana", "bota cuadrada", "cinturón piel"]},
            {"name": "Regional Chic", "growth": "+27%", "key_items": ["traje sastre", "accesorio dorado", "bota puntiaguda"]},
        ],
        "region": region,
    }


TOOLS_SCHEMA = {
    "tools": [
        {"name": "get_style_posts", "description": "Search fashion/style posts", "inputSchema": {"type": "object", "properties": {"query": {"type": "string"}, "limit": {"type": "integer", "default": 12}}, "required": ["query"]}},
        {"name": "analyze_outfit", "description": "Analyze outfit description and classify style", "inputSchema": {"type": "object", "properties": {"description": {"type": "string"}}, "required": ["description"]}},
        {"name": "trending_styles", "description": "Get trending styles by region", "inputSchema": {"type": "object", "properties": {"region": {"type": "string", "default": "MX"}}}},
    ]
}


@app.post("/mcp")
async def mcp_handler(request: Request):
    body = await request.json()
    method = body.get("method")
    params = body.get("params", {})

    if method == "get_schema":
        return {"jsonrpc": "2.0", "id": body.get("id"), "result": TOOLS_SCHEMA}
    elif method == "get_style_posts":
        result = await get_style_posts(params.get("query", "norteño"), params.get("limit", 12))
    elif method == "analyze_outfit":
        result = await analyze_outfit(params.get("description", ""))
    elif method == "trending_styles":
        result = await trending_styles(params.get("region", "MX"))
    else:
        return {"jsonrpc": "2.0", "id": body.get("id"), "error": {"code": -32601, "message": f"Method not found: {method}"}}

    return {"jsonrpc": "2.0", "id": body.get("id"), "result": result}


@app.get("/health")
async def health():
    return {"status": "ok", "service": "fashion-mcp", "port": 8005}
