from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid

from .policies import PolicyDecision, TenantPolicy
from .registry import SkillRegistry


@dataclass(slots=True)
class AgentRuntimeSession:
    tenant_id: str
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class RuntimeManager:
    def __init__(self, registry: SkillRegistry) -> None:
        self.registry = registry

    def start_session(self, tenant_id: str) -> AgentRuntimeSession:
        return AgentRuntimeSession(tenant_id=tenant_id)

    def authorize(self, policy: TenantPolicy, skill_name: str) -> PolicyDecision:
        skill = self.registry.get(skill_name)
        if skill is None:
            return PolicyDecision(False, f"Skill '{skill_name}' is not registered")
        return policy.evaluate(skill_name, skill.scopes)
