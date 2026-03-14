# System Overview

This repository bootstraps an AI Operating System for a multi-agent swarm platform.

## Core Layers
- **Orchestrator**: Registers agents/skills and routes tasks.
- **Agents**: Domain-focused workers that execute skills.
- **Skills**: Reusable callable modules with a standard interface.
- **Memory**: Task history, knowledge store, and vector memory scaffold.
- **Configs/Prompts**: Declarative setup and reasoning policy.
