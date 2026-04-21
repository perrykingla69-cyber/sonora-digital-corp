from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class TaxCalculationResult(BaseModel):
    ingresos: float = 0.0
    gastos: float = 0.0
    isr: float
    iva: float
    ieps: float = 0.0
    base_gravable: float
    total_impuestos: float
    fuente: str


class CFDIValidationError(BaseModel):
    field: str
    error: str
    suggestion: Optional[str] = None


class CFDIValidationResult(BaseModel):
    valid: bool
    errors: List[CFDIValidationError] = []
    version: str = "4.0"


class ComplianceObligation(BaseModel):
    obligacion: str
    deadline: str
    descripcion: str
    dias_restantes: int
    riesgo: str  # green|yellow|red


class ComplianceCheckResult(BaseModel):
    obligaciones: List[ComplianceObligation]
    riesgo_general: str
    proximo_vencimiento: Optional[str] = None


class TaxCatalogItem(BaseModel):
    codigo: str
    descripcion: str
    valor: Optional[float] = None


class TaxCatalogResult(BaseModel):
    items: List[TaxCatalogItem]
    updated: str
    source: str


class ReceiptValidationResult(BaseModel):
    deductible: bool
    requisitos: List[str]
    advertencias: List[str] = []


class AlertDeadlineResult(BaseModel):
    obligacion: str
    deadline: str
    alerta_fecha: str
    dias_restantes: int


class DeductionSuggestion(BaseModel):
    categoria: str
    descripcion: str
    monto_estimado: float


class SuggestDeductionsResult(BaseModel):
    sugerencias: List[DeductionSuggestion]
    impacto_estimado: float
    ahorro_potencial: float


class ComplianceReportResult(BaseModel):
    periodo: str
    regimen: str
    resumen: str
    obligaciones_cumplidas: List[str]
    obligaciones_pendientes: List[str]
    riesgo: str


class FiscalOperationResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    latency_ms: Optional[int] = None
