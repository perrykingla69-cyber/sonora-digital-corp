"""Agent registry for the AI Operating System orchestrator."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, Optional


@dataclass
class AgentRegistration:
    """Metadata representing an agent registered with the orchestrator."""

    name: str
    instance: object
    capabilities: list[str] = field(default_factory=list)


class AgentRegistry:
    """Stores and resolves agents by name and capability."""

    def __init__(self) -> None:
        self._agents: Dict[str, AgentRegistration] = {}

    def register(self, name: str, agent_instance: object, capabilities: Optional[Iterable[str]] = None) -> None:
        capabilities_list = list(capabilities or [])
        self._agents[name] = AgentRegistration(
            name=name,
            instance=agent_instance,
            capabilities=capabilities_list,
        )

    def get(self, name: str) -> Optional[AgentRegistration]:
        return self._agents.get(name)

    def list_agents(self) -> list[AgentRegistration]:
        return list(self._agents.values())

    def find_by_capability(self, capability: str) -> list[AgentRegistration]:
        return [agent for agent in self._agents.values() if capability in agent.capabilities]
