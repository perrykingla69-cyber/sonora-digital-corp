"""
MYSTIC Evals - Runner de evaluaciones
"""
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
import httpx

from .contracts import EvalCase, EvalResult, EvalSuite
from .scorer import EvalScorer

logger = logging.getLogger(__name__)


class EvalRunner:
    """
    Ejecuta suites de evaluación contra el Brain IA.
    
    Uso:
        runner = EvalRunner(api_url="http://localhost:8000", token="xxx")
        suite = EvalSuite.from_yaml("cases/fiscal_mx.yaml")
        results = runner.run(suite)
        report = runner.generate_report(results)
    """
    
    def __init__(
        self,
        api_url: str = "http://localhost:8000",
        token: Optional[str] = None,
        tenant_id: Optional[str] = None,
    ):
        self.api_url = api_url.rstrip("/")
        self.token = token
        self.tenant_id = tenant_id
        self.scorer = EvalScorer()
    
    def run(
        self,
        suite: EvalSuite,
        conversation_id: Optional[str] = None,
    ) -> List[EvalResult]:
        """
        Ejecutar todos los casos de una suite.
        
        Returns:
            Lista de EvalResult por cada caso
        """
        results = []
        
        for i, case in enumerate(suite.cases):
            logger.info(f"[{i+1}/{len(suite.cases)}] Evaluando: {case.name}")
            
            try:
                # Llamar al Brain IA
                answer_data = self._call_brain(
                    query=case.query,
                    tenant_id=case.tenant_id or self.tenant_id,
                    conversation_id=conversation_id,
                )
                
                # Calcular score
                result = self.scorer.score(
                    case=case,
                    actual_answer=answer_data.get("answer", ""),
                    actual_sources=answer_data.get("sources", []),
                    actual_tool_calls=answer_data.get("tool_calls", []),
                    latency_ms=answer_data.get("latency_ms", 0),
                    confidence=answer_data.get("confidence", 0.0),
                )
                
                results.append(result)
                
                status_icon = "✓" if result.passed else "✗"
                logger.info(f"  {status_icon} Score: {result.answer_match:.2f} | "
                           f"Latency: {result.latency_ms}ms | "
                           f"Confidence: {result.confidence:.2f}")
                
            except Exception as e:
                logger.error(f"  Error: {e}")
                results.append(EvalResult(
                    case_id=case.id,
                    case_name=case.name,
                    status="error",
                    error=str(e),
                ))
        
        return results
    
    def _call_brain(
        self,
        query: str,
        tenant_id: Optional[str],
        conversation_id: Optional[str],
    ) -> Dict[str, Any]:
        """Llamar al endpoint del Brain IA."""
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        
        payload = {
            "query": query,
            "tenant_id": tenant_id or "default",
            "conversation_id": conversation_id,
        }
        
        with httpx.Client(timeout=60) as client:
            response = client.post(
                f"{self.api_url}/api/brain/ask",
                json=payload,
                headers=headers,
            )
            response.raise_for_status()
            return response.json()
    
    def generate_report(
        self,
        results: List[EvalResult],
        output_format: str = "table",
    ) -> str:
        """Generar reporte de resultados."""
        total = len(results)
        passed = sum(1 for r in results if r.status == "pass")
        failed = sum(1 for r in results if r.status == "fail")
        errors = sum(1 for r in results if r.status == "error")
        
        avg_answer_match = sum(r.answer_match for r in results) / total if total else 0
        avg_latency = sum(r.latency_ms for r in results) / total if total else 0
        
        if output_format == "json":
            report = {
                "summary": {
                    "total": total,
                    "passed": passed,
                    "failed": failed,
                    "errors": errors,
                    "pass_rate": passed / total if total else 0,
                    "avg_answer_match": avg_answer_match,
                    "avg_latency_ms": avg_latency,
                },
                "results": [
                    {
                        "case_id": r.case_id,
                        "case_name": r.case_name,
                        "status": r.status,
                        "answer_match": r.answer_match,
                        "sources_match": r.sources_match,
                        "tool_calls_match": r.tool_calls_match,
                        "latency_ms": r.latency_ms,
                        "confidence": r.confidence,
                        "error": r.error,
                    }
                    for r in results
                ],
            }
            return json.dumps(report, indent=2)
        
        # Formato table (por defecto)
        lines = [
            "=" * 70,
            "MYSTIC EVAL REPORT",
            "=" * 70,
            "",
            "SUMMARY",
            f"  Total cases:     {total}",
            f"  Passed:          {passed} ({passed/total*100:.1f}%)" if total else "  Passed:          0",
            f"  Failed:          {failed}",
            f"  Errors:          {errors}",
            "",
            "METRICS",
            f"  Avg answer match: {avg_answer_match:.2f}",
            f"  Avg latency:      {avg_latency:.0f}ms",
            "",
            "RESULTS BY CASE",
            "-" * 70,
        ]
        
        for r in results:
            icon = "✓" if r.status == "pass" else ("✗" if r.status == "fail" else "⚠")
            lines.append(
                f"{icon} {r.case_name:<30} | "
                f"score={r.answer_match:.2f} | "
                f"latency={r.latency_ms:>5}ms | "
                f"conf={r.confidence:.2f}"
            )
            if r.error:
                lines.append(f"  ERROR: {r.error}")
        
        lines.append("")
        lines.append("=" * 70)
        
        return "\n".join(lines)


def main():
    """CLI simple para ejecutar evals."""
    import argparse
    
    parser = argparse.ArgumentParser(description="MYSTIC Eval Runner")
    parser.add_argument("--suite", required=True, help="Path al YAML de la suite")
    parser.add_argument("--api-url", default="http://localhost:8000")
    parser.add_argument("--token", help="JWT token")
    parser.add_argument("--tenant", help="Tenant ID")
    parser.add_argument("--output", choices=["table", "json"], default="table")
    parser.add_argument("--verbose", "-v", action="store_true")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.basicConfig(level=logging.INFO)
    
    runner = EvalRunner(
        api_url=args.api_url,
        token=args.token,
        tenant_id=args.tenant,
    )
    
    suite = EvalSuite.from_yaml(args.suite)
    results = runner.run(suite)
    report = runner.generate_report(results, output_format=args.output)
    
    print(report)


if __name__ == "__main__":
    main()
