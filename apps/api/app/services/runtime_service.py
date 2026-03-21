from __future__ import annotations

from functools import lru_cache
from pathlib import Path
import sys

RUNTIME_PACKAGE_ROOT = Path(__file__).resolve().parents[4] / "packages" / "agent-runtime"
if str(RUNTIME_PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(RUNTIME_PACKAGE_ROOT))

SKILLS_PACKAGE_ROOT = Path(__file__).resolve().parents[4] / "packages" / "skills"
if str(SKILLS_PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(SKILLS_PACKAGE_ROOT))

from agent_runtime import RuntimeManager, SkillDefinition, SkillRegistry, TenantPolicy  # type: ignore
from skills_v2 import SkillCatalog  # type: ignore


class RuntimeService:
    def __init__(self, catalog_path: str | Path | None = None) -> None:
        self.registry = SkillRegistry()
        catalog = self._load_catalog(catalog_path)
        for entry in catalog.list():
            self.registry.register(
                SkillDefinition(name=entry.name, description=entry.description, scopes=entry.scopes)
            )
        self.manager = RuntimeManager(self.registry)

    def list_skills(self) -> list[SkillDefinition]:
        return self.registry.list()

    def start_session(self, tenant_id: str):
        return self.manager.start_session(tenant_id)

    def authorize(self, tenant_id: str, skill_name: str, allowed_skills: set[str], blocked_scopes: set[str]):
        policy = TenantPolicy(tenant_id=tenant_id, allowed_skills=allowed_skills, blocked_scopes=blocked_scopes)
        return self.manager.authorize(policy, skill_name)

    @staticmethod
    def _load_catalog(catalog_path: str | Path | None) -> SkillCatalog:
        path = Path(catalog_path) if catalog_path else Path(__file__).resolve().parents[4] / "backend" / "app" / "ai" / "configs" / "skills.yaml"
        if path.exists():
            return SkillCatalog.from_yaml(path)
        return SkillCatalog.default()


@lru_cache(maxsize=1)
def get_runtime_service() -> RuntimeService:
    return RuntimeService()
