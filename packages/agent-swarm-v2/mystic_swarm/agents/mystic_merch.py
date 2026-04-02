"""
MYSTIC_MERCH - Agente de Merchandising Print-on-Demand
Crea productos variables, gestiona proveedores, sincroniza con Printful disfrazado
"""
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import httpx
import json

class ProductCategory(Enum):
    GORRAS = "gorras"
    ACCESORIOS_HOMBRE = "accesorios_hombre"
    ACCESORIOS_MUJER = "accesorios_mujer"
    ROPA_NICHO = "ropa_nicho"
    EDICION_LIMITADA = "edicion_limitada"

class SupplierType(Enum):
    MEXICO_LOCAL = "mexico_local"
    IMPORTACION_USA = "importacion_usa"
    IMPORTACION_CHINA = "importacion_china"
    PRINTFUL_GLOBAL = "printful_global"

@dataclass
class ProductVariant:
    sku: str
    name: str
    color: str
    size: Optional[str]
    base_cost: float
    retail_price: float
    stock_available: int
    supplier: SupplierType

@dataclass
class SeasonalCollection:
    season: str  # "verano_2026", "otoño_2026"
    theme: str
    max_units: int
    signature: str  # Firma del cliente
    products: List[ProductVariant] = field(default_factory=list)
    launch_date: datetime = field(default_factory=datetime.now)
    fomo_deadline: Optional[datetime] = None

@dataclass
class PrintfulOrder:
    order_id: str
    external_id: str  # ID del cliente
    items: List[Dict]
    branding: Dict[str, str]  # Logo, colores, nombre marca
    shipping: Dict[str, Any]
    status: str = "draft"  # draft, pending, processing, shipped

