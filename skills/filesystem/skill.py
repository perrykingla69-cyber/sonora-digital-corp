"""Filesystem skill — read, write, list, delete files."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from skills.base_skill import BaseSkill


class Skill(BaseSkill):
    name = "filesystem"
    description = "Read, write, list, and delete files on the local filesystem."

    def execute(self, action: str, path: str, content: str = "", encoding: str = "utf-8") -> Any:
        """
        Actions:
            read   — read file contents (returns str)
            write  — write content to file (creates parent dirs if needed)
            append — append content to file
            list   — list directory contents (returns list of str)
            exists — check if path exists (returns bool)
            delete — delete a file
            mkdir  — create directory (parents=True, exist_ok=True)
        """
        p = Path(path)
        action = action.lower()

        if action == "read":
            return p.read_text(encoding=encoding)

        if action == "write":
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding=encoding)
            return f"Written {len(content)} chars to {path}"

        if action == "append":
            p.parent.mkdir(parents=True, exist_ok=True)
            with p.open("a", encoding=encoding) as fh:
                fh.write(content)
            return f"Appended {len(content)} chars to {path}"

        if action == "list":
            if not p.is_dir():
                raise ValueError(f"{path} is not a directory")
            entries = sorted(os.listdir(p))
            return entries

        if action == "exists":
            return p.exists()

        if action == "delete":
            p.unlink(missing_ok=True)
            return f"Deleted {path}"

        if action == "mkdir":
            p.mkdir(parents=True, exist_ok=True)
            return f"Directory created: {path}"

        raise ValueError(f"Unknown action '{action}'. Valid: read, write, append, list, exists, delete, mkdir")
