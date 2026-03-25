"""
Tool Use Integration para HERMES Brain
Detecta intención de ejecutar acciones y usa herramientas LangChain-style
"""
from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class ToolCall:
    """Representa una llamada a herramienta detectada en el input del usuario."""
    tool_name: str
    arguments: Dict[str, Any]
    confidence: float  # 0.0 - 1.0
    original_phrase: str = ""


@dataclass 
class ToolUseResult:
    """Resultado de la ejecución de herramienta(s)."""
    tool_calls: List[ToolCall]
    results: List[Dict[str, Any]]
    should_respond_with_tool_result: bool
    natural_language_summary: str


# ── Patrones de detección de intención ────────────────────────────────────────

TOOL_PATTERNS = {
    "n8n_trigger": [
        (r"(ejecuta|corre|activa|dispara)\s+(el\s+)?(workflow|proceso|automatización)\s+['\"]?(\w+)['\"]?", 0.9),
        (r"(inicia|comienza)\s+(el\s+)?(proceso\s+de\s+)?(['\"]?\w+['\"]?)", 0.7),
        (r"(haz|realiza)\s+(un\s+)?(cierre|clasificación|pedimento|onboarding)", 0.85),
    ],
    "database_query": [
        (r"(busca|muestra|lista|dame|consulta)\s+(las\s+)?(facturas|nóminas|empleados|clientes|proveedores)", 0.9),
        (r"(cuántas?\s+(facturas|nóminas|empleados)|total\s+de\s+(facturas|ventas))", 0.85),
        (r"(actualiza|cambia|modifica|edita)\s+(la\s+)?(factura|nómina|empleado)", 0.85),
        (r"(crea|agrega|registra)\s+(una\s+)?(factura|nómina|empleado|cliente)", 0.85),
        (r"(elimina|borra|cancela)\s+(la\s+)?(factura|nómina|empleado)", 0.8),
    ],
    "sat_query": [
        (r"(verifica|valida|consulta)\s+(el\s+)?(cfdi|factura)\s+['\"]?([A-F0-9-]+)['\"]?", 0.95),
        (r"(consulta|busca)\s+(el\s+)?(rfc|contribuyente)\s+['\"]?(\w+)['\"]?", 0.9),
        (r"(cuándo\s+vence|fecha\s+límite|calendario)\s+(del\s+)?(mes|año|SAT)?", 0.8),
    ],
    "rag_index": [
        (r"(indexa|guarda|almacena)\s+(estos\s+)?(documentos|archivos|datos)", 0.85),
        (r"(agrega\s+a\s+la\s+base\s+de\s+conocimiento|entrena\s+con\s+esto)", 0.8),
    ],
}

# Keywords para extracción de argumentos
ARG_KEYWORDS = {
    "facturas": {"entity": "facturas", "keywords": ["factura", "facturas", "cfdi", "ingreso", "egreso"]},
    "nóminas": {"entity": "nomina", "keywords": ["nómina", "nominas", "sueldo", "salario", "imss"]},
    "empleados": {"entity": "empleados", "keywords": ["empleado", "empleados", "trabajador", "trabajadores"]},
    "clientes": {"entity": "clientes", "keywords": ["cliente", "clientes", "receptor", "comprador"]},
    "proveedores": {"entity": "proveedores", "keywords": ["proveedor", "proveedores", "emisor", "vendedor"]},
}


def detect_tool_calls(user_input: str) -> List[ToolCall]:
    """
    Detecta si el input del usuario requiere ejecutar herramientas.
    Retorna lista de ToolCall con confianza > 0.7
    """
    tool_calls = []
    input_lower = user_input.lower()
    
    for tool_name, patterns in TOOL_PATTERNS.items():
        for pattern, base_confidence in patterns:
            match = re.search(pattern, input_lower, re.IGNORECASE)
            if match:
                # Extraer argumentos del match
                arguments = extract_arguments(tool_name, match, user_input)
                
                # Ajustar confianza según calidad de argumentos
                confidence = base_confidence
                if arguments and len(arguments) > 0:
                    confidence = min(confidence + 0.1, 1.0)
                
                tool_calls.append(ToolCall(
                    tool_name=tool_name,
                    arguments=arguments,
                    confidence=confidence,
                    original_phrase=match.group(0)
                ))
                break  # Solo un match por herramienta
    
    # Filtrar por confianza mínima
    return [tc for tc in tool_calls if tc.confidence >= 0.7]


