from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import yaml

DEFAULT_SCOPES = {
    "web_search": {"web:read"},
    "analysis": {"analysis:run"},
    "filesystem": {"filesystem:read", "filesystem:write"},
    "github": {"github:write"},
    "shell": {"shell:execute"},
    "memory.search": {"memory:read"},
    "memory.feedback": {"memory:write"},
}


@dataclass(slots=True)
class SkillCatalogEntry:
    name: str
    description: str
    module: str
    entrypoint: str = "run"
    scopes: set[str] = field(default_factory=set)


class SkillCatalog:
    def __init__(self, entries: list[SkillCatalogEntry]) -> None:
        self.entries = entries

    @classmethod
    def from_yaml(cls, config_path: str | Path) -> "SkillCatalog":
        path = Path(config_path)
        payload = yaml.safe_load(path.read_text()) or {}
        entries = [
            SkillCatalogEntry(
                name=item["name"],
                description=item.get("description", ""),
                module=item["module"],
                entrypoint=item.get("entrypoint", "run"),
                scopes=set(item.get("scopes", [])) or set(DEFAULT_SCOPES.get(item["name"], set())),
            )
            for item in payload.get("skills", [])
        ]
        return cls(entries)

    @classmethod
    def default(cls) -> "SkillCatalog":
        return cls(
            entries=[
                SkillCatalogEntry(name=name, description=name.replace(".", " "), module=f"skills.{name}", scopes=scopes)
                for name, scopes in DEFAULT_SCOPES.items()
            ]
        )

    def list(self) -> list[SkillCatalogEntry]:
        return list(self.entries)