class MYSTICMerchAgent:
    """
    Agente especializado en crear y gestionar merch personalizado
    con proveedores de calidad y sistema Printful disfrazado
    """
    
    def __init__(self, printful_api_key: Optional[str] = None):
        self.printful_key = printful_api_key
        self.supplier_db = self._init_suppliers()
        self.active_collections: Dict[str, SeasonalCollection] = {}
        
    def _init_suppliers(self) -> Dict[SupplierType, List[Dict]]:
        """Base de datos de proveedores calificados"""
        return {
            SupplierType.MEXICO_LOCAL: [
                {"name": "GorrasPremiumMX", "location": "CDMX", "moq": 12, "lead_time_days": 3, "quality_score": 4.8},
                {"name": "AccesoriosJalisco", "location": "Guadalajara", "moq": 24, "lead_time_days": 5, "quality_score": 4.6},
            ],
            SupplierType.IMPORTACION_USA: [
                {"name": "CapAmerica", "location": "Florida", "moq": 48, "lead_time_days": 14, "quality_score": 4.9},
            ],
            SupplierType.PRINTFUL_GLOBAL: [
                {"name": "Printful_US", "location": "USA/Latvia", "moq": 1, "lead_time_days": 7, "quality_score": 4.7},
            ]
        }
    
    async def create_seasonal_collection(
        self,
        tenant_id: str,
        season: str,
        theme: str,
        signature: str,
        categories: List[ProductCategory],
        max_units: int = 100,
        fomo_days: int = 7
    ) -> SeasonalCollection:
        """
        Crea una colección temporal firmada con FOMO integrado
        """
        collection = SeasonalCollection(
            season=season,
            theme=theme,
            max_units=max_units,
            signature=signature,
            fomo_deadline=datetime.now() + __import__('datetime').timedelta(days=fomo_days)
        )
        
        # Generar productos variables por categoría
        for category in categories:
            variants = await self._generate_variants(category, theme, signature)
            collection.products.extend(variants)
        
        self.active_collections[f"{tenant_id}_{season}"] = collection
        
        return collection
    
    async def _generate_variants(
        self,
        category: ProductCategory,
        theme: str,
        signature: str
    ) -> List[ProductVariant]:
        """Genera variantes de producto según categoría"""
        variants = []
        
        if category == ProductCategory.GORRAS:
            colors = ["Negro", "Blanco", "Beige", "Navy"]
            for i, color in enumerate(colors):
                variants.append(ProductVariant(
                    sku=f"GOR-{theme[:3].upper()}-{color[:3].upper()}-{i}",
                    name=f"Gorra {theme} - {color} (Firmada: {signature})",
                    color=color,
                    size=None,
                    base_cost=180.0,  # MXN
                    retail_price=450.0,
                    stock_available=25,
                    supplier=SupplierType.MEXICO_LOCAL
                ))
        
        elif category == ProductCategory.ACCESORIOS_HOMBRE:
            items = ["Cinturón Premium", "Cartera Minimal", "Llavero Metálico"]
            for item in items:
                variants.append(ProductVariant(
                    sku=f"ACC-H-{item[:3].upper()}-{theme[:3].upper()}",
                    name=f"{item} {theme} (Ed. {signature})",
                    color="Negro/Café",
                    size="Único",
                    base_cost=120.0,
                    retail_price=350.0,
                    stock_available=15,
                    supplier=SupplierType.MEXICO_LOCAL
                ))
        
        # Similar para otros categorías...
        
        return variants
    
    async def find_optimal_supplier(
        self,
        product_type: ProductCategory,
        quantity: int,
        priority: str = "quality"  # quality, speed, cost
    ) -> Tuple[SupplierType, Dict]:
        """
        Encuentra el mejor proveedor según prioridad
        """
        candidates = []
        
        for supplier_type, suppliers in self.supplier_db.items():
            for supplier in suppliers:
                if supplier["moq"] <= quantity:
                    score = self._calculate_supplier_score(supplier, priority)
                    candidates.append((supplier_type, supplier, score))
        
        # Ordenar por score
        candidates.sort(key=lambda x: x[2], reverse=True)
        
        return candidates[0][0], candidates[0][1] if candidates else (SupplierType.PRINTFUL_GLOBAL, {})
    
    def _calculate_supplier_score(self, supplier: Dict, priority: str) -> float:
        """Calcula score ponderado del proveedor"""
        weights = {
            "quality": {"quality": 0.6, "speed": 0.2, "cost": 0.2},
            "speed": {"quality": 0.2, "speed": 0.6, "cost": 0.2},
            "cost": {"quality": 0.2, "speed": 0.2, "cost": 0.6}
        }
        
        w = weights.get(priority, weights["quality"])
        
        # Normalizar métricas (0-1)
        quality_norm = supplier["quality_score"] / 5.0
        speed_norm = 1 - (supplier["lead_time_days"] / 30)  # Menos días = mejor
        cost_norm = 0.5  # Placeholder para costo
        
        return (quality_norm * w["quality"] + 
                speed_norm * w["speed"] + 
                cost_norm * w["cost"])
    
    async def create_printful_order(
        self,
        tenant_id: str,
        customer_data: Dict[str, Any],
        items: List[Dict],
        branding: Dict[str, str]
    ) -> PrintfulOrder:
        """
        Crea orden en Printful solo cuando el cliente paga (disfrazado)
        """
        # Simulación - en producción llamaría a Printful API
        order = PrintfulOrder(
            order_id=f"MYSTIC-{datetime.now().strftime('%Y%m%d%H%M%S')}-{tenant_id[:6]}",
            external_id=tenant_id,
            items=items,
            branding=branding,
            shipping=customer_data.get("shipping", {}),
            status="pending"
        )
        
        # Aquí iría la llamada real a Printful:
        # async with httpx.AsyncClient() as client:
        #     response = await client.post(
        #         "https://api.printful.com/orders",
        #         headers={"Authorization": f"Bearer {self.printful_key}"},
        #         json={...}
        #     )
        
        return order
    
    async def calculate_profit_projection(
        self,
        collection: SeasonalCollection,
        marketing_budget: float = 0
    ) -> Dict[str, Any]:
        """
        Calcula proyección de ganancias para una colección
        """
        total_cost = sum(p.base_cost for p in collection.products)
        total_revenue = sum(p.retail_price for p in collection.products)
        potential_profit = total_revenue - total_cost - marketing_budget
        
        return {
            "collection": collection.theme,
            "units": len(collection.products),
            "cost_total": total_cost,
            "revenue_potential": total_revenue,
            "profit_potential": potential_profit,
            "margin_percent": (potential_profit / total_revenue * 100) if total_revenue > 0 else 0,
            "break_even_units": int(total_cost / (total_revenue / len(collection.products))) if collection.products else 0
        }
    
    async def generate_fomo_content(
        self,
        collection: SeasonalCollection,
        platforms: List[str] = ["instagram", "tiktok", "whatsapp"]
    ) -> List[Dict[str, str]]:
        """
        Genera contenido listo para redes con FOMO
        """
        days_left = (collection.fomo_deadline - datetime.now()).days
        
        content = []
        for platform in platforms:
            if platform == "instagram":
                content.append({
                    "platform": platform,
                    "format": "carousel",
                    "caption": f"🔥 COLECCIÓN {collection.theme.upper()} 🔥\n\nSolo {collection.max_units} unidades firmadas '{collection.signature}'\n⏰ {days_left} días para cerrar\n\n¿Cuál es tu favorita? 👇",
                    "cta": "Link en bio para ordenar",
                    "hashtags": ["#EdicionLimitada", f"#{collection.theme.replace(' ', '')}", "#MysticMerch"]
                })
            elif platform == "tiktok":
                content.append({
                    "platform": platform,
                    "format": "video",
                    "hook": f"POV: Eres uno de los {collection.max_units} que tendrá esto...",
                    "caption": f"Serie firmada {collection.signature} | {days_left} días ⏰",
                    "sound_trend": "usar audio viral de escasez"
                })
            elif platform == "whatsapp":
                content.append({
                    "platform": platform,
                    "format": "status",
                    "text": f"⚡ {collection.signature} ⚡\n{collection.theme}\nSolo {collection.max_units} unidades\nPedidos por DM 🔥"
                })
        
        return content
    
    def get_collection_status(self, tenant_id: str, season: str) -> Optional[Dict]:
        """Obtiene estado de una colección activa"""
        key = f"{tenant_id}_{season}"
        collection = self.active_collections.get(key)
        
        if not collection:
            return None
        
        sold = 0  # En producción, consultar base de datos
        remaining = collection.max_units - sold
        progress = (sold / collection.max_units) * 100
        
        return {
            "theme": collection.theme,
            "signature": collection.signature,
            "total_units": collection.max_units,
            "sold": sold,
            "remaining": remaining,
            "progress_percent": progress,
            "fomo_active": datetime.now() < collection.fomo_deadline,
            "days_remaining": max(0, (collection.fomo_deadline - datetime.now()).days)
        }