def extract_arguments(tool_name: str, match: re.Match, full_input: str) -> Dict[str, Any]:
    """Extrae argumentos del match basado en el tipo de herramienta."""
    args = {}
    
    if tool_name == "n8n_trigger":
        # Intentar extraer nombre del workflow
        words = full_input.lower().split()
        workflow_keywords = ["cierre", "clasificación", "clasificacion", "pedimento", "onboarding", "mensual"]
        for word in words:
            if word in workflow_keywords:
                args["workflow_name"] = word
                break
        
        # Payload por defecto
        args["payload"] = {"source": "brain", "triggered_by": "user_request"}
        args["wait_for_response"] = "espera" in full_input.lower() or "resultado" in full_input.lower()
        
    elif tool_name == "database_query":
        # Determinar entidad
        for keyword, config in ARG_KEYWORDS.items():
            if keyword in full_input.lower():
                args["entity"] = config["entity"]
                break
        
        # Determinar operación
        if any(w in full_input.lower() for w in ["busca", "muestra", "lista", "dame", "consulta", "cuántas"]):
            args["operation"] = "list"
        elif any(w in full_input.lower() for w in ["actualiza", "cambia", "modifica", "edita"]):
            args["operation"] = "update"
        elif any(w in full_input.lower() for w in ["crea", "agrega", "registra"]):
            args["operation"] = "create"
        elif any(w in full_input.lower() for w in ["elimina", "borra", "cancela"]):
            args["operation"] = "delete"
        else:
            args["operation"] = "list"
        
        args["filters"] = {}
        args["limit"] = 50
        
    elif tool_name == "sat_query":
        # Detectar acción
        if any(w in full_input.lower() for w in ["verifica", "valida", "cfdi"]):
            args["action"] = "verificar_cfdi"
            # Intentar extraer UUID
            uuid_match = re.search(r'[A-F0-9]{8}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{12}', full_input, re.IGNORECASE)
            if uuid_match:
                args["uuid"] = uuid_match.group(0)
        elif any(w in full_input.lower() for w in ["rfc", "contribuyente"]):
            args["action"] = "consultar_contribuyente"
            # Intentar extraer RFC
            rfc_match = re.search(r'\b[A-ZÑ&]{3,4}\d{6}[A-Z0-9]{2,3}\b', full_input)
            if rfc_match:
                args["rfc"] = rfc_match.group(0)
        else:
            args["action"] = "calendario"
    
    elif tool_name == "rag_index":
        args["collection"] = "general"
        args["documents"] = [{"title": "Documento indexado", "content": full_input}]
    
    return args


async def execute_tool_call(tool_call: ToolCall, tenant_id: Optional[str] = None) -> Dict[str, Any]:
    """Ejecuta una llamada a herramienta y retorna el resultado."""
    try:
        from app.ai.tools.base import get_tool
    except ImportError:
        try:
            from tools.base import get_tool
        except ImportError:
            from ai.tools.base import get_tool
    
    tool = get_tool(tool_call.tool_name)
    if not tool:
        return {"error": f"Herramienta '{tool_call.tool_name}' no encontrada"}
    
    try:
        result = tool(input_data=tool_call.arguments, tenant_id=tenant_id)
        return result.model_dump()
    except Exception as e:
        logger.error(f"Tool execution failed: {e}")
        return {"error": str(e), "status": "error"}


async def process_with_tools(
    question: str,
    tenant_id: Optional[str] = None,
    execute_tools: bool = True
) -> ToolUseResult:
    """
    Procesa pregunta detectando si requiere tool use.
    
    Si execute_tools=True, ejecuta las herramientas detectadas.
    Si execute_tools=False, solo detecta pero no ejecuta (útil para confirmación).
    """
    # Detectar tool calls
    tool_calls = detect_tool_calls(question)
    
    if not tool_calls:
        return ToolUseResult(
            tool_calls=[],
            results=[],
            should_respond_with_tool_result=False,
            natural_language_summary=""
        )
    
    results = []
    if execute_tools:
        # Ejecutar cada herramienta detectada
        for tc in tool_calls:
            result = await execute_tool_call(tc, tenant_id)
            results.append(result)
    
    # Generar resumen en lenguaje natural
    summary = generate_tool_summary(tool_calls, results)
    
    return ToolUseResult(
        tool_calls=tool_calls,
        results=results,
        should_respond_with_tool_result=len(results) > 0,
        natural_language_summary=summary
    )


