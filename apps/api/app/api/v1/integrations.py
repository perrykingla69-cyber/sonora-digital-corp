"""
Integrations — Spotify OAuth + Stats
Flujo: code → token exchange → profile → DB (Fernet encrypted)
Rate limit: handled upstream (nginx 30r/m + FastAPI depends)
"""

from __future__ import annotations

import logging
import time
from typing import Optional

import httpx
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import text

from app.core.config import settings
from app.core.database import get_tenant_session
from app.core.deps import AuthUser
from app.core.redis import redis_client
from app.core.security import decrypt, encrypt

router = APIRouter()
logger = logging.getLogger(__name__)

SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE = "https://api.spotify.com/v1"

# Cache TTL — 1 hora para stats agregadas (evita martillar la API)
STATS_CACHE_TTL = 3600


# ── Helpers internos ──────────────────────────────────────────

async def _get_spotify_tokens(user_id: str, tenant_id: str) -> Optional[dict]:
    """Lee tokens de DB y los desencripta. Retorna None si no hay integración."""
    async with get_tenant_session(tenant_id) as db:
        r = await db.execute(
            text("""
                SELECT access_token_enc, refresh_token_enc, expires_at,
                       artist_name, followers, profile_image_url, spotify_user_id
                FROM spotify_integrations
                WHERE user_id = :uid AND tenant_id = :tid
            """),
            {"uid": user_id, "tid": tenant_id},
        )
        row = r.fetchone()
    if not row:
        return None
    return dict(row._mapping)


async def _refresh_spotify_token(user_id: str, tenant_id: str, refresh_token_enc: str) -> str:
    """Renueva access_token usando refresh_token. Actualiza DB. Retorna nuevo access_token."""
    if not settings.SPOTIFY_CLIENT_ID or not settings.SPOTIFY_CLIENT_SECRET:
        raise HTTPException(503, "Spotify no configurado. Contacta al administrador.")

    refresh_token = decrypt(refresh_token_enc)

    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.post(
            SPOTIFY_TOKEN_URL,
            data={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
            },
            auth=(settings.SPOTIFY_CLIENT_ID, settings.SPOTIFY_CLIENT_SECRET),
        )
        if r.status_code != 200:
            logger.error("Spotify token refresh failed: %s", r.text)
            raise HTTPException(401, "Token de Spotify expirado. Reconecta tu cuenta.")
        data = r.json()

    new_access_token = data["access_token"]
    new_expires_at = int(time.time()) + data.get("expires_in", 3600)
    new_refresh_token = data.get("refresh_token", refresh_token)  # Spotify a veces rota el refresh

    async with get_tenant_session(tenant_id) as db:
        await db.execute(
            text("""
                UPDATE spotify_integrations
                SET access_token_enc = :at,
                    refresh_token_enc = :rt,
                    expires_at = :exp,
                    updated_at = NOW()
                WHERE user_id = :uid AND tenant_id = :tid
            """),
            {
                "at": encrypt(new_access_token),
                "rt": encrypt(new_refresh_token),
                "exp": new_expires_at,
                "uid": user_id,
                "tid": tenant_id,
            },
        )

    return new_access_token


async def _get_valid_access_token(user_id: str, tenant_id: str) -> str:
    """Devuelve access_token válido, renovándolo si expiró."""
    row = await _get_spotify_tokens(user_id, tenant_id)
    if not row:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "Cuenta de Spotify no conectada. Usa POST /integrations/spotify/authorize primero.",
        )

    expires_at = row["expires_at"] or 0
    # Renovar si expira en menos de 5 minutos
    if int(time.time()) >= expires_at - 300:
        return await _refresh_spotify_token(user_id, tenant_id, row["refresh_token_enc"])

    return decrypt(row["access_token_enc"])


