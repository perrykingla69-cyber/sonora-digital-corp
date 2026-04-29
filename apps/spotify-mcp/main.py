"""
Spotify Trends MCP — JSON-RPC server (port 8003)
Tools: search_artist, top_tracks, related_artists, get_schema
"""
import os
import json
import httpx
from fastapi import FastAPI, Request, HTTPException

app = FastAPI(title="Spotify Trends MCP", version="1.0.0")

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID", "")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET", "")
_spotify_token: str | None = None


async def get_spotify_token() -> str:
    global _spotify_token
    if _spotify_token:
        return _spotify_token
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://accounts.spotify.com/api/token",
            data={"grant_type": "client_credentials"},
            auth=(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET),
        )
        resp.raise_for_status()
        _spotify_token = resp.json()["access_token"]
        return _spotify_token


async def search_artist(name: str) -> dict:
    token = await get_spotify_token()
    async with httpx.AsyncClient() as client:
        r = await client.get(
            "https://api.spotify.com/v1/search",
            params={"q": name, "type": "artist", "limit": 5},
            headers={"Authorization": f"Bearer {token}"},
        )
        items = r.json().get("artists", {}).get("items", [])
        return {"artists": [{"id": a["id"], "name": a["name"], "popularity": a["popularity"], "followers": a["followers"]["total"]} for a in items]}


async def top_tracks(artist_id: str, market: str = "MX") -> dict:
    token = await get_spotify_token()
    async with httpx.AsyncClient() as client:
        r = await client.get(
            f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks",
            params={"market": market},
            headers={"Authorization": f"Bearer {token}"},
        )
        tracks = r.json().get("tracks", [])
        return {"tracks": [{"name": t["name"], "popularity": t["popularity"], "preview_url": t.get("preview_url")} for t in tracks[:10]]}


async def related_artists(artist_id: str) -> dict:
    token = await get_spotify_token()
    async with httpx.AsyncClient() as client:
        r = await client.get(
            f"https://api.spotify.com/v1/artists/{artist_id}/related-artists",
            headers={"Authorization": f"Bearer {token}"},
        )
        artists = r.json().get("artists", [])
        return {"related": [{"id": a["id"], "name": a["name"], "popularity": a["popularity"]} for a in artists[:8]]}


TOOLS_SCHEMA = {
    "tools": [
        {"name": "search_artist", "description": "Search for an artist on Spotify", "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]}},
        {"name": "top_tracks", "description": "Get top tracks for an artist", "inputSchema": {"type": "object", "properties": {"artist_id": {"type": "string"}, "market": {"type": "string", "default": "MX"}}, "required": ["artist_id"]}},
        {"name": "related_artists", "description": "Get related artists", "inputSchema": {"type": "object", "properties": {"artist_id": {"type": "string"}}, "required": ["artist_id"]}},
    ]
}


@app.post("/mcp")
async def mcp_handler(request: Request):
    body = await request.json()
    method = body.get("method")
    params = body.get("params", {})

    if method == "get_schema":
        return {"jsonrpc": "2.0", "id": body.get("id"), "result": TOOLS_SCHEMA}

    if method == "search_artist":
        result = await search_artist(params.get("name", ""))
    elif method == "top_tracks":
        result = await top_tracks(params.get("artist_id", ""), params.get("market", "MX"))
    elif method == "related_artists":
        result = await related_artists(params.get("artist_id", ""))
    else:
        return {"jsonrpc": "2.0", "id": body.get("id"), "error": {"code": -32601, "message": f"Method not found: {method}"}}

    return {"jsonrpc": "2.0", "id": body.get("id"), "result": result}


@app.get("/health")
async def health():
    return {"status": "ok", "service": "spotify-mcp", "port": 8003}
