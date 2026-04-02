"""
LangChain-style Tools para HERMES
Herramientas ejecutables por el Brain/Orchestrator con schema formal
"""
from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Type
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


# ── Base Tool con Schema Formal (Skills 2.5) ──────────────────────────────────

class ToolInput(BaseModel):
    """Base schema para input de herramientas."""
    pass


class ToolResult(BaseModel):
    """Resultado estandarizado de herramienta."""
    tool_name: str
    status: str  # "success" | "error"
    data: Any = None
    error: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    tenant_id: Optional[str] = None
    execution_time_ms: Optional[int] = None


class BaseTool(ABC):
    """
    Herramienta base estilo LangChain con:
    - JSON schema para input/output
    - Tenant awareness
    - Telemetría básica
    - Permisos por rol
    """
    name: str = "base_tool"
    description: str = ""
    input_schema: Type[ToolInput] = ToolInput
    
    # Metadatos para Skills 2.5
    category: str = "general"  # n8n, database, sat, filesystem, etc.
    requires_auth: bool = True
    allowed_roles: List[str] = ["admin", "contador", "analista"]
    rate_limit_per_minute: int = 60
    
    @abstractmethod
    def execute(self, **kwargs: Any) -> Any:
        """Implementar lógica de la herramienta."""
        pass
    
    def __call__(self, input_data: Dict[str, Any], tenant_id: Optional[str] = None) -> ToolResult:
        """Ejecutar herramienta con telemetría."""
        start = datetime.now()
        try:
            # Validar schema de entrada
            validated = self.input_schema(**input_data)
            
            # Ejecutar
            result = self.execute(**validated.model_dump())
            
            elapsed = int((datetime.now() - start).total_seconds() * 1000)
            
            return ToolResult(
                tool_name=self.name,
                status="success",
                data=result,
                tenant_id=tenant_id,
                execution_time_ms=elapsed
            )
        except Exception as e:
            logger.error(f"Tool {self.name} failed: {e}")
            elapsed = int((datetime.now() - start).total_seconds() * 1000)
            return ToolResult(
                tool_name=self.name,
                status="error",
                error=str(e),
                tenant_id=tenant_id,
                execution_time_ms=elapsed
            )
    
    def get_openai_function_def(self) -> Dict[str, Any]:
        """Retorna definición compatible con OpenAI function calling."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.input_schema.model_json_schema()
        }


# ── Tool: N8N Trigger ─────────────────────────────────────────────────────────

class N8NTriggerInput(ToolInput):
    workflow_name: str = Field(..., description="Nombre del workflow en N8N")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Datos para el webhook")
    wait_for_response: bool = Field(default=False, description="Esperar respuesta síncrona")


class N8NTriggerTool(BaseTool):
    name = "n8n_trigger"
    description = "Ejecuta un workflow de N8N vía webhook. Útil para automatizaciones."
    input_schema = N8NTriggerInput
    category = "n8n"
    allowed_roles = ["admin", "contador", "analista"]
    
    def execute(self, workflow_name: str, payload: Dict[str, Any], wait_for_response: bool = False) -> Dict:
        import httpx
        
        # Mapeo nombre → webhook URL (configurable)
        WORKFLOW_MAP = {
            "clasificacion_arancelaria": "http://localhost:5678/webhook/clasificar-arancel",
            "pedimento": "http://localhost:5678/webhook/pedimento",
            "onboarding": "http://localhost:5678/webhook/onboarding-complete",
            "cierre_mensual": "http://localhost:5678/webhook/cierre-mensual",
        }
        
        url = WORKFLOW_MAP.get(workflow_name.lower().replace(" ", "_").replace("-", "_"))
        if not url:
            raise ValueError(f"Workflow '{workflow_name}' no encontrado. Disponibles: {list(WORKFLOW_MAP.keys())}")
        
        with httpx.Client(timeout=30.0) as client:
            response = client.post(url, json=payload)
            response.raise_for_status()
            
            if wait_for_response:
                return {"triggered": True, "response": response.json()}
            else:
                return {"triggered": True, "workflow": workflow_name, "async": True}


# ── Tool: SAT Query ───────────────────────────────────────────────────────────

class SATQueryInput(ToolInput):
    action: str = Field(..., description="acción: verificar_cfdi, consultar_contribuyente, calendario")
    rfc: Optional[str] = Field(None, description="RFC del contribuyente")
    uuid: Optional[str] = Field(None, description="UUID del CFDI")
    fecha: Optional[str] = Field(None, description="Fecha YYYY-MM-DD")


class SATQueryTool(BaseTool):
    name = "sat_query"
    description = "Consulta servicios del SAT: verificación CFDI, estado contribuyente, calendario fiscal."
    input_schema = SATQueryInput
    category = "sat"
    allowed_roles = ["admin", "contador"]
    
    def execute(self, action: str, rfc: Optional[str] = None, uuid: Optional[str] = None, fecha: Optional[str] = None) -> Dict:
        import httpx
        
        BASE_URL = "http://localhost:8000/api/sat"
        
        if action == "verificar_cfdi":
            if not uuid:
                raise ValueError("UUID requerido para verificar CFDI")
            url = f"{BASE_URL}/verificar/{uuid}"
            
        elif action == "consultar_contribuyente":
            if not rfc:
                raise ValueError("RFC requerido para consultar contribuyente")
            url = f"{BASE_URL}/contribuyente/{rfc}"
            
        elif action == "calendario":
            url = f"{BASE_URL}/calendario"
            if fecha:
                url += f"?fecha={fecha}"
        else:
            raise ValueError(f"Acción '{action}' no válida. Usa: verificar_cfdi, consultar_contribuyente, calendario")
        
        with httpx.Client(timeout=30.0) as client:
            response = client.get(url)
            response.raise_for_status()
            return response.json()


# ── Tool: Database Query ──────────────────────────────────────────────────────

class DBQueryInput(ToolInput):
    entity: str = Field(..., description="Entidad: facturas, nomina, empleados, clientes, proveedores")
    operation: str = Field(..., description="operación: list, get, create, update, delete")
    filters: Dict[str, Any] = Field(default_factory=dict, description="Filtros para búsqueda")
    data: Optional[Dict[str, Any]] = Field(None, description="Datos para create/update")
    limit: int = Field(default=100, description="Límite de resultados")


class DBQueryTool(BaseTool):
    name = "database_query"
    description = "Consulta y modifica la base de datos PostgreSQL. Entidades: facturas, nómina, empleados, etc."
    input_schema = DBQueryInput
    category = "database"
    allowed_roles = ["admin", "contador"]
    
    def execute(self, entity: str, operation: str, filters: Dict[str, Any] = None, 
                data: Dict[str, Any] = None, limit: int = 100) -> Dict:
        from sqlalchemy import text
        from database import get_db
        
        # Mapeo entidad → tabla
        TABLE_MAP = {
            "facturas": "facturas",
            "nomina": "nominas",
            "empleados": "empleados",
            "clientes": "contactos",
            "proveedores": "contactos",
            "usuarios": "usuarios",
        }
        
        table = TABLE_MAP.get(entity.lower())
        if not table:
            raise ValueError(f"Entidad '{entity}' no válida. Disponibles: {list(TABLE_MAP.keys())}")
        
        db = next(get_db())
        try:
            if operation == "list":
                where_clause = ""
                params = {}
                if filters:
                    conditions = []
                    for i, (k, v) in enumerate(filters.items()):
                        conditions.append(f"{k} = :param_{i}")
                        params[f"param_{i}"] = v
                    where_clause = " WHERE " + " AND ".join(conditions)
                
                query = text(f"SELECT * FROM {table}{where_clause} LIMIT :limit")
                params["limit"] = limit
                result = db.execute(query, params).fetchall()
                return {"count": len(result), "data": [dict(r._mapping) for r in result]}
            
            elif operation == "get":
                if not filters or "id" not in filters:
                    raise ValueError("Filtro 'id' requerido para operación get")
                query = text(f"SELECT * FROM {table} WHERE id = :id")
                result = db.execute(query, {"id": filters["id"]}).fetchone()
                return {"data": dict(result._mapping) if result else None}
            
            elif operation == "create":
                if not data:
                    raise ValueError("Datos requeridos para create")
                columns = ", ".join(data.keys())
                placeholders = ", ".join([f":{k}" for k in data.keys()])
                query = text(f"INSERT INTO {table} ({columns}) VALUES ({placeholders}) RETURNING *")
                result = db.execute(query, data).fetchone()
                db.commit()
                return {"created": True, "data": dict(result._mapping)}
            
            elif operation == "update":
                if not filters or "id" not in filters:
                    raise ValueError("Filtro 'id' requerido para update")
                if not data:
                    raise ValueError("Datos requeridos para update")
                set_clause = ", ".join([f"{k} = :{k}" for k in data.keys()])
                query = text(f"UPDATE {table} SET {set_clause} WHERE id = :id RETURNING *")
                params = {**data, "id": filters["id"]}
                result = db.execute(query, params).fetchone()
                db.commit()
                return {"updated": True, "data": dict(result._mapping)}
            
            elif operation == "delete":
                if not filters or "id" not in filters:
                    raise ValueError("Filtro 'id' requerido para delete")
                query = text(f"DELETE FROM {table} WHERE id = :id")
                db.execute(query, {"id": filters["id"]})
                db.commit()
                return {"deleted": True, "id": filters["id"]}
            
            else:
                raise ValueError(f"Operación '{operation}' no válida. Usa: list, get, create, update, delete")
        
        finally:
            db.close()


# ── Tool: RAG Index ───────────────────────────────────────────────────────────

class RAGIndexInput(ToolInput):
    collection: str = Field(..., description="Colección Qdrant: fourgea, triple_r, legal, general")
    documents: List[Dict[str, str]] = Field(..., description="Lista de docs con 'title', 'content', 'metadata'")
    tenant_id: Optional[str] = Field(None, description="ID del tenant para aislamiento")


class RAGIndexTool(BaseTool):
    name = "rag_index"
    description = "Indexa documentos en Qdrant para búsqueda semántica. Soporta multi-tenant."
    input_schema = RAGIndexInput
    category = "rag"
    allowed_roles = ["admin", "contador"]
    
    def execute(self, collection: str, documents: List[Dict[str, str]], tenant_id: Optional[str] = None) -> Dict:
        from qdrant_client import QdrantClient
        from qdrant_client.models import Distance, VectorParams, PointStruct
        import hashlib
        
        client = QdrantClient(host="localhost", port=6333)
        
        # Crear colección si no existe
        collections = client.get_collections().collections
        if not any(c.name == collection for c in collections):
            client.create_collection(
                collection_name=collection,
                vectors_config=VectorParams(size=768, distance=Distance.COSINE)
            )
        
        indexed = 0
        for doc in documents:
            # Generar embedding con Ollama
            import httpx
            resp = httpx.post("http://localhost:11434/api/embeddings", json={
                "model": "nomic-embed-text",
                "prompt": doc.get("content", "")[:4000]
            })
            embedding = resp.json().get("embedding", [])
            
            if not embedding:
                continue
            
            # ID único basado en contenido
            doc_id = hashlib.md5(doc.get("content", "")[:100].encode()).hexdigest()
            
            point = PointStruct(
                id=int(doc_id[:12], 16),
                vector=embedding,
                payload={
                    "title": doc.get("title", ""),
                    "content": doc.get("content", ""),
                    "metadata": doc.get("metadata", {}),
                    "tenant_id": tenant_id
                }
            )
            
            client.upsert(collection_name=collection, points=[point])
            indexed += 1
        
        return {"indexed": indexed, "collection": collection, "tenant_id": tenant_id}


# ── Tool Catalog para registro automático ─────────────────────────────────────

TOOL_CATALOG: Dict[str, Type[BaseTool]] = {
    "n8n_trigger": N8NTriggerTool,
    "sat_query": SATQueryTool,
    "database_query": DBQueryTool,
    "rag_index": RAGIndexTool,
}


def get_tool(tool_name: str) -> Optional[BaseTool]:
    """Obtiene instancia de herramienta por nombre."""
    tool_class = TOOL_CATALOG.get(tool_name)
    if tool_class:
        return tool_class()
    return None


def list_tools() -> List[Dict[str, Any]]:
    """Lista todas las herramientas disponibles con metadata."""
    return [
        {
            "name": tool.name,
            "description": tool.description,
            "category": tool.category,
            "requires_auth": tool.requires_auth,
            "allowed_roles": tool.allowed_roles,
            "rate_limit": tool.rate_limit_per_minute,
            "schema": tool.input_schema.model_json_schema() if hasattr(tool, 'input_schema') else {}
        }
        for tool in [cls() for cls in TOOL_CATALOG.values()]
    ]