async def _spotify_get(path: str, access_token: str, params: Optional[dict] = None) -> dict:
    """GET a la Spotify API con manejo de 429 rate-limit."""
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get(
            f"{SPOTIFY_API_BASE}{path}",
            headers={"Authorization": f"Bearer {access_token}"},
            params=params or {},
        )
        if r.status_code == 429:
            retry_after = int(r.headers.get("Retry-After", 5))
            raise HTTPException(
                status.HTTP_429_TOO_MANY_REQUESTS,
                f"Spotify rate limit. Intenta en {retry_after}s.",
                headers={"Retry-After": str(retry_after)},
            )
        if r.status_code == 401:
            raise HTTPException(401, "Token de Spotify inválido. Reconecta tu cuenta.")
        if r.status_code == 403:
            raise HTTPException(403, "Permiso denegado por Spotify.")
        if not r.is_success:
            logger.error("Spotify API error %s: %s", r.status_code, r.text)
            raise HTTPException(502, f"Error de Spotify API: {r.status_code}")
        return r.json()


# ── Response schemas ──────────────────────────────────────────

class SpotifyAuthorizeResponse(BaseModel):
    success: bool
    artist_name: str
    followers: int
    profile_image_url: Optional[str] = None


class SpotifyStatusResponse(BaseModel):
    connected: bool
    artist_name: Optional[str] = None
    followers: Optional[int] = None
    expires_in: Optional[int] = None  # segundos restantes


class SpotifyProfileResponse(BaseModel):
    id: str
    display_name: str
    followers: int
    profile_image_url: Optional[str] = None


class SpotifyTrack(BaseModel):
    id: str
    name: str
    popularity: int
    spotify_url: str
    preview_url: Optional[str] = None


class SpotifyCurrentStatsResponse(BaseModel):
    followers: int
    monthly_listeners: Optional[int] = None  # Solo disponible via Artist API (public profile)
    total_plays: Optional[int] = None
    new_followers: Optional[int] = None
    followers_trend: str = "stable"  # up | down | stable


# ── Endpoints OAuth ───────────────────────────────────────────

@router.post(
    "/spotify/authorize",
    response_model=SpotifyAuthorizeResponse,
    summary="Conectar cuenta de Spotify",
    description="Intercambia el OAuth code por tokens y guarda la integración",
)
async def spotify_authorize(
    code: str,
    current_user: AuthUser,
):
    """
    Conecta la cuenta de Spotify del usuario.

    1. Intercambia el authorization code por access_token + refresh_token
    2. Obtiene el perfil del usuario (nombre artístico, followers, foto)
    3. Guarda tokens encriptados con Fernet en DB
    """
    if not settings.SPOTIFY_CLIENT_ID or not settings.SPOTIFY_CLIENT_SECRET:
        raise HTTPException(503, "Spotify no configurado. Contacta al administrador.")
    if not code or not code.strip():
        raise HTTPException(400, "El código de autorización es requerido.")

    uid = str(current_user.user_id)
    tid = str(current_user.tenant_id)

    # 1. Exchange code → tokens
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.post(
            SPOTIFY_TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": settings.SPOTIFY_REDIRECT_URI,
            },
            auth=(settings.SPOTIFY_CLIENT_ID, settings.SPOTIFY_CLIENT_SECRET),
        )
        if r.status_code != 200:
            logger.error("Spotify token exchange failed: %s %s", r.status_code, r.text)
            detail = "Código de autorización inválido o expirado."
            try:
                err = r.json()
                if "error_description" in err:
                    detail = err["error_description"]
            except Exception:
                pass
            raise HTTPException(400, detail)
        token_data = r.json()

    access_token = token_data["access_token"]
    refresh_token = token_data["refresh_token"]
    expires_at = int(time.time()) + token_data.get("expires_in", 3600)

    # 2. Obtener perfil
    try:
        profile = await _spotify_get("/me", access_token)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Spotify profile fetch failed: %s", e)
        raise HTTPException(502, "No se pudo obtener el perfil de Spotify.")

    artist_name = profile.get("display_name") or profile.get("id", "Artista")
    followers = profile.get("followers", {}).get("total", 0)
    images = profile.get("images", [])
    profile_image_url = images[0].get("url") if images else None
    spotify_user_id = profile.get("id", "")

    # 3. Upsert en DB (encriptado)
    async with get_tenant_session(tid) as db:
        await db.execute(
            text("""
                INSERT INTO spotify_integrations
                    (user_id, tenant_id, spotify_user_id, access_token_enc, refresh_token_enc,
                     expires_at, artist_name, followers, profile_image_url)
                VALUES
                    (:uid, :tid, :sid, :at, :rt, :exp, :name, :fol, :img)
                ON CONFLICT (user_id, tenant_id)
                DO UPDATE SET
                    spotify_user_id    = EXCLUDED.spotify_user_id,
                    access_token_enc   = EXCLUDED.access_token_enc,
                    refresh_token_enc  = EXCLUDED.refresh_token_enc,
                    expires_at         = EXCLUDED.expires_at,
                    artist_name        = EXCLUDED.artist_name,
                    followers          = EXCLUDED.followers,
                    profile_image_url  = EXCLUDED.profile_image_url,
                    updated_at         = NOW()
            """),
            {
                "uid": uid, "tid": tid,
                "sid": spotify_user_id,
                "at": encrypt(access_token),
                "rt": encrypt(refresh_token),
                "exp": expires_at,
                "name": artist_name,
                "fol": followers,
                "img": profile_image_url,
            },
        )

    logger.info("Spotify connected for user %s: %s (%d followers)", uid, artist_name, followers)

    return SpotifyAuthorizeResponse(
        success=True,
        artist_name=artist_name,
        followers=followers,
        profile_image_url=profile_image_url,
    )


