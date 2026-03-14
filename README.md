# Sonora Digital Corp - AI Operating System Bootstrap

This repository now contains the initial architecture for an **AI Operating System** powering a multi-agent swarm platform.

## Structure

- `orchestrator/` - Core orchestration layer (agent registry, skill registry, routing, execution)
- `agents/` - Initial domain agents (`infra_agent`, `dev_agent`, `knowledge_agent`, `business_agent`)
- `skills/` - Shared skill modules (`filesystem`, `shell`, `github`, `web_search`, `analysis`)
- `memory/` - Task history, knowledge store, vector memory scaffold
- `configs/` - Declarative YAML configs for agents and skills
- `prompts/` - Swarm philosophy and orchestrator coordination logic
- `docs/` - System and architecture documentation
- `scripts/` - Startup/initialization scripts
- `tests/` - Placeholder for validation and regression suites

## Orchestrator Capabilities

The orchestrator currently supports:

1. **Agent registration**
2. **Skill registration**
3. **Task routing** (explicit target or capability-based)
4. **Sequential swarm execution scaffold** for future parallel coordination

## Getting Started

```bash
./scripts/start_system.sh
```

This startup script initializes memory components, validates skill and agent configs, and starts the orchestrator runtime scaffold.
