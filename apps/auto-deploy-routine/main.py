"""
Auto Deploy Routine — HERMES OS
Monitoreo de Git pushes, trigger de pipeline CI/CD, verificación health, notificaciones al CEO.
Patrón: Fiscal Agent (determinístico + LLM fallback).
"""

import asyncio
import json
import os
import re
import sys
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
import httpx
import subprocess

# Logging JSON
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)


class DeploymentStatus(str, Enum):
    """Estados posibles de deployment."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILURE = "failure"
    ROLLBACK = "rollback"


class DeploymentAction(BaseModel):
    """Acción de deployment."""
    action: str  # monitor_git_push, trigger_pipeline, verify_health, notify_deployment
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    status: DeploymentStatus = DeploymentStatus.PENDING
    details: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None


class AutoDeployConfig(BaseModel):
    """Auto Deploy configuration."""
    github_repo: str = Field(default_factory=lambda: os.getenv("GITHUB_REPO", "perrykingla69-cyber/sonora-digital-corp"))
    github_token: str = Field(default_factory=lambda: os.getenv("GITHUB_TOKEN", ""))
    github_webhook_secret: str = Field(default_factory=lambda: os.getenv("GITHUB_WEBHOOK_SECRET", ""))

    vps_host: str = Field(default_factory=lambda: os.getenv("VPS_HOST", "vps.sonora.io"))
    vps_ssh_key: str = Field(default_factory=lambda: os.getenv("VPS_SSH_KEY_PATH", "/root/.ssh/vps_key"))
    vps_deploy_user: str = Field(default_factory=lambda: os.getenv("VPS_DEPLOY_USER", "root"))

    telegram_token_ceo: str = Field(default_factory=lambda: os.getenv("TELEGRAM_TOKEN_CEO", ""))
    telegram_ceo_chat_id: str = Field(default_factory=lambda: os.getenv("CEO_CHAT_ID", "5738935134"))

    health_check_url: str = Field(default_factory=lambda: os.getenv("HEALTH_CHECK_URL", "http://hermes-api:8000/health"))
    health_check_timeout: int = Field(default=30)

    openrouter_key: str = Field(default_factory=lambda: os.getenv("OPENROUTER_API_KEY", ""))
    model: str = Field(default="google/gemini-2.0-flash-001")
    environment: str = Field(default=os.getenv("ENVIRONMENT", "production"))


class AutoDeployRoutine:
    """Agent para automatizar deployments con monitoreo de Git, CI/CD y health checks."""

    def __init__(self, config: AutoDeployConfig):
        self.config = config
        self.logger = logging.getLogger("AutoDeployRoutine")
        self.http_client = None
        self.deployment_history: List[DeploymentAction] = []

    async def setup(self) -> None:
        """Initialize HTTP client and validate configuration."""
        logging.basicConfig(level=logging.INFO)
        self.logger.info("agent_setup", extra={
            "agent": "auto-deploy-routine",
            "repo": self.config.github_repo,
            "vps_host": self.config.vps_host,
        })

        self.http_client = httpx.AsyncClient(timeout=60.0)

        # Validate critical config
        if not self.config.github_token:
            self.logger.warning("missing_config", extra={"field": "GITHUB_TOKEN"})
        if not self.config.telegram_token_ceo:
            self.logger.warning("missing_config", extra={"field": "TELEGRAM_TOKEN_CEO"})

    async def cleanup(self) -> None:
        """Close HTTP client."""
        if self.http_client:
            await self.http_client.aclose()

    # ============ CORE OPERATIONS ============

    async def monitor_git_push(self, webhook_payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Monitorea pushes a GitHub y extrae metadata.
        Determinístico: parsea payload de GitHub webhook.
        """
        action = DeploymentAction(action="monitor_git_push")

        try:
            if not webhook_payload:
                action.error = "webhook_payload is required"
                action.status = DeploymentStatus.FAILURE
                self.deployment_history.append(action)
                return action.model_dump()

            # Parsear metadata del push
            ref = webhook_payload.get("ref", "")
            branch = ref.split("/")[-1] if ref else ""

            commits = webhook_payload.get("commits", [])
            commit_count = len(commits)

            pusher = webhook_payload.get("pusher", {})
            pusher_name = pusher.get("name", "unknown")

            repository = webhook_payload.get("repository", {})
            repo_name = repository.get("name", "unknown")

            # Validar que es rama main/master
            is_main = branch in ["main", "master"]

            action.details = {
                "branch": branch,
                "commit_count": commit_count,
                "pusher": pusher_name,
                "repo": repo_name,
                "is_main": is_main,
                "commits": [
                    {
                        "sha": c.get("id", "")[:7],
                        "message": c.get("message", ""),
                        "author": c.get("author", {}).get("name", "")
                    }
                    for c in commits[:5]
                ]
            }

            action.status = DeploymentStatus.SUCCESS
            self.logger.info("git_push_monitored", extra={
                "branch": branch,
                "commits": commit_count,
                "pusher": pusher_name,
                "is_main": is_main,
            })

        except Exception as e:
            action.error = str(e)
            action.status = DeploymentStatus.FAILURE
            self.logger.error("monitor_git_push_error", extra={"error": str(e)})

        self.deployment_history.append(action)
        return action.model_dump()

    async def trigger_pipeline(self, branch: str = "main", reason: str = "") -> Dict[str, Any]:
        """
        Dispara GitHub Actions workflow para deploy.
        Usa GitHub REST API para triggear workflow_dispatch.
        """
        action = DeploymentAction(action="trigger_pipeline")

        try:
            if not self.config.github_token:
                action.error = "GITHUB_TOKEN not configured"
                action.status = DeploymentStatus.FAILURE
                self.deployment_history.append(action)
                return action.model_dump()

            # Validar rama
            if branch not in ["main", "master", "develop"]:
                action.error = f"Invalid branch: {branch}"
                action.status = DeploymentStatus.FAILURE
                self.deployment_history.append(action)
                return action.model_dump()

            # GitHub API endpoint para triggear workflow
            owner, repo = self.config.github_repo.split("/")
            url = f"https://api.github.com/repos/{owner}/{repo}/actions/workflows/deploy.yml/dispatches"

            headers = {
                "Authorization": f"Bearer {self.config.github_token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            }

            payload = {
                "ref": branch,
                "inputs": {
                    "reason": reason or "Auto-triggered deployment",
                }
            }

            # POST al workflow
            response = await self.http_client.post(url, json=payload, headers=headers)

            if response.status_code in [201, 204]:
                action.status = DeploymentStatus.IN_PROGRESS
                action.details = {
                    "workflow": "deploy.yml",
                    "branch": branch,
                    "github_response_code": response.status_code,
                    "reason": reason,
                }
                self.logger.info("pipeline_triggered", extra={
                    "workflow": "deploy.yml",
                    "branch": branch,
                    "code": response.status_code,
                })
            else:
                action.error = f"GitHub API error: {response.status_code} {response.text}"
                action.status = DeploymentStatus.FAILURE
                self.logger.error("pipeline_trigger_failed", extra={
                    "code": response.status_code,
                    "text": response.text,
                })

        except Exception as e:
            action.error = str(e)
            action.status = DeploymentStatus.FAILURE
            self.logger.error("trigger_pipeline_error", extra={"error": str(e)})

        self.deployment_history.append(action)
        return action.model_dump()

    async def verify_health(self, services: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Verifica health checks de servicios desplegados.
        Determinístico: HTTP GET a endpoints y parsea respuestas.
        """
        action = DeploymentAction(action="verify_health")

        if services is None:
            services = ["api", "frontend", "postgres", "redis"]

        health_results = {}
        all_healthy = True

        try:
            # Health check API principal
            try:
                response = await self.http_client.get(
                    self.config.health_check_url,
                    timeout=self.config.health_check_timeout
                )
                api_healthy = response.status_code == 200
                health_results["api"] = {
                    "healthy": api_healthy,
                    "code": response.status_code,
                    "timestamp": datetime.utcnow().isoformat(),
                }
                if not api_healthy:
                    all_healthy = False
            except Exception as e:
                health_results["api"] = {
                    "healthy": False,
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat(),
                }
                all_healthy = False

            # Verificar servicios en VPS via SSH (simple check)
            for service in services[1:]:
                try:
                    cmd = f"systemctl is-active {service}"
                    result = subprocess.run(
                        ["ssh", "-i", self.config.vps_ssh_key,
                         f"{self.config.vps_deploy_user}@{self.config.vps_host}",
                         cmd],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    is_active = result.returncode == 0
                    health_results[service] = {
                        "healthy": is_active,
                        "active": is_active,
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                    if not is_active:
                        all_healthy = False
                except Exception as e:
                    health_results[service] = {
                        "healthy": False,
                        "error": str(e),
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                    all_healthy = False

            action.details = {
                "services_checked": len(health_results),
                "all_healthy": all_healthy,
                "results": health_results,
            }

            action.status = DeploymentStatus.SUCCESS if all_healthy else DeploymentStatus.FAILURE
            self.logger.info("health_check_completed", extra={
                "all_healthy": all_healthy,
                "services": len(health_results),
            })

        except Exception as e:
            action.error = str(e)
            action.status = DeploymentStatus.FAILURE
            self.logger.error("verify_health_error", extra={"error": str(e)})

        self.deployment_history.append(action)
        return action.model_dump()

    async def notify_deployment(self, status: DeploymentStatus, details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Notifica al CEO via Telegram sobre estado del deployment.
        Determinístico: formatea mensaje, envía a Telegram.
        """
        action = DeploymentAction(action="notify_deployment")

        try:
            if not self.config.telegram_token_ceo:
                action.error = "TELEGRAM_TOKEN_CEO not configured"
                action.status = DeploymentStatus.FAILURE
                self.deployment_history.append(action)
                return action.model_dump()

            # Formato del mensaje según status
            status_emoji = {
                DeploymentStatus.SUCCESS: "✅",
                DeploymentStatus.FAILURE: "🔴",
                DeploymentStatus.IN_PROGRESS: "🔄",
                DeploymentStatus.ROLLBACK: "⚠️",
                DeploymentStatus.PENDING: "⏳",
            }

            emoji = status_emoji.get(status, "❓")

            message = f"{emoji} DEPLOYMENT {status.upper()}\n\n"
            message += f"Repo: {self.config.github_repo}\n"
            message += f"Time: {datetime.utcnow().isoformat()}\n\n"

            # Agregar detalles
            if details:
                for key, value in details.items():
                    if isinstance(value, (dict, list)):
                        message += f"{key}: {json.dumps(value, indent=2)}\n"
                    else:
                        message += f"{key}: {value}\n"

            # Telegram Bot API
            telegram_url = f"https://api.telegram.org/bot{self.config.telegram_token_ceo}/sendMessage"

            payload = {
                "chat_id": self.config.telegram_ceo_chat_id,
                "text": message,
                "parse_mode": "HTML",
            }

            response = await self.http_client.post(telegram_url, json=payload)

            if response.status_code == 200:
                action.status = DeploymentStatus.SUCCESS
                action.details = {
                    "notification_sent": True,
                    "chat_id": self.config.telegram_ceo_chat_id,
                    "deployment_status": status.value,
                }
                self.logger.info("notification_sent", extra={
                    "status": status.value,
                    "chat_id": self.config.telegram_ceo_chat_id,
                })
            else:
                action.error = f"Telegram API error: {response.status_code}"
                action.status = DeploymentStatus.FAILURE
                self.logger.error("notification_failed", extra={
                    "code": response.status_code,
                })

        except Exception as e:
            action.error = str(e)
            action.status = DeploymentStatus.FAILURE
            self.logger.error("notify_deployment_error", extra={"error": str(e)})

        self.deployment_history.append(action)
        return action.model_dump()

    # ============ ORCHESTRATION ============

    async def handle_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Orquesta flujo completo desde webhook GitHub:
        1. monitor_git_push
        2. trigger_pipeline (si es main)
        3. verify_health (después de deploy)
        4. notify_deployment
        """
        results = {
            "workflow": "webhook_deployment",
            "timestamp": datetime.utcnow().isoformat(),
            "steps": {}
        }

        try:
            # Step 1: Monitor
            monitor_result = await self.monitor_git_push(payload)
            results["steps"]["monitor"] = monitor_result

            branch = monitor_result.get("details", {}).get("branch", "")
            is_main = monitor_result.get("details", {}).get("is_main", False)

            # Step 2: Trigger si es main
            if is_main and monitor_result["status"] == "success":
                trigger_result = await self.trigger_pipeline(
                    branch=branch,
                    reason="Auto-triggered from GitHub push"
                )
                results["steps"]["trigger"] = trigger_result

            # Step 3: Verify health (después de delay)
            await asyncio.sleep(5)  # Esperar a que CI/CD inicie
            health_result = await self.verify_health()
            results["steps"]["health"] = health_result

            # Step 4: Notify
            final_status = health_result["status"]
            notify_result = await self.notify_deployment(
                status=final_status,
                details=results["steps"]
            )
            results["steps"]["notify"] = notify_result

            results["overall_status"] = final_status

        except Exception as e:
            results["error"] = str(e)
            results["overall_status"] = "failure"
            self.logger.error("webhook_handler_error", extra={"error": str(e)})

        return results

    async def run(self) -> None:
        """Main entrypoint para agente independiente (polling mode)."""
        await self.setup()

        try:
            self.logger.info("agent_running", extra={
                "agent": "auto-deploy-routine",
                "mode": "independent",
            })

            # En modo independiente, simplemente espera (sería usado vía webhook)
            while True:
                await asyncio.sleep(60)

        finally:
            await self.cleanup()


# ============ CLI ENTRYPOINT ============

async def main():
    """CLI entrypoint."""
    config = AutoDeployConfig()
    agent = AutoDeployRoutine(config)

    await agent.run()


if __name__ == "__main__":
    asyncio.run(main())
