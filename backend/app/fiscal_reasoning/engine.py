from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import json
import re
from datetime import datetime

class NormativaType(Enum):
    Ley_Aduanera = "Ley Aduanera"
    RGCE = "Reglas Generales de Comercio Exterior"
    RMF = "Resolución Miscelánea Fiscal"
    DOF = "Diario Oficial de la Federación"
    CFDI = "Comprobante Fiscal Digital"

@dataclass
class RazonamientoPaso:
    numero: int
    tipo: str
    contenido: str
    fundamento_legal: Optional[str] = None
    confianza: float = 1.0
    subpasos: List['RazonamientoPaso'] = field(default_factory=list)

@dataclass
class AnalisisFiscal:
    situacion: str
    normativa_aplicable: List[NormativaType]
    pasos_razonamiento: List[RazonamientoPaso]
    conclusion: str
    riesgo_fiscal: str
    recomendaciones: List[str]
    documentacion_requerida: List[str]
    cadena_fundamentos: str = field(init=False)

    def __post_init__(self):
        self.cadena_fundamentos = self._generar_cadena()

    def _generar_cadena(self) -> str:
        fundamento_parts = []
        for paso in self.pasos_razonamiento:
            if paso.fundamento_legal:
                fundamento_parts.append(f"{paso.numero}. {paso.fundamento_legal}")
        return " → ".join(fundamento_parts)

