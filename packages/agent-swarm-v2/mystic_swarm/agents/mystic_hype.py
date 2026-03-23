"""
MYSTIC_HYPE - Agente de Marketing y Viralización
Gestiona campañas, drops virales, influencer seeding y growth hacking
"""
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import random

class HypeStrategy(Enum):
    DROP_LIMITADO = "drop_limitado"
    INFLUENCER_SEED = "influencer_seed"
    WAITLIST_FOMO = "waitlist_fomo"
    COLLAB_SORPRESA = "collab_sorpresa"
    RETO_VIRAL = "reto_viral"
    MYSTERY_BOX = "mystery_box"

class Platform(Enum):
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    WHATSAPP = "whatsapp"
    TWITTER_X = "twitter_x"
    YOUTUBE = "youtube"
    TELEGRAM = "telegram"

@dataclass
class InfluencerProfile:
    handle: str
    platform: Platform
    followers: int
    engagement_rate: float  # 0.0 - 1.0
    niche: str              # "streetwear", "fitness", "tech", etc.
    price_per_post: float   # MXN
    tier: str               # nano, micro, macro, mega

@dataclass
class HypeCampaign:
    campaign_id: str
    name: str
    strategy: HypeStrategy
    product_ref: str
    start_date: datetime
    end_date: datetime
    budget: float
    target_audience: Dict[str, Any]
    kpis: Dict[str, float]
    content_pieces: List[Dict] = field(default_factory=list)
    influencers: List[InfluencerProfile] = field(default_factory=list)
    results: Dict[str, Any] = field(default_factory=dict)
    status: str = "draft"

@dataclass
class WaitlistEntry:
    email: str
    phone: Optional[str]
    position: int
    referrals: int = 0
    signed_up_at: datetime = field(default_factory=datetime.now)
    vip_unlocked: bool = False

