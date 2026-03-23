# mystic_types/__init__.py
"""
MYSTIC Shared Types - Tipos compartidos para toda la plataforma
"""
from .contracts import (
    TenantConfig,
    UserContext,
    BrainRequest,
    BrainResponse,
    ToolDefinition,
    ToolResult,
    SkillDefinition,
    WorkflowTrigger,
    RAGDocument,
    EmbeddingConfig,
)

__version__ = "0.1.0"
__all__ = [
    "TenantConfig",
    "UserContext", 
    "BrainRequest",
    "BrainResponse",
    "ToolDefinition",
    "ToolResult",
    "SkillDefinition",
    "WorkflowTrigger",
    "RAGDocument",
    "EmbeddingConfig",
]
