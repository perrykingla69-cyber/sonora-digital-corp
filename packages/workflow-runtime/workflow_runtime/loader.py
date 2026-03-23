"""
MYSTIC Workflow Runtime - Cargador de definiciones de workflows
"""
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class WorkflowNode(BaseModel):
    """Nodo individual de un workflow N8N."""
    id: str
    name: str
    type: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    position: List[int] = Field(default_factory=lambda: [0, 0])


class WorkflowTrigger(BaseModel):
    """Configuración de trigger."""
    type: str  # cron, webhook, event
    cron_expression: Optional[str] = None
    webhook_path: Optional[str] = None
    event_name: Optional[str] = None


class WorkflowDefinition(BaseModel):
    """Definición completa de un workflow."""
    id: str
    name: str
    nodes: List[WorkflowNode] = Field(default_factory=list)
    connections: Dict[str, Any] = Field(default_factory=dict)
    trigger: Optional[WorkflowTrigger] = None
    active: bool = True
    tags: List[str] = Field(default_factory=list)
    tenant_filter: List[str] = Field(default_factory=list)

    @classmethod
    def from_file(cls, path: Path) -> "WorkflowDefinition":
        """Cargar workflow desde archivo JSON de N8N."""
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        trigger = None
        # Detectar trigger del primer nodo (usualmente Schedule Trigger o Webhook)
        if data.get("nodes"):
            first_node = data["nodes"][0]
            if first_node.get("type") == "n8n-nodes-base.scheduleTrigger":
                rule = first_node.get("parameters", {}).get("rule", {})
                interval = rule.get("interval", [{}])[0] if rule.get("interval") else {}
                trigger = WorkflowTrigger(
                    type="cron",
                    cron_expression=interval.get("field", "")
                )
            elif first_node.get("type") == "n8n-nodes-base.webhook":
                trigger = WorkflowTrigger(
                    type="webhook",
                    webhook_path=first_node.get("parameters", {}).get("path", "")
                )
        
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            nodes=[WorkflowNode(**n) for n in data.get("nodes", [])],
            connections=data.get("connections", {}),
            trigger=trigger,
            active=data.get("active", True),
            tags=data.get("tags", []),
        )


class WorkflowLoader:
    """Cargador de workflows desde directorio."""
    
    def __init__(self, workflows_dir: Path):
        self.workflows_dir = workflows_dir
        self._cache: Dict[str, WorkflowDefinition] = {}
    
    def load(self, workflow_id: str) -> Optional[WorkflowDefinition]:
        """Cargar un workflow específico por ID."""
        if workflow_id in self._cache:
            return self._cache[workflow_id]
        
        # Buscar archivo que contenga el ID
        for file in self.workflows_dir.glob("*.json"):
            try:
                wf = WorkflowDefinition.from_file(file)
                if wf.id == workflow_id:
                    self._cache[workflow_id] = wf
                    return wf
            except Exception:
                continue
        
        return None
    
    def load_by_name(self, name: str) -> Optional[WorkflowDefinition]:
        """Cargar workflow por nombre."""
        for file in self.workflows_dir.glob("*.json"):
            try:
                wf = WorkflowDefinition.from_file(file)
                if wf.name.lower() == name.lower():
                    self._cache[wf.id] = wf
                    return wf
            except Exception:
                continue
        
        return None
    
    def list_all(self) -> List[WorkflowDefinition]:
        """Listar todos los workflows disponibles."""
        workflows = []
        for file in self.workflows_dir.glob("*.json"):
            try:
                wf = WorkflowDefinition.from_file(file)
                workflows.append(wf)
            except Exception:
                continue
        
        return workflows
    
    def reload(self):
        """Recargar todos los workflows (limpia cache)."""
        self._cache.clear()
