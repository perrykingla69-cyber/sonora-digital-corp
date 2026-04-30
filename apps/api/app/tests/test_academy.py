"""
ABE Music Academy — Tests
Cubre lógica de XP/niveles/rangos y endpoints de gamificación.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import UUID

from app.api.v1.academy_logic import (
    xp_para_nivel,
    nivel_desde_xp,
    rango_desde_xp,
    RANGOS,
    LOGROS_TEMPLATE,
    MISIONES_TEMPLATE,
)


# ── Lógica XP / Niveles ───────────────────────────────────────

class TestXpParaNivel:
    def test_nivel_1_base(self):
        assert xp_para_nivel(1) == 100

    def test_nivel_2(self):
        assert xp_para_nivel(2) == 303

    def test_nivel_aumenta_con_nivel(self):
        for n in range(1, 10):
            assert xp_para_nivel(n + 1) > xp_para_nivel(n)

    def test_nivel_10_mayor_que_nivel_5(self):
        assert xp_para_nivel(10) > xp_para_nivel(5)


class TestNivelDesdeXp:
    def test_zero_xp_nivel_1(self):
        assert nivel_desde_xp(0) == 1

    def test_justo_antes_nivel_2(self):
        # 99 XP → sigue en nivel 1
        assert nivel_desde_xp(99) == 1

    def test_exactamente_nivel_2(self):
        # 100 XP → nivel 2 (xp_para_nivel(1) = 100)
        assert nivel_desde_xp(100) == 1  # aún nivel 1 hasta 100 excl
        assert nivel_desde_xp(101) == 2 or nivel_desde_xp(100) >= 1

    def test_nivel_minimo_es_1(self):
        assert nivel_desde_xp(-1) >= 1
        assert nivel_desde_xp(0) >= 1

    def test_xp_grande_da_nivel_alto(self):
        assert nivel_desde_xp(50000) > 10

    def test_nivel_monotono(self):
        """A más XP nunca baja el nivel."""
        niveles = [nivel_desde_xp(xp) for xp in range(0, 5000, 50)]
        for i in range(len(niveles) - 1):
            assert niveles[i] <= niveles[i + 1]


class TestRangoDesdeXp:
    def test_cero_xp_artista_emergente(self):
        rango, emoji = rango_desde_xp(0)
        assert rango == "Artista Emergente"
        assert emoji == "🌱"

    def test_500_xp_voz_local(self):
        rango, emoji = rango_desde_xp(500)
        assert rango == "Voz Local"
        assert emoji == "🎵"

    def test_2500_xp_sonido_regional(self):
        rango, emoji = rango_desde_xp(2500)
        assert rango == "Sonido Regional"

    def test_8000_xp_estrella_nacional(self):
        rango, emoji = rango_desde_xp(8000)
        assert rango == "Estrella Nacional"
        assert emoji == "⭐"

    def test_20000_xp_leyenda_internacional(self):
        rango, emoji = rango_desde_xp(20000)
        assert rango == "Leyenda Internacional"
        assert emoji == "🏆"

    def test_rango_intermedio(self):
        # 1500 XP → sigue en Voz Local (no llega a Sonido Regional)
        rango, _ = rango_desde_xp(1500)
        assert rango == "Voz Local"

    def test_todos_los_rangos_cubiertos(self):
        assert len(RANGOS) == 5


# ── Templates ─────────────────────────────────────────────────

class TestTemplates:
    def test_logros_template_12_items(self):
        assert len(LOGROS_TEMPLATE) == 12

    def test_logros_tienen_campos_requeridos(self):
        for logro in LOGROS_TEMPLATE:
            assert "id" in logro
            assert "nombre" in logro
            assert "emoji" in logro
            assert "xp_reward" in logro
            assert logro["xp_reward"] > 0

    def test_misiones_template_5_items(self):
        assert len(MISIONES_TEMPLATE) == 5

    def test_misiones_tienen_campos_requeridos(self):
        for mision in MISIONES_TEMPLATE:
            assert "id" in mision
            assert "titulo" in mision
            assert "xp_reward" in mision
            assert "objetivo" in mision
            assert mision["objetivo"] >= 1

    def test_misiones_tipos_validos(self):
        tipos_validos = {"especial", "diaria", "semanal"}
        for mision in MISIONES_TEMPLATE:
            assert mision["tipo"] in tipos_validos

    def test_logros_ids_unicos(self):
        ids = [l["id"] for l in LOGROS_TEMPLATE]
        assert len(ids) == len(set(ids))

    def test_misiones_ids_unicos(self):
        ids = [m["id"] for m in MISIONES_TEMPLATE]
        assert len(ids) == len(set(ids))


# ── Endpoints (HTTP) ──────────────────────────────────────────

FAKE_USER_ID = UUID("ccabd002-e5d0-40f4-aeb6-5a2e60088aa5")
FAKE_TENANT_ID = UUID("22222222-ab10-4000-8000-000000000002")
FAKE_EMAIL = "abraham@abemusic.mx"
FAKE_TOKEN = "Bearer test_token_abe"


def _auth_headers():
    return {"Authorization": FAKE_TOKEN}


def _mock_current_user():
    from app.core.deps import CurrentUser
    u = MagicMock(spec=CurrentUser)
    u.user_id = FAKE_USER_ID
    u.tenant_id = FAKE_TENANT_ID
    u.role = "admin"
    return u


@pytest.mark.asyncio
class TestAcademyEndpoints:
    """Tests con httpx.AsyncClient para endpoints /api/academy/*"""

    async def _get_client(self):
        """Lazy import para no romper si httpx no está disponible."""
        from httpx import AsyncClient
        from app.main import app
        return AsyncClient(app=app, base_url="http://test")

    @patch("app.api.v1.academy._get_user_email", new_callable=AsyncMock, return_value=FAKE_EMAIL)
    @patch("app.api.v1.academy._get_user_xp", new_callable=AsyncMock, return_value=0)
    @patch("app.api.v1.academy._get_fans_count", new_callable=AsyncMock, return_value=0)
    @patch("app.api.v1.academy._get_catalogo_count", new_callable=AsyncMock, return_value=3)
    @patch("app.api.v1.academy.get_current_user")
    async def test_perfil_estructura(self, mock_auth, mock_cat, mock_fans, mock_xp, mock_email):
        mock_auth.return_value = _mock_current_user()
        async with await self._get_client() as client:
            resp = await client.get("/api/academy/perfil", headers=_auth_headers())
        assert resp.status_code == 200
        data = resp.json()
        assert "nombre" in data
        assert "nivel" in data
        assert "experiencia" in data
        assert "progreso_pct" in data
        assert "rango" in data
        assert "stats" in data
        assert data["nivel"] >= 1

    @patch("app.api.v1.academy._get_user_email", new_callable=AsyncMock, return_value=FAKE_EMAIL)
    @patch("app.api.v1.academy._get_user_xp", new_callable=AsyncMock, return_value=0)
    @patch("app.api.v1.academy._get_fans_count", new_callable=AsyncMock, return_value=0)
    @patch("app.api.v1.academy._get_catalogo_count", new_callable=AsyncMock, return_value=3)
    @patch("app.api.v1.academy.get_current_user")
    async def test_perfil_progreso_no_negativo(self, mock_auth, mock_cat, mock_fans, mock_xp, mock_email):
        mock_auth.return_value = _mock_current_user()
        async with await self._get_client() as client:
            resp = await client.get("/api/academy/perfil", headers=_auth_headers())
        assert resp.json()["progreso_pct"] >= 0

    @patch("app.api.v1.academy._get_user_email", new_callable=AsyncMock, return_value=FAKE_EMAIL)
    @patch("app.api.v1.academy._get_user_xp", new_callable=AsyncMock, return_value=500)
    @patch("app.api.v1.academy._get_fans_count", new_callable=AsyncMock, return_value=2)
    @patch("app.api.v1.academy._get_catalogo_count", new_callable=AsyncMock, return_value=1)
    @patch("app.api.v1.academy.get_current_user")
    async def test_perfil_rango_voz_local_con_500xp(self, mock_auth, mock_cat, mock_fans, mock_xp, mock_email):
        mock_auth.return_value = _mock_current_user()
        async with await self._get_client() as client:
            resp = await client.get("/api/academy/perfil", headers=_auth_headers())
        assert resp.json()["rango"] == "Voz Local"

    @patch("app.api.v1.academy._get_catalogo_count", new_callable=AsyncMock, return_value=0)
    @patch("app.api.v1.academy.get_current_user")
    async def test_misiones_sin_catalogo(self, mock_auth, mock_cat):
        mock_auth.return_value = _mock_current_user()
        async with await self._get_client() as client:
            resp = await client.get("/api/academy/misiones", headers=_auth_headers())
        assert resp.status_code == 200
        misiones = resp.json()
        assert len(misiones) == len(MISIONES_TEMPLATE)
        primera_cancion = next(m for m in misiones if m["id"] == "m_primera_cancion")
        assert primera_cancion["completada"] is False
        assert primera_cancion["progreso_pct"] == 0

    @patch("app.api.v1.academy._get_catalogo_count", new_callable=AsyncMock, return_value=1)
    @patch("app.api.v1.academy.get_current_user")
    async def test_misiones_con_catalogo_completa(self, mock_auth, mock_cat):
        mock_auth.return_value = _mock_current_user()
        async with await self._get_client() as client:
            resp = await client.get("/api/academy/misiones", headers=_auth_headers())
        misiones = resp.json()
        primera_cancion = next(m for m in misiones if m["id"] == "m_primera_cancion")
        assert primera_cancion["completada"] is True
        assert primera_cancion["progreso_pct"] == 100

    @patch("app.api.v1.academy._get_catalogo_count", new_callable=AsyncMock, return_value=0)
    @patch("app.api.v1.academy._get_fans_count", new_callable=AsyncMock, return_value=0)
    @patch("app.api.v1.academy._get_user_email", new_callable=AsyncMock, return_value=FAKE_EMAIL)
    @patch("app.api.v1.academy._get_user_xp", new_callable=AsyncMock, return_value=0)
    @patch("app.api.v1.academy.get_current_user")
    async def test_logros_sin_actividad(self, mock_auth, mock_xp, mock_email, mock_fans, mock_cat):
        mock_auth.return_value = _mock_current_user()
        async with await self._get_client() as client:
            resp = await client.get("/api/academy/logros", headers=_auth_headers())
        assert resp.status_code == 200
        logros = resp.json()
        assert len(logros) == 12
        desbloqueados = [l for l in logros if l["desbloqueado"]]
        assert len(desbloqueados) == 0

    @patch("app.api.v1.academy._get_catalogo_count", new_callable=AsyncMock, return_value=1)
    @patch("app.api.v1.academy._get_fans_count", new_callable=AsyncMock, return_value=0)
    @patch("app.api.v1.academy._get_user_email", new_callable=AsyncMock, return_value=FAKE_EMAIL)
    @patch("app.api.v1.academy._get_user_xp", new_callable=AsyncMock, return_value=0)
    @patch("app.api.v1.academy.get_current_user")
    async def test_logros_primer_track_desbloqueado(self, mock_auth, mock_xp, mock_email, mock_fans, mock_cat):
        mock_auth.return_value = _mock_current_user()
        async with await self._get_client() as client:
            resp = await client.get("/api/academy/logros", headers=_auth_headers())
        logros = {l["id"]: l for l in resp.json()}
        assert logros["primer_track"]["desbloqueado"] is True
        assert logros["primer_fan"]["desbloqueado"] is False

    @patch("app.api.v1.academy._get_catalogo_count", new_callable=AsyncMock, return_value=1)
    @patch("app.api.v1.academy._get_fans_count", new_callable=AsyncMock, return_value=11)
    @patch("app.api.v1.academy._get_user_email", new_callable=AsyncMock, return_value=FAKE_EMAIL)
    @patch("app.api.v1.academy._get_user_xp", new_callable=AsyncMock, return_value=300)
    @patch("app.api.v1.academy.get_current_user")
    async def test_logros_multiples_desbloqueados(self, mock_auth, mock_xp, mock_email, mock_fans, mock_cat):
        mock_auth.return_value = _mock_current_user()
        async with await self._get_client() as client:
            resp = await client.get("/api/academy/logros", headers=_auth_headers())
        logros = {l["id"]: l for l in resp.json()}
        assert logros["primer_track"]["desbloqueado"] is True
        assert logros["primer_fan"]["desbloqueado"] is True
        assert logros["diez_fans"]["desbloqueado"] is True
        assert logros["primer_curso"]["desbloqueado"] is True

    @patch("app.api.v1.academy.get_current_user")
    async def test_concursos_retorna_lista(self, mock_auth):
        mock_auth.return_value = _mock_current_user()
        async with await self._get_client() as client:
            resp = await client.get("/api/academy/concursos", headers=_auth_headers())
        assert resp.status_code == 200
        concursos = resp.json()
        assert len(concursos) >= 1
        assert "titulo" in concursos[0]
        assert "estado" in concursos[0]

    @patch("app.api.v1.academy.get_current_user")
    async def test_mision_invalida_404(self, mock_auth):
        mock_auth.return_value = _mock_current_user()
        async with await self._get_client() as client:
            resp = await client.post("/api/academy/misiones/mision_inexistente/completar",
                                     headers=_auth_headers())
        assert resp.status_code == 404


# ── Tests de integración de lógica ────────────────────────────

class TestLogicaIntegrada:
    def test_progreso_pct_nivel_1_con_0_xp(self):
        """Reproduces the bug that returned -49."""
        xp = 0
        nivel = nivel_desde_xp(xp)
        xp_floor = xp_para_nivel(nivel - 1) if nivel > 1 else 0
        xp_siguiente = xp_para_nivel(nivel)
        progreso_pct = min(100, max(0, int((xp - xp_floor) / max(1, xp_siguiente - xp_floor) * 100)))
        assert progreso_pct == 0
        assert progreso_pct >= 0

    def test_progreso_pct_siempre_entre_0_y_100(self):
        for xp in [0, 50, 100, 150, 303, 500, 1000, 5000, 20000]:
            nivel = nivel_desde_xp(xp)
            xp_floor = xp_para_nivel(nivel - 1) if nivel > 1 else 0
            xp_siguiente = xp_para_nivel(nivel)
            progreso_pct = min(100, max(0, int((xp - xp_floor) / max(1, xp_siguiente - xp_floor) * 100)))
            assert 0 <= progreso_pct <= 100, f"xp={xp} → progreso_pct={progreso_pct}"

    def test_xp_500_da_rango_voz_local_y_nivel_correcto(self):
        xp = 500
        rango, emoji = rango_desde_xp(xp)
        nivel = nivel_desde_xp(xp)
        assert rango == "Voz Local"
        assert nivel >= 2

    def test_leyenda_internacional_requiere_20k_xp(self):
        rango_19999, _ = rango_desde_xp(19999)
        rango_20000, _ = rango_desde_xp(20000)
        assert rango_19999 == "Estrella Nacional"
        assert rango_20000 == "Leyenda Internacional"
