from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class SkillDefinition:
    name: str
    description: str
    scopes: set[str] = field(default_factory=set)


class SkillRegistry:
    def __init__(self) -> None:
        self._skills: dict[str, SkillDefinition] = {}

    def register(self, definition: SkillDefinition) -> None:
        self._skills[definition.name] = definition

    def get(self, name: str) -> SkillDefinition | None:
        return self._skills.get(name)

    def list(self) -> list[SkillDefinition]:
        return list(self._skills.values())
