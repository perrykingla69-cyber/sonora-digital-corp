"""
MYSTIC Evals - Contratos y esquemas de evaluación
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Literal


@dataclass
class EvalCase:
    """Caso individual de evaluación."""
    id: str
    name: str
    category: str  # fiscal, legal, contable, aduanas, general
    query: str
    expected_answer: str
    expected_sources: List[str] = field(default_factory=list)
    expected_tool_calls: List[str] = field(default_factory=list)
    max_latency_ms: int = 5000
    min_confidence: float = 0.7
    tenant_id: Optional[str] = None
    tags: List[str] = field(default_factory=list)


@dataclass
class EvalResult:
    """Resultado de evaluación de un caso."""
    case_id: str
    case_name: str
    status: Literal["pass", "fail", "error"]
    
    # Métricas de calidad
    answer_match: float = 0.0  # 0-1 similitud con respuesta esperada
    sources_match: float = 0.0  # 0-1 fuentes correctas
    tool_calls_match: bool = False  # herramientas llamadas correctamente
    
    # Métricas de rendimiento
    latency_ms: int = 0
    confidence: float = 0.0
    
    # Detalles
    actual_answer: str = ""
    actual_sources: List[str] = field(default_factory=list)
    actual_tool_calls: List[str] = field(default_factory=list)
    error: Optional[str] = None
    
    # Timestamp
    evaluated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    @property
    def passed(self) -> bool:
        return self.status == "pass"


@dataclass
class EvalSuite:
    """Suite completa de evaluación."""
    name: str
    description: str
    cases: List[EvalCase] = field(default_factory=list)
    
    # Filtros
    categories: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    
    @classmethod
    def from_yaml(cls, path: str) -> "EvalSuite":
        """Cargar suite desde archivo YAML."""
        import yaml
        
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        
        cases = []
        for c in data.get("cases", []):
            cases.append(EvalCase(
                id=c.get("id", ""),
                name=c.get("name", ""),
                category=c.get("category", "general"),
                query=c["query"],
                expected_answer=c.get("expected_answer", ""),
                expected_sources=c.get("expected_sources", []),
                expected_tool_calls=c.get("expected_tool_calls", []),
                max_latency_ms=c.get("max_latency_ms", 5000),
                min_confidence=c.get("min_confidence", 0.7),
                tenant_id=c.get("tenant_id"),
                tags=c.get("tags", []),
            ))
        
        return cls(
            name=data.get("name", "Untitled Suite"),
            description=data.get("description", ""),
            cases=cases,
            categories=data.get("categories", []),
            tags=data.get("tags", []),
        )
    
    def add_case(self, case: EvalCase):
        """Agregar caso a la suite."""
        self.cases.append(case)
    
    def filter_by_category(self, category: str) -> "EvalSuite":
        """Filtrar casos por categoría."""
        filtered = [c for c in self.cases if c.category == category]
        return EvalSuite(
            name=f"{self.name} - {category}",
            description=self.description,
            cases=filtered,
            categories=[category],
            tags=self.tags,
        )
