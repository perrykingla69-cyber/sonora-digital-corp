# Agent Swarm Architecture

## Agents
- `infra_agent`: infrastructure and runtime operations.
- `dev_agent`: implementation and development workflows.
- `knowledge_agent`: research and context synthesis.
- `business_agent`: planning, strategy, and reporting.

## Interaction Model
1. Orchestrator receives objective.
2. Task router picks an agent by target/capability.
3. Agent executes requested skill.
4. Results are returned and persisted to memory.
5. Future enhancement: run coordinated parallel swarm execution.
