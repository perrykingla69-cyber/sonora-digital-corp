"""
MYSTIC SWARM COORDINATOR
Orquestador central que coordina todos los agentes del ecosistema
"""
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import asyncio

from .agents.mystic_merch import MYSTICMerchAgent, ProductCategory, SeasonalCollection
from .agents.mystic_vision import MYSTICVisionAgent
from .agents.mystic_academy import MysticAcademy, gamificar_agente
from .agents.mystic_chain import MYSTICChainAgent, ChainNetwork
from .agents.mystic_hype import MYSTICHypeAgent, Platform

class SwarmTask(Enum):
    LAUNCH_COLLECTION = "launch_collection"
    CREATE_CONTENT = "create_content"
    MINT_NFTS = "mint_nfts"
    RUN_CAMPAIGN = "run_campaign"
    FULL_DROP = "full_drop"  # Orquesta todo el pipeline

@dataclass
class SwarmResult:
    task: SwarmTask
    tenant_id: str
    success: bool
    data: Dict[str, Any]
    agents_used: List[str]
    duration_ms: float
    created_at: datetime = field(default_factory=datetime.now)
    errors: List[str] = field(default_factory=list)

class MysticSwarmCoordinator:
    """
    Coordinador central del Mystic Agent Swarm V2.
    Orquesta Merch + Vision + Academy + Chain + Hype en pipelines cohesivos.
    """

    def __init__(self, config: Optional[Dict] = None):
        cfg = config or {}
        self.merch   = MYSTICMerchAgent(printful_api_key=cfg.get("printful_key"))
        self.vision  = MYSTICVisionAgent(ollama_url=cfg.get("ollama_url", "http://localhost:11434"))
        self.academy = MysticAcademy()
        self.chain   = MYSTICChainAgent(rpc_url=cfg.get("rpc_url"))
        self.hype    = MYSTICHypeAgent()
        self._results: List[SwarmResult] = []

    # ── Pipeline principal: Full Drop ─────────────────────────────────────────

    async def run_full_drop_pipeline(
        self,
        tenant_id: str,
        season: str,
        theme: str,
        signature: str,
        categories: List[ProductCategory],
        max_units: int = 100,
        budget_marketing: float = 5_000.0,
        mint_nfts: bool = True,
        drop_date: Optional[datetime] = None
    ) -> SwarmResult:
        """
        Pipeline completo de lanzamiento:
        1. Crear colección (Merch)
        2. Generar lookbook (Vision)
        3. Mintear NFTs (Chain)
        4. Crear waitlist + campaña de hype (Hype)
        5. Registrar agentes en academia (Academy)
        """
        start = datetime.now()
        agents_used = []
        errors = []
        result_data: Dict[str, Any] = {}

        drop_dt = drop_date or datetime.now().replace(hour=12, minute=0) + __import__('datetime').timedelta(days=7)

        # 1. Colección de merch
        try:
            collection = await self.merch.create_seasonal_collection(
                tenant_id=tenant_id,
                season=season,
                theme=theme,
                signature=signature,
                categories=categories,
                max_units=max_units
            )
            projection = await self.merch.calculate_profit_projection(collection, budget_marketing)
            result_data["collection"] = {
                "season": collection.season,
                "theme": collection.theme,
                "products": len(collection.products),
                "projection": projection
            }
            agents_used.append("MYSTICMerchAgent")
        except Exception as e:
            errors.append(f"Merch: {e}")

        # 2. Lookbook visual (paralelo con paso 3 y 4)
        vision_task = asyncio.create_task(
            self.vision.create_seasonal_lookbook(
                collection_theme=theme,
                products=[p.name for p in collection.products[:6]] if "collection" in result_data else [],
                num_shots=6
            )
        )

        # 3. Mint NFTs (opcional)
        chain_task = None
        if mint_nfts:
            chain_task = asyncio.create_task(
                self.chain.mint_collection_nft(
                    collection_name=f"{theme} {season}",
                    theme=theme,
                    signature=signature,
                    max_supply=max_units,
                    network=ChainNetwork.POLYGON
                )
            )

        # 4. Campaña de hype
        hype_task = asyncio.create_task(
            self.hype.launch_drop_campaign(
                product_name=f"{theme} Collection",
                collection_theme=theme,
                units_available=max_units,
                drop_date=drop_dt,
                budget=budget_marketing
            )
        )

        # Esperar tareas paralelas
        lookbook = await vision_task
        result_data["lookbook_shots"] = len(lookbook)
        agents_used.append("MYSTICVisionAgent")

        if chain_task:
            try:
                nft_result = await chain_task
                result_data["nfts"] = nft_result
                agents_used.append("MYSTICChainAgent")
            except Exception as e:
                errors.append(f"Chain: {e}")

        try:
            campaign = await hype_task
            waitlist = await self.hype.create_waitlist(campaign.campaign_id)
            result_data["campaign"] = {
                "id": campaign.campaign_id,
                "content_pieces": len(campaign.content_pieces),
                "waitlist_url": waitlist["waitlist_url"]
            }
            agents_used.append("MYSTICHypeAgent")
        except Exception as e:
            errors.append(f"Hype: {e}")

        # 5. Registrar en academia
        estudiante = gamificar_agente(self.academy, tenant_id, f"Tenant_{tenant_id[:8]}")
        estudiante.ganar_xp(150, f"Lanzó colección: {theme}")
        result_data["academy"] = estudiante._generar_resumen()
        agents_used.append("MysticAcademy")

        duration = (datetime.now() - start).total_seconds() * 1000

        result = SwarmResult(
            task=SwarmTask.FULL_DROP,
            tenant_id=tenant_id,
            success=len(errors) == 0,
            data=result_data,
            agents_used=agents_used,
            duration_ms=round(duration, 2),
            errors=errors
        )
        self._results.append(result)
        return result

    # ── Pipelines individuales ────────────────────────────────────────────────

    async def create_collection_only(
        self,
        tenant_id: str,
        season: str,
        theme: str,
        signature: str,
        categories: List[ProductCategory],
        max_units: int = 100
    ) -> SeasonalCollection:
        return await self.merch.create_seasonal_collection(
            tenant_id, season, theme, signature, categories, max_units
        )

    async def generate_content_pack(
        self,
        product_name: str,
        platforms: List[str] = None
    ) -> Dict:
        platforms = platforms or ["instagram", "tiktok", "whatsapp"]
        images = await self.vision.generate_social_content_pack(product_name, platforms)
        fomo_content = []  # Se puede extender con hype agent
        return {"images": {k: len(v) for k, v in images.items()}, "fomo_content": fomo_content}

    async def run_campaign_only(
        self,
        tenant_id: str,
        product_name: str,
        theme: str,
        units: int,
        budget: float,
        drop_date: datetime
    ) -> Dict:
        campaign = await self.hype.launch_drop_campaign(
            product_name, theme, units, drop_date, budget
        )
        waitlist = await self.hype.create_waitlist(campaign.campaign_id)
        return {"campaign_id": campaign.campaign_id, "waitlist": waitlist}

    # ── Historial y métricas ──────────────────────────────────────────────────

    def get_swarm_summary(self) -> Dict[str, Any]:
        """Resumen de todas las operaciones del swarm"""
        total = len(self._results)
        successful = sum(1 for r in self._results if r.success)
        avg_duration = sum(r.duration_ms for r in self._results) / total if total else 0

        agent_usage: Dict[str, int] = {}
        for r in self._results:
            for agent in r.agents_used:
                agent_usage[agent] = agent_usage.get(agent, 0) + 1

        return {
            "total_operations": total,
            "successful": successful,
            "failed": total - successful,
            "success_rate": f"{(successful/total*100):.1f}%" if total else "N/A",
            "avg_duration_ms": round(avg_duration, 2),
            "agent_usage": agent_usage,
            "leaderboard": self.academy.obtener_leaderboard(5)
        }