@router.get(
    "/spotify/status",
    response_model=SpotifyStatusResponse,
    summary="Estado de la integración Spotify",
)
async def spotify_status(current_user: AuthUser):
    """Retorna si Spotify está conectado y datos básicos del artista."""
    uid = str(current_user.user_id)
    tid = str(current_user.tenant_id)

    row = await _get_spotify_tokens(uid, tid)
    if not row:
        return SpotifyStatusResponse(connected=False)

    expires_at = row.get("expires_at") or 0
    expires_in = max(0, expires_at - int(time.time()))

    return SpotifyStatusResponse(
        connected=True,
        artist_name=row.get("artist_name"),
        followers=row.get("followers"),
        expires_in=expires_in,
    )


@router.post(
    "/spotify/disconnect",
    summary="Desconectar cuenta de Spotify",
    status_code=200,
)
async def spotify_disconnect(current_user: AuthUser):
    """
    Revoca el acceso y elimina los tokens de la DB.
    El token de Spotify no tiene endpoint de revocación en la API pública,
    así que solo eliminamos localmente.
    """
    uid = str(current_user.user_id)
    tid = str(current_user.tenant_id)

    async with get_tenant_session(tid) as db:
        result = await db.execute(
            text("""
                DELETE FROM spotify_integrations
                WHERE user_id = :uid AND tenant_id = :tid
            """),
            {"uid": uid, "tid": tid},
        )

    deleted = result.rowcount > 0
    if not deleted:
        raise HTTPException(404, "No hay integración de Spotify activa.")

    # Invalidar caché de stats
    cache_key = f"spotify:stats:{uid}"
    await redis_client.delete(cache_key)

    logger.info("Spotify disconnected for user %s", uid)
    return {"success": True, "message": "Cuenta de Spotify desconectada."}


# ── Endpoints Stats ───────────────────────────────────────────

@router.get(
    "/spotify/me",
    response_model=SpotifyProfileResponse,
    summary="Perfil del artista en Spotify",
)
async def get_spotify_profile(current_user: AuthUser):
    """
    Obtiene el perfil actualizado del artista desde la Spotify API.
    También actualiza followers y nombre en DB.
    """
    uid = str(current_user.user_id)
    tid = str(current_user.tenant_id)

    access_token = await _get_valid_access_token(uid, tid)
    profile = await _spotify_get("/me", access_token)

    artist_name = profile.get("display_name") or profile.get("id", "Artista")
    followers = profile.get("followers", {}).get("total", 0)
    images = profile.get("images", [])
    profile_image_url = images[0].get("url") if images else None

    # Actualizar followers en DB (background sync)
    try:
        async with get_tenant_session(tid) as db:
            await db.execute(
                text("""
                    UPDATE spotify_integrations
                    SET artist_name = :name, followers = :fol,
                        profile_image_url = :img, updated_at = NOW()
                    WHERE user_id = :uid AND tenant_id = :tid
                """),
                {"name": artist_name, "fol": followers, "img": profile_image_url,
                 "uid": uid, "tid": tid},
            )
    except Exception as e:
        logger.warning("Failed to update spotify profile in DB: %s", e)

    return SpotifyProfileResponse(
        id=profile.get("id", ""),
        display_name=artist_name,
        followers=followers,
        profile_image_url=profile_image_url,
    )


