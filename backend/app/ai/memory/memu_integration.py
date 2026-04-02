"""
memU Integration — HERMES AI OS
Memoria proactiva 24/7 para Brain IA.
Usa memu-py (v0.1.8) sobre Ollama local (DeepSeek-R1:1.5b).
"""
import os
from typing import Optional
from memu import MemoryAgent, config as memu_config

# Config memU con Ollama local
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434/v1")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "deepseek-r1:1.5b")

def get_memu_agent(tenant_id: str) -> Optional[MemoryAgent]:
    """Crea un agente memU con Ollama local para el tenant."""
    try:
        agent = MemoryAgent(
            llm_provider="openai",   # Ollama usa API compatible OpenAI
            llm_base_url=OLLAMA_URL,
            llm_model=OLLAMA_MODEL,
            llm_api_key="ollama",    # dummy key para Ollama
            scope=f"hermes:{tenant_id}",
        )
        return agent
    except Exception as e:
        print(f"[memU] Error inicializando agente: {e}")
        return None


async def memorize_interaction(
    tenant_id: str,
    user_message: str,
    ai_response: str,
    channel: str = "web",
) -> bool:
    """Guarda una interacción en memU para contexto futuro."""
    agent = get_memu_agent(tenant_id)
    if not agent:
        return False
    try:
        await agent.memorize(
            content=f"[{channel}] Usuario: {user_message}\nAsistente: {ai_response}",
            metadata={"tenant_id": tenant_id, "channel": channel},
        )
        return True
    except Exception as e:
        print(f"[memU] Error memorizando: {e}")
        return False


async def recall_context(tenant_id: str, query: str, top_k: int = 5) -> str:
    """Recupera contexto relevante de memU para una consulta."""
    agent = get_memu_agent(tenant_id)
    if not agent:
        return ""
    try:
        memories = await agent.recall(query=query, top_k=top_k)
        if not memories:
            return ""
        context_lines = [f"- {m.content}" for m in memories]
        return "Contexto previo relevante:\n" + "\n".join(context_lines)
    except Exception as e:
        print(f"[memU] Error recuperando contexto: {e}")
        return ""
