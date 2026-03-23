from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum, auto
from datetime import datetime
import asyncio
import json
import httpx
import hashlib

class CampaignType(Enum):
    MVE_URGENTE = auto()
    CIERRE_MENSUAL = auto()
    FREEMIUM_PROMO = auto()
    NUEVA_FUNCION = auto()
    EDUCATIVO_FISCAL = auto()
    CASO_EXITO = auto()

class ContentFormat(Enum):
    REEL_15S = "reel_15s"
    REEL_30S = "reel_30s"
    CARRUSEL = "carrusel"
    STORY = "story"
    POST_ALTO = "post_alto"
    WHATSAPP_BLAST = "whatsapp_blast"
    EMAIL = "email"
    LANDING_HERO = "landing_hero"

@dataclass
class ContentPiece:
    piece_id: str
    campaign_type: CampaignType
    format: ContentFormat
    headline: str
    copy: str
    cta: str
    visual_prompt: str
    hashtags: List[str]
    audio_script: Optional[str] = None
    target_audience: str = "contadores_mexico"
    generated_at: datetime = field(default_factory=datetime.now)
    performance_prediction: float = 0.0

class ContentEngine:
    """
    Fábrica automática de contenido fiscal para redes sociales.
    Genera 50+ piezas semanales sin intervención humana.
    """
    
    TEMPLATES_REELS = {
        CampaignType.MVE_URGENTE: {
            "hook": "⚠️ {dias} días para el MVE y aún no lo tienes listo...",
            "problem": "La nueva ley del 1 de abril cambia TODO",
            "solution": "Con Mystic: MVE en 3 clics, validado por IA",
            "cta": "Link en bio - Gratis hasta el 31",
            "visual_style": "urgency_red_black_tech"
        },
        CampaignType.CIERRE_MENSUAL: {
            "hook": "Son las 11:58pm del último día del mes...",
            "problem": "¿Otra vez haciendo cierre manual?",
            "solution": "Pre-cierre automático + CFDIs verificados",
            "cta": "Tu contador IA nunca duerme",
            "visual_style": "dark_mode_dashboard_glow"
        }
    }
    
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.ollama_url = ollama_url
        self.brand_voice = {
            "tono": "profesional_cercano",
            "urgencia": "medio_alta",
            "emojis": ["📊", "⚡", "🧠", "✅", "🚨"],
            "evitar": ["barato", "fácil", "magia", "solo"]
        }
        
    async def generate_campaign(self, campaign_type: CampaignType, formats: List[ContentFormat]) -> List[ContentPiece]:
        """Genera campaña completa en múltiples formatos"""
        pieces = []
        
        for fmt in formats:
            piece = await self._generate_single_piece(campaign_type, fmt)
            pieces.append(piece)
            
        # Optimizar para cross-posting
        pieces = self._optimize_cross_posting(pieces)
        
        return pieces
    
    async def _generate_single_piece(self, campaign_type: CampaignType, fmt: ContentFormat) -> ContentPiece:
        """Genera una pieza de contenido individual"""
        
        # 1. Generar copy con LLM
        copy_data = await self._generate_copy_with_llm(campaign_type, fmt)
        
        # 2. Generar prompt visual
        visual_prompt = await self._generate_visual_prompt(copy_data, fmt)
        
        # 3. Predecir performance
        prediction = self._predict_performance(copy_data, fmt)
        
        piece_id = hashlib.md5(f"{campaign_type.name}_{fmt.value}_{datetime.now().isoformat()}".encode()).hexdigest()[:12]
        
        return ContentPiece(
            piece_id=piece_id,
            campaign_type=campaign_type,
            format=fmt,
            headline=copy_data["headline"],
            copy=copy_data["body"],
            cta=copy_data["cta"],
            visual_prompt=visual_prompt,
            hashtags=copy_data["hashtags"],
            audio_script=copy_data.get("audio_script"),
            performance_prediction=prediction
        )
    
    async def _generate_copy_with_llm(self, campaign_type: CampaignType, fmt: ContentFormat) -> Dict:
        """Usa LLM para generar copy persuasivo"""
        
        template = self.TEMPLATES_REELS.get(campaign_type, {})
        
        prompt = f"""
        Eres copywriter senior para Mystic (plataforma contable-fiscal con IA).
        Genera copy para {fmt.value} sobre: {campaign_type.name}
        
        Tono: {self.brand_voice['tono']}
        Restricciones: No uses {', '.join(self.brand_voice['evitar'])}
        
        Estructura requerida:
        - Headline mágico (máx 8 palabras)
        - Body persuasivo (adaptado a {fmt.value})
        - CTA fuerte
        - 5 hashtags estratégicos
        
        Contexto: {json.dumps(template, indent=2)}
        
        Responde en JSON exacto.
        """
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": "qwen2.5-coder:32b",
                    "prompt": prompt,
                    "format": "json",
                    "stream": False,
                    "options": {"temperature": 0.8}
                },
                timeout=30.0
            )
            
        result = json.loads(response.json().get("response", "{}"))
        
        return {
            "headline": result.get("headline", "Transforma tu contabilidad con IA"),
            "body": result.get("body", "Automatiza tu cumplimiento fiscal."),
            "cta": result.get("cta", "Prueba gratis"),
            "hashtags": result.get("hashtags", ["#Contabilidad", "#IA", "#México"]),
            "audio_script": result.get("audio_script") if fmt in [ContentFormat.REEL_15S, ContentFormat.REEL_30S] else None
        }
    
    async def _generate_visual_prompt(self, copy_data: Dict, fmt: ContentFormat) -> str:
        """Genera prompt para generación de imagen/video"""
        
        base_prompts = {
            ContentFormat.REEL_15S: "Cinematic tech shot, dark premium background, glowing cyan UI elements, motion blur, 8k",
            ContentFormat.CARRUSEL: "Clean infographic style, glassmorphism cards, data visualization, professional gradient",
            ContentFormat.LANDING_HERO: "Hyper-realistic 3D render, abstract data flows, holographic interface, volumetric lighting"
        }
        
        style = base_prompts.get(fmt, "Professional tech aesthetic, dark mode")
        
        prompt = f"""
        Genera prompt para FLUX/Wan de imagen {fmt.value}:
        
        Mensaje: {copy_data['headline']}
        Estilo base: {style}
        
        Incluye:
        - Composición específica
        - Iluminación dramática
        - Paleta de colores (cyan #00D4FF, magenta #FF006E, dark #0A0A0F)
        - Detalles técnicos de render
        
        Responde solo el prompt optimizado.
        """
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.ollama_url}/api/generate",
                json={"model": "qwen2.5-coder:32b", "prompt": prompt, "stream": False},
                timeout=20.0
            )
            
        return response.json().get("response", style)
    
    def _predict_performance(self, copy_data: Dict, fmt: ContentFormat) -> float:
        """Predice performance basado en patrones históricos"""
        # Algoritmo simple - en producción usar ML
        score = 0.5
        
        # Factores positivos
        if len(copy_data["headline"]) < 50: score += 0.1
        if "?" in copy_data["headline"]: score += 0.05
        if any(e in copy_data["body"] for e in ["⚠️", "🚨", "💰"]): score += 0.1
        if "gratis" in copy_data["cta"].lower() or "free" in copy_data["cta"].lower(): score += 0.15
        
        # Factores negativos
        if len(copy_data["body"]) > 300: score -= 0.1
        if any(word in copy_data["body"].lower() for word in ["barato", "fácil", "solo"]): score -= 0.2
            
        return min(max(score, 0.0), 1.0)
    
    def _optimize_cross_posting(self, pieces: List[ContentPiece]) -> List[ContentPiece]:
        """Optimiza piezas para publicación cruzada sin duplicar"""
        # Asegurar que hashtags varíen entre plataformas
        for i, piece in enumerate(pieces):
            if i > 0:
                piece.hashtags = [h for h in piece.hashtags if h not in pieces[i-1].hashtags] + \
                                [h for h in pieces[i-1].hashtags if h not in piece.hashtags][:2]
        return pieces
    
    async def schedule_content_pipeline(self, days_ahead: int = 30) -> Dict[str, Any]:
        """Genera pipeline de contenido para los próximos días"""
        
        calendar = {}
        campaign_rotation = [
            CampaignType.MVE_URGENTE,
            CampaignType.CIERRE_MENSUAL,
            CampaignType.FREEMIUM_PROMO,
            CampaignType.EDUCATIVO_FISCAL
        ]
        
        for day in range(days_ahead):
            date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            date = date.replace(day=date.day + day)
            
            # Seleccionar campaña según día
            campaign = campaign_rotation[day % len(campaign_rotation)]
            
            # Generar piezas para ese día
            pieces = await self.generate_campaign(
                campaign,
                [ContentFormat.REEL_15S, ContentFormat.CARRUSEL, ContentFormat.STORY]
            )
            
            calendar[date.strftime("%Y-%m-%d")] = {
                "campaign": campaign.name,
                "pieces": [{"id": p.piece_id, "format": p.format.value, "prediction": p.performance_prediction} for p in pieces]
            }
            
        return {
            "total_days": days_ahead,
            "total_pieces": days_ahead * 3,
            "estimated_engagement": sum(p["prediction"] for day in calendar.values() for p in day["pieces"]) / (days_ahead * 3),
            "calendar": calendar
        }