@router.get(
    "/spotify/top-tracks",
    response_model=list[SpotifyTrack],
    summary="Top tracks del artista",
)
async def get_top_tracks(
    time_range: str = "medium_term",
    limit: int = 5,
    current_user: AuthUser = None,
):
    """
    Obtiene los top tracks del usuario autenticado.

    - **time_range**: short_term (4 semanas) | medium_term (6 meses) | long_term (todo el tiempo)
    - **limit**: 1-50 tracks (default: 5)
    """
    # Validación de parámetros
    valid_ranges = {"short_term", "medium_term", "long_term"}
    if time_range not in valid_ranges:
        raise HTTPException(400, f"time_range inválido. Valores: {', '.join(valid_ranges)}")
    if not 1 <= limit <= 50:
        raise HTTPException(400, "limit debe estar entre 1 y 50.")

    uid = str(current_user.user_id)
    tid = str(current_user.tenant_id)

    access_token = await _get_valid_access_token(uid, tid)
    data = await _spotify_get(
        "/me/top/tracks",
        access_token,
        params={"time_range": time_range, "limit": limit},
    )

    tracks = []
    for item in data.get("items", []):
        tracks.append(SpotifyTrack(
            id=item.get("id", ""),
            name=item.get("name", ""),
            popularity=item.get("popularity", 0),
            spotify_url=item.get("external_urls", {}).get("spotify", ""),
            preview_url=item.get("preview_url"),
        ))

    return tracks


@router.get(
    "/spotify/current-stats",
    response_model=SpotifyCurrentStatsResponse,
    summary="Estadísticas actuales del artista",
)
async def get_current_stats(current_user: AuthUser):
    """
    Estadísticas agregadas del artista. Caché de 1 hora para no martillar la API.

    Nota: monthly_listeners y total_plays no están disponibles en la Spotify Web API
    estándar (solo en Spotify for Artists). Se retornan como null a menos que
    estén disponibles vía el perfil público.
    """
    uid = str(current_user.user_id)
    tid = str(current_user.tenant_id)

    # Revisar caché
    cache_key = f"spotify:stats:{uid}"
    cached = await redis_client.get(cache_key)
    if cached:
        import json
        return SpotifyCurrentStatsResponse(**json.loads(cached))

    # Obtener perfil fresco de Spotify
    access_token = await _get_valid_access_token(uid, tid)
    profile = await _spotify_get("/me", access_token)

    current_followers = profile.get("followers", {}).get("total", 0)

    # Obtener followers previos de DB para calcular tendencia
    row = await _get_spotify_tokens(uid, tid)
    prev_followers = row.get("followers", current_followers) if row else current_followers
    new_followers = current_followers - prev_followers

    if new_followers > 0:
        trend = "up"
    elif new_followers < 0:
        trend = "down"
    else:
        trend = "stable"

    stats = SpotifyCurrentStatsResponse(
        followers=current_followers,
        monthly_listeners=None,   # Requiere Spotify for Artists API (privada)
        total_plays=None,          # Requiere Spotify for Artists API (privada)
        new_followers=new_followers if new_followers != 0 else None,
        followers_trend=trend,
    )

    # Actualizar followers en DB
    try:
        async with get_tenant_session(tid) as db:
            await db.execute(
                text("""
                    UPDATE spotify_integrations
                    SET followers = :fol, updated_at = NOW()
                    WHERE user_id = :uid AND tenant_id = :tid
                """),
                {"fol": current_followers, "uid": uid, "tid": tid},
            )
    except Exception as e:
        logger.warning("Failed to update followers in DB: %s", e)

    # Guardar en caché
    import json
    await redis_client.setex(cache_key, STATS_CACHE_TTL, json.dumps(stats.model_dump()))

    return stats