class MotorRazonamientoFiscal:
    PATRONES_MVE = {
        "incrementables_art65": ["fletes", "seguros", "embalajes", "manipulación", "carga", "descarga", "almacenaje"],
        "decrementables_art66": ["construcción", "instalación", "mantenimiento", "transporte post-importación"],
        "metodos_valoracion": ["transacción", "identica", "similar", "deductivo", "computado", "fallback"]
    }

    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.ollama_url = ollama_url
        self.cache_interpretaciones: Dict[str, Any] = {}

    async def analizar_situacion_mve(self, datos_operacion: Dict) -> AnalisisFiscal:
        hechos = self._extraer_hechos(datos_operacion)
        normativa = self._identificar_normativa(hechos)
        paso_metodo = await self._analizar_metodo_valoracion(hechos, normativa)
        paso_ajustes = await self._analizar_ajustes_valor(hechos)
        paso_vinculacion = await self._analizar_vinculacion(hechos)
        paso_documentacion = self._validar_documentacion(hechos)
        conclusion, riesgo = self._generar_conclusion(hechos, [paso_metodo, paso_ajustes, paso_vinculacion, paso_documentacion])
        return AnalisisFiscal(
            situacion=hechos.get("descripcion_operacion", ""),
            normativa_aplicable=normativa,
            pasos_razonamiento=[paso_metodo, paso_ajustes, paso_vinculacion, paso_documentacion],
            conclusion=conclusion,
            riesgo_fiscal=riesgo,
            recomendaciones=self._generar_recomendaciones(hechos, riesgo),
            documentacion_requerida=self._listar_documentacion_obligatoria(hechos)
        )

    def _extraer_hechos(self, datos: Dict) -> Dict:
        return {
            "descripcion_operacion": datos.get("descripcion", ""),
            "valor_mercancia": datos.get("valor", 0),
            "moneda": datos.get("moneda", "MXN"),
            "incoterm": datos.get("incoterm", ""),
            "pais_origen": datos.get("pais_origen", ""),
            "vinculacion": datos.get("vinculacion", False),
            "tipo_mercancia": datos.get("tipo", ""),
            "facturas_soporte": datos.get("facturas", []),
            "gastos_adicionales": datos.get("gastos", {})
        }

    def _identificar_normativa(self, hechos: Dict) -> List[NormativaType]:
        aplicables = [NormativaType.Ley_Aduanera, NormativaType.RGCE]
        if hechos.get("incoterm") in ["EXW", "FCA", "FOB", "CIF", "DDP"]:
            aplicables.append(NormativaType.DOF)
        if any(f.get("es_cfdi") for f in hechos.get("facturas_soporte", [])):
            aplicables.append(NormativaType.CFDI)
        return aplicables

    async def _analizar_metodo_valoracion(self, hechos: Dict, normativa: List[NormativaType]) -> RazonamientoPaso:
        prompt = f"""
        Como experto en valoración aduanera mexicana, analiza:
        Operación: {hechos['descripcion_operacion']}
        Valor declarado: {hechos['valor_mercancia']} {hechos['moneda']}
        INCOTERM: {hechos['incoterm']}
        Vinculación: {"Sí" if hechos['vinculacion'] else "No"}
        Determina: 1. Método de valoración aplicable según Art. 54-65 Ley Aduanera, 2. Justificación técnica, 3. Fundamento legal específico, 4. Riesgos de ajuste.
        Responde en JSON estructurado.
        """
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.ollama_url}/api/generate",
                json={"model": "qwen2.5-coder:32b", "prompt": prompt, "format": "json", "stream": False, "options": {"temperature": 0.1}},
                timeout=45.0
            )
        resultado = json.loads(response.json().get("response", "{}"))
        return RazonamientoPaso(
            numero=1,
            tipo="norma",
            contenido=f"Método de valoración: {resultado.get('metodo', 'No determinado')}",
            fundamento_legal=resultado.get("fundamento", "Art. 54 Ley Aduanera"),
            confianza=resultado.get("confianza", 0.8),
            subpasos=[
                RazonamientoPaso(numero=1.1, tipo="interpretacion", contenido=resultado.get("justificacion", ""), confianza=0.9),
                RazonamientoPaso(numero=1.2, tipo="conclusion", contenido=f"Riesgo de ajuste: {resultado.get('riesgo_ajuste', 'medio')}", confianza=0.85)
            ]
        )

    async def _analizar_ajustes_valor(self, hechos: Dict) -> RazonamientoPaso:
        gastos = hechos.get("gastos_adicionales", {})
        incrementables_detectados = []
        decrementables_detectados = []
        for concepto, monto in gastos.items():
            concepto_lower = concepto.lower()
            if any(inc in concepto_lower for inc in self.PATRONES_MVE["incrementables_art65"]):
                incrementables_detectados.append({"concepto": concepto, "monto": monto})
            elif any(dec in concepto_lower for dec in self.PATRONES_MVE["decrementables_art66"]):
                decrementables_detectados.append({"concepto": concepto, "monto": monto})
        return RazonamientoPaso(
            numero=2,
            tipo="interpretacion",
            contenido=f"Análisis de ajustes: {len(incrementables_detectados)} incrementables, {len(decrementables_detectados)} decrementables",
            fundamento_legal="Arts. 65 y 66 Ley Aduanera",
            confianza=0.9,
            subpasos=[
                RazonamientoPaso(numero=2.1, tipo="hecho", contenido=f"Incrementables: {json.dumps(incrementables_detectados)}", confianza=0.95),
                RazonamientoPaso(numero=2.2, tipo="hecho", contenido=f"Decrementables: {json.dumps(decrementables_detectados)}", confianza=0.95)
            ]
        )

    async def _analizar_vinculacion(self, hechos: Dict) -> RazonamientoPaso:
        if not hechos.get("vinculacion"):
            return RazonamientoPaso(
                numero=3,
                tipo="conclusion",
                contenido="No se detecta vinculación. Aplica valor de transacción.",
                fundamento_legal="Art. 54 fracción I Ley Aduanera",
                confianza=0.95
            )
        return RazonamientoPaso(
            numero=3,
            tipo="interpretacion",
            contenido="Análisis de vinculación requerido - precio potencialmente influenciado",
            fundamento_legal="Art. 54 fracción II Ley Aduanera",
            confianza=0.75,
            subpasos=[]
        )

    def _validar_documentacion(self, hechos: Dict) -> RazonamientoPaso:
        facturas = hechos.get("facturas_soporte", [])
        documentos_faltantes = []
        checklist = [
            ("factura_comercial", any(f.get("tipo") == "comercial" for f in facturas)),
            ("conocimiento_embarque", hechos.get("conocimiento_embarque")),
            ("comprobante_pago", any(f.get("es_comprobante_pago") for f in facturas)),
            ("contrato_compraventa", hechos.get("contrato")),
            ("garantia_aduanera", hechos.get("garantia"))
        ]
        for doc, presente in checklist:
            if not presente:
                documentos_faltantes.append(doc)
        confianza = 1.0 - (len(documentos_faltantes) * 0.15)
        return RazonamientoPaso(
            numero=4,
            tipo="hecho",
            contenido=f"Documentación: {len(facturas)} facturas presentes, {len(documentos_faltantes)} faltantes",
            fundamento_legal="Anexo 1 RGCE 2025 - Expediente probatorio MVE",
            confianza=max(confianza, 0.4),
            subpasos=[RazonamientoPaso(numero=4.1, tipo="conclusion", contenido=f"Faltantes: {', '.join(documentos_faltantes)}", confianza=0.9 if not documentos_faltantes else 0.6)]
        )

    def _generar_conclusion(self, hechos: Dict, pasos: List[RazonamientoPaso]) -> Tuple[str, str]:
        riesgo_score = sum((1 - p.confianza) * 2 for p in pasos) / len(pasos)
        if riesgo_score < 0.3:
            riesgo = "bajo"
        elif riesgo_score < 0.6:
            riesgo = "medio"
        elif riesgo_score < 0.9:
            riesgo = "alto"
        else:
            riesgo = "critico"
        conclusion = f"La operación de importación de {hechos['tipo_mercancia']} por valor de {hechos['valor_mercancia']} {hechos['moneda']} puede valorarse bajo el método {pasos[0].contenido}. Riesgo fiscal: {riesgo.upper()}."
        return conclusion.strip(), riesgo

    def _generar_recomendaciones(self, hechos: Dict, riesgo: str) -> List[str]:
        if riesgo in ["alto", "critico"]:
            return ["Solicitar opinión de valoración previa", "Preparar defensa fiscal documentada", "Considerar ajuste preventivo al valor declarado"]
        elif riesgo == "medio":
            return ["Verificar completitud de expediente probatorio", "Documentar criterios de valoración utilizados", "Mantener respaldo de información financiera del extranjero"]
        else:
            return ["Proceder con presentación de MVE", "Conservar documentación soporte por 5 años", "Monitorear cambios normativos"]

    def _listar_documentacion_obligatoria(self, hechos: Dict) -> List[str]:
        base = ["Factura comercial (original o copia certificada)", "Conocimiento de embarque, guía aérea o documento de transporte", "Pedimento de importación"]
        if hechos.get("vinculacion"):
            base.extend(["Declaración de vinculación", "Estados financieros del vendedor", "Análisis de precios de transferencia (si aplica)"])
        if hechos.get("incoterm") in ["CIF", "CFR"]:
            base.append("Póliza de seguro internacional")
        return base

    def generar_defensa_fiscal(self, analisis: AnalisisFiscal) -> str:
        defensa = f"""DEFENSA FISCAL - ANÁLISIS DE VALORACIÓN ADUANERA
        
I. HECHOS
{analisis.situacion}

II. FUNDAMENTACIÓN JURÍDICA
{analisis.cadena_fundamentos}

III. ANÁLISIS DE RIESGO
Nivel: {analisis.riesgo_fiscal}

IV. RAZONAMIENTO
"""
        for paso in analisis.pasos_razonamiento:
            defensa += f"\n{paso.numero}. {paso.contenido}\n"
            if paso.fundamento_legal:
                defensa += f"   Fundamento: {paso.fundamento_legal}\n"
            for sub in paso.subpasos:
                defensa += f"   {sub.numero}. {sub.contenido}\n"
        defensa += f"\nV. CONCLUSIÓN\n{analisis.conclusion}\n\nVI. RECOMENDACIONES\n"
        for i, rec in enumerate(analisis.recomendaciones, 1):
            defensa += f"{i}. {rec}\n"
        defensa += f"\nVII. DOCUMENTACIÓN REQUERIDA\n"
        for doc in analisis.documentacion_requerida:
            defensa += f"- {doc}\n"
        defensa += f"\nFecha: {datetime.now().isoformat()}\nSistema: Hermes Fiscal AI v2.0"
        return defensa
