"""API integration tests using FastAPI TestClient."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from fastapi.testclient import TestClient
from backend.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_root(client):
    r = client.get("/")
    assert r.status_code == 200
    assert r.json()["system"] == "MYSTIC AI OS"


def test_status(client):
    r = client.get("/status")
    assert r.status_code == 200
    data = r.json()
    assert "agents" in data
    assert "dev_agent" in data["agents"]


def test_list_agents(client):
    r = client.get("/agents")
    assert r.status_code == 200
    names = [a["name"] for a in r.json()]
    assert "infra_agent" in names
    assert "knowledge_agent" in names


def test_list_skills(client):
    r = client.get("/skills")
    assert r.status_code == 200
    names = [s["name"] for s in r.json()]
    assert "filesystem" in names
    assert "shell" in names


def test_execute_task_shell(client):
    r = client.post("/task", json={
        "agent": "infra_agent",
        "payload": {
            "skill": "shell",
            "args": {"command": "echo mystic_ok"}
        }
    })
    assert r.status_code == 200
    data = r.json()
    assert data["agent"] == "infra_agent"
    assert data["result"]["status"] == "ok"
    assert data["result"]["result"]["stdout"] == "mystic_ok"


def test_execute_task_filesystem(client, tmp_path):
    path = str(tmp_path / "api_test.txt")
    r = client.post("/task", json={
        "agent": "dev_agent",
        "payload": {
            "skill": "filesystem",
            "args": {"action": "write", "path": path, "content": "desde API"}
        }
    })
    assert r.status_code == 200
    assert r.json()["result"]["status"] == "ok"


def test_execute_task_by_capability(client):
    r = client.post("/task", json={
        "capability": "infrastructure",
        "payload": {
            "skill": "shell",
            "args": {"command": "echo infra"}
        }
    })
    assert r.status_code == 200
    assert r.json()["agent"] == "infra_agent"


def test_execute_swarm(client):
    r = client.post("/swarm", json={
        "tasks": [
            {
                "agent": "infra_agent",
                "payload": {"skill": "shell", "args": {"command": "echo task1"}}
            },
            {
                "agent": "dev_agent",
                "payload": {"skill": "analysis", "args": {"action": "stats", "text": "hola mundo test"}}
            }
        ]
    })
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 2
    assert len(data["results"]) == 2


def test_memory_tasks(client):
    r = client.get("/memory/tasks?limit=5")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_knowledge_crud(client):
    # PUT
    r = client.post("/memory/knowledge", json={"key": "test_cliente", "value": "Fourgea"})
    assert r.status_code == 200

    # GET
    r = client.get("/memory/knowledge/test_cliente")
    assert r.status_code == 200
    assert r.json()["value"] == "Fourgea"

    # DELETE
    r = client.delete("/memory/knowledge/test_cliente")
    assert r.status_code == 200

    # GET 404
    r = client.get("/memory/knowledge/test_cliente")
    assert r.status_code == 404


def test_vector_add_and_search(client):
    client.post("/memory/vectors", json={
        "key": "v1",
        "text": "filtración de aceite industrial Fourgea"
    })
    r = client.post("/memory/vectors/search", json={"query": "aceite", "limit": 5})
    assert r.status_code == 200
    results = r.json()["results"]
    assert any(res["key"] == "v1" for res in results)


def test_invalid_agent_returns_400(client):
    r = client.post("/task", json={
        "agent": "agente_inexistente",
        "payload": {"skill": "shell", "args": {"command": "echo x"}}
    })
    assert r.status_code == 400
