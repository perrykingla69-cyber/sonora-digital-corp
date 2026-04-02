"""Basic smoke tests for all skills and the orchestrator."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from skills.filesystem.skill import Skill as FSSkill
from skills.shell.skill import Skill as ShellSkill
from skills.analysis.skill import Skill as AnalysisSkill
from agents.base_agent import BaseAgent
from orchestrator.orchestrator import Orchestrator
from memory import TaskHistory, KnowledgeStore, VectorMemory


# ---- Filesystem -------------------------------------------------------

def test_filesystem_write_read(tmp_path):
    skill = FSSkill()
    path = str(tmp_path / "test.txt")
    result = skill(action="write", path=path, content="hola mundo")
    assert result["status"] == "ok"

    result = skill(action="read", path=path)
    assert result["status"] == "ok"
    assert result["result"] == "hola mundo"


def test_filesystem_list(tmp_path):
    skill = FSSkill()
    (tmp_path / "a.txt").write_text("a")
    (tmp_path / "b.txt").write_text("b")
    result = skill(action="list", path=str(tmp_path))
    assert result["status"] == "ok"
    assert "a.txt" in result["result"]


def test_filesystem_exists(tmp_path):
    skill = FSSkill()
    result = skill(action="exists", path=str(tmp_path / "nope.txt"))
    assert result["result"] is False


# ---- Shell ------------------------------------------------------------

def test_shell_echo():
    skill = ShellSkill()
    result = skill(command="echo hello")
    assert result["status"] == "ok"
    assert result["result"]["stdout"] == "hello"
    assert result["result"]["returncode"] == 0


def test_shell_blocked_command():
    skill = ShellSkill()
    result = skill(command="rm -rf / --no-preserve-root")
    assert result["status"] == "error"
    assert "blocked" in result["error"].lower()


# ---- Analysis ---------------------------------------------------------

def test_analysis_stats():
    skill = AnalysisSkill()
    result = skill(action="stats", text="Hello world. This is a test sentence.")
    assert result["status"] == "ok"
    stats = result["result"]
    assert stats["words"] >= 7
    assert stats["sentences"] >= 2


def test_analysis_keywords():
    skill = AnalysisSkill()
    text = "Fourgea purifica aceite industrial. Fourgea filtra aceite hidráulico. Aceite es importante."
    result = skill(action="keywords", text=text, top_n=3)
    assert result["status"] == "ok"
    keywords = [k["keyword"] for k in result["result"]]
    assert "aceite" in keywords or "fourgea" in keywords


# ---- Memory -----------------------------------------------------------

def test_task_history():
    th = TaskHistory()
    record = th.store("t1", {"agent": "dev_agent"}, {"status": "ok"})
    assert record.task_id == "t1"
    assert th.find("t1") is not None
    assert len(th.recent(5)) == 1


def test_knowledge_store():
    ks = KnowledgeStore()
    ks.put("company", "Fourgea")
    assert ks.get("company") == "Fourgea"
    results = ks.search("comp")
    assert "company" in results


def test_vector_memory_lexical():
    vm = VectorMemory()
    vm.add("doc1", "Filtración de aceite industrial para minería")
    vm.add("doc2", "Dashboard web React para contabilidad")
    results = vm.similarity_search("aceite")
    assert len(results) == 1
    assert results[0].key == "doc1"


# ---- BaseAgent --------------------------------------------------------

def test_base_agent_register_and_call():
    from skills.filesystem.skill import Skill as FS
    agent = BaseAgent(name="test_agent", role="testing")
    agent.register_skill("filesystem", FS())
    result = agent({"skill": "filesystem", "args": {"action": "exists", "path": "/tmp"}})
    assert result["agent"] == "test_agent"
    assert result["result"]["status"] == "ok"


def test_base_agent_missing_skill():
    agent = BaseAgent(name="test_agent", role="testing")
    with pytest.raises(ValueError, match="does not have skill"):
        agent.run_skill("nonexistent")


# ---- Orchestrator -----------------------------------------------------

def test_orchestrator_status():
    orch = Orchestrator.from_config("configs/agents.yaml", "configs/skills.yaml")
    status = orch.status()
    assert "dev_agent" in status["agents"]
    assert "filesystem" in status["skills"]


def test_orchestrator_execute_task(tmp_path):
    orch = Orchestrator.from_config("configs/agents.yaml", "configs/skills.yaml")
    path = str(tmp_path / "orch_test.txt")
    result = orch.execute_task({
        "agent": "dev_agent",
        "payload": {
            "skill": "filesystem",
            "args": {"action": "write", "path": path, "content": "test"},
        },
    })
    assert result["agent"] == "dev_agent"
    assert result["result"]["status"] == "ok"
