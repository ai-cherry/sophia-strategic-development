#!/usr/bin/env python3
"""
Create forks of target MCP repositories to ai-cherry organization
"""

import subprocess
import time

import requests


def get_github_token():
    """Extract GitHub token from git remote."""
    try:
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            cwd="/home/ubuntu/sophia-main",
        )

        if result.returncode == 0:
            remote_url = result.stdout.strip()
            if "github_pat_" in remote_url:
                start = remote_url.find("github_pat_")
                end = remote_url.find("@github.com")
                if start != -1 and end != -1:
                    return remote_url[start:end]
        return None
    except Exception:
        return None


def fork_repository(owner, repo, org, token):
    """Fork a repository to the organization."""
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Sophia-AI-Fork-Manager",
    }

    fork_data = {"organization": org}

    response = requests.post(
        f"https://api.github.com/repos/{owner}/{repo}/forks",
        headers=headers,
        json=fork_data,
    )

    if response.status_code == 202:
        return response.json()
    elif response.status_code == 422:
        return {"message": "fork_exists"}
    else:
        return None


def main():
    """Main fork creation function."""

    token = get_github_token()
    if not token:
        return 1

    forks_to_create = [
        ("makenotion", "notion-mcp-server"),
        ("korotovsky", "slack-mcp-server"),
    ]

    org = "ai-cherry"

    for owner, repo in forks_to_create:
        result = fork_repository(owner, repo, org, token)
        if result:
            # Wait a bit between forks to avoid rate limiting
            time.sleep(2)

    return 0


if __name__ == "__main__":
    exit(main())
