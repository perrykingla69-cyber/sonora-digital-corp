"""Core orchestrator implementation for the AI Operating System."""

from __future__ import annotations

from typing import Any

from orchestrator.agent_registry import AgentRegistry
from orchestrator.skill_registry import SkillRegistry
from orchestrator.task_router import TaskRouter


class Orchestrator:
    """Coordinates agents, skills, and task execution for the swarm."""

    def __init__(self) -> None:
        self.agent_registry = AgentRegistry()
        self.skill_registry = SkillRegistry()
        self.task_router = TaskRouter(self.agent_registry)

    def register_agent(self, name: str, agent_instance: object, capabilities: list[str] | None = None) -> None:
        self.agent_registry.register(name, agent_instance, capabilities)

    def register_skill(self, name: str, skill_handler, description: str = "") -> None:
        self.skill_registry.register(name, skill_handler, description)

    def route_task(self, task: dict[str, Any]):
        return self.task_router.route(task)

    def execute_task(self, task: dict[str, Any]) -> dict:
        agent = self.route_task(task)
        payload = task.get("payload", {})
        return agent(payload)

    def execute_swarm(self, tasks: list[dict[str, Any]]) -> list[dict]:
        """Initial swarm execution loop (sequential); can be parallelized in future."""
        results = []
        for task in tasks:
            results.append(self.execute_task(task))
        return results
