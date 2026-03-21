from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class PolicyDecision:
    allowed: bool
    reason: str


@dataclass(slots=True)
class TenantPolicy:
    tenant_id: str
    allowed_skills: set[str] = field(default_factory=set)
    blocked_scopes: set[str] = field(default_factory=set)

    def evaluate(self, skill_name: str, scopes: set[str]) -> PolicyDecision:
        if self.allowed_skills and skill_name not in self.allowed_skills:
            return PolicyDecision(False, f"Skill '{skill_name}' is not enabled for tenant '{self.tenant_id}'")
        if self.blocked_scopes.intersection(scopes):
            return PolicyDecision(False, f"Blocked scopes for tenant '{self.tenant_id}': {sorted(self.blocked_scopes.intersection(scopes))}")
        return PolicyDecision(True, "allowed")
