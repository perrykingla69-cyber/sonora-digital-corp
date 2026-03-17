"""Agent registry — stores and resolves agents by name and capability."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, Optional


@dataclass
class AgentRegistration:
    name: str
    instance: object
    capabilities: list[str] = field(default_factory=list)


class AgentRegistry:
    def __init__(self) -> None:
        self._agents: Dict[str, AgentRegistration] = {}

    def register(self, name: str, agent_instance: object, capabilities: Iterable[str] | None = None) -> None:
        self._agents[name] = AgentRegistration(
            name=name,
            instance=agent_instance,
            capabilities=list(capabilities or []),
        )

    def get(self, name: str) -> Optional[AgentRegistration]:
        return self._agents.get(name)

    def list_agents(self) -> list[AgentRegistration]:
        return list(self._agents.values())

    def find_by_capability(self, capability: str) -> list[AgentRegistration]:
        return [a for a in self._agents.values() if capability in a.capabilities]
