"""GitHub skill — interact with GitHub via gh CLI."""

from __future__ import annotations

import json
import subprocess
from typing import Any

from skills.base_skill import BaseSkill

GH_BIN = "/home/mystic/.local/bin/gh"  # gh CLI installed in VPS


def _gh(args: list[str], cwd: str | None = None) -> dict:
    """Run a gh command and return parsed output."""
    result = subprocess.run(
        [GH_BIN] + args,
        capture_output=True,
        text=True,
        cwd=cwd,
        timeout=30,
    )
    stdout = result.stdout.strip()
    stderr = result.stderr.strip()
    return {
        "stdout": stdout,
        "stderr": stderr,
        "returncode": result.returncode,
    }


def _gh_json(args: list[str], cwd: str | None = None) -> Any:
    """Run gh command with JSON output."""
    raw = _gh(args, cwd=cwd)
    if raw["returncode"] != 0:
        raise RuntimeError(f"gh error: {raw['stderr']}")
    if not raw["stdout"]:
        return {}
    return json.loads(raw["stdout"])


class Skill(BaseSkill):
    name = "github"
    description = "Interact with GitHub: list repos, PRs, issues, create PRs, push code."

    def execute(self, action: str, **kwargs: Any) -> Any:
        """
        Actions:
            list_repos   — list repos for authenticated user
            list_prs     — list open PRs for a repo (repo=owner/name)
            list_issues  — list open issues for a repo (repo=owner/name)
            view_pr      — view a PR (repo=owner/name, number=int)
            create_pr    — create PR (repo, title, body, base, head)
            merge_pr     — merge a PR (repo, number)
            repo_info    — get repo details (repo=owner/name)
            auth_status  — check gh auth status
            run          — run arbitrary gh subcommand (args=list[str])
        """
        action = action.lower()

        if action == "auth_status":
            return _gh(["auth", "status"])

        if action == "list_repos":
            return _gh_json(["repo", "list", "--json", "name,description,url,isPrivate", "--limit", "30"])

        if action == "repo_info":
            repo = kwargs["repo"]
            return _gh_json(["repo", "view", repo, "--json",
                             "name,description,url,defaultBranchRef,stargazerCount,forkCount"])

        if action == "list_prs":
            repo = kwargs["repo"]
            return _gh_json(["pr", "list", "--repo", repo, "--json",
                             "number,title,state,headRefName,createdAt", "--limit", "20"])

        if action == "view_pr":
            repo = kwargs["repo"]
            number = str(kwargs["number"])
            return _gh_json(["pr", "view", number, "--repo", repo, "--json",
                             "number,title,state,body,files,commits"])

        if action == "create_pr":
            repo = kwargs["repo"]
            title = kwargs["title"]
            body = kwargs.get("body", "")
            base = kwargs.get("base", "main")
            head = kwargs.get("head")
            args = ["pr", "create", "--repo", repo, "--title", title,
                    "--body", body, "--base", base]
            if head:
                args += ["--head", head]
            return _gh(args, cwd=kwargs.get("cwd"))

        if action == "merge_pr":
            repo = kwargs["repo"]
            number = str(kwargs["number"])
            strategy = kwargs.get("strategy", "--merge")
            return _gh(["pr", "merge", number, "--repo", repo, strategy])

        if action == "list_issues":
            repo = kwargs["repo"]
            return _gh_json(["issue", "list", "--repo", repo, "--json",
                             "number,title,state,labels,createdAt", "--limit", "20"])

        if action == "run":
            args = kwargs.get("args", [])
            cwd = kwargs.get("cwd")
            return _gh(args, cwd=cwd)

        raise ValueError(f"Unknown action '{action}'. Valid: list_repos, repo_info, list_prs, view_pr, create_pr, merge_pr, list_issues, auth_status, run")
