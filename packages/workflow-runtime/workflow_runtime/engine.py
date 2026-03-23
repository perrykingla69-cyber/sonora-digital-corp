"""
MYSTIC Workflow Runtime - Motor de ejecución de workflows
"""
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
import httpx

from .loader import WorkflowDefinition, WorkflowLoader

logger = logging.getLogger(__name__)


@dataclass
class WorkflowExecutionResult:
    """Resultado de ejecución de workflow."""
    workflow_id: str
    workflow_name: str
    status: str  # success, error, timeout
    execution_time_ms: int = 0
    result: Any = None
    error: Optional[str] = None
    triggered_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class WorkflowEngine:
    """
    Motor de ejecución de workflows N8N.
    
    Permite:
    - Ejecutar workflows vía API de N8N
    - Ejecutar triggers cron manualmente
    - Monitorear estado de ejecuciones
    """
    
    def __init__(
        self,
        n8n_base_url: str = "http://localhost:5678",
        n8n_api_key: Optional[str] = None,
        timeout_seconds: int = 300,
    ):
        self.n8n_base_url = n8n_base_url.rstrip("/")
        self.n8n_api_key = n8n_api_key
        self.timeout_seconds = timeout_seconds
        self._loader: Optional[WorkflowLoader] = None
    
    def set_loader(self, loader: WorkflowLoader):
        """Configurar cargador de workflows."""
        self._loader = loader
    
    def execute(
        self,
        workflow_id: str,
        data: Optional[Dict[str, Any]] = None,
        wait: bool = False,
    ) -> WorkflowExecutionResult:
        """
        Ejecutar un workflow específico.
        
        Args:
            workflow_id: ID del workflow en N8N
            data: Datos para pasar al webhook
            wait: Si True, espera a que termine la ejecución
        
        Returns:
            WorkflowExecutionResult con el resultado
        """
        start_time = time.time()
        
        headers = {}
        if self.n8n_api_key:
            headers["X-N8N-API-KEY"] = self.n8n_api_key
        
        # URL para ejecutar workflow
        exec_url = f"{self.n8n_base_url}/webhook/{workflow_id}"
        
        try:
            with httpx.Client(timeout=self.timeout_seconds) as client:
                response = client.post(
                    exec_url,
                    json=data or {},
                    headers=headers,
                )
                
                execution_time = int((time.time() - start_time) * 1000)
                
                if response.status_code in (200, 202):
                    return WorkflowExecutionResult(
                        workflow_id=workflow_id,
                        workflow_name=workflow_id,
                        status="success",
                        execution_time_ms=execution_time,
                        result=response.json() if response.content else None,
                    )
                else:
                    return WorkflowExecutionResult(
                        workflow_id=workflow_id,
                        workflow_name=workflow_id,
                        status="error",
                        execution_time_ms=execution_time,
                        error=f"HTTP {response.status_code}: {response.text[:200]}",
                    )
        
        except httpx.TimeoutException:
            return WorkflowExecutionResult(
                workflow_id=workflow_id,
                workflow_name=workflow_id,
                status="timeout",
                execution_time_ms=int((time.time() - start_time) * 1000),
                error=f"Timeout after {self.timeout_seconds}s",
            )
        except Exception as e:
            return WorkflowExecutionResult(
                workflow_id=workflow_id,
                workflow_name=workflow_id,
                status="error",
                execution_time_ms=int((time.time() - start_time) * 1000),
                error=str(e),
            )
    
    def execute_by_name(
        self,
        name: str,
        data: Optional[Dict[str, Any]] = None,
        wait: bool = False,
    ) -> WorkflowExecutionResult:
        """Ejecutar workflow por nombre en lugar de ID."""
        if not self._loader:
            return WorkflowExecutionResult(
                workflow_id=name,
                workflow_name=name,
                status="error",
                error="WorkflowLoader no configurado",
            )
        
        wf = self._loader.load_by_name(name)
        if not wf:
            return WorkflowExecutionResult(
                workflow_id=name,
                workflow_name=name,
                status="error",
                error=f"Workflow '{name}' no encontrado",
            )
        
        return self.execute(wf.id, data, wait)
    
    def list_workflows(self) -> List[Dict[str, Any]]:
        """Listar workflows disponibles desde N8N API."""
        headers = {}
        if self.n8n_api_key:
            headers["X-N8N-API-KEY"] = self.n8n_api_key
        
        try:
            with httpx.Client(timeout=30) as client:
                response = client.get(
                    f"{self.n8n_base_url}/api/v1/workflows",
                    headers=headers,
                )
                response.raise_for_status()
                return response.json().get("data", [])
        except Exception as e:
            logger.error(f"Error listando workflows: {e}")
            return []
    
    def get_workflow_info(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Obtener información detallada de un workflow."""
        headers = {}
        if self.n8n_api_key:
            headers["X-N8N-API-KEY"] = self.n8n_api_key
        
        try:
            with httpx.Client(timeout=30) as client:
                response = client.get(
                    f"{self.n8n_base_url}/api/v1/workflows/{workflow_id}",
                    headers=headers,
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error obteniendo workflow {workflow_id}: {e}")
            return None
    
    def trigger_cron_workflows(self) -> List[WorkflowExecutionResult]:
        """
        Ejecutar manualmente todos los workflows con trigger cron.
        Útil para testing o recuperación después de downtime.
        """
        if not self._loader:
            logger.warning("WorkflowLoader no configurado")
            return []
        
        results = []
        for wf in self._loader.list_all():
            if wf.trigger and wf.trigger.type == "cron":
                logger.info(f"Ejecutando cron workflow: {wf.name}")
                result = self.execute(wf.id, wait=False)
                results.append(result)
        
        return results
