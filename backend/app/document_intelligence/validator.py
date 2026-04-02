from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import hashlib
import json
import re
from datetime import datetime

class DocumentType(Enum):
    CFDI = "CFDI"
    FACTURA_EXTRANJERA = "FACTURA_EXTRANJERA"
    CONOCIMIENTO_EMBARQUE = "BL"
    POLIZA_SEGURO = "SEGURO"
    CONTRATO = "CONTRATO"
    PEDIMENTO = "PEDIMENTO"
    MVE = "MVE"
    COVE = "COVE"

class ValidationSeverity(Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    SUGGESTION = "suggestion"

@dataclass
class ValidationResult:
    field: str
    expected: Any
    found: Any
    severity: ValidationSeverity
    message: str
    auto_fixable: bool = False
    suggestion: Optional[str] = None

@dataclass
class DocumentAnalysis:
    doc_type: DocumentType
    confidence: float
    extracted_fields: Dict[str, Any]
    validations: List[ValidationResult]
    cross_references: Dict[str, List[str]]
    hash_fingerprint: str
    processing_time_ms: int

class DocumentIntelligencePipeline:
    FIELD_PATTERNS = {
        DocumentType.CFDI: {
            "uuid": r"[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}",
            "rfc_emisor": r"[A-ZÑ&]{3,4}[0-9]{6}[A-Z0-9]{3}",
            "rfc_receptor": r"[A-ZÑ&]{3,4}[0-9]{6}[A-Z0-9]{3}",
            "total": r"\d+\.\d{2}",
            "fecha": r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}"
        },
        DocumentType.FACTURA_EXTRANJERA: {
            "numero_factura": r"[A-Z0-9\-]+",
            "fecha": r"\d{1,2}[/-]\d{1,2}[/-]\d{2,4}",
            "moneda": r"(USD|EUR|GBP|MXN|JPY)",
            "incoterm": r"(EXW|FCA|FAS|FOB|CFR|CIF|CPT|CIP|DAP|DPU|DDP)"
        }
    }

    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.ollama_url = ollama_url
        self.validation_history: List[DocumentAnalysis] = []

    async def process_document(self, content: bytes, filename: str) -> DocumentAnalysis:
        start_time = datetime.now()
        doc_type, confidence = await self._classify_document(content, filename)
        extracted = await self._extract_fields(content, doc_type)
        validations = self._validate_document(extracted, doc_type)
        cross_refs = await self._cross_validate(extracted, doc_type)
        fingerprint = hashlib.sha256(content).hexdigest()[:16]
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        analysis = DocumentAnalysis(
            doc_type=doc_type,
            confidence=confidence,
            extracted_fields=extracted,
            validations=validations,
            cross_references=cross_refs,
            hash_fingerprint=fingerprint,
            processing_time_ms=int(processing_time)
        )
        self.validation_history.append(analysis)
        return analysis

    async def _classify_document(self, content: bytes, filename: str) -> Tuple[DocumentType, float]:
        filename_lower = filename.lower()
        if "cfdi" in filename_lower or content[:1000].find(b"Comprobante Fiscal") != -1:
            return DocumentType.CFDI, 0.95
        if any(x in filename_lower for x in ["bl", "bill of lading", "conocimiento"]):
            return DocumentType.CONOCIMIENTO_EMBARQUE, 0.90
        if "mve" in filename_lower or "manifestacion" in filename_lower:
            return DocumentType.MVE, 0.92
        return DocumentType.FACTURA_EXTRANJERA, 0.70

    async def _extract_fields(self, content: bytes, doc_type: DocumentType) -> Dict[str, Any]:
        if doc_type == DocumentType.CFDI:
            return self._extract_cfdi_fields(content)
        extracted = {}
        text_content = content.decode('utf-8', errors='ignore')
        patterns = self.FIELD_PATTERNS.get(doc_type, {})
        for field, pattern in patterns.items():
            matches = re.findall(pattern, text_content, re.IGNORECASE)
            if matches:
                extracted[field] = matches[0]
        return extracted

    def _extract_cfdi_fields(self, xml_content: bytes) -> Dict[str, Any]:
        import xml.etree.ElementTree as ET
        try:
            root = ET.fromstring(xml_content)
            ns = {'cfdi': 'http://www.sat.gob.mx/cfd/4'}
            comprobante = root
            emisor = root.find('.//cfdi:Emisor', ns)
            receptor = root.find('.//cfdi:Receptor', ns)
            conceptos = root.findall('.//cfdi:Concepto', ns)
            return {
                "uuid": root.attrib.get('UUID', ''),
                "serie": root.attrib.get('Serie', ''),
                "folio": root.attrib.get('Folio', ''),
                "fecha_emision": root.attrib.get('Fecha', ''),
                "total": float(root.attrib.get('Total', 0)),
                "subtotal": float(root.attrib.get('SubTotal', 0)),
                "moneda": root.attrib.get('Moneda', 'MXN'),
                "tipo_comprobante": root.attrib.get('TipoDeComprobante', ''),
                "lugar_expedicion": root.attrib.get('LugarExpedicion', ''),
                "rfc_emisor": emisor.attrib.get('Rfc', '') if emisor is not None else '',
                "nombre_emisor": emisor.attrib.get('Nombre', '') if emisor is not None else '',
                "rfc_receptor": receptor.attrib.get('Rfc', '') if receptor is not None else '',
                "nombre_receptor": receptor.attrib.get('Nombre', '') if receptor is not None else '',
                "uso_cfdi": receptor.attrib.get('UsoCFDI', '') if receptor is not None else '',
                "conceptos": [{"clave": c.attrib.get('ClaveProdServ', ''), "descripcion": c.attrib.get('Descripcion', ''), "cantidad": float(c.attrib.get('Cantidad', 0)), "valor_unitario": float(c.attrib.get('ValorUnitario', 0)), "importe": float(c.attrib.get('Importe', 0))} for c in conceptos],
                "num_conceptos": len(conceptos),
                "total_conceptos": sum(float(c.attrib.get('Importe', 0)) for c in conceptos)
            }
        except Exception as e:
            return {"error": f"Error parseando CFDI: {str(e)}"}

    def _validate_document(self, extracted: Dict[str, Any], doc_type: DocumentType) -> List[ValidationResult]:
        validations = []
        if doc_type == DocumentType.CFDI:
            validations.extend(self._validate_cfdi(extracted))
        elif doc_type == DocumentType.FACTURA_EXTRANJERA:
            validations.extend(self._validate_factura_extranjera(extracted))
        elif doc_type == DocumentType.MVE:
            validations.extend(self._validate_mve(extracted))
        return validations

    def _validate_cfdi(self, fields: Dict[str, Any]) -> List[ValidationResult]:
        validations = []
        uuid = fields.get('uuid', '')
        if not re.match(r'[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}', uuid, re.I):
            validations.append(ValidationResult(field="uuid", expected="UUID válido RFC 4122", found=uuid, severity=ValidationSeverity.ERROR, message="UUID con formato inválido - posible CFDI falso", auto_fixable=False))
        subtotal = fields.get('subtotal', 0)
        total = fields.get('total', 0)
        suma_conceptos = fields.get('total_conceptos', 0)
        if abs(suma_conceptos - subtotal) > 0.01:
            validations.append(ValidationResult(field="importes", expected=f"SubTotal ({subtotal}) = Suma conceptos ({suma_conceptos})", found=f"Diferencia: {abs(suma_conceptos - subtotal)}", severity=ValidationSeverity.WARNING, message="Inconsistencia en suma de conceptos", auto_fixable=False, suggestion="Verificar descuentos globales o conceptos con valor 0"))
        rfc_emisor = fields.get('rfc_emisor', '')
        if len(rfc_emisor) not in [12, 13]:
            validations.append(ValidationResult(field="rfc_emisor", expected="RFC válido (12-13 caracteres)", found=rfc_emisor, severity=ValidationSeverity.ERROR, message="RFC emisor con longitud inválida"))
        try:
            fecha = datetime.fromisoformat(fields.get('fecha_emision', '').replace('Z', '+00:00'))
            if fecha > datetime.now():
                validations.append(ValidationResult(field="fecha_emision", expected="Fecha pasada o presente", found=fields.get('fecha_emision'), severity=ValidationSeverity.ERROR, message="Fecha de emisión en el futuro - posible anomalía"))
        except:
            pass
        return validations

    def _validate_factura_extranjera(self, fields: Dict[str, Any]) -> List[ValidationResult]:
        validations = []
        incoterm = fields.get('incoterm', '')
        incoterms_validos = ['EXW', 'FCA', 'FAS', 'FOB', 'CFR', 'CIF', 'CPT', 'CIP', 'DAP', 'DPU', 'DDP']
        if incoterm and incoterm.upper() not in incoterms_validos:
            validations.append(ValidationResult(field="incoterm", expected=f"INCOTERM válido: {', '.join(incoterms_validos)}", found=incoterm, severity=ValidationSeverity.WARNING, message="INCOTERM no reconocido o versión antigua", suggestion="Verificar si es INCOTERM 2020"))
        moneda = fields.get('moneda', '')
        if moneda and moneda not in ['USD', 'EUR', 'GBP', 'MXN', 'JPY', 'CAD']:
            validations.append(ValidationResult(field="moneda", expected="Moneda ISO estándar", found=moneda, severity=ValidationSeverity.INFO, message="Moneda no estándar - verificar tipo de cambio"))
        return validations

    def _validate_mve(self, fields: Dict[str, Any]) -> List[ValidationResult]:
        validations = []
        campos_obligatorios = ['rfc_importador', 'numero_pedimento', 'fecha_presentacion', 'valor_dolares', 'incoterm', 'metodo_valoracion']
        for campo in campos_obligatorios:
            if not fields.get(campo):
                validations.append(ValidationResult(field=campo, expected="Valor presente", found="Ausente", severity=ValidationSeverity.ERROR, message=f"Campo obligatorio MVE ausente: {campo}"))
        metodo = fields.get('metodo_valoracion', '')
        metodos_validos = ['1', '2', '3', '4', '5', '6']
        if metodo and metodo not in metodos_validos:
            validations.append(ValidationResult(field="metodo_valoracion", expected="Método 1-6 según Art. 54-59 LA", found=metodo, severity=ValidationSeverity.ERROR, message="Método de valoración no reconocido"))
        return validations

    async def _cross_validate(self, extracted: Dict[str, Any], doc_type: DocumentType) -> Dict[str, List[str]]:
        cross_refs = {}
        for prev in self.validation_history[-10:]:
            refs = []
            if (extracted.get('rfc_emisor') and extracted.get('rfc_emisor') == prev.extracted_fields.get('rfc_receptor')):
                refs.append(f"RFC vinculado con {prev.doc_type.value}")
            if (extracted.get('total') and prev.extracted_fields.get('total')):
                diff = abs(extracted['total'] - prev.extracted_fields['total'])
                if diff < 1.0:
                    refs.append(f"Monto coincidente con {prev.doc_type.value}")
                elif diff < extracted['total'] * 0.05:
                    refs.append(f"Monto similar (diff {diff}) con {prev.doc_type.value}")
            if refs:
                cross_refs[prev.hash_fingerprint] = refs
        return cross_refs

    def generate_compliance_report(self, analyses: List[DocumentAnalysis]) -> Dict[str, Any]:
        total_errors = sum(1 for a in analyses for v in a.validations if v.severity == ValidationSeverity.ERROR)
        total_warnings = sum(1 for a in analyses for v in a.validations if v.severity == ValidationSeverity.WARNING)
        can_proceed = total_errors == 0
        return {
            "operacion_completa": can_proceed,
            "nivel_riesgo": "critico" if total_errors > 2 else "alto" if total_errors > 0 else "medio" if total_warnings > 3 else "bajo",
            "total_documentos": len(analyses),
            "errores_bloqueantes": total_errors,
            "advertencias": total_warnings,
            "documentos_analizados": [{"tipo": a.doc_type.value, "confianza": a.confidence, "estado": "valido" if all(v.severity != ValidationSeverity.ERROR for v in a.validations) else "con_errores", "validaciones_criticas": [v.message for v in a.validations if v.severity in [ValidationSeverity.ERROR, ValidationSeverity.WARNING]]} for a in analyses],
            "recomendaciones_accion": ["Corregir errores bloqueantes antes de presentar MVE" if total_errors > 0 else "Documentación lista para presentación", "Revisar advertencias de inconsistencia" if total_warnings > 0 else "Sin inconsistencias detectadas", "Verificar cross-referencias entre documentos"]
        }
