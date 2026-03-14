"""Skill registry used by orchestrator and agents."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Optional


@dataclass
class SkillRegistration:
    """Metadata for registered skill modules."""

    name: str
    handler: Callable[..., dict]
    description: str = ""


class SkillRegistry:
    """Stores callable skill handlers by skill name."""

    def __init__(self) -> None:
        self._skills: Dict[str, SkillRegistration] = {}

    def register(self, name: str, handler: Callable[..., dict], description: str = "") -> None:
        self._skills[name] = SkillRegistration(name=name, handler=handler, description=description)

    def get(self, name: str) -> Optional[SkillRegistration]:
        return self._skills.get(name)

    def list_skills(self) -> list[SkillRegistration]:
        return list(self._skills.values())

    def execute(self, name: str, **kwargs) -> dict:
        skill = self.get(name)
        if not skill:
            raise ValueError(f"Skill '{name}' is not registered")
        return skill.handler(**kwargs)
