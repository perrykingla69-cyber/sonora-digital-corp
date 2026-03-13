"""Core orchestrator — coordinates agents, skills, and task execution."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from agents.base_agent import BaseAgent
from orchestrator.agent_registry import AgentRegistry
from orchestrator.skill_registry import SkillRegistry
from orchestrator.task_router import TaskRouter
from memory.task_history import TaskHistory
from memory.knowledge_store import KnowledgeStore


class Orchestrator:
    """
    Central coordinator for the AI Operating System.
    Loads agents and skills from config, routes tasks, persists results.
    """

    def __init__(self) -> None:
        self.agent_registry = AgentRegistry()
        self.skill_registry = SkillRegistry()
        self.task_router = TaskRouter(self.agent_registry)
        self.task_history = TaskHistory()
        self.knowledge_store = KnowledgeStore()
        self._task_counter = 0

    # ------------------------------------------------------------------
    # Bootstrap from config files
    # ------------------------------------------------------------------

    @classmethod
    def from_config(cls, agents_config: str, skills_config: str) -> "Orchestrator":
        """Build a fully wired Orchestrator from YAML config files."""
        orch = cls()
        orch._load_skills(skills_config)
        orch._load_agents(agents_config)
        return orch

    def _load_skills(self, skills_config: str) -> None:
        import importlib
        data = yaml.safe_load(Path(skills_config).read_text())
        for skill_def in data.get("skills", []):
            name = skill_def["name"]
            module_path = skill_def["module"]
            entrypoint = skill_def.get("entrypoint", "run")
            try:
                module = importlib.import_module(module_path)
                handler = getattr(module, entrypoint)
                self.skill_registry.register(name, handler, skill_def.get("description", ""))
            except Exception as exc:
                import warnings
                warnings.warn(f"Could not load skill '{name}': {exc}")

    def _load_agents(self, agents_config: str) -> None:
        agents_dir = Path(agents_config).parent.parent / "agents"
        data = yaml.safe_load(Path(agents_config).read_text())
        for agent_def in data.get("agents", []):
            name = agent_def["name"]
            config_path = agents_dir / name / "config.yaml"
            try:
                agent = BaseAgent.from_config(config_path)
                self.agent_registry.register(name, agent, agent_def.get("capabilities", []))
            except Exception as exc:
                import warnings
                warnings.warn(f"Could not load agent '{name}': {exc}")

    # ------------------------------------------------------------------
    # Registration API
    # ------------------------------------------------------------------

    def register_agent(self, name: str, agent: BaseAgent, capabilities: list[str] | None = None) -> None:
        self.agent_registry.register(name, agent, capabilities)

    def register_skill(self, name: str, handler, description: str = "") -> None:
        self.skill_registry.register(name, handler, description)

    # ------------------------------------------------------------------
    # Task execution
    # ------------------------------------------------------------------

    def execute_task(self, task: dict[str, Any]) -> dict:
        """Route a task to the correct agent and persist the result."""
        self._task_counter += 1
        task_id = task.get("id") or f"task-{self._task_counter}"

        agent = self.task_router.route(task)
        payload = task.get("payload", {})
        result = agent(payload)

        self.task_history.store(task_id, task, result)
        return result

    def execute_swarm(self, tasks: list[dict[str, Any]]) -> list[dict]:
        """Execute multiple tasks sequentially. Future: parallelize."""
        return [self.execute_task(t) for t in tasks]

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    def status(self) -> dict:
        return {
            "agents": [a.name for a in self.agent_registry.list_agents()],
            "skills": [s.name for s in self.skill_registry.list_skills()],
            "tasks_executed": self._task_counter,
        }
