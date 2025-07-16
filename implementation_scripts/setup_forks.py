#!/usr/bin/env python3
"""Setup and manage forked MCP repositories."""


import requests
from backend.core.auto_esc_config import get_config_value


def fork_repository(owner, repo, org):
    """Fork a repository to the organization."""
    headers = {
        "Authorization": f'token {get_config_value("GITHUB_TOKEN")}',
        "Accept": "application/vnd.github.v3+json",
    }

    fork_data = {"organization": org}

    response = requests.post(
        f"https://api.github.com/repos/{owner}/{repo}/forks",
        headers=headers,
        json=fork_data,
    )

    if response.status_code == 202:
        return response.json()
    else:
        return None


def main():
    """Main fork setup function."""
    forks_to_create = [
        ("makenotion", "notion-mcp-server"),
        ("korotovsky", "slack-mcp-server"),
        ("brightdata", "mcp-server"),
    ]

    org = "ai-cherry"

    for owner, repo in forks_to_create:
        fork_repository(owner, repo, org)


if __name__ == "__main__":
    main()
