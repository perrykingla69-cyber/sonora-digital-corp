from __future__ import annotations

from functools import lru_cache
from pathlib import Path
import sys

RUNTIME_PACKAGE_ROOT = Path(__file__).resolve().parents[4] / "packages" / "agent-runtime"
if str(RUNTIME_PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(RUNTIME_PACKAGE_ROOT))

from agent_runtime import RuntimeManager, SkillDefinition, SkillRegistry, TenantPolicy  # type: ignore


class RuntimeService:
    def __init__(self) -> None:
        self.registry = SkillRegistry()
        self.registry.register(SkillDefinition(name="memory.search", description="Search tenant memory", scopes={"memory:read"}))
        self.registry.register(SkillDefinition(name="memory.feedback", description="Write memory feedback", scopes={"memory:write"}))
        self.registry.register(SkillDefinition(name="github.write", description="Write code/github state", scopes={"github:write"}))
        self.manager = RuntimeManager(self.registry)

    def list_skills(self) -> list[SkillDefinition]:
        return self.registry.list()

    def start_session(self, tenant_id: str):
        return self.manager.start_session(tenant_id)

    def authorize(self, tenant_id: str, skill_name: str, allowed_skills: set[str], blocked_scopes: set[str]):
        policy = TenantPolicy(tenant_id=tenant_id, allowed_skills=allowed_skills, blocked_scopes=blocked_scopes)
        return self.manager.authorize(policy, skill_name)


@lru_cache(maxsize=1)
def get_runtime_service() -> RuntimeService:
    return RuntimeService()
