#!/usr/bin/env python3
"""
MYSTIC Brain Eval - Script principal para evaluar calidad del Brain IA
"""
import argparse
import sys
from pathlib import Path

# Agregar packages al path
sys.path.insert(0, str(Path(__file__).parent))

from mystic_evals import EvalSuite, EvalRunner


def main():
    parser = argparse.ArgumentParser(description="MYSTIC Brain Evaluation")
    parser.add_argument("--suite", required=True, help="Path al YAML de la suite")
    parser.add_argument("--api-url", default="http://localhost:8000", help="URL de la API")
    parser.add_argument("--token", help="JWT token de autenticación")
    parser.add_argument("--tenant", help="Tenant ID")
    parser.add_argument("--output", choices=["table", "json"], default="table", help="Formato de output")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose mode")
    parser.add_argument("--category", help="Filtrar por categoría")
    
    args = parser.parse_args()
    
    # Cargar suite
    print(f"Cargando suite: {args.suite}")
    suite = EvalSuite.from_yaml(args.suite)
    
    # Filtrar por categoría si se especifica
    if args.category:
        suite = suite.filter_by_category(args.category)
        print(f"Filtrado por categoría: {args.category} ({len(suite.cases)} casos)")
    
    print(f"Total casos a evaluar: {len(suite.cases)}")
    print("-" * 50)
    
    # Configurar runner
    runner = EvalRunner(
        api_url=args.api_url,
        token=args.token,
        tenant_id=args.tenant,
    )
    
    # Ejecutar evaluaciones
    results = runner.run(suite)
    
    # Generar reporte
    report = runner.generate_report(results, output_format=args.output)
    print("\n" + report)
    
    # Guardar resultado JSON si se solicita
    if args.output == "json":
        output_file = "eval_results.json"
        with open(output_file, "w") as f:
            f.write(report)
        print(f"\nResultados guardados en: {output_file}")
    
    # Determinar exit code
    passed = sum(1 for r in results if r.status == "pass")
    total = len(results)
    pass_rate = passed / total if total > 0 else 0
    
    if pass_rate < 0.8:
        print(f"\n⚠️  WARNING: Pass rate {pass_rate:.1%} below 80%")
        return 1
    
    print(f"\n✓ Pass rate: {pass_rate:.1%}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
