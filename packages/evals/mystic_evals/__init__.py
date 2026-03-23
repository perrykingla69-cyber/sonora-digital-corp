# mystic_evals/__init__.py
"""
MYSTIC Evals - Framework de evaluación de calidad del Brain IA
"""
from .contracts import EvalCase, EvalResult, EvalSuite
from .runner import EvalRunner
from .scorer import EvalScorer

__version__ = "0.1.0"
__all__ = [
    "EvalCase",
    "EvalResult", 
    "EvalSuite",
    "EvalRunner",
    "EvalScorer",
]
