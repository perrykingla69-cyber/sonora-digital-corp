import asyncio
from datetime import datetime
from operations import validate_cfdi, calculate_taxes, check_compliance
from operations import get_tax_catalogs, validate_receipt, alert_deadline
from operations import suggest_deductions, generate_compliance_report


class FiscalAgent:
    """Dispatcher de operaciones fiscales determinísticas."""

    OPERATIONS = {
        'validate_cfdi': validate_cfdi.validate_cfdi,
        'calculate_taxes': calculate_taxes.calculate_taxes,
        'check_compliance': check_compliance.check_compliance,
        'get_tax_catalogs': get_tax_catalogs.get_tax_catalogs,
        'validate_receipt': validate_receipt.validate_receipt,
        'alert_deadline': alert_deadline.alert_deadline,
        'suggest_deductions': suggest_deductions.suggest_deductions,
        'generate_compliance_report': generate_compliance_report.generate_compliance_report,
    }

    async def execute(self, operation: str, inputs: dict, tenant_id: str = None) -> dict:
        """Ejecuta operación fiscal. Returns {success, data, error, latency_ms}."""

        start = datetime.now()

        if operation not in self.OPERATIONS:
            return {
                'success': False,
                'error': f"Operación '{operation}' no existe",
                'data': None,
                'latency_ms': int((datetime.now() - start).total_seconds() * 1000)
            }

        try:
            op_func = self.OPERATIONS[operation]

            # Map inputs a kwargs
            result = op_func(**inputs)

            return {
                'success': True,
                'data': result.model_dump() if hasattr(result, 'model_dump') else result,
                'error': None,
                'latency_ms': int((datetime.now() - start).total_seconds() * 1000)
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'data': None,
                'latency_ms': int((datetime.now() - start).total_seconds() * 1000)
            }

    async def health(self) -> dict:
        """Health check: valida todas las operaciones."""
        return {
            'status': 'ok',
            'operations_count': len(self.OPERATIONS),
            'operations': list(self.OPERATIONS.keys()),
            'timestamp': datetime.now().isoformat()
        }
