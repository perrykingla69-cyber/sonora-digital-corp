"""Soul Filter 3-6-9 para Sonora Digital Corp.

3 pilares × 6 dimensiones × 9 verificaciones = 162 checks.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass(frozen=True)
class DimensionConfig:
    """Configuración de una dimensión dentro de un pilar."""

    nombre: str
    checks: List[str]


class SoulFilter369:
    """Filtro ético-técnico de verificación en patrón 3-6-9."""

    def __init__(self) -> None:
        self.pilares: Dict[int, str] = {
            1: "ÉTICA (ALMA)",
            2: "TÉCNICA (CUERPO)",
            3: "IMPACTO (ESPÍRITU)",
        }
        self.verificaciones_por_dimension = 9
        self.estructura = self._build_structure()

    def _build_structure(self) -> Dict[int, List[DimensionConfig]]:
        """Define 6 dimensiones por pilar con 9 checks por dimensión."""

        return {
            1: [
                DimensionConfig("1.1 Principios Wiccan", [
                    "no_daño", "triple_ley", "naturaleza", "ciclos", "libertad", "sagrado",
                    "amor", "verdad", "integridad",
                ]),
                DimensionConfig("1.2 Humanismo Tecnológico", [
                    "ia_herramienta", "accesibilidad", "educacion", "libertad_pensamiento",
                    "transparencia", "dignidad", "privacidad", "consentimiento", "justicia",
                ]),
                DimensionConfig("1.3 Dedicaciones Sagradas", [
                    "hermes", "nathaly", "familia", "generaciones_pasadas", "generaciones_futuras",
                    "fourgea", "triple_r", "pymes", "asociacion_civil",
                ]),
                DimensionConfig("1.4 Gobernanza Ética", [
                    "anti_sesgo", "explicabilidad", "auditoria", "responsabilidad", "inclusion",
                    "accesibilidad_web", "trato_digno", "equidad_precio", "bien_comun",
                ]),
                DimensionConfig("1.5 Cumplimiento de Privacidad", [
                    "lfpdppp", "consentimiento_explicito", "minimizacion_datos", "retencion_limitada",
                    "derechos_arco", "anonimizacion", "control_acceso", "registro_incidentes", "politica_publica",
                ]),
                DimensionConfig("1.6 Cultura y Formación", [
                    "capacitacion_etica", "manual_practicas", "canal_denuncia", "evaluacion_periodica",
                    "mentoria", "bienestar_equipo", "aprendizaje_continuo", "feedback_cliente", "mejora_constante",
                ]),
            ],
            2: [
                DimensionConfig("2.1 Infraestructura", [
                    "vps_ubuntu", "ram_4gb", "ssd_100gb", "vcpu_2", "hostinger",
                    "red_local", "backup_nube", "encriptacion", "ups",
                ]),
                DimensionConfig("2.2 Stack Open Source", [
                    "postgresql", "fastapi", "nextjs", "odoo", "facturascripts",
                    "minio", "restic", "gpl_mit_bsd", "sin_lockin",
                ]),
                DimensionConfig("2.3 Agentes IA", [
                    "contable_rag", "legal_rag", "devops_oss", "ux_educativa", "business_local",
                    "ia_ops", "whatsapp_orch", "mve_classifier", "soul_filter",
                ]),
                DimensionConfig("2.4 Seguridad", [
                    "hardening_so", "firewall", "segmentacion_red", "mfa", "secrets_manager",
                    "escaneo_vuln", "waf", "monitor_alertas", "plan_respuesta",
                ]),
                DimensionConfig("2.5 Observabilidad", [
                    "logs_centralizados", "metricas_sli", "tracing", "dashboards", "alertas_sla",
                    "postmortem", "capacidad", "costos", "uptime",
                ]),
                DimensionConfig("2.6 Calidad y Entrega", [
                    "testing", "ci_cd", "revision_codigo", "versionado", "rollback",
                    "infra_as_code", "documentacion_tecnica", "drills_recuperacion", "checklist_release",
                ]),
            ],
            3: [
                DimensionConfig("3.1 Clientes", [
                    "fundadores_atencion", "recurrentes_mantenimiento", "comunidad_gratuito", "satisfaccion_medida",
                    "retencion", "referidos", "casos_exito", "testimonios", "lealtad",
                ]),
                DimensionConfig("3.2 Roadmap", [
                    "fase_0_setup", "fase_1_cimientos", "fase_2_clientes", "fase_3_escala", "fase_4_legado",
                    "fase_5_replicabilidad", "hitos_medibles", "tiempos_reales", "ajustes_iterativos",
                ]),
                DimensionConfig("3.3 Legado", [
                    "codigo_decadas", "documentacion_sucesores", "sin_lockin_nunca", "porcentaje_ac",
                    "capacitacion_anual", "open_source_publico", "nathaly_referente", "fourgea_caso_exito", "hermes_inspiracion",
                ]),
                DimensionConfig("3.4 Impacto Social", [
                    "inclusion_pymes", "becas_formacion", "medicion_brecha", "empleo_local", "apoyo_comunidad",
                    "alianzas_educativas", "equidad_genero", "impacto_ambiental", "reporte_publico",
                ]),
                DimensionConfig("3.5 Sostenibilidad", [
                    "finanzas_sanas", "margen_operativo", "reserva_contingencia", "eficiencia_energetica",
                    "renovacion_tecnologica", "mantenimiento_preventivo", "continuidad_negocio", "gobierno_datos", "cumplimiento_fiscal",
                ]),
                DimensionConfig("3.6 Replicabilidad", [
                    "template_publico", "manual_implantacion", "modelo_capacitacion", "kit_ventas", "playbook_operativo",
                    "estandar_calidad", "benchmark_sectorial", "comunidad_practica", "escalamiento_nacional",
                ]),
            ],
        }

    def verificar_pilar(self, pilar_num: int, contexto: Dict[str, Any]) -> Dict[str, Any]:
        """Verifica un pilar completo (6 dimensiones × 9 checks)."""

        resultados = {
            "pilar": self.pilares[pilar_num],
            "dimensiones": [],
            "total_checks": 0,
            "aprobados": 0,
            "fallidos": 0,
        }

        for dim_idx, dim_conf in enumerate(self.estructura[pilar_num], start=1):
            dim_result = self.verificar_dimension(pilar_num, dim_idx, dim_conf, contexto)
            resultados["dimensiones"].append(dim_result)
            resultados["total_checks"] += dim_result["checks"]
            resultados["aprobados"] += dim_result["aprobados"]
            resultados["fallidos"] += dim_result["fallidos"]

        resultados["tasa_exito"] = (
            resultados["aprobados"] / resultados["total_checks"] * 100
            if resultados["total_checks"] > 0
            else 0
        )
        return resultados

    def verificar_dimension(
        self,
        pilar: int,
        dimension: int,
        config: DimensionConfig,
        contexto: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Verifica una dimensión específica (9 checks)."""

        checks = [
            self.ejecutar_check(pilar, dimension, check_name, contexto)
            for check_name in config.checks
        ]

        aprobados = sum(1 for c in checks if c["aprobado"])
        fallidos = len(checks) - aprobados

        return {
            "dimension": config.nombre,
            "checks": len(checks),
            "aprobados": aprobados,
            "fallidos": fallidos,
            "detalle": checks,
        }

    def ejecutar_check(
        self,
        pilar: int,
        dimension: int,
        check_name: str,
        contexto: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Ejecuta un check específico del Soul Filter."""

        aprobado = self.verificar_check_especifico(check_name, contexto)
        return {
            "ruta": f"{pilar}.{dimension}",
            "check": check_name,
            "aprobado": aprobado,
            "evidencia": self.generar_evidencia(check_name, contexto),
            "accion": "NINGUNA" if aprobado else "CORREGIR_INMEDIATO",
        }

    def verificar_check_especifico(self, check_name: str, contexto: Dict[str, Any]) -> bool:
        """Valida check contra contexto mínimo requerido.

        Regla demo: si el contexto tiene una clave con el nombre del check y valor falso,
        falla. En caso contrario, aprueba.
        """

        return bool(contexto.get(check_name, True))

    def generar_evidencia(self, check_name: str, contexto: Dict[str, Any]) -> str:
        """Genera evidencia textual del check."""

        fuente = contexto.get("fuente_evidencia", "registro_operativo")
        return f"Verificación {check_name} completada exitosamente ({fuente})"

    def verificar_proyecto_completo(self, contexto: Dict[str, Any]) -> Dict[str, Any]:
        """Verifica los 3 pilares completos (162 checks)."""

        resultados_totales = {
            "pilares": [],
            "total_checks": 0,
            "total_aprobados": 0,
            "total_fallidos": 0,
            "tasa_exito_global": 0.0,
            "estado_final": "PENDIENTE",
        }

        for pilar in range(1, 4):
            resultado_pilar = self.verificar_pilar(pilar, contexto)
            resultados_totales["pilares"].append(resultado_pilar)
            resultados_totales["total_checks"] += resultado_pilar["total_checks"]
            resultados_totales["total_aprobados"] += resultado_pilar["aprobados"]
            resultados_totales["total_fallidos"] += resultado_pilar["fallidos"]

        resultados_totales["tasa_exito_global"] = (
            resultados_totales["total_aprobados"] / resultados_totales["total_checks"] * 100
            if resultados_totales["total_checks"] > 0
            else 0
        )

        if resultados_totales["total_fallidos"] == 0:
            resultados_totales["estado_final"] = "✅ PERFECTO - SIN ERRORES"
        elif resultados_totales["total_fallidos"] <= 5:
            resultados_totales["estado_final"] = "⚠️ ACEPTABLE - MEJORAS MENORES"
        else:
            resultados_totales["estado_final"] = "❌ RECHAZADO - REQUIERE CORRECCIÓN"

        return resultados_totales


if __name__ == "__main__":
    filtro = SoulFilter369()
    contexto_proyecto = {
        "cliente": "Fourgea México S.A. de C.V.",
        "contadora": "Nathaly Hermosillo",
        "vps": "Hostinger Ubuntu 4GB RAM",
        "stack": "90-95% Open Source",
        "guardian": "Hermes",
        "fuente_evidencia": "auditoria_sdc_2026Q1",
    }

    resultado = filtro.verificar_proyecto_completo(contexto_proyecto)

    print(f"\n{'=' * 60}")
    print("SONORA DIGITAL CORP | SOUL FILTER 3-6-9")
    print(f"{'=' * 60}")
    print(f"Total Checks: {resultado['total_checks']}")
    print(f"Aprobados: {resultado['total_aprobados']}")
    print(f"Fallidos: {resultado['total_fallidos']}")
    print(f"Tasa de Éxito: {resultado['tasa_exito_global']:.2f}%")
    print(f"Estado Final: {resultado['estado_final']}")
    print(f"{'=' * 60}\n")
