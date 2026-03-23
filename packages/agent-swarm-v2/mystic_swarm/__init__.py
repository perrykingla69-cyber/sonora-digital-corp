"""MYSTIC Swarm V2 — Ecosistema completo de agentes orquestados"""
from .coordinator import MysticSwarmCoordinator, SwarmTask, SwarmResult
from .agents import (
    MYSTICMerchAgent,
    MYSTICVisionAgent,
    MYSTICAcademyAgent,
    MYSTICChainAgent,
    MYSTICHypeAgent,
)

__version__ = "2.0.0"
__all__ = [
    "MysticSwarmCoordinator",
    "SwarmTask",
    "SwarmResult",
    "MYSTICMerchAgent",
    "MYSTICVisionAgent",
    "MYSTICAcademyAgent",
    "MYSTICChainAgent",
    "MYSTICHypeAgent",
]
