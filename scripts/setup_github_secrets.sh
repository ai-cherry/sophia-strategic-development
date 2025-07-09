#!/bin/bash

# GitHub Secrets Setup Script for Sophia AI Lambda Labs Deployment
# This script sets up all necessary secrets for GitHub Actions

echo "🔐 Setting up GitHub Secrets for Sophia AI Lambda Labs Deployment..."

# Check if gh CLI is authenticated
if ! gh auth status >/dev/null 2>&1; then
    echo "❌ GitHub CLI not authenticated. Please run: gh auth login"
    exit 1
fi

# Get repository info
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
echo "📦 Repository: $REPO"

# Lambda Labs Secrets
echo "🔑 Setting Lambda Labs secrets..."

# Cloud API credentials
gh secret set LAMBDA_CLOUD_API_KEY --body "secret_sophiacloudapi_17cf7f3cedca48f18b4b8ea46cbb258f.EsLXt0lkGlhZ1Nd369Ld5DMSuhJg9O9y"
gh secret set LAMBDA_API_CLOUD_ENDPOINT --body "https://cloud.lambda.ai/api/v1/instances"

# Regular API credentials
gh secret set LAMBDA_API_KEY --body "secret_sophia5apikey_a404a99d985d41828d7020f0b9a122a2.PjbWZb0lLubKu1nmyWYLy9Ycl3vyL18o"
gh secret set LAMBDA_API_ENDPOINT --body "https://cloud.lambda.ai/api/v1/instances"

# SSH Keys
gh secret set LAMBDA_SSH_KEY --body "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCKAPI0WU9UcB5vVnneP3oExytrPcD0PON5NeQxeNAJOWQSWi/fvkQ97dhAEtjyddmaCti7LFrp3CW+4gtGSiC+2/jOVqERLkmycbC8UZNpyqCiLIwO4MkIuxVNiRkg/ucPuf0DjakJh92xFDIyeDAR55OrpMWqX6O0+OZL0DFXE7jBDaloez+oLytM16CMHtlnx+5Br7O+RoPLEFvBz9RZyqlzs5144pvgHyRSwuvXBcYLKqT24kAPqvxc0SqGYLnNAD1q96BPqMwZONAFPDf3jTFGznmO+I3f+cyiR9Mai7Na9C2/21UJL/9APt7unjQhyQtCF++pwUXxhJX42tId SophiaSSH5"

