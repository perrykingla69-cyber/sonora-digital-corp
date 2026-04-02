from typing import Tuple
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import json
import statistics
from collections import deque

class RiskIndicator(Enum):
    VENCIMIENTO_PROXIMO = "vencimiento_proximo"
    SALDO_FAVOR_ANOMALO = "saldo_favor_anomalo"
    VARIACION_IVA_ALTA = "variacion_iva_alta"
    OPERACION_VINCULADA = "operacion_vinculada"
    CAMBIO_REGIMEN = "cambio_regimen"
    RETENCION_ISR_BAJA = "retencion_isr_baja"
    FACTURACION_INUSUAL = "facturacion_inusual"

@dataclass
class RiskSignal:
    indicator: RiskIndicator
    severity: float
    description: str
    affected_periods: List[str]
    recommended_action: str
    auto_fix_available: bool
    confidence: float

@dataclass
class PredictiveAlert:
    alert_id: str
    tenant_id: str
    signals: List[RiskSignal]
    composite_score: float
    predicted_issue: str
    time_horizon_days: int
    generated_at: datetime
    expires_at: datetime

class PredictiveFiscalEngine:
    def __init__(self, qdrant_client=None):
        self.qdrant = qdrant_client
        self.historical_patterns = {}
        self.alert_threshold = 0.7

    async def analyze_tenant_risk(self, tenant_id: str, months_history: int = 12) -> List[PredictiveAlert]:
        alerts = []
        signals = await self._analyze_time_series(tenant_id, months_history)
        anomalies = await self._detect_anomalies(tenant_id, signals)
        calendar_risks = self._check_calendar_risks(tenant_id)
        for anomaly in anomalies:
            alert = self._create_alert_from_signals(tenant_id, [anomaly] + [s for s in signals if s.indicator in self._related_indicators(anomaly.indicator)])
            if alert.composite_score > self.alert_threshold:
                alerts.append(alert)
        for risk in calendar_risks:
            alert = PredictiveAlert(
                alert_id=f"cal_{tenant_id}_{risk['date']}",
                tenant_id=tenant_id,
                signals=[RiskSignal(indicator=RiskIndicator.VENCIMIENTO_PROXIMO, severity=risk['urgency'], description=f"Vencimiento próximo: {risk['obligation']}", affected_periods=[risk['period']], recommended_action=risk['action'], auto_fix_available=risk.get('auto_fix', False), confidence=0.95)],
                composite_score=risk['urgency'],
                predicted_issue=risk['obligation'],
                time_horizon_days=risk['days_remaining'],
                generated_at=datetime.now(),
                expires_at=datetime.now() + timedelta(days=risk['days_remaining'])
            )
            alerts.append(alert)
        return sorted(alerts, key=lambda x: x.composite_score, reverse=True)

    async def _analyze_time_series(self, tenant_id: str, months: int) -> List[RiskSignal]:
        signals = []
        historical = await self._get_historical_data(tenant_id, months)
        if not historical:
            return signals
        iva_series = [h.get('iva_cargo', 0) - h.get('iva_favor', 0) for h in historical]
        if len(iva_series) >= 3:
            trend = self._calculate_trend(iva_series)
            volatility = statistics.stdev(iva_series) if len(iva_series) > 1 else 0
            mean_iva = statistics.mean(iva_series)
            if volatility > mean_iva * 0.3:
                signals.append(RiskSignal(indicator=RiskIndicator.VARIACION_IVA_ALTA, severity=min(volatility / mean_iva, 1.0) if mean_iva > 0 else 0.5, description=f"Alta variabilidad en saldos de IVA (CV: {volatility/mean_iva:.1%})", affected_periods=[h['period'] for h in historical[-3:]], recommended_action="Revisar consistencia de declaraciones y acreditamientos", auto_fix_available=False, confidence=0.8))
        fact_series = [h.get('total_facturado', 0) for h in historical]
        if len(fact_series) >= 6:
            recent_mean = statistics.mean(fact_series[-3:])
            older_mean = statistics.mean(fact_series[:-3])
            if older_mean > 0 and abs(recent_mean - older_mean) / older_mean > 0.5:
                signals.append(RiskSignal(indicator=RiskIndicator.FACTURACION_INUSUAL, severity=min(abs(recent_mean - older_mean) / older_mean, 1.0), description=f"Cambio significativo en facturación: {((recent_mean/older_mean-1)*100):+.0f}%", affected_periods=[historical[-1]['period']], recommended_action="Verificar si hay cambio de actividad o omisión de ingresos", auto_fix_available=False, confidence=0.75))
        ret_series = [h.get('isr_retenido', 0) for h in historical]
        ingresos_series = [h.get('total_ingresos', 1) for h in historical]
        if len(ret_series) >= 3:
            ratios = [r/i for r, i in zip(ret_series, ingresos_series) if i > 0]
            avg_ratio = statistics.mean(ratios) if ratios else 0
            if avg_ratio < 0.05 and any(r > 0.1 for r in ratios[:-3] if len(ratios) > 3):
                signals.append(RiskSignal(indicator=RiskIndicator.RETENCION_ISR_BAJA, severity=0.7, description="Disminución anormal en retenciones de ISR", affected_periods=[historical[-1]['period']], recommended_action="Verificar si clientes cambiaron a régimen SIMPLIFICADO o dejaron de retener", auto_fix_available=False, confidence=0.7))
        return signals

    def _calculate_trend(self, series: List[float]) -> float:
        n = len(series)
        if n < 2:
            return 0.0
        x_mean = (n - 1) / 2
        y_mean = statistics.mean(series)
        numerator = sum((i - x_mean) * (y - y_mean) for i, y in enumerate(series))
        denominator = sum((i - x_mean) ** 2 for i in range(n))
        return numerator / denominator if denominator != 0 else 0

    async def _detect_anomalies(self, tenant_id: str, baseline_signals: List[RiskSignal]) -> List[RiskSignal]:
        anomalies = []
        similar_patterns = await self._get_similar_patterns(tenant_id)
        for signal in baseline_signals:
            if signal.severity > 0.8:
                anomalies.append(signal)
        return anomalies

    def _check_calendar_risks(self, tenant_id: str) -> List[Dict]:
        risks = []
        today = datetime.now()
        regimen = self._get_tenant_regimen(tenant_id)
        obligaciones = self._get_obligaciones_regimen(regimen)
        for obl in obligaciones:
            next_due = self._calculate_next_due_date(obl, today)
            days_remaining = (next_due - today).days
            if days_remaining <= 7:
                risks.append({'obligation': obl['nombre'], 'date': next_due.isoformat(), 'days_remaining': days_remaining, 'urgency': 1.0 if days_remaining <= 2 else 0.8 if days_remaining <= 5 else 0.6, 'period': obl.get('periodo', 'mensual'), 'action': f"Presentar {obl['nombre']} antes de {next_due.strftime('%d/%m/%Y')}", 'auto_fix': obl.get('puede_automatizarse', False)})
        return risks

    def _create_alert_from_signals(self, tenant_id: str, signals: List[RiskSignal]) -> PredictiveAlert:
        individual_scores = [s.severity for s in signals]
        composite = 1 - (1 - max(individual_scores)) * (1 - statistics.mean(individual_scores))
        main_signal = max(signals, key=lambda x: x.severity * x.confidence)
        return PredictiveAlert(
            alert_id=f"pred_{tenant_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            tenant_id=tenant_id,
            signals=signals,
            composite_score=composite,
            predicted_issue=main_signal.description,
            time_horizon_days=30,
            generated_at=datetime.now(),
            expires_at=datetime.now() + timedelta(days=7)
        )

    def _related_indicators(self, indicator: RiskIndicator) -> List[RiskIndicator]:
        relations = {
            RiskIndicator.VARIACION_IVA_ALTA: [RiskIndicator.FACTURACION_INUSUAL],
            RiskIndicator.FACTURACION_INUSUAL: [RiskIndicator.VARIACION_IVA_ALTA, RiskIndicator.RETENCION_ISR_BAJA],
            RiskIndicator.RETENCION_ISR_BAJA: [RiskIndicator.FACTURACION_INUSUAL]
        }
        return relations.get(indicator, [])

    async def generate_preemptive_actions(self, alert: PredictiveAlert) -> List[Dict]:
        actions = []
        for signal in alert.signals:
            if signal.indicator == RiskIndicator.VENCIMIENTO_PROXIMO and signal.auto_fix_available:
                actions.append({'type': 'auto_prepare', 'description': f"Preparar borrador de {signal.description}", 'automation': 'generate_draft_declaration', 'params': {'period': signal.affected_periods[0]}})
            elif signal.indicator == RiskIndicator.VARIACION_IVA_ALTA:
                actions.append({'type': 'review', 'description': "Análisis detallado de acreditamientos de IVA", 'automation': 'generate_iva_reconciliation_report', 'params': {'periods': signal.affected_periods}})
            elif signal.indicator == RiskIndicator.FACTURACION_INUSUAL:
                actions.append({'type': 'alert', 'description': "Notificar a contador sobre cambio en facturación", 'automation': 'send_alert_to_accountant', 'params': {'severity': signal.severity, 'trend': 'up' if 'aumento' in signal.description else 'down'}})
        return actions

    # Placeholders para métodos que necesitan implementación con tu infraestructura actual
    async def _get_historical_data(self, tenant_id: str, months: int):
        # Implementar: consulta a tu base de datos PostgreSQL
        return []

    async def _get_similar_patterns(self, tenant_id: str):
        # Implementar: búsqueda en Qdrant
        return []

    def _get_tenant_regimen(self, tenant_id: str):
        # Implementar: consulta a base de datos
        return "GENERAL"

    def _get_obligaciones_regimen(self, regimen: str):
        # Implementar: catálogo de obligaciones fiscales
        return []

    def _calculate_next_due_date(self, obl: dict, today: datetime):
        # Implementar: lógica de cálculo de fechas de vencimiento
        return today + timedelta(days=5)
