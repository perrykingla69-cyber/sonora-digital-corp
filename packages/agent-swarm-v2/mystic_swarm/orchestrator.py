from typing import Dict, List, Optional, Callable, Any, TypedDict
from dataclasses import dataclass, field
from enum import Enum, auto
import asyncio
import json
import hashlib
from datetime import datetime
from collections import defaultdict
import httpx
from qdrant_client import QdrantClient
from pydantic import BaseModel, Field

class AgentRole(Enum):
    STRATEGIST = auto()
    EXECUTOR = auto()
    VALIDATOR = auto()
    MEMORY_KEEPER = auto()
    FALLBACK = auto()

class TaskPriority(Enum):
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4

@dataclass
class AgentCapability:
    name: str
    description: str
    required_tools: List[str]
    max_execution_time: int = 30
    fallback_agents: List[str] = field(default_factory=list)

@dataclass
class SwarmTask:
    id: str
    objective: str
    context: Dict[str, Any]
    priority: TaskPriority
    required_capabilities: List[str]
    max_retries: int = 3
    created_at: datetime = field(default_factory=datetime.now)
    assigned_agent: Optional[str] = None
    execution_trace: List[Dict] = field(default_factory=list)

class AgentSwarmOrchestrator:
    def __init__(self, qdrant_url: str = "http://localhost:6333"):
        self.qdrant = QdrantClient(url=qdrant_url)
        self.agents: Dict[str, AgentCapability] = {}
        self.active_tasks: Dict[str, SwarmTask] = {}
        self.memory_collection = "swarm_memory_v2"
        self._ensure_memory_store()

    def _ensure_memory_store(self):
        try:
            self.qdrant.create_collection(
                collection_name=self.memory_collection,
                vectors_config={"size": 768, "distance": "Cosine"}
            )
        except Exception:
            pass

    def register_agent(self, agent_id: str, capability: AgentCapability):
        self.agents[agent_id] = capability

    async def execute_complex_task(self, task: SwarmTask) -> Dict[str, Any]:
        subtasks = await self._decompose_task(task)
        assignments = self._route_subtasks(subtasks)
        results = await self._execute_parallel(assignments, task)
        final_result = await self._synthesize_results(results, task)
        await self._persist_execution_memory(task, results, final_result)
        return final_result

    async def _decompose_task(self, task: SwarmTask) -> List[SwarmTask]:
        prompt = f"""
        Descompón esta tarea fiscal/contable en subtareas atómicas:
        Objetivo: {task.objective}
        Contexto: {json.dumps(task.context, indent=2)}
        Responde en JSON con lista de subtareas.
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:11434/api/generate",
                json={"model": "qwen2.5-coder:32b", "prompt": prompt, "format": "json", "stream": False},
                timeout=60.0
            )
        decomposition = response.json()
        subtasks_data = json.loads(decomposition.get("response", "[]"))
        subtasks = []
        for i, st_data in enumerate(subtasks_data.get("subtasks", [])):
            subtask = SwarmTask(
                id=f"{task.id}_sub_{i}",
                objective=st_data["objective"],
                context={**task.context, "parent_task": task.id},
                priority=task.priority,
                required_capabilities=st_data.get("capabilities", []),
                max_retries=task.max_retries
            )
            subtasks.append(subtask)
        return subtasks

    def _route_subtasks(self, subtasks: List[SwarmTask]) -> Dict[str, List[SwarmTask]]:
        assignments = defaultdict(list)
        for subtask in subtasks:
            best_agent = None
            best_score = -1
            for agent_id, capability in self.agents.items():
                score = self._calculate_capability_match(subtask.required_capabilities, capability)
                if score > best_score:
                    best_score = score
                    best_agent = agent_id
            if best_agent:
                assignments[best_agent].append(subtask)
            else:
                assignments["fallback_agent"].append(subtask)
        return dict(assignments)

    def _calculate_capability_match(self, required: List[str], capability: AgentCapability) -> float:
        if not required:
            return 0.5
        matches = sum(1 for cap in required if cap in capability.required_tools)
        return matches / len(required) * (1.0 if capability.name in required else 0.8)

    async def _execute_parallel(self, assignments: Dict[str, List[SwarmTask]], parent_task: SwarmTask) -> List[Dict[str, Any]]:
        semaphore = asyncio.Semaphore(5)
        async def execute_with_guard(agent_id: str, subtask: SwarmTask):
            async with semaphore:
                return await self._execute_with_recovery(agent_id, subtask, parent_task)
        tasks = []
        for agent_id, subtasks in assignments.items():
            for subtask in subtasks:
                tasks.append(execute_with_guard(agent_id, subtask))
        return await asyncio.gather(*tasks, return_exceptions=True)

    async def _execute_with_recovery(self, agent_id: str, subtask: SwarmTask, parent_task: SwarmTask) -> Dict[str, Any]:
        capability = self.agents.get(agent_id)
        retries = 0
        while retries < subtask.max_retries:
            try:
                result = await self._call_agent_api(agent_id, subtask)
                if self._validate_result(result, subtask):
                    return {"subtask_id": subtask.id, "agent": agent_id, "status": "success", "result": result, "retries": retries}
            except Exception as e:
                retries += 1
                subtask.execution_trace.append({"attempt": retries, "error": str(e), "timestamp": datetime.now().isoformat()})
                if capability and capability.fallback_agents and retries >= subtask.max_retries // 2:
                    for fallback_id in capability.fallback_agents:
                        try:
                            result = await self._call_agent_api(fallback_id, subtask)
                            return {"subtask_id": subtask.id, "agent": fallback_id, "status": "success_via_fallback", "result": result, "retries": retries}
                        except Exception:
                            continue
                await asyncio.sleep(2 ** retries)
        return {"subtask_id": subtask.id, "agent": agent_id, "status": "failed", "error": "Max retries exceeded", "trace": subtask.execution_trace}

    async def _call_agent_api(self, agent_id: str, subtask: SwarmTask) -> Any:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"http://localhost:8000/api/agents/{agent_id}/execute",
                json={"task": subtask.objective, "context": subtask.context, "timeout": self.agents[agent_id].max_execution_time if agent_id in self.agents else 30},
                timeout=60.0
            )
            return response.json()

    def _validate_result(self, result: Any, subtask: SwarmTask) -> bool:
        if not result:
            return False
        if isinstance(result, dict):
            return result.get("success", False) or "data" in result
        return True

    async def _synthesize_results(self, results: List[Dict], task: SwarmTask) -> Dict[str, Any]:
        successful = [r for r in results if isinstance(r, dict) and r.get("status") == "success"]
        failed = [r for r in results if isinstance(r, dict) and r.get("status") == "failed"]
        if not successful:
            return {"success": False, "error": "All subtasks failed", "failed_subtasks": failed, "recommendation": "Escalar a intervención humana"}
        synthesis_prompt = f"""
        Sintetiza estos resultados en una respuesta coherente:
        Tarea original: {task.objective}
        Resultados parciales: {json.dumps(successful, indent=2)}
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:11434/api/generate",
                json={"model": "qwen2.5-coder:32b", "prompt": synthesis_prompt, "stream": False},
                timeout=30.0
            )
        synthesis = response.json().get("response", "")
        return {
            "success": True,
            "synthesis": synthesis,
            "subtask_results": successful,
            "failed_count": len(failed),
            "execution_time": (datetime.now() - task.created_at).total_seconds()
        }

    async def _persist_execution_memory(self, task: SwarmTask, results: List[Dict], final: Dict):
        memory_entry = {
            "task_pattern": task.objective,
            "context_hash": hashlib.md5(json.dumps(task.context, sort_keys=True).encode()).hexdigest(),
            "strategy_used": [r.get("agent") for r in results if isinstance(r, dict)],
            "success": final.get("success", False),
            "timestamp": datetime.now().isoformat()
        }
