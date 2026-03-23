# packages/evals

Framework de evaluación de calidad para el Brain IA de MYSTIC.

## Instalación

```bash
pip install -e packages/evals
```

## Uso

### CLI

```bash
mystic-eval --suite packages/evals/mystic_evals/cases/fiscal_mx.yaml \
            --api-url http://localhost:8000 \
            --token $JWT_TOKEN \
            --tenant fourgea
```

### Python API

```python
from mystic_evals import EvalSuite, EvalRunner

suite = EvalSuite.from_yaml("cases/fiscal_mx.yaml")
runner = EvalRunner(api_url="http://localhost:8000", token="jwt_token")
results = runner.run(suite)
print(runner.generate_report(results))
```

## Componentes

- `EvalCase` - Caso individual de prueba
- `EvalSuite` - Colección de casos (YAML)
- `EvalScorer` - Calcula scores de calidad
- `EvalRunner` - Ejecuta suite y genera reportes

## Desarrollo

```bash
cd packages/evals
pip install -e ".[dev]"
pytest
```
