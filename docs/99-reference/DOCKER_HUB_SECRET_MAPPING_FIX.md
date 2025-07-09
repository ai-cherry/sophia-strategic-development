# Docker Hub Secret Mapping - THE PERMANENT FIX

## THE PROBLEM

The Docker Hub credentials have been a daily fucking battle because of inconsistent naming across:
- GitHub Secrets
- Pulumi ESC
- Application code
- CI/CD workflows

## THE SOLUTION

### 1. GitHub Secret Names (SOURCE OF TRUTH)

```
DOCKER_USERNAME    # NOT DOCKERHUB_USERNAME, NOT DOCKER_USER_NAME
DOCKER_TOKEN       # NOT DOCKER_HUB_ACCESS_TOKEN, NOT DOCKER_PASSWORD
```

### 2. Pulumi ESC Mapping

```yaml
docker_username: ${{ secrets.DOCKER_USERNAME }}
docker_token: ${{ secrets.DOCKER_TOKEN }}
```

### 3. Application Code Mapping

In `backend/core/auto_esc_config.py`:

```python
# ESC key mappings
"docker_token": "DOCKER_TOKEN",  # PRIMARY
"docker_hub_access_token": "DOCKER_TOKEN",  # Maps to same
"docker_password": "DOCKER_TOKEN",  # Maps to same
"docker_hub_username": "DOCKER_USERNAME",  # PRIMARY
"docker_username": "DOCKER_USERNAME",  # Maps to same
```

### 4. GitHub Actions Usage

```yaml
- name: Login to Docker Hub
  uses: docker/login-action@v3
  with:
    username: ${{ secrets.DOCKER_USERNAME }}
    password: ${{ secrets.DOCKER_TOKEN }}
```

## HOW TO TEST

1. **Check current mapping:**
   ```bash
   python3 test_docker_config.py
   ```

2. **Fix sync manually:**
   ```bash
   export DOCKER_USERNAME="scoobyjava15"
   export DOCKER_TOKEN="your-actual-token"
   python3 scripts/fix_secret_sync.py
   ```

3. **Verify in Pulumi ESC:**
   ```bash
   pulumi env get default/sophia-ai-production --show-secrets | grep docker
   ```

## WHAT CHANGED

| OLD (WRONG) | NEW (CORRECT) |
|-------------|---------------|
| DOCKERHUB_USERNAME | DOCKER_USERNAME |
| DOCKER_HUB_ACCESS_TOKEN | DOCKER_TOKEN |
| DOCKER_PERSONAL_ACCESS_TOKEN | DOCKER_TOKEN |
| DOCKER_USER_NAME | DOCKER_USERNAME |

## WHY THIS KEEPS BREAKING

1. Multiple people adding secrets with different names
2. No single source of truth for naming
3. Sync scripts not enforcing the mapping
4. Documentation scattered across multiple files

## THE PERMANENT FIX

1. **This document** is the source of truth
2. **fix_secret_sync.py** enforces the mapping
3. **auto_esc_config.py** handles all variations
4. **GitHub Actions** use consistent names

## NEVER AGAIN

If someone adds a new Docker Hub secret with a different name:
1. DO NOT use it
2. Update the mapping in auto_esc_config.py
3. Point them to this document
4. Run fix_secret_sync.py to fix it

The correct names are:
- `DOCKER_USERNAME`
- `DOCKER_TOKEN`

Period. End of story. No variations. 