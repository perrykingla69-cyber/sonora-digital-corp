"""Shell skill — run shell commands safely via subprocess."""

from __future__ import annotations

import subprocess
from typing import Any

from skills.base_skill import BaseSkill

# Commands that are never allowed regardless of context
_BLOCKED = frozenset({"rm -rf /", "mkfs", "dd if=", ":(){:|:&};:"})


class Skill(BaseSkill):
    name = "shell"
    description = "Execute shell commands and return stdout/stderr/returncode."

    def execute(
        self,
        command: str,
        cwd: str | None = None,
        timeout: int = 30,
        env: dict | None = None,
    ) -> Any:
        """
        Args:
            command: Shell command string to execute.
            cwd:     Working directory (optional).
            timeout: Max seconds to wait (default 30).
            env:     Extra environment variables (merged with current env).

        Returns dict with stdout, stderr, returncode.
        """
        # Basic safety check
        for blocked in _BLOCKED:
            if blocked in command:
                raise PermissionError(f"Command contains blocked pattern: '{blocked}'")

        import os
        full_env = os.environ.copy()
        if env:
            full_env.update(env)

        proc = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=timeout,
            env=full_env,
        )
        return {
            "stdout": proc.stdout.strip(),
            "stderr": proc.stderr.strip(),
            "returncode": proc.returncode,
        }
