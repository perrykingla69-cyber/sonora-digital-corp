from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "packages" / "agent-runtime"))

from agent_runtime import RuntimeManager, SkillDefinition, SkillRegistry, TenantPolicy


def test_runtime_manager_creates_session_and_allows_enabled_skill():
    registry = SkillRegistry()
    registry.register(SkillDefinition(name="memory.search", description="Search memory", scopes={"memory:read"}))
    runtime = RuntimeManager(registry)
    session = runtime.start_session("tenant-a")
    decision = runtime.authorize(
        TenantPolicy(tenant_id="tenant-a", allowed_skills={"memory.search"}),
        "memory.search",
    )

    assert session.tenant_id == "tenant-a"
    assert decision.allowed is True


def test_runtime_manager_blocks_skill_when_scope_is_blocked():
    registry = SkillRegistry()
    registry.register(SkillDefinition(name="github.write", description="Write to GitHub", scopes={"github:write"}))
    runtime = RuntimeManager(registry)
    decision = runtime.authorize(
        TenantPolicy(tenant_id="tenant-a", allowed_skills={"github.write"}, blocked_scopes={"github:write"}),
        "github.write",
    )

    assert decision.allowed is False
    assert "Blocked scopes" in decision.reason
