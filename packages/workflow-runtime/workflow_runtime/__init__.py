# workflow_runtime/__init__.py
"""
MYSTIC Workflow Runtime - Ejecutor de workflows N8N y automatizaciones
"""
from .engine import WorkflowEngine, WorkflowExecutionResult
from .loader import WorkflowLoader, WorkflowDefinition

__version__ = "0.1.0"
__all__ = [
    "WorkflowEngine",
    "WorkflowExecutionResult",
    "WorkflowLoader",
    "WorkflowDefinition",
]
