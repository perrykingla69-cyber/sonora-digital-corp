from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class ValidateCFDIRequest(BaseModel):
    xml_content: Optional[str] = None
    json_content: Optional[Dict[str, Any]] = None


class CalculateTaxesRequest(BaseModel):
    ingresos: float = Field(..., gt=0, description="Ingresos brutos")
    gastos: float = Field(default=0, ge=0, description="Gastos deducibles")
    periodo: str = Field(..., description="YYYYMM")
    regimen: str = Field(..., description="PM|PF_Honorarios|PF_Asalariado|RIF")


class CheckComplianceRequest(BaseModel):
    regimen: str
    month: int = Field(..., ge=1, le=12)
    taxpayer_id: Optional[str] = None


class GetTaxCatalogsRequest(BaseModel):
    query: str = Field(..., description="tabla18|tasas_iva|tasas_isr")
    period: Optional[str] = None


class ValidateReceiptRequest(BaseModel):
    tipo: str = Field(..., description="recibo|factura|cfdi")
    monto: float = Field(..., gt=0)
    rfc_emisor: Optional[str] = None
    deducibilidad: Optional[str] = None


class AlertDeadlineRequest(BaseModel):
    obligacion: str = Field(..., description="ISR_Mensual|IMSS|CFDI_Emisión")
    month: Optional[int] = None
    year: Optional[int] = None


class SuggestDeductionsRequest(BaseModel):
    regimen: str
    ingresos: float = Field(..., gt=0)
    gastos_actuales: Optional[float] = None


class ComplianceReportRequest(BaseModel):
    period: str = Field(..., description="YYYYMM")
    regimen: str
    tenant_id: Optional[str] = None


class FiscalOperationRequest(BaseModel):
    operation: str
    inputs: Dict[str, Any]
    tenant_id: Optional[str] = None
