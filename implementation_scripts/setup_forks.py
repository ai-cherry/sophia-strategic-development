#!/usr/bin/env python3
"""Setup and manage forked MCP repositories."""

import requests
import json
import os

def fork_repository(owner, repo, org):
    """Fork a repository to the organization."""
    headers = {
        'Authorization': f'token {os.environ.get("GITHUB_TOKEN")}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    fork_data = {
        'organization': org
    }
    
    response = requests.post(
        f'https://api.github.com/repos/{owner}/{repo}/forks',
        headers=headers,
        json=fork_data
    )
    
    if response.status_code == 202:
        print(f"✅ Successfully forked {owner}/{repo} to {org}")
        return response.json()
    else:
        print(f"❌ Failed to fork {owner}/{repo}: {response.status_code}")
        return None

def main():
    """Main fork setup function."""
    forks_to_create = [
        ('makenotion', 'notion-mcp-server'),
        ('korotovsky', 'slack-mcp-server'),
        ('brightdata', 'mcp-server')
    ]
    
    org = 'ai-cherry'
    
    for owner, repo in forks_to_create:
        fork_repository(owner, repo, org)

if __name__ == '__main__':
    main()