# Private SSH Key (multiline)
gh secret set LAMBDA_PRIVATE_SSH_KEY --body "-----BEGIN RSA PRIVATE KEY-----
MIIEogIBAAKCAQEAsctiuxhwWHR6Vw2MCEKFQTo0fDd0cDE4G2S7AexGvQZvTyqy
Vl/bBqVE8k3ToTO1VzVynbX4UIv4jmtZ+f85uAkCfkW9xIhfrdMGLVIoMs7UN0rS
iuFdyUD7pf41RDGah35+FfpxQWq+gL0ac9LCFwhE66YyeB2MzG6hrabsKVAAK7Tv
GSYH2ApULQdSowZP0niIshBEy9Sq3px1Vylyon7RsY3UWwEgcrEpQens4s3aJDMe
o/du4cUhbtMJf3RqcDrva9aL3ub0n1Xq5o57lju7umtqlfsJXP776Vyg2oobviaf
LeLg3ZkRHNFgkUz6nWXSZkEyeeM0nSaKIbBoawIDAQABAoIBABvsIbbZeTdjH52R
Wpcnf08FqZ2Chg5ipHmk4bvFFDz2iD+qKHTpO/g4t3HIaD6uZMHr+nKrU/KucNxJ
Hsnk2/c7rwEOyeVWN5SQii1O9FI6ali+rv8xsq17P6pLmKj7k1XJN1sTSHsqHP4R
9NgQ1vuQCGbr5Iw5s9WdYFXp27gG/cwCPcRmtbDwxWypNqBJXCuzryTcj12mXWxx
KXyR1D2i64kYJvfX4XpdO2fHqCwy9OQe6XXCgfO8EmY16GEBA9OYFz7TWD05g/ag
e4C3PhO/OJ8wdd6EUA8/DS8ycN8iAxrqJJ4O8ZRKhPWVTIWG++2b9AJlc+vy+lCo
4PbAWKECgYEA4SZhKQnDAHzt6xuHkVZCxcFGDQPtEhdPc3B23SIFgRtCCss4h5NC
20WoxjsULv+CWG6rlTxNojUS3dKwS/xZs7RZRVleV6Rd3nWikuRDTZTDXQBsxRfr
mgrfdnRKhCkqBfvxEsiRz/dewUL4owkZYyr3B8T6NRDXuCNeWKHHlgsCgYEAyifp
VmQ9aCS3PrZTVo9CwCz7vh0NHjrZ1LQpJzGWld/BKzwmqZeOe3EKlNI0BaYH43sb
38uTq5A0TnjfD16hqeWhy7oIgAabnKUU894PkMZNt4xjk9iRFKvsJiCZxv4vN5MY
MraJRj61jH/9BtXnLAhqsnH7tJYN2uAzufjB0yECgYAyalipStFKg672zWRO7ATp
qTyZX36vZV7aF53WKG8ZGNRx/E19NkFrPi7rrID5gSdby/RJ54Xuw3mlCC+H5Erl
zYWL3NYeQ+TtEmREBi736U7RvW2duJx+Et809BdXfqw1SNQTg6v66IZkOi3YvAne
Rdmo+LeaOFpFlk3jBN7fPwKBgAhMLxWus56Ms0DNtwn8g17j+clJ4/nzrHFAm9fR
/z5TmtgtdeDMKbsDXs3Q+vWoZPZ/XRuIfZ0zJBJ8f5tf5P7WQBfeoO6wVr7NP9jq
qnTkztfT2Vp+LyZMEDtYZzd1w3ZigUHDoErT1BvaPQaEzSJPjiGY8B3vcs4jGbxu
a3ZBAoGARVeKJRgiPHQTxguouBYLSpKr5kuF+sYp0TB3XvOPlMPjKMLIryOajRpd
3ot+NheIx7IOO8nbRBjcdr1CsxvKVrC6K1iEyV1cOwrGo2JednJr5cY92oE3Q3BZ
Si02dEz1jsNZT5IObnR+EZU3x3tUPVwobDfLiVIhf5iOHg48b/w=
-----END RSA PRIVATE KEY-----"

# Docker Hub credentials (if you have them)
echo "🐳 Setting Docker Hub secrets..."
gh secret set DOCKER_HUB_USERNAME --body "scoobyjava15"
# Note: You'll need to set DOCKER_HUB_ACCESS_TOKEN manually

# Lambda Labs Instance Information
echo "📍 Setting Lambda Labs instance information..."
gh secret set LAMBDA_INSTANCE_IPS --body "104.171.202.103,192.222.58.232,104.171.202.117,104.171.202.134,155.248.194.183"
gh secret set LAMBDA_INSTANCE_NAMES --body "sophia-production-instance,sophia-ai-core,sophia-mcp-orchestrator,sophia-data-pipeline,sophia-development"

# Pulumi ESC Configuration
echo "☁️ Setting Pulumi ESC configuration..."
gh secret set PULUMI_ORG --body "scoobyjava-org"
gh secret set PULUMI_STACK --body "sophia-ai-production"
# Note: You'll need to set PULUMI_ACCESS_TOKEN manually

echo "✅ GitHub secrets setup complete!"
echo ""
echo "⚠️  Manual steps required:"
echo "1. Set DOCKER_HUB_ACCESS_TOKEN secret"
echo "2. Set PULUMI_ACCESS_TOKEN secret"
echo ""
echo "To verify secrets, run:"
echo "gh secret list"
