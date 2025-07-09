# Lambda Labs Setup Requirements

To complete the Lambda Labs cleanup and deployment for Sophia AI, please provide:

## 1. Lambda Labs API Key
One of your Lambda Labs API keys (preferably the "pulumi" one):
```bash
export LAMBDA_LABS_API_KEY='your-api-key-here'
```

## 2. SSH Private Key Location
Confirm the location of your SSH private key:
```bash
export LAMBDA_SSH_KEY_PATH='~/.ssh/sophia-ai-key'  # or your actual path
```

## 3. GitHub Personal Access Token
For cloning the private repository:
```bash
export GITHUB_TOKEN='ghp_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
```

## 4. Instance Decisions
Confirm which instances to keep/remove:

### KEEP (Recommended):
- **sophia-ai-production** (192.222.58.232) - 8x V100 GPUs
  - Main production server for heavy AI workloads
- **orchestra-sophia-prod** (150.230.47.71) - 1x A10 GPU
  - MCP server orchestration
- **sophia-ai-production-gpu** (129.153.123.54) - 1x A100 GPU
  - Advanced AI operations

### REMOVE (Recommended):
- cherry-ai-production (150.136.94.139) - 8x A100 (overkill)
- orchestra-dev-fresh (192.9.142.8) - dev instance
- orchestra-karen-prod (146.235.230.166) - unrelated
- sophia-ai-production (170.9.9.253) - duplicate
- sophia-ai-production-1751279028 (129.153.119.115) - duplicate
- sophia-ai-production (64.181.231.85) - duplicate

## 5. SSH Key Decisions

### KEEP:
- sophia-ai-key
- cherry-ai-collaboration-20250604
- sophia-deployment-key-20250621
- sophia-prod-key-2025

### REMOVE:
- manus-fresh-key
- cherry-ai-key (if duplicate of sophia-ai-key)

## 6. API Key Cleanup

### DELETE:
- fuckyou (unprofessional)
- helpplease (test key)
- Manus (if not needed)
- manus 2 (if not needed)

### CREATE NEW:
- sophia-ai-prod
- sophia-ai-dev
- sophia-ai-pulumi

## Running the Cleanup

Once you provide the above information, run:

```bash
# Make scripts executable
chmod +x scripts/lambda_labs_cleanup_and_deploy.py
chmod +x scripts/lambda_labs_deployment.sh

# Set environment variables
export LAMBDA_LABS_API_KEY='your-api-key'
export LAMBDA_SSH_KEY_PATH='~/.ssh/sophia-ai-key'
export GITHUB_TOKEN='your-github-token'

# Run the cleanup tool
python scripts/lambda_labs_cleanup_and_deploy.py
```

The script will:
1. Show a dry-run preview of all changes
2. Ask for confirmation before making any changes
3. Clean up instances, SSH keys, and API keys
4. Deploy Sophia AI to the remaining instances

## Total Estimated Savings

By removing unnecessary instances:
- Save ~$5,000-10,000/month in GPU costs
- Reduce complexity and maintenance overhead
- Focus resources on production workloads
