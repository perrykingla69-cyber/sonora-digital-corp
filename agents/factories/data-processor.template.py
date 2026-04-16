"""
Agent: {{AGENT_NAME}}
Type: data-processor
Description: {{AGENT_DESCRIPTION}}
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import os
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="{{AGENT_NAME}} — Data Processor")

AGENT_ID = os.getenv("AGENT_ID", "{{AGENT_ID}}")
TENANT_ID = os.getenv("TENANT_ID", "{{TENANT_ID}}")
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY", "")
# Procesamiento de datos usa Claude para mayor precisión
MODEL = "anthropic/claude-3-5-haiku"

PROCESSOR_PROMPT = """Eres {{AGENT_NAME}}, un procesador de datos especializado en {{VERTICALES}}.

{{AGENT_DESCRIPTION}}

Tu función es analizar datos, extraer insights y generar reportes estructurados.
Siempre devuelve resultados en JSON válido cuando se solicite estructura.
Sé preciso con números, fechas y estadísticas."""


class ProcessRequest(BaseModel):
    data: str | dict | list
    analysis_type: str = "summary"  # summary | insights | trends | anomalies | report
    output_format: str = "text"  # text | json | markdown
    user_id: str = ""


class ProcessResponse(BaseModel):
    result: str | dict
    analysis_type: str
    tokens_used: int = 0


@app.post("/process", response_model=ProcessResponse)
async def process_data(body: ProcessRequest):
    data_str = json.dumps(body.data) if not isinstance(body.data, str) else body.data

    format_instruction = ""
    if body.output_format == "json":
        format_instruction = "\nDevuelve SOLO JSON válido, sin texto adicional."
    elif body.output_format == "markdown":
        format_instruction = "\nFormatea la respuesta en Markdown con headers y listas."

    prompt = f"""Análisis tipo: {body.analysis_type}

Datos a procesar:
{data_str}

{format_instruction}

Proporciona un análisis detallado y accionable."""

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENROUTER_KEY}"},
            json={
                "model": MODEL,
                "messages": [
                    {"role": "system", "content": PROCESSOR_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                "max_tokens": 2000,
            },
        )
        resp.raise_for_status()
        data = resp.json()

    raw = data["choices"][0]["message"]["content"]
    tokens = data.get("usage", {}).get("total_tokens", 0)

    # Parse JSON si se solicitó
    result: str | dict = raw
    if body.output_format == "json":
        try:
            result = json.loads(raw)
        except json.JSONDecodeError:
            result = {"raw": raw, "parse_error": "El modelo no devolvió JSON válido"}

    return ProcessResponse(
        result=result,
        analysis_type=body.analysis_type,
        tokens_used=tokens,
    )


@app.get("/health")
async def health():
    return {"status": "ok", "agent": "{{AGENT_NAME}}", "agent_id": AGENT_ID}
