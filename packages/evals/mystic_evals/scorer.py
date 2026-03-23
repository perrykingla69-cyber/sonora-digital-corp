"""
MYSTIC Evals - Scorer de calidad de respuestas
"""
import re
from typing import List, Optional
from difflib import SequenceMatcher

from .contracts import EvalCase, EvalResult


class EvalScorer:
    """
    Scorer para evaluar calidad de respuestas del Brain IA.
    
    Criterios:
    - Similitud semántica con respuesta esperada
    - Match de fuentes citadas
    - Match de herramientas llamadas
    - Latencia dentro de límites
    - Confianza mínima alcanzada
    """
    
    def __init__(
        self,
        answer_weight: float = 0.4,
        sources_weight: float = 0.2,
        tools_weight: float = 0.2,
        performance_weight: float = 0.2,
    ):
        self.answer_weight = answer_weight
        self.sources_weight = sources_weight
        self.tools_weight = tools_weight
        self.performance_weight = performance_weight
    
    def score(
        self,
        case: EvalCase,
        actual_answer: str,
        actual_sources: List[str],
        actual_tool_calls: List[str],
        latency_ms: int,
        confidence: float,
    ) -> EvalResult:
        """
        Calcular score para un caso de evaluación.
        
        Returns:
            EvalResult con métricas detalladas
        """
        # 1. Score de respuesta (similitud textual)
        answer_match = self._compute_answer_similarity(
            case.expected_answer, actual_answer
        )
        
        # 2. Score de fuentes
        sources_match = self._compute_sources_match(
            case.expected_sources, actual_sources
        )
        
        # 3. Match de herramientas
        tools_match = self._compute_tools_match(
            case.expected_tool_calls, actual_tool_calls
        )
        
        # 4. Score de rendimiento
        perf_score = self._compute_performance_score(
            latency_ms, confidence, case.max_latency_ms, case.min_confidence
        )
        
        # Score ponderado total
        total_score = (
            answer_match * self.answer_weight +
            sources_match * self.sources_weight +
            (1.0 if tools_match else 0.0) * self.tools_weight +
            perf_score * self.performance_weight
        )
        
        # Determinar status
        status = self._determine_status(
            total_score, answer_match, sources_match, tools_match,
            latency_ms, confidence, case
        )
        
        return EvalResult(
            case_id=case.id,
            case_name=case.name,
            status=status,
            answer_match=answer_match,
            sources_match=sources_match,
            tool_calls_match=tools_match,
            latency_ms=latency_ms,
            confidence=confidence,
            actual_answer=actual_answer,
            actual_sources=actual_sources,
            actual_tool_calls=actual_tool_calls,
        )
    
    def _compute_answer_similarity(self, expected: str, actual: str) -> float:
        """Calcular similitud entre respuesta esperada y actual."""
        if not expected or not actual:
            return 0.0
        
        # Normalizar texto
        def normalize(text: str) -> str:
            text = text.lower()
            text = re.sub(r"[^\w\s]", " ", text)
            text = re.sub(r"\s+", " ", text).strip()
            return text
        
        expected_norm = normalize(expected)
        actual_norm = normalize(actual)
        
        # Sequence matcher para similitud
        return SequenceMatcher(None, expected_norm, actual_norm).ratio()
    
    def _compute_sources_match(self, expected: List[str], actual: List[str]) -> float:
        """Calcular match de fuentes citadas."""
        if not expected:
            return 1.0  # No se esperan fuentes, cualquier cosa es válida
        
        if not actual:
            return 0.0
        
        # Porcentaje de fuentes esperadas que están en las actuales
        expected_set = set(s.lower().strip() for s in expected)
        actual_set = set(s.lower().strip() for s in actual)
        
        matches = len(expected_set & actual_set)
        return matches / len(expected_set)
    
    def _compute_tools_match(self, expected: List[str], actual: List[str]) -> bool:
        """Verificar si las herramientas llamadas coinciden."""
        if not expected:
            return True  # No se esperan herramientas específicas
        
        if not actual:
            return False
        
        expected_set = set(t.lower().strip() for t in expected)
        actual_set = set(t.lower().strip() for t in actual)
        
        # Todas las herramientas esperadas deben estar presentes
        return expected_set <= actual_set
    
    def _compute_performance_score(
        self,
        latency_ms: int,
        confidence: float,
        max_latency: int,
        min_confidence: float,
    ) -> float:
        """Calcular score de rendimiento."""
        # Score de latencia (1.0 si está dentro del límite, 0 si excede 2x)
        if latency_ms <= max_latency:
            latency_score = 1.0
        elif latency_ms >= max_latency * 2:
            latency_score = 0.0
        else:
            latency_score = 1.0 - (latency_ms - max_latency) / max_latency
        
        # Score de confianza
        if confidence >= min_confidence:
            confidence_score = 1.0
        else:
            confidence_score = max(0.0, confidence / min_confidence)
        
        return (latency_score + confidence_score) / 2
    
    def _determine_status(
        self,
        total_score: float,
        answer_match: float,
        sources_match: float,
        tools_match: bool,
        latency_ms: int,
        confidence: float,
        case: EvalCase,
    ) -> str:
        """Determinar si el caso pasó o falló."""
        # Falla automática si:
        - Respuesta muy diferente (< 0.3)
        - Herramientas requeridas no llamadas
        - Latencia excede 2x el límite
        - Confianza muy baja (< 0.3)
        
        if answer_match < 0.3:
            return "fail"
        
        if not tools_match:
            return "fail"
        
        if latency_ms > case.max_latency_ms * 2:
            return "fail"
        
        if confidence < 0.3:
            return "fail"
        
        # Pasa si score total >= 0.7
        if total_score >= 0.7:
            return "pass"
        
        return "fail"