def generate_tool_summary(tool_calls: List[ToolCall], results: List[Dict]) -> str:
    """Genera resumen en lenguaje natural de las herramientas ejecutadas."""
    if not tool_calls:
        return ""
    
    summaries = []
    for i, (tc, result) in enumerate(zip(tool_calls, results)):
        if tc.tool_name == "n8n_trigger":
            workflow = tc.arguments.get("workflow_name", "desconocido")
            if result.get("status") == "success":
                summaries.append(f"✅ Workflow '{workflow}' ejecutado exitosamente")
            else:
                summaries.append(f"❌ Error ejecutando workflow '{workflow}': {result.get('error', 'desconocido')}")
        
        elif tc.tool_name == "database_query":
            entity = tc.arguments.get("entity", "datos")
            op = tc.arguments.get("operation", "consulta")
            if result.get("status") == "success":
                data = result.get("data", {})
                count = data.get("count", len(data.get("data", [])))
                summaries.append(f"📊 {op.capitalize()} de {entity}: {count} registros encontrados")
            else:
                summaries.append(f"❌ Error en {op} de {entity}: {result.get('error', 'desconocido')}")
        
        elif tc.tool_name == "sat_query":
            action = tc.arguments.get("action", "consulta")
            if result.get("status") == "success":
                summaries.append(f"✅ Consulta SAT ({action}) completada")
            else:
                summaries.append(f"❌ Error en consulta SAT: {result.get('error', 'desconocido')}")
        
        elif tc.tool_name == "rag_index":
            if result.get("status") == "success":
                indexed = result.get("data", {}).get("indexed", 0)
                summaries.append(f"📚 {indexed} documentos indexados en Qdrant")
            else:
                summaries.append(f"❌ Error indexando documentos: {result.get('error', 'desconocido')}")
    
    return "\n".join(summaries)


# ── Integración con el endpoint /api/brain/ask ────────────────────────────────

async def brain_ask_with_tools(
    question: str,
    rag_fn,  # async function para RAG
    ollama_fn,  # function para LLM
    tenant_id: Optional[str] = None,
    db_session=None
) -> Dict[str, Any]:
    """
    Versión mejororada de brain_ask que integra tool use.
    
    Flujo:
    1. Detectar si la pregunta requiere ejecutar herramientas
    2. Si SÍ: ejecutar herramientas, incorporar resultados al contexto
    3. Si NO: flujo RAG normal
    4. Generar respuesta con Ollama incluyendo resultados de herramientas si existen
    """
    # Paso 1: Detectar tool use
    tool_result = await process_with_tools(question, tenant_id, execute_tools=True)
    
    # Paso 2: Obtener contexto RAG (siempre, para tener información adicional)
    rag_context = await rag_fn(question, tenant_id=tenant_id)
    
    # Paso 3: Construir prompt final
    prompt_parts = []
    
    # Agregar resultados de herramientas si existen
    if tool_result.tool_calls:
        prompt_parts.append("=== RESULTADOS DE HERRAMIENTAS EJECUTADAS ===")
        prompt_parts.append(tool_result.natural_language_summary)
        for result in tool_result.results:
            if result.get("status") == "success":
                prompt_parts.append(f"Datos: {json.dumps(result.get('data', {}), ensure_ascii=False)[:1000]}")
        prompt_parts.append("")
    
    # Agregar contexto RAG
    if rag_context:
        prompt_parts.append("=== CONTEXTO DOCUMENTAL ===")
        for chunk in rag_context[:3]:
            prompt_parts.append(f"[{chunk.get('title', '')}]\n{chunk.get('content', '')[:300]}")
    
    # Prompt final para Ollama
    system_prompt = """Eres un asistente contable experto de HERMES. 
Responde de forma clara, concisa y profesional.
Si hay resultados de herramientas ejecutadas, úsalos como fuente primaria de verdad.
Si hay contexto documental, intégralo en tu respuesta.
Si no tienes información suficiente, sé honesto y di qué necesitas."""
    
    user_prompt = f"Pregunta: {question}\n\n" + "\n".join(prompt_parts)
    
    # Paso 4: Llamar a Ollama
    try:
        llm_response = ollama_fn(system_prompt, user_prompt)
    except Exception as e:
        logger.error(f"Ollama failed: {e}")
        # Fallback: devolver resultados de herramientas directamente
        if tool_result.results:
            llm_response = f"Aquí están los resultados:\n\n{tool_result.natural_language_summary}"
        else:
            llm_response = "Lo siento, tuve un error procesando tu pregunta. Por favor intenta de nuevo."
    
    return {
        "answer": llm_response,
        "tool_calls": [
            {"tool": tc.tool_name, "arguments": tc.arguments, "confidence": tc.confidence}
            for tc in tool_result.tool_calls
        ] if tool_result.tool_calls else [],
        "tool_results": tool_result.results,
        "rag_used": len(rag_context) > 0,
        "sources": [c.get("title") for c in rag_context[:3]] if rag_context else []
    }
