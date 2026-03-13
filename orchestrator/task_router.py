"""Task router for selecting the most suitable agent for a task."""

from __future__ import annotations

from typing import Any

from orchestrator.agent_registry import AgentRegistry


class TaskRouter:
    """Routes tasks to agents by explicit name or capability matching."""

    def __init__(self, agent_registry: AgentRegistry) -> None:
        self.agent_registry = agent_registry

    def route(self, task: dict[str, Any]):
        target_agent = task.get("agent")
        if target_agent:
            registration = self.agent_registry.get(target_agent)
            if not registration:
                raise ValueError(f"Requested agent '{target_agent}' was not found")
            return registration.instance

        capability = task.get("capability")
        if capability:
            matches = self.agent_registry.find_by_capability(capability)
            if not matches:
                raise ValueError(f"No agents registered for capability '{capability}'")
            return matches[0].instance

        agents = self.agent_registry.list_agents()
        if not agents:
            raise RuntimeError("No agents are registered")
        return agents[0].instance
