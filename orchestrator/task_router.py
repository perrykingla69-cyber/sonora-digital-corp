"""Task router — selects the most suitable agent for a given task."""

from __future__ import annotations

from typing import Any

from orchestrator.agent_registry import AgentRegistry


class TaskRouter:
    def __init__(self, agent_registry: AgentRegistry) -> None:
        self.agent_registry = agent_registry

    def route(self, task: dict[str, Any]):
        """
        Routing priority:
          1. Explicit agent name  (task["agent"])
          2. Capability match     (task["capability"])
          3. First registered agent (fallback)
        """
        target = task.get("agent")
        if target:
            reg = self.agent_registry.get(target)
            if not reg:
                raise ValueError(f"Agent '{target}' not found")
            return reg.instance

        capability = task.get("capability")
        if capability:
            matches = self.agent_registry.find_by_capability(capability)
            if not matches:
                raise ValueError(f"No agent registered for capability '{capability}'")
            return matches[0].instance

        agents = self.agent_registry.list_agents()
        if not agents:
            raise RuntimeError("No agents registered")
        return agents[0].instance