class MYSTICHypeAgent:
    """
    Agente de marketing y viralización para el ecosistema Mystic
    Crea y gestiona campañas de hype, waitlists y seeding de influencers
    """

    def __init__(self):
        self.active_campaigns: Dict[str, HypeCampaign] = {}
        self.waitlists: Dict[str, List[WaitlistEntry]] = {}
        self.influencer_db: List[InfluencerProfile] = self._seed_influencer_db()

    # ── Campañas ──────────────────────────────────────────────────────────────

    async def launch_drop_campaign(
        self,
        product_name: str,
        collection_theme: str,
        units_available: int,
        drop_date: datetime,
        budget: float = 5000.0,
        platforms: List[Platform] = None
    ) -> HypeCampaign:
        """
        Lanza campaña de drop limitado con cuenta regresiva y FOMO
        """
        platforms = platforms or [Platform.INSTAGRAM, Platform.TIKTOK, Platform.WHATSAPP]
        campaign_id = f"DROP_{collection_theme[:4].upper()}_{drop_date.strftime('%Y%m%d')}"

        campaign = HypeCampaign(
            campaign_id=campaign_id,
            name=f"Drop: {product_name}",
            strategy=HypeStrategy.DROP_LIMITADO,
            product_ref=product_name,
            start_date=datetime.now(),
            end_date=drop_date,
            budget=budget,
            target_audience={
                "age_range": "18-35",
                "interests": ["streetwear", "moda", "edición limitada"],
                "location": "México"
            },
            kpis={
                "impressions_target": units_available * 1000,
                "conversions_target": units_available,
                "engagement_rate_target": 0.05,
                "cost_per_acquisition": budget / units_available
            }
        )

        # Generar plan de contenido
        campaign.content_pieces = self._generate_drop_content_plan(
            product_name, collection_theme, units_available, drop_date, platforms
        )

        self.active_campaigns[campaign_id] = campaign
        return campaign

    def _generate_drop_content_plan(
        self,
        product: str,
        theme: str,
        units: int,
        drop_date: datetime,
        platforms: List[Platform]
    ) -> List[Dict]:
        """Genera calendario de contenido pre-drop"""
        days_before = (drop_date - datetime.now()).days
        plan = []

        # Semana previa: teaser
        if days_before >= 7:
            plan.append({
                "day": -7,
                "type": "teaser",
                "platforms": [p.value for p in platforms],
                "content": f"Algo viene... {theme} 👀",
                "hook": "No te lo puedes perder",
                "cta": "Activa notificaciones"
            })

        # 3 días antes: reveal parcial
        if days_before >= 3:
            plan.append({
                "day": -3,
                "type": "reveal_parcial",
                "platforms": [p.value for p in platforms],
                "content": f"Solo {units} unidades de {product} disponibles",
                "hook": f"¿Quieres ser uno de los {units}?",
                "cta": "Link en bio para waitlist"
            })

        # 24h antes: countdown
        plan.append({
            "day": -1,
            "type": "countdown",
            "platforms": [p.value for p in platforms],
            "content": f"24 HORAS para el drop de {product}",
            "hook": "El reloj corre...",
            "cta": "Comparte para subir en la lista"
        })

        # Día del drop: lanzamiento
        plan.append({
            "day": 0,
            "type": "launch",
            "platforms": [p.value for p in platforms],
            "content": f"YA DISPONIBLE: {product} — Edición {theme}",
            "hook": f"Solo {units} en existencia. Ahora.",
            "cta": "Ordenar ahora — link en bio"
        })

        # Post-drop: FOMO de escasez
        plan.append({
            "day": 1,
            "type": "scarcity_update",
            "platforms": [p.value for p in platforms],
            "content": f"Quedan pocas unidades de {product}",
            "hook": "Los que esperaron... perdieron",
            "cta": "Últimas unidades disponibles"
        })

        return plan

    # ── Waitlist con Referidos ────────────────────────────────────────────────

    async def create_waitlist(
        self,
        product_id: str,
        vip_threshold_referrals: int = 3
    ) -> Dict[str, Any]:
        """Crea waitlist viral con sistema de referidos"""
        self.waitlists[product_id] = []
        return {
            "product_id": product_id,
            "waitlist_url": f"https://mystic.app/waitlist/{product_id}",
            "vip_threshold": vip_threshold_referrals,
            "share_message": f"Únete antes que yo para la colección exclusiva: mystic.app/waitlist/{product_id}",
            "created_at": datetime.now().isoformat()
        }

    async def join_waitlist(
        self,
        product_id: str,
        email: str,
        phone: Optional[str] = None,
        referred_by: Optional[str] = None
    ) -> Dict[str, Any]:
        """Registra entrada en waitlist y gestiona referidos"""
        if product_id not in self.waitlists:
            return {"error": "Waitlist no encontrada"}

        wl = self.waitlists[product_id]
        position = len(wl) + 1

        entry = WaitlistEntry(email=email, phone=phone, position=position)
        wl.append(entry)

        # Bonificar al referidor
        if referred_by:
            for e in wl:
                if e.email == referred_by:
                    e.referrals += 1
                    if e.referrals >= 3:
                        e.vip_unlocked = True

        return {
            "position": position,
            "email": email,
            "share_url": f"https://mystic.app/waitlist/{product_id}?ref={email.split('@')[0]}",
            "message": f"Estás en el puesto #{position}. Refiere 3 amigos para acceso VIP."
        }

    # ── Influencer Seeding ────────────────────────────────────────────────────

    async def find_influencers(
        self,
        niche: str,
        budget: float,
        min_engagement: float = 0.03,
        preferred_tier: str = "micro"
    ) -> List[Dict]:
        """Encuentra influencers óptimos para el presupuesto"""
        candidates = [
            inf for inf in self.influencer_db
            if inf.niche == niche
            and inf.engagement_rate >= min_engagement
            and inf.price_per_post <= budget
            and inf.tier == preferred_tier
        ]

        candidates.sort(key=lambda x: x.engagement_rate * x.followers, reverse=True)

        return [
            {
                "handle": inf.handle,
                "platform": inf.platform.value,
                "followers": inf.followers,
                "engagement": f"{inf.engagement_rate*100:.1f}%",
                "niche": inf.niche,
                "price_per_post": inf.price_per_post,
                "tier": inf.tier,
                "estimated_reach": int(inf.followers * inf.engagement_rate)
            }
            for inf in candidates[:10]
        ]

    async def create_seeding_kit(
        self,
        product_name: str,
        collection_theme: str,
        influencer: InfluencerProfile
    ) -> Dict[str, Any]:
        """Genera kit de briefing para influencer"""
        return {
            "influencer": influencer.handle,
            "product": product_name,
            "briefing": {
                "objetivo": f"Generar hype para el drop de {product_name}",
                "tono": "Auténtico, casual, exclusivo — NO parecer anuncio",
                "mensajes_clave": [
                    f"Colección limitada {collection_theme}",
                    "Solo para los que saben",
                    "Edición firmada — no se repite"
                ],
                "no_hacer": [
                    "No mencionar precio directamente",
                    "No usar hashtags genéricos de marca",
                    "No hacer unboxing forzado"
                ],
                "formatos_sugeridos": self._get_formats_by_platform(influencer.platform),
                "cta": "Link en bio / Swipe up / Responde para info"
            },
            "assets_provistos": [
                "Pack de fotos HD del producto",
                "Logo vectorial Mystic",
                "Paleta de colores de temporada",
                "Texto de pie sugerido"
            ],
            "deadline_post": (datetime.now() + timedelta(days=2)).isoformat(),
            "pago_acordado": influencer.price_per_post
        }

    def _get_formats_by_platform(self, platform: Platform) -> List[str]:
        formats = {
            Platform.INSTAGRAM: ["Reel 15-30s", "Story con link", "Carrusel producto"],
            Platform.TIKTOK: ["Video POV 15-60s", "Dueto con trend", "Get Ready With Me"],
            Platform.YOUTUBE: ["Mención en video", "Shorts unboxing"],
            Platform.TWITTER_X: ["Tweet con foto", "Thread de colección"],
            Platform.WHATSAPP: ["Status con imagen", "Mensaje a comunidad"],
            Platform.TELEGRAM: ["Post en canal", "Story"]
        }
        return formats.get(platform, ["Post estándar"])

    # ── Analytics y ROI ───────────────────────────────────────────────────────

    async def calculate_campaign_roi(
        self,
        campaign_id: str,
        units_sold: int,
        revenue: float
    ) -> Dict[str, Any]:
        """Calcula ROI real de una campaña"""
        campaign = self.active_campaigns.get(campaign_id)
        if not campaign:
            return {"error": "Campaña no encontrada"}

        roi = ((revenue - campaign.budget) / campaign.budget) * 100
        cac = campaign.budget / units_sold if units_sold > 0 else 0

        campaign.results = {
            "units_sold": units_sold,
            "revenue": revenue,
            "spend": campaign.budget,
            "profit": revenue - campaign.budget,
            "roi_pct": round(roi, 2),
            "cac": round(cac, 2),
            "roas": round(revenue / campaign.budget, 2)
        }
        campaign.status = "completed"

        return campaign.results

    # ── Seed Data ─────────────────────────────────────────────────────────────

    def _seed_influencer_db(self) -> List[InfluencerProfile]:
        """Base de datos de ejemplo de influencers"""
        return [
            InfluencerProfile("@street_mex", Platform.INSTAGRAM, 45_000, 0.072, "streetwear", 1_800, "micro"),
            InfluencerProfile("@modamxtt", Platform.TIKTOK, 120_000, 0.095, "streetwear", 3_500, "macro"),
            InfluencerProfile("@elstilo_mx", Platform.INSTAGRAM, 18_000, 0.11, "streetwear", 900, "nano"),
            InfluencerProfile("@fitnessmx_pro", Platform.INSTAGRAM, 65_000, 0.058, "fitness", 2_200, "micro"),
            InfluencerProfile("@techlifemx", Platform.YOUTUBE, 90_000, 0.041, "tech", 4_000, "macro"),
            InfluencerProfile("@gorras.mx", Platform.TIKTOK, 32_000, 0.13, "streetwear", 1_200, "micro"),
        ]
