"""Agent implementation module."""

from __future__ import annotations

from typing import Callable


class BaseAgent:
    """Base agent that can invoke multiple registered skills."""

    def __init__(self, name: str, role: str, skills: dict[str, Callable[..., dict]]) -> None:
        self.name = name
        self.role = role
        self.skills = skills

    def add_skill(self, skill_name: str, handler: Callable[..., dict]) -> None:
        self.skills[skill_name] = handler

    def run_skill(self, skill_name: str, **kwargs) -> dict:
        if skill_name not in self.skills:
            raise ValueError(f"Skill '{skill_name}' is not available for agent '{self.name}'")
        return self.skills[skill_name](**kwargs)

    def __call__(self, payload: dict) -> dict:
        skill = payload.get("skill")
        args = payload.get("args", {})
        if skill:
            result = self.run_skill(skill, **args)
            return {"agent": self.name, "role": self.role, "skill": skill, "result": result}
        return {
            "agent": self.name,
            "role": self.role,
            "message": "No skill requested; agent acknowledged payload",
            "payload": payload,
        }
