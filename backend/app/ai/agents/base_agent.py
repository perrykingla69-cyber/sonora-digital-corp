"""Base agent — shared class imported by all domain agents."""

from __future__ import annotations

import importlib
from pathlib import Path
from typing import Any, Callable

import yaml


class BaseAgent:
    """
    Base agent that auto-loads skills from its config.yaml and
    exposes a standard __call__ interface for the orchestrator.
    """

    def __init__(
        self,
        name: str,
        role: str,
        skills: dict[str, Callable[..., dict]] | None = None,
    ) -> None:
        self.name = name
        self.role = role
        self._skills: dict[str, Callable[..., dict]] = skills or {}

    # ------------------------------------------------------------------
    # Factory: build agent from config.yaml
    # ------------------------------------------------------------------

    @classmethod
    def from_config(cls, config_path: str | Path) -> "BaseAgent":
        """Instantiate an agent and auto-wire its skills from config.yaml."""
        path = Path(config_path)
        data = yaml.safe_load(path.read_text())

        agent = cls(name=data["name"], role=data["role"])

        for skill_name in data.get("skills", []):
            try:
                module = importlib.import_module(f"skills.{skill_name}")
                agent.register_skill(skill_name, module.run)
            except (ImportError, AttributeError) as exc:
                # Log but don't crash — missing skill degrades gracefully
                import warnings
                warnings.warn(f"[{data['name']}] Could not load skill '{skill_name}': {exc}")

        return agent

    # ------------------------------------------------------------------
    # Skill management
    # ------------------------------------------------------------------

    def register_skill(self, skill_name: str, handler: Callable[..., dict]) -> None:
        """Register a skill handler under the given name."""
        self._skills[skill_name] = handler

    def has_skill(self, skill_name: str) -> bool:
        return skill_name in self._skills

    def list_skills(self) -> list[str]:
        return list(self._skills.keys())

    def run_skill(self, skill_name: str, **kwargs: Any) -> dict:
        """Execute a named skill with keyword arguments."""
        if skill_name not in self._skills:
            raise ValueError(
                f"Agent '{self.name}' does not have skill '{skill_name}'. "
                f"Available: {self.list_skills()}"
            )
        return self._skills[skill_name](**kwargs)

    # ------------------------------------------------------------------
    # Orchestrator interface
    # ------------------------------------------------------------------

    def __call__(self, payload: dict) -> dict:
        """
        Payload schema:
            {
                "skill": "filesystem",   # skill to invoke
                "args":  {"action": "read", "path": "/tmp/foo.txt"}
            }
        If no skill is specified, returns agent info.
        """
        skill = payload.get("skill")
        args = payload.get("args", {})

        if skill:
            result = self.run_skill(skill, **args)
            return {
                "agent": self.name,
                "role": self.role,
                "skill": skill,
                "result": result,
            }

        return {
            "agent": self.name,
            "role": self.role,
            "skills": self.list_skills(),
            "message": "No skill requested. Send payload with 'skill' key.",
        }

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name!r} skills={self.list_skills()}>"
