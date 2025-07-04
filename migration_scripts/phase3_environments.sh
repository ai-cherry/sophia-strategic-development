#!/bin/bash
# Phase 3: Staging and Development Secrets
set -e

echo '🔐 Starting secret migration...'

# Migrate ANTHROPIC_API_KEY -> SOPHIA_ANTHROPIC_API_KEY_STG
if gh secret list --org ai-cherry | grep -q 'ANTHROPIC_API_KEY'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="ANTHROPIC_API_KEY") | .value')
  gh secret set SOPHIA_ANTHROPIC_API_KEY_STG --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated ANTHROPIC_API_KEY -> SOPHIA_ANTHROPIC_API_KEY_STG'
else
  echo '⚠️  ANTHROPIC_API_KEY not found'
fi

# Migrate ANTHROPIC_API_KEY -> SOPHIA_ANTHROPIC_API_KEY_DEV
if gh secret list --org ai-cherry | grep -q 'ANTHROPIC_API_KEY'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="ANTHROPIC_API_KEY") | .value')
  gh secret set SOPHIA_ANTHROPIC_API_KEY_DEV --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated ANTHROPIC_API_KEY -> SOPHIA_ANTHROPIC_API_KEY_DEV'
else
  echo '⚠️  ANTHROPIC_API_KEY not found'
fi

# Migrate DOCKER_TOKEN -> SOPHIA_DOCKER_TOKEN_STG
if gh secret list --org ai-cherry | grep -q 'DOCKER_TOKEN'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="DOCKER_TOKEN") | .value')
  gh secret set SOPHIA_DOCKER_TOKEN_STG --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated DOCKER_TOKEN -> SOPHIA_DOCKER_TOKEN_STG'
else
  echo '⚠️  DOCKER_TOKEN not found'
fi

# Migrate DOCKER_TOKEN -> SOPHIA_DOCKER_TOKEN_DEV
if gh secret list --org ai-cherry | grep -q 'DOCKER_TOKEN'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="DOCKER_TOKEN") | .value')
  gh secret set SOPHIA_DOCKER_TOKEN_DEV --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated DOCKER_TOKEN -> SOPHIA_DOCKER_TOKEN_DEV'
else
  echo '⚠️  DOCKER_TOKEN not found'
fi

# Migrate DOCKER_USERNAME -> SOPHIA_DOCKER_TOKEN_STG
if gh secret list --org ai-cherry | grep -q 'DOCKER_USERNAME'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="DOCKER_USERNAME") | .value')
  gh secret set SOPHIA_DOCKER_TOKEN_STG --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated DOCKER_USERNAME -> SOPHIA_DOCKER_TOKEN_STG'
else
  echo '⚠️  DOCKER_USERNAME not found'
fi

# Migrate DOCKER_USERNAME -> SOPHIA_DOCKER_TOKEN_DEV
if gh secret list --org ai-cherry | grep -q 'DOCKER_USERNAME'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="DOCKER_USERNAME") | .value')
  gh secret set SOPHIA_DOCKER_TOKEN_DEV --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated DOCKER_USERNAME -> SOPHIA_DOCKER_TOKEN_DEV'
else
  echo '⚠️  DOCKER_USERNAME not found'
fi

# Migrate GITHUB_ACTOR -> SOPHIA_GITHUB_TOKEN_STG
if gh secret list --org ai-cherry | grep -q 'GITHUB_ACTOR'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="GITHUB_ACTOR") | .value')
  gh secret set SOPHIA_GITHUB_TOKEN_STG --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated GITHUB_ACTOR -> SOPHIA_GITHUB_TOKEN_STG'
else
  echo '⚠️  GITHUB_ACTOR not found'
fi

# Migrate GITHUB_ACTOR -> SOPHIA_GITHUB_TOKEN_DEV
if gh secret list --org ai-cherry | grep -q 'GITHUB_ACTOR'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="GITHUB_ACTOR") | .value')
  gh secret set SOPHIA_GITHUB_TOKEN_DEV --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated GITHUB_ACTOR -> SOPHIA_GITHUB_TOKEN_DEV'
else
  echo '⚠️  GITHUB_ACTOR not found'
fi

# Migrate GITHUB_JOB -> SOPHIA_GITHUB_TOKEN_STG
if gh secret list --org ai-cherry | grep -q 'GITHUB_JOB'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="GITHUB_JOB") | .value')
  gh secret set SOPHIA_GITHUB_TOKEN_STG --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated GITHUB_JOB -> SOPHIA_GITHUB_TOKEN_STG'
else
  echo '⚠️  GITHUB_JOB not found'
fi

# Migrate GITHUB_JOB -> SOPHIA_GITHUB_TOKEN_DEV
if gh secret list --org ai-cherry | grep -q 'GITHUB_JOB'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="GITHUB_JOB") | .value')
  gh secret set SOPHIA_GITHUB_TOKEN_DEV --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated GITHUB_JOB -> SOPHIA_GITHUB_TOKEN_DEV'
else
  echo '⚠️  GITHUB_JOB not found'
fi

# Migrate GITHUB_PAT -> SOPHIA_GITHUB_PASSWORD_STG
if gh secret list --org ai-cherry | grep -q 'GITHUB_PAT'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="GITHUB_PAT") | .value')
  gh secret set SOPHIA_GITHUB_PASSWORD_STG --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated GITHUB_PAT -> SOPHIA_GITHUB_PASSWORD_STG'
else
  echo '⚠️  GITHUB_PAT not found'
fi

# Migrate GITHUB_PAT -> SOPHIA_GITHUB_PASSWORD_DEV
if gh secret list --org ai-cherry | grep -q 'GITHUB_PAT'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="GITHUB_PAT") | .value')
  gh secret set SOPHIA_GITHUB_PASSWORD_DEV --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated GITHUB_PAT -> SOPHIA_GITHUB_PASSWORD_DEV'
else
  echo '⚠️  GITHUB_PAT not found'
fi

# Migrate GITHUB_REF -> SOPHIA_GITHUB_TOKEN_STG
if gh secret list --org ai-cherry | grep -q 'GITHUB_REF'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="GITHUB_REF") | .value')
  gh secret set SOPHIA_GITHUB_TOKEN_STG --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated GITHUB_REF -> SOPHIA_GITHUB_TOKEN_STG'
else
  echo '⚠️  GITHUB_REF not found'
fi

# Migrate GITHUB_REF -> SOPHIA_GITHUB_TOKEN_DEV
if gh secret list --org ai-cherry | grep -q 'GITHUB_REF'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="GITHUB_REF") | .value')
  gh secret set SOPHIA_GITHUB_TOKEN_DEV --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated GITHUB_REF -> SOPHIA_GITHUB_TOKEN_DEV'
else
  echo '⚠️  GITHUB_REF not found'
fi

# Migrate GITHUB_SHA -> SOPHIA_GITHUB_TOKEN_STG
if gh secret list --org ai-cherry | grep -q 'GITHUB_SHA'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="GITHUB_SHA") | .value')
  gh secret set SOPHIA_GITHUB_TOKEN_STG --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated GITHUB_SHA -> SOPHIA_GITHUB_TOKEN_STG'
else
  echo '⚠️  GITHUB_SHA not found'
fi

# Migrate GITHUB_SHA -> SOPHIA_GITHUB_TOKEN_DEV
if gh secret list --org ai-cherry | grep -q 'GITHUB_SHA'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="GITHUB_SHA") | .value')
  gh secret set SOPHIA_GITHUB_TOKEN_DEV --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated GITHUB_SHA -> SOPHIA_GITHUB_TOKEN_DEV'
else
  echo '⚠️  GITHUB_SHA not found'
fi

# Migrate GITHUB_TOKEN -> SOPHIA_GITHUB_TOKEN_STG
if gh secret list --org ai-cherry | grep -q 'GITHUB_TOKEN'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="GITHUB_TOKEN") | .value')
  gh secret set SOPHIA_GITHUB_TOKEN_STG --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated GITHUB_TOKEN -> SOPHIA_GITHUB_TOKEN_STG'
else
  echo '⚠️  GITHUB_TOKEN not found'
fi

# Migrate GITHUB_TOKEN -> SOPHIA_GITHUB_TOKEN_DEV
if gh secret list --org ai-cherry | grep -q 'GITHUB_TOKEN'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="GITHUB_TOKEN") | .value')
  gh secret set SOPHIA_GITHUB_TOKEN_DEV --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated GITHUB_TOKEN -> SOPHIA_GITHUB_TOKEN_DEV'
else
  echo '⚠️  GITHUB_TOKEN not found'
fi

# Migrate GITHUB_WORKFLOW -> SOPHIA_GITHUB_TOKEN_STG
if gh secret list --org ai-cherry | grep -q 'GITHUB_WORKFLOW'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="GITHUB_WORKFLOW") | .value')
  gh secret set SOPHIA_GITHUB_TOKEN_STG --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated GITHUB_WORKFLOW -> SOPHIA_GITHUB_TOKEN_STG'
else
  echo '⚠️  GITHUB_WORKFLOW not found'
fi

# Migrate GITHUB_WORKFLOW -> SOPHIA_GITHUB_TOKEN_DEV
if gh secret list --org ai-cherry | grep -q 'GITHUB_WORKFLOW'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="GITHUB_WORKFLOW") | .value')
  gh secret set SOPHIA_GITHUB_TOKEN_DEV --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated GITHUB_WORKFLOW -> SOPHIA_GITHUB_TOKEN_DEV'
else
  echo '⚠️  GITHUB_WORKFLOW not found'
fi

# Migrate GONG_ACCESS_KEY -> SOPHIA_GONG_API_KEY_STG
if gh secret list --org ai-cherry | grep -q 'GONG_ACCESS_KEY'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="GONG_ACCESS_KEY") | .value')
  gh secret set SOPHIA_GONG_API_KEY_STG --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated GONG_ACCESS_KEY -> SOPHIA_GONG_API_KEY_STG'
else
  echo '⚠️  GONG_ACCESS_KEY not found'
fi

# Migrate GONG_ACCESS_KEY -> SOPHIA_GONG_API_KEY_DEV
if gh secret list --org ai-cherry | grep -q 'GONG_ACCESS_KEY'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="GONG_ACCESS_KEY") | .value')
  gh secret set SOPHIA_GONG_API_KEY_DEV --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated GONG_ACCESS_KEY -> SOPHIA_GONG_API_KEY_DEV'
else
  echo '⚠️  GONG_ACCESS_KEY not found'
fi

# Migrate GONG_ACCESS_KEY_SECRET -> SOPHIA_GONG_CLIENT_SECRET_STG
if gh secret list --org ai-cherry | grep -q 'GONG_ACCESS_KEY_SECRET'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="GONG_ACCESS_KEY_SECRET") | .value')
  gh secret set SOPHIA_GONG_CLIENT_SECRET_STG --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated GONG_ACCESS_KEY_SECRET -> SOPHIA_GONG_CLIENT_SECRET_STG'
else
  echo '⚠️  GONG_ACCESS_KEY_SECRET not found'
fi

# Migrate GONG_ACCESS_KEY_SECRET -> SOPHIA_GONG_CLIENT_SECRET_DEV
if gh secret list --org ai-cherry | grep -q 'GONG_ACCESS_KEY_SECRET'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="GONG_ACCESS_KEY_SECRET") | .value')
  gh secret set SOPHIA_GONG_CLIENT_SECRET_DEV --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated GONG_ACCESS_KEY_SECRET -> SOPHIA_GONG_CLIENT_SECRET_DEV'
else
  echo '⚠️  GONG_ACCESS_KEY_SECRET not found'
fi

# Migrate GONG_API_KEY -> SOPHIA_GONG_API_KEY_STG
if gh secret list --org ai-cherry | grep -q 'GONG_API_KEY'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="GONG_API_KEY") | .value')
  gh secret set SOPHIA_GONG_API_KEY_STG --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated GONG_API_KEY -> SOPHIA_GONG_API_KEY_STG'
else
  echo '⚠️  GONG_API_KEY not found'
fi

# Migrate GONG_API_KEY -> SOPHIA_GONG_API_KEY_DEV
if gh secret list --org ai-cherry | grep -q 'GONG_API_KEY'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="GONG_API_KEY") | .value')
  gh secret set SOPHIA_GONG_API_KEY_DEV --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated GONG_API_KEY -> SOPHIA_GONG_API_KEY_DEV'
else
  echo '⚠️  GONG_API_KEY not found'
fi

# Migrate GONG_API_SECRET -> SOPHIA_GONG_CLIENT_SECRET_STG
if gh secret list --org ai-cherry | grep -q 'GONG_API_SECRET'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="GONG_API_SECRET") | .value')
  gh secret set SOPHIA_GONG_CLIENT_SECRET_STG --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated GONG_API_SECRET -> SOPHIA_GONG_CLIENT_SECRET_STG'
else
  echo '⚠️  GONG_API_SECRET not found'
fi

# Migrate GONG_API_SECRET -> SOPHIA_GONG_CLIENT_SECRET_DEV
if gh secret list --org ai-cherry | grep -q 'GONG_API_SECRET'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="GONG_API_SECRET") | .value')
  gh secret set SOPHIA_GONG_CLIENT_SECRET_DEV --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated GONG_API_SECRET -> SOPHIA_GONG_CLIENT_SECRET_DEV'
else
  echo '⚠️  GONG_API_SECRET not found'
fi

# Migrate GONG_BASE_URL -> SOPHIA_GONG_API_KEY_STG
if gh secret list --org ai-cherry | grep -q 'GONG_BASE_URL'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="GONG_BASE_URL") | .value')
  gh secret set SOPHIA_GONG_API_KEY_STG --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated GONG_BASE_URL -> SOPHIA_GONG_API_KEY_STG'
else
  echo '⚠️  GONG_BASE_URL not found'
fi

# Migrate GONG_BASE_URL -> SOPHIA_GONG_API_KEY_DEV
if gh secret list --org ai-cherry | grep -q 'GONG_BASE_URL'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="GONG_BASE_URL") | .value')
  gh secret set SOPHIA_GONG_API_KEY_DEV --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated GONG_BASE_URL -> SOPHIA_GONG_API_KEY_DEV'
else
  echo '⚠️  GONG_BASE_URL not found'
fi

# Migrate GONG_CLIENT_ID -> SOPHIA_GONG_API_KEY_STG
if gh secret list --org ai-cherry | grep -q 'GONG_CLIENT_ID'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="GONG_CLIENT_ID") | .value')
  gh secret set SOPHIA_GONG_API_KEY_STG --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated GONG_CLIENT_ID -> SOPHIA_GONG_API_KEY_STG'
else
  echo '⚠️  GONG_CLIENT_ID not found'
fi

# Migrate GONG_CLIENT_ID -> SOPHIA_GONG_API_KEY_DEV
if gh secret list --org ai-cherry | grep -q 'GONG_CLIENT_ID'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="GONG_CLIENT_ID") | .value')
  gh secret set SOPHIA_GONG_API_KEY_DEV --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated GONG_CLIENT_ID -> SOPHIA_GONG_API_KEY_DEV'
else
  echo '⚠️  GONG_CLIENT_ID not found'
fi

# Migrate GONG_CLIENT_SECRET -> SOPHIA_GONG_CLIENT_SECRET_STG
if gh secret list --org ai-cherry | grep -q 'GONG_CLIENT_SECRET'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="GONG_CLIENT_SECRET") | .value')
  gh secret set SOPHIA_GONG_CLIENT_SECRET_STG --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated GONG_CLIENT_SECRET -> SOPHIA_GONG_CLIENT_SECRET_STG'
else
  echo '⚠️  GONG_CLIENT_SECRET not found'
fi

# Migrate GONG_CLIENT_SECRET -> SOPHIA_GONG_CLIENT_SECRET_DEV
if gh secret list --org ai-cherry | grep -q 'GONG_CLIENT_SECRET'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="GONG_CLIENT_SECRET") | .value')
  gh secret set SOPHIA_GONG_CLIENT_SECRET_DEV --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated GONG_CLIENT_SECRET -> SOPHIA_GONG_CLIENT_SECRET_DEV'
else
  echo '⚠️  GONG_CLIENT_SECRET not found'
fi

# Migrate HUBSPOT_ACCESS_TOKEN -> SOPHIA_HUBSPOT_TOKEN_STG
if gh secret list --org ai-cherry | grep -q 'HUBSPOT_ACCESS_TOKEN'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="HUBSPOT_ACCESS_TOKEN") | .value')
  gh secret set SOPHIA_HUBSPOT_TOKEN_STG --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated HUBSPOT_ACCESS_TOKEN -> SOPHIA_HUBSPOT_TOKEN_STG'
else
  echo '⚠️  HUBSPOT_ACCESS_TOKEN not found'
fi

# Migrate HUBSPOT_ACCESS_TOKEN -> SOPHIA_HUBSPOT_TOKEN_DEV
if gh secret list --org ai-cherry | grep -q 'HUBSPOT_ACCESS_TOKEN'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="HUBSPOT_ACCESS_TOKEN") | .value')
  gh secret set SOPHIA_HUBSPOT_TOKEN_DEV --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated HUBSPOT_ACCESS_TOKEN -> SOPHIA_HUBSPOT_TOKEN_DEV'
else
  echo '⚠️  HUBSPOT_ACCESS_TOKEN not found'
fi

# Migrate HUBSPOT_API_KEY -> SOPHIA_HUBSPOT_API_KEY_STG
if gh secret list --org ai-cherry | grep -q 'HUBSPOT_API_KEY'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="HUBSPOT_API_KEY") | .value')
  gh secret set SOPHIA_HUBSPOT_API_KEY_STG --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated HUBSPOT_API_KEY -> SOPHIA_HUBSPOT_API_KEY_STG'
else
  echo '⚠️  HUBSPOT_API_KEY not found'
fi

# Migrate HUBSPOT_API_KEY -> SOPHIA_HUBSPOT_API_KEY_DEV
if gh secret list --org ai-cherry | grep -q 'HUBSPOT_API_KEY'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="HUBSPOT_API_KEY") | .value')
  gh secret set SOPHIA_HUBSPOT_API_KEY_DEV --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated HUBSPOT_API_KEY -> SOPHIA_HUBSPOT_API_KEY_DEV'
else
  echo '⚠️  HUBSPOT_API_KEY not found'
fi

# Migrate HUBSPOT_API_TOKEN -> SOPHIA_HUBSPOT_TOKEN_STG
if gh secret list --org ai-cherry | grep -q 'HUBSPOT_API_TOKEN'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="HUBSPOT_API_TOKEN") | .value')
  gh secret set SOPHIA_HUBSPOT_TOKEN_STG --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated HUBSPOT_API_TOKEN -> SOPHIA_HUBSPOT_TOKEN_STG'
else
  echo '⚠️  HUBSPOT_API_TOKEN not found'
fi

# Migrate HUBSPOT_API_TOKEN -> SOPHIA_HUBSPOT_TOKEN_DEV
if gh secret list --org ai-cherry | grep -q 'HUBSPOT_API_TOKEN'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="HUBSPOT_API_TOKEN") | .value')
  gh secret set SOPHIA_HUBSPOT_TOKEN_DEV --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated HUBSPOT_API_TOKEN -> SOPHIA_HUBSPOT_TOKEN_DEV'
else
  echo '⚠️  HUBSPOT_API_TOKEN not found'
fi

# Migrate LAMBDA_API_KEY -> SOPHIA_LAMBDA_API_KEY_STG
if gh secret list --org ai-cherry | grep -q 'LAMBDA_API_KEY'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="LAMBDA_API_KEY") | .value')
  gh secret set SOPHIA_LAMBDA_API_KEY_STG --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated LAMBDA_API_KEY -> SOPHIA_LAMBDA_API_KEY_STG'
else
  echo '⚠️  LAMBDA_API_KEY not found'
fi

# Migrate LAMBDA_API_KEY -> SOPHIA_LAMBDA_API_KEY_DEV
if gh secret list --org ai-cherry | grep -q 'LAMBDA_API_KEY'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="LAMBDA_API_KEY") | .value')
  gh secret set SOPHIA_LAMBDA_API_KEY_DEV --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated LAMBDA_API_KEY -> SOPHIA_LAMBDA_API_KEY_DEV'
else
  echo '⚠️  LAMBDA_API_KEY not found'
fi

# Migrate LAMBDA_IP_ADDRESS -> SOPHIA_LAMBDA_TOKEN_STG
if gh secret list --org ai-cherry | grep -q 'LAMBDA_IP_ADDRESS'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="LAMBDA_IP_ADDRESS") | .value')
  gh secret set SOPHIA_LAMBDA_TOKEN_STG --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated LAMBDA_IP_ADDRESS -> SOPHIA_LAMBDA_TOKEN_STG'
else
  echo '⚠️  LAMBDA_IP_ADDRESS not found'
fi

# Migrate LAMBDA_IP_ADDRESS -> SOPHIA_LAMBDA_TOKEN_DEV
if gh secret list --org ai-cherry | grep -q 'LAMBDA_IP_ADDRESS'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="LAMBDA_IP_ADDRESS") | .value')
  gh secret set SOPHIA_LAMBDA_TOKEN_DEV --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated LAMBDA_IP_ADDRESS -> SOPHIA_LAMBDA_TOKEN_DEV'
else
  echo '⚠️  LAMBDA_IP_ADDRESS not found'
fi

# Migrate LAMBDA_LABS_API_KEY -> SOPHIA_LAMBDA_API_KEY_STG
if gh secret list --org ai-cherry | grep -q 'LAMBDA_LABS_API_KEY'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="LAMBDA_LABS_API_KEY") | .value')
  gh secret set SOPHIA_LAMBDA_API_KEY_STG --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated LAMBDA_LABS_API_KEY -> SOPHIA_LAMBDA_API_KEY_STG'
else
  echo '⚠️  LAMBDA_LABS_API_KEY not found'
fi

# Migrate LAMBDA_LABS_API_KEY -> SOPHIA_LAMBDA_API_KEY_DEV
if gh secret list --org ai-cherry | grep -q 'LAMBDA_LABS_API_KEY'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="LAMBDA_LABS_API_KEY") | .value')
  gh secret set SOPHIA_LAMBDA_API_KEY_DEV --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated LAMBDA_LABS_API_KEY -> SOPHIA_LAMBDA_API_KEY_DEV'
else
  echo '⚠️  LAMBDA_LABS_API_KEY not found'
fi

# Migrate LINEAR_API_KEY -> SOPHIA_LINEAR_API_KEY_STG
if gh secret list --org ai-cherry | grep -q 'LINEAR_API_KEY'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="LINEAR_API_KEY") | .value')
  gh secret set SOPHIA_LINEAR_API_KEY_STG --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated LINEAR_API_KEY -> SOPHIA_LINEAR_API_KEY_STG'
else
  echo '⚠️  LINEAR_API_KEY not found'
fi

# Migrate LINEAR_API_KEY -> SOPHIA_LINEAR_API_KEY_DEV
if gh secret list --org ai-cherry | grep -q 'LINEAR_API_KEY'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="LINEAR_API_KEY") | .value')
  gh secret set SOPHIA_LINEAR_API_KEY_DEV --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated LINEAR_API_KEY -> SOPHIA_LINEAR_API_KEY_DEV'
else
  echo '⚠️  LINEAR_API_KEY not found'
fi

# Migrate LLAMAINDEX_OPENAI_API_KEY -> SOPHIA_OPENAI_API_KEY_STG
if gh secret list --org ai-cherry | grep -q 'LLAMAINDEX_OPENAI_API_KEY'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="LLAMAINDEX_OPENAI_API_KEY") | .value')
  gh secret set SOPHIA_OPENAI_API_KEY_STG --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated LLAMAINDEX_OPENAI_API_KEY -> SOPHIA_OPENAI_API_KEY_STG'
else
  echo '⚠️  LLAMAINDEX_OPENAI_API_KEY not found'
fi

# Migrate LLAMAINDEX_OPENAI_API_KEY -> SOPHIA_OPENAI_API_KEY_DEV
if gh secret list --org ai-cherry | grep -q 'LLAMAINDEX_OPENAI_API_KEY'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="LLAMAINDEX_OPENAI_API_KEY") | .value')
  gh secret set SOPHIA_OPENAI_API_KEY_DEV --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated LLAMAINDEX_OPENAI_API_KEY -> SOPHIA_OPENAI_API_KEY_DEV'
else
  echo '⚠️  LLAMAINDEX_OPENAI_API_KEY not found'
fi

# Migrate LLAMAINDEX_PINECONE_API_KEY -> SOPHIA_PINECONE_API_KEY_STG
if gh secret list --org ai-cherry | grep -q 'LLAMAINDEX_PINECONE_API_KEY'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="LLAMAINDEX_PINECONE_API_KEY") | .value')
  gh secret set SOPHIA_PINECONE_API_KEY_STG --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated LLAMAINDEX_PINECONE_API_KEY -> SOPHIA_PINECONE_API_KEY_STG'
else
  echo '⚠️  LLAMAINDEX_PINECONE_API_KEY not found'
fi

# Migrate LLAMAINDEX_PINECONE_API_KEY -> SOPHIA_PINECONE_API_KEY_DEV
if gh secret list --org ai-cherry | grep -q 'LLAMAINDEX_PINECONE_API_KEY'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="LLAMAINDEX_PINECONE_API_KEY") | .value')
  gh secret set SOPHIA_PINECONE_API_KEY_DEV --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated LLAMAINDEX_PINECONE_API_KEY -> SOPHIA_PINECONE_API_KEY_DEV'
else
  echo '⚠️  LLAMAINDEX_PINECONE_API_KEY not found'
fi

# Migrate LLAMAINDEX_WEAVIATE_API_KEY -> SOPHIA_WEAVIATE_API_KEY_STG
if gh secret list --org ai-cherry | grep -q 'LLAMAINDEX_WEAVIATE_API_KEY'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="LLAMAINDEX_WEAVIATE_API_KEY") | .value')
  gh secret set SOPHIA_WEAVIATE_API_KEY_STG --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated LLAMAINDEX_WEAVIATE_API_KEY -> SOPHIA_WEAVIATE_API_KEY_STG'
else
  echo '⚠️  LLAMAINDEX_WEAVIATE_API_KEY not found'
fi

# Migrate LLAMAINDEX_WEAVIATE_API_KEY -> SOPHIA_WEAVIATE_API_KEY_DEV
if gh secret list --org ai-cherry | grep -q 'LLAMAINDEX_WEAVIATE_API_KEY'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="LLAMAINDEX_WEAVIATE_API_KEY") | .value')
  gh secret set SOPHIA_WEAVIATE_API_KEY_DEV --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated LLAMAINDEX_WEAVIATE_API_KEY -> SOPHIA_WEAVIATE_API_KEY_DEV'
else
  echo '⚠️  LLAMAINDEX_WEAVIATE_API_KEY not found'
fi

# Migrate NAMECHEAP_API_KEY -> SOPHIA_NAMECHEAP_API_KEY_STG
if gh secret list --org ai-cherry | grep -q 'NAMECHEAP_API_KEY'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="NAMECHEAP_API_KEY") | .value')
  gh secret set SOPHIA_NAMECHEAP_API_KEY_STG --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated NAMECHEAP_API_KEY -> SOPHIA_NAMECHEAP_API_KEY_STG'
else
  echo '⚠️  NAMECHEAP_API_KEY not found'
fi

# Migrate NAMECHEAP_API_KEY -> SOPHIA_NAMECHEAP_API_KEY_DEV
if gh secret list --org ai-cherry | grep -q 'NAMECHEAP_API_KEY'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="NAMECHEAP_API_KEY") | .value')
  gh secret set SOPHIA_NAMECHEAP_API_KEY_DEV --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated NAMECHEAP_API_KEY -> SOPHIA_NAMECHEAP_API_KEY_DEV'
else
  echo '⚠️  NAMECHEAP_API_KEY not found'
fi

# Migrate NAMECHEAP_API_USER -> SOPHIA_NAMECHEAP_TOKEN_STG
if gh secret list --org ai-cherry | grep -q 'NAMECHEAP_API_USER'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="NAMECHEAP_API_USER") | .value')
  gh secret set SOPHIA_NAMECHEAP_TOKEN_STG --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated NAMECHEAP_API_USER -> SOPHIA_NAMECHEAP_TOKEN_STG'
else
  echo '⚠️  NAMECHEAP_API_USER not found'
fi

# Migrate NAMECHEAP_API_USER -> SOPHIA_NAMECHEAP_TOKEN_DEV
if gh secret list --org ai-cherry | grep -q 'NAMECHEAP_API_USER'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="NAMECHEAP_API_USER") | .value')
  gh secret set SOPHIA_NAMECHEAP_TOKEN_DEV --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated NAMECHEAP_API_USER -> SOPHIA_NAMECHEAP_TOKEN_DEV'
else
  echo '⚠️  NAMECHEAP_API_USER not found'
fi

# Migrate NAMECHEAP_USERNAME -> SOPHIA_NAMECHEAP_TOKEN_STG
if gh secret list --org ai-cherry | grep -q 'NAMECHEAP_USERNAME'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="NAMECHEAP_USERNAME") | .value')
  gh secret set SOPHIA_NAMECHEAP_TOKEN_STG --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated NAMECHEAP_USERNAME -> SOPHIA_NAMECHEAP_TOKEN_STG'
else
  echo '⚠️  NAMECHEAP_USERNAME not found'
fi

# Migrate NAMECHEAP_USERNAME -> SOPHIA_NAMECHEAP_TOKEN_DEV
if gh secret list --org ai-cherry | grep -q 'NAMECHEAP_USERNAME'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="NAMECHEAP_USERNAME") | .value')
  gh secret set SOPHIA_NAMECHEAP_TOKEN_DEV --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated NAMECHEAP_USERNAME -> SOPHIA_NAMECHEAP_TOKEN_DEV'
else
  echo '⚠️  NAMECHEAP_USERNAME not found'
fi

# Migrate OPENAI_API_KEY -> SOPHIA_OPENAI_API_KEY_STG
if gh secret list --org ai-cherry | grep -q 'OPENAI_API_KEY'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="OPENAI_API_KEY") | .value')
  gh secret set SOPHIA_OPENAI_API_KEY_STG --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated OPENAI_API_KEY -> SOPHIA_OPENAI_API_KEY_STG'
else
  echo '⚠️  OPENAI_API_KEY not found'
fi

# Migrate OPENAI_API_KEY -> SOPHIA_OPENAI_API_KEY_DEV
if gh secret list --org ai-cherry | grep -q 'OPENAI_API_KEY'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="OPENAI_API_KEY") | .value')
  gh secret set SOPHIA_OPENAI_API_KEY_DEV --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated OPENAI_API_KEY -> SOPHIA_OPENAI_API_KEY_DEV'
else
  echo '⚠️  OPENAI_API_KEY not found'
fi

# Migrate PINECONE_API_KEY -> SOPHIA_PINECONE_API_KEY_STG
if gh secret list --org ai-cherry | grep -q 'PINECONE_API_KEY'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="PINECONE_API_KEY") | .value')
  gh secret set SOPHIA_PINECONE_API_KEY_STG --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated PINECONE_API_KEY -> SOPHIA_PINECONE_API_KEY_STG'
else
  echo '⚠️  PINECONE_API_KEY not found'
fi

# Migrate PINECONE_API_KEY -> SOPHIA_PINECONE_API_KEY_DEV
if gh secret list --org ai-cherry | grep -q 'PINECONE_API_KEY'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="PINECONE_API_KEY") | .value')
  gh secret set SOPHIA_PINECONE_API_KEY_DEV --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated PINECONE_API_KEY -> SOPHIA_PINECONE_API_KEY_DEV'
else
  echo '⚠️  PINECONE_API_KEY not found'
fi

# Migrate PINECONE_ENVIRONMENT -> SOPHIA_PINECONE_PASSWORD_STG
if gh secret list --org ai-cherry | grep -q 'PINECONE_ENVIRONMENT'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="PINECONE_ENVIRONMENT") | .value')
  gh secret set SOPHIA_PINECONE_PASSWORD_STG --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated PINECONE_ENVIRONMENT -> SOPHIA_PINECONE_PASSWORD_STG'
else
  echo '⚠️  PINECONE_ENVIRONMENT not found'
fi

# Migrate PINECONE_ENVIRONMENT -> SOPHIA_PINECONE_PASSWORD_DEV
if gh secret list --org ai-cherry | grep -q 'PINECONE_ENVIRONMENT'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="PINECONE_ENVIRONMENT") | .value')
  gh secret set SOPHIA_PINECONE_PASSWORD_DEV --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated PINECONE_ENVIRONMENT -> SOPHIA_PINECONE_PASSWORD_DEV'
else
  echo '⚠️  PINECONE_ENVIRONMENT not found'
fi

# Migrate PINECONE_INDEX_NAME -> SOPHIA_PINECONE_PASSWORD_STG
if gh secret list --org ai-cherry | grep -q 'PINECONE_INDEX_NAME'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="PINECONE_INDEX_NAME") | .value')
  gh secret set SOPHIA_PINECONE_PASSWORD_STG --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated PINECONE_INDEX_NAME -> SOPHIA_PINECONE_PASSWORD_STG'
else
  echo '⚠️  PINECONE_INDEX_NAME not found'
fi

# Migrate PINECONE_INDEX_NAME -> SOPHIA_PINECONE_PASSWORD_DEV
if gh secret list --org ai-cherry | grep -q 'PINECONE_INDEX_NAME'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="PINECONE_INDEX_NAME") | .value')
  gh secret set SOPHIA_PINECONE_PASSWORD_DEV --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated PINECONE_INDEX_NAME -> SOPHIA_PINECONE_PASSWORD_DEV'
else
  echo '⚠️  PINECONE_INDEX_NAME not found'
fi

# Migrate PORTKEY_API_KEY -> SOPHIA_PORTKEY_API_KEY_STG
if gh secret list --org ai-cherry | grep -q 'PORTKEY_API_KEY'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="PORTKEY_API_KEY") | .value')
  gh secret set SOPHIA_PORTKEY_API_KEY_STG --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated PORTKEY_API_KEY -> SOPHIA_PORTKEY_API_KEY_STG'
else
  echo '⚠️  PORTKEY_API_KEY not found'
fi

# Migrate PORTKEY_API_KEY -> SOPHIA_PORTKEY_API_KEY_DEV
if gh secret list --org ai-cherry | grep -q 'PORTKEY_API_KEY'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="PORTKEY_API_KEY") | .value')
  gh secret set SOPHIA_PORTKEY_API_KEY_DEV --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated PORTKEY_API_KEY -> SOPHIA_PORTKEY_API_KEY_DEV'
else
  echo '⚠️  PORTKEY_API_KEY not found'
fi

# Migrate PULUMI_ACCESS_TOKEN -> SOPHIA_PULUMI_TOKEN_STG
if gh secret list --org ai-cherry | grep -q 'PULUMI_ACCESS_TOKEN'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="PULUMI_ACCESS_TOKEN") | .value')
  gh secret set SOPHIA_PULUMI_TOKEN_STG --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated PULUMI_ACCESS_TOKEN -> SOPHIA_PULUMI_TOKEN_STG'
else
  echo '⚠️  PULUMI_ACCESS_TOKEN not found'
fi

# Migrate PULUMI_ACCESS_TOKEN -> SOPHIA_PULUMI_TOKEN_DEV
if gh secret list --org ai-cherry | grep -q 'PULUMI_ACCESS_TOKEN'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="PULUMI_ACCESS_TOKEN") | .value')
  gh secret set SOPHIA_PULUMI_TOKEN_DEV --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated PULUMI_ACCESS_TOKEN -> SOPHIA_PULUMI_TOKEN_DEV'
else
  echo '⚠️  PULUMI_ACCESS_TOKEN not found'
fi

# Migrate PULUMI_BACKEND_URL_DEV -> SOPHIA_PULUMI_TOKEN_STG
if gh secret list --org ai-cherry | grep -q 'PULUMI_BACKEND_URL_DEV'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="PULUMI_BACKEND_URL_DEV") | .value')
  gh secret set SOPHIA_PULUMI_TOKEN_STG --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated PULUMI_BACKEND_URL_DEV -> SOPHIA_PULUMI_TOKEN_STG'
else
  echo '⚠️  PULUMI_BACKEND_URL_DEV not found'
fi

# Migrate PULUMI_BACKEND_URL_DEV -> SOPHIA_PULUMI_TOKEN_DEV
if gh secret list --org ai-cherry | grep -q 'PULUMI_BACKEND_URL_DEV'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="PULUMI_BACKEND_URL_DEV") | .value')
  gh secret set SOPHIA_PULUMI_TOKEN_DEV --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated PULUMI_BACKEND_URL_DEV -> SOPHIA_PULUMI_TOKEN_DEV'
else
  echo '⚠️  PULUMI_BACKEND_URL_DEV not found'
fi

# Migrate PULUMI_BACKEND_URL_PROD -> SOPHIA_PULUMI_TOKEN_STG
if gh secret list --org ai-cherry | grep -q 'PULUMI_BACKEND_URL_PROD'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="PULUMI_BACKEND_URL_PROD") | .value')
  gh secret set SOPHIA_PULUMI_TOKEN_STG --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated PULUMI_BACKEND_URL_PROD -> SOPHIA_PULUMI_TOKEN_STG'
else
  echo '⚠️  PULUMI_BACKEND_URL_PROD not found'
fi

# Migrate PULUMI_BACKEND_URL_PROD -> SOPHIA_PULUMI_TOKEN_DEV
if gh secret list --org ai-cherry | grep -q 'PULUMI_BACKEND_URL_PROD'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="PULUMI_BACKEND_URL_PROD") | .value')
  gh secret set SOPHIA_PULUMI_TOKEN_DEV --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated PULUMI_BACKEND_URL_PROD -> SOPHIA_PULUMI_TOKEN_DEV'
else
  echo '⚠️  PULUMI_BACKEND_URL_PROD not found'
fi

# Migrate PULUMI_BACKEND_URL_STAGING -> SOPHIA_PULUMI_TOKEN_STG
if gh secret list --org ai-cherry | grep -q 'PULUMI_BACKEND_URL_STAGING'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="PULUMI_BACKEND_URL_STAGING") | .value')
  gh secret set SOPHIA_PULUMI_TOKEN_STG --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated PULUMI_BACKEND_URL_STAGING -> SOPHIA_PULUMI_TOKEN_STG'
else
  echo '⚠️  PULUMI_BACKEND_URL_STAGING not found'
fi

# Migrate PULUMI_BACKEND_URL_STAGING -> SOPHIA_PULUMI_TOKEN_DEV
if gh secret list --org ai-cherry | grep -q 'PULUMI_BACKEND_URL_STAGING'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="PULUMI_BACKEND_URL_STAGING") | .value')
  gh secret set SOPHIA_PULUMI_TOKEN_DEV --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated PULUMI_BACKEND_URL_STAGING -> SOPHIA_PULUMI_TOKEN_DEV'
else
  echo '⚠️  PULUMI_BACKEND_URL_STAGING not found'
fi

# Migrate PULUMI_CONFIG_PASSPHRASE -> SOPHIA_PULUMI_TOKEN_STG
if gh secret list --org ai-cherry | grep -q 'PULUMI_CONFIG_PASSPHRASE'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="PULUMI_CONFIG_PASSPHRASE") | .value')
  gh secret set SOPHIA_PULUMI_TOKEN_STG --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated PULUMI_CONFIG_PASSPHRASE -> SOPHIA_PULUMI_TOKEN_STG'
else
  echo '⚠️  PULUMI_CONFIG_PASSPHRASE not found'
fi

# Migrate PULUMI_CONFIG_PASSPHRASE -> SOPHIA_PULUMI_TOKEN_DEV
if gh secret list --org ai-cherry | grep -q 'PULUMI_CONFIG_PASSPHRASE'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="PULUMI_CONFIG_PASSPHRASE") | .value')
  gh secret set SOPHIA_PULUMI_TOKEN_DEV --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated PULUMI_CONFIG_PASSPHRASE -> SOPHIA_PULUMI_TOKEN_DEV'
else
  echo '⚠️  PULUMI_CONFIG_PASSPHRASE not found'
fi

# Migrate PULUMI_IP_ADDRESS -> SOPHIA_PULUMI_TOKEN_STG
if gh secret list --org ai-cherry | grep -q 'PULUMI_IP_ADDRESS'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="PULUMI_IP_ADDRESS") | .value')
  gh secret set SOPHIA_PULUMI_TOKEN_STG --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated PULUMI_IP_ADDRESS -> SOPHIA_PULUMI_TOKEN_STG'
else
  echo '⚠️  PULUMI_IP_ADDRESS not found'
fi

# Migrate PULUMI_IP_ADDRESS -> SOPHIA_PULUMI_TOKEN_DEV
if gh secret list --org ai-cherry | grep -q 'PULUMI_IP_ADDRESS'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="PULUMI_IP_ADDRESS") | .value')
  gh secret set SOPHIA_PULUMI_TOKEN_DEV --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated PULUMI_IP_ADDRESS -> SOPHIA_PULUMI_TOKEN_DEV'
else
  echo '⚠️  PULUMI_IP_ADDRESS not found'
fi

# Migrate PULUMI_ORG -> SOPHIA_PULUMI_TOKEN_STG
if gh secret list --org ai-cherry | grep -q 'PULUMI_ORG'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="PULUMI_ORG") | .value')
  gh secret set SOPHIA_PULUMI_TOKEN_STG --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated PULUMI_ORG -> SOPHIA_PULUMI_TOKEN_STG'
else
  echo '⚠️  PULUMI_ORG not found'
fi

# Migrate PULUMI_ORG -> SOPHIA_PULUMI_TOKEN_DEV
if gh secret list --org ai-cherry | grep -q 'PULUMI_ORG'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="PULUMI_ORG") | .value')
  gh secret set SOPHIA_PULUMI_TOKEN_DEV --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated PULUMI_ORG -> SOPHIA_PULUMI_TOKEN_DEV'
else
  echo '⚠️  PULUMI_ORG not found'
fi

# Migrate PULUMI_STACK -> SOPHIA_PULUMI_TOKEN_STG
if gh secret list --org ai-cherry | grep -q 'PULUMI_STACK'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="PULUMI_STACK") | .value')
  gh secret set SOPHIA_PULUMI_TOKEN_STG --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated PULUMI_STACK -> SOPHIA_PULUMI_TOKEN_STG'
else
  echo '⚠️  PULUMI_STACK not found'
fi

# Migrate PULUMI_STACK -> SOPHIA_PULUMI_TOKEN_DEV
if gh secret list --org ai-cherry | grep -q 'PULUMI_STACK'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="PULUMI_STACK") | .value')
  gh secret set SOPHIA_PULUMI_TOKEN_DEV --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated PULUMI_STACK -> SOPHIA_PULUMI_TOKEN_DEV'
else
  echo '⚠️  PULUMI_STACK not found'
fi

# Migrate SLACK_APP_TOKEN -> SOPHIA_SLACK_TOKEN_STG
if gh secret list --org ai-cherry | grep -q 'SLACK_APP_TOKEN'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="SLACK_APP_TOKEN") | .value')
  gh secret set SOPHIA_SLACK_TOKEN_STG --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated SLACK_APP_TOKEN -> SOPHIA_SLACK_TOKEN_STG'
else
  echo '⚠️  SLACK_APP_TOKEN not found'
fi

# Migrate SLACK_APP_TOKEN -> SOPHIA_SLACK_TOKEN_DEV
if gh secret list --org ai-cherry | grep -q 'SLACK_APP_TOKEN'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="SLACK_APP_TOKEN") | .value')
  gh secret set SOPHIA_SLACK_TOKEN_DEV --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated SLACK_APP_TOKEN -> SOPHIA_SLACK_TOKEN_DEV'
else
  echo '⚠️  SLACK_APP_TOKEN not found'
fi

# Migrate SLACK_BOT_TOKEN -> SOPHIA_SLACK_TOKEN_STG
if gh secret list --org ai-cherry | grep -q 'SLACK_BOT_TOKEN'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="SLACK_BOT_TOKEN") | .value')
  gh secret set SOPHIA_SLACK_TOKEN_STG --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated SLACK_BOT_TOKEN -> SOPHIA_SLACK_TOKEN_STG'
else
  echo '⚠️  SLACK_BOT_TOKEN not found'
fi

# Migrate SLACK_BOT_TOKEN -> SOPHIA_SLACK_TOKEN_DEV
if gh secret list --org ai-cherry | grep -q 'SLACK_BOT_TOKEN'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="SLACK_BOT_TOKEN") | .value')
  gh secret set SOPHIA_SLACK_TOKEN_DEV --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated SLACK_BOT_TOKEN -> SOPHIA_SLACK_TOKEN_DEV'
else
  echo '⚠️  SLACK_BOT_TOKEN not found'
fi

# Migrate SLACK_CLIENT_ID -> SOPHIA_SLACK_BOT_TOKEN_STG
if gh secret list --org ai-cherry | grep -q 'SLACK_CLIENT_ID'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="SLACK_CLIENT_ID") | .value')
  gh secret set SOPHIA_SLACK_BOT_TOKEN_STG --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated SLACK_CLIENT_ID -> SOPHIA_SLACK_BOT_TOKEN_STG'
else
  echo '⚠️  SLACK_CLIENT_ID not found'
fi

# Migrate SLACK_CLIENT_ID -> SOPHIA_SLACK_BOT_TOKEN_DEV
if gh secret list --org ai-cherry | grep -q 'SLACK_CLIENT_ID'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="SLACK_CLIENT_ID") | .value')
  gh secret set SOPHIA_SLACK_BOT_TOKEN_DEV --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated SLACK_CLIENT_ID -> SOPHIA_SLACK_BOT_TOKEN_DEV'
else
  echo '⚠️  SLACK_CLIENT_ID not found'
fi

# Migrate SLACK_CLIENT_SECRET -> SOPHIA_SLACK_CLIENT_SECRET_STG
if gh secret list --org ai-cherry | grep -q 'SLACK_CLIENT_SECRET'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="SLACK_CLIENT_SECRET") | .value')
  gh secret set SOPHIA_SLACK_CLIENT_SECRET_STG --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated SLACK_CLIENT_SECRET -> SOPHIA_SLACK_CLIENT_SECRET_STG'
else
  echo '⚠️  SLACK_CLIENT_SECRET not found'
fi

# Migrate SLACK_CLIENT_SECRET -> SOPHIA_SLACK_CLIENT_SECRET_DEV
if gh secret list --org ai-cherry | grep -q 'SLACK_CLIENT_SECRET'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="SLACK_CLIENT_SECRET") | .value')
  gh secret set SOPHIA_SLACK_CLIENT_SECRET_DEV --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated SLACK_CLIENT_SECRET -> SOPHIA_SLACK_CLIENT_SECRET_DEV'
else
  echo '⚠️  SLACK_CLIENT_SECRET not found'
fi

# Migrate SLACK_SIGNING_SECRET -> SOPHIA_SLACK_CLIENT_SECRET_STG
if gh secret list --org ai-cherry | grep -q 'SLACK_SIGNING_SECRET'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="SLACK_SIGNING_SECRET") | .value')
  gh secret set SOPHIA_SLACK_CLIENT_SECRET_STG --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated SLACK_SIGNING_SECRET -> SOPHIA_SLACK_CLIENT_SECRET_STG'
else
  echo '⚠️  SLACK_SIGNING_SECRET not found'
fi

# Migrate SLACK_SIGNING_SECRET -> SOPHIA_SLACK_CLIENT_SECRET_DEV
if gh secret list --org ai-cherry | grep -q 'SLACK_SIGNING_SECRET'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="SLACK_SIGNING_SECRET") | .value')
  gh secret set SOPHIA_SLACK_CLIENT_SECRET_DEV --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated SLACK_SIGNING_SECRET -> SOPHIA_SLACK_CLIENT_SECRET_DEV'
else
  echo '⚠️  SLACK_SIGNING_SECRET not found'
fi

# Migrate SLACK_WEBHOOK -> SOPHIA_SLACK_BOT_TOKEN_STG
if gh secret list --org ai-cherry | grep -q 'SLACK_WEBHOOK'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="SLACK_WEBHOOK") | .value')
  gh secret set SOPHIA_SLACK_BOT_TOKEN_STG --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated SLACK_WEBHOOK -> SOPHIA_SLACK_BOT_TOKEN_STG'
else
  echo '⚠️  SLACK_WEBHOOK not found'
fi

# Migrate SLACK_WEBHOOK -> SOPHIA_SLACK_BOT_TOKEN_DEV
if gh secret list --org ai-cherry | grep -q 'SLACK_WEBHOOK'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="SLACK_WEBHOOK") | .value')
  gh secret set SOPHIA_SLACK_BOT_TOKEN_DEV --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated SLACK_WEBHOOK -> SOPHIA_SLACK_BOT_TOKEN_DEV'
else
  echo '⚠️  SLACK_WEBHOOK not found'
fi

# Migrate SLACK_WEBHOOK_URL -> SOPHIA_SLACK_BOT_TOKEN_STG
if gh secret list --org ai-cherry | grep -q 'SLACK_WEBHOOK_URL'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="SLACK_WEBHOOK_URL") | .value')
  gh secret set SOPHIA_SLACK_BOT_TOKEN_STG --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated SLACK_WEBHOOK_URL -> SOPHIA_SLACK_BOT_TOKEN_STG'
else
  echo '⚠️  SLACK_WEBHOOK_URL not found'
fi

# Migrate SLACK_WEBHOOK_URL -> SOPHIA_SLACK_BOT_TOKEN_DEV
if gh secret list --org ai-cherry | grep -q 'SLACK_WEBHOOK_URL'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="SLACK_WEBHOOK_URL") | .value')
  gh secret set SOPHIA_SLACK_BOT_TOKEN_DEV --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated SLACK_WEBHOOK_URL -> SOPHIA_SLACK_BOT_TOKEN_DEV'
else
  echo '⚠️  SLACK_WEBHOOK_URL not found'
fi

# Migrate SNOWFLAKE_ACCOUNT -> SOPHIA_SNOWFLAKE_PASSWORD_STG
if gh secret list --org ai-cherry | grep -q 'SNOWFLAKE_ACCOUNT'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="SNOWFLAKE_ACCOUNT") | .value')
  gh secret set SOPHIA_SNOWFLAKE_PASSWORD_STG --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated SNOWFLAKE_ACCOUNT -> SOPHIA_SNOWFLAKE_PASSWORD_STG'
else
  echo '⚠️  SNOWFLAKE_ACCOUNT not found'
fi

# Migrate SNOWFLAKE_ACCOUNT -> SOPHIA_SNOWFLAKE_PASSWORD_DEV
if gh secret list --org ai-cherry | grep -q 'SNOWFLAKE_ACCOUNT'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="SNOWFLAKE_ACCOUNT") | .value')
  gh secret set SOPHIA_SNOWFLAKE_PASSWORD_DEV --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated SNOWFLAKE_ACCOUNT -> SOPHIA_SNOWFLAKE_PASSWORD_DEV'
else
  echo '⚠️  SNOWFLAKE_ACCOUNT not found'
fi

# Migrate SNOWFLAKE_DATABASE -> SOPHIA_SNOWFLAKE_PASSWORD_STG
if gh secret list --org ai-cherry | grep -q 'SNOWFLAKE_DATABASE'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="SNOWFLAKE_DATABASE") | .value')
  gh secret set SOPHIA_SNOWFLAKE_PASSWORD_STG --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated SNOWFLAKE_DATABASE -> SOPHIA_SNOWFLAKE_PASSWORD_STG'
else
  echo '⚠️  SNOWFLAKE_DATABASE not found'
fi

# Migrate SNOWFLAKE_DATABASE -> SOPHIA_SNOWFLAKE_PASSWORD_DEV
if gh secret list --org ai-cherry | grep -q 'SNOWFLAKE_DATABASE'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="SNOWFLAKE_DATABASE") | .value')
  gh secret set SOPHIA_SNOWFLAKE_PASSWORD_DEV --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated SNOWFLAKE_DATABASE -> SOPHIA_SNOWFLAKE_PASSWORD_DEV'
else
  echo '⚠️  SNOWFLAKE_DATABASE not found'
fi

# Migrate SNOWFLAKE_PASSWORD -> SOPHIA_SNOWFLAKE_PASSWORD_STG
if gh secret list --org ai-cherry | grep -q 'SNOWFLAKE_PASSWORD'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="SNOWFLAKE_PASSWORD") | .value')
  gh secret set SOPHIA_SNOWFLAKE_PASSWORD_STG --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated SNOWFLAKE_PASSWORD -> SOPHIA_SNOWFLAKE_PASSWORD_STG'
else
  echo '⚠️  SNOWFLAKE_PASSWORD not found'
fi

# Migrate SNOWFLAKE_PASSWORD -> SOPHIA_SNOWFLAKE_PASSWORD_DEV
if gh secret list --org ai-cherry | grep -q 'SNOWFLAKE_PASSWORD'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="SNOWFLAKE_PASSWORD") | .value')
  gh secret set SOPHIA_SNOWFLAKE_PASSWORD_DEV --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated SNOWFLAKE_PASSWORD -> SOPHIA_SNOWFLAKE_PASSWORD_DEV'
else
  echo '⚠️  SNOWFLAKE_PASSWORD not found'
fi

# Migrate SNOWFLAKE_PAT -> SOPHIA_SNOWFLAKE_PASSWORD_STG
if gh secret list --org ai-cherry | grep -q 'SNOWFLAKE_PAT'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="SNOWFLAKE_PAT") | .value')
  gh secret set SOPHIA_SNOWFLAKE_PASSWORD_STG --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated SNOWFLAKE_PAT -> SOPHIA_SNOWFLAKE_PASSWORD_STG'
else
  echo '⚠️  SNOWFLAKE_PAT not found'
fi

# Migrate SNOWFLAKE_PAT -> SOPHIA_SNOWFLAKE_PASSWORD_DEV
if gh secret list --org ai-cherry | grep -q 'SNOWFLAKE_PAT'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="SNOWFLAKE_PAT") | .value')
  gh secret set SOPHIA_SNOWFLAKE_PASSWORD_DEV --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated SNOWFLAKE_PAT -> SOPHIA_SNOWFLAKE_PASSWORD_DEV'
else
  echo '⚠️  SNOWFLAKE_PAT not found'
fi

# Migrate SNOWFLAKE_ROLE -> SOPHIA_SNOWFLAKE_PASSWORD_STG
if gh secret list --org ai-cherry | grep -q 'SNOWFLAKE_ROLE'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="SNOWFLAKE_ROLE") | .value')
  gh secret set SOPHIA_SNOWFLAKE_PASSWORD_STG --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated SNOWFLAKE_ROLE -> SOPHIA_SNOWFLAKE_PASSWORD_STG'
else
  echo '⚠️  SNOWFLAKE_ROLE not found'
fi

# Migrate SNOWFLAKE_ROLE -> SOPHIA_SNOWFLAKE_PASSWORD_DEV
if gh secret list --org ai-cherry | grep -q 'SNOWFLAKE_ROLE'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="SNOWFLAKE_ROLE") | .value')
  gh secret set SOPHIA_SNOWFLAKE_PASSWORD_DEV --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated SNOWFLAKE_ROLE -> SOPHIA_SNOWFLAKE_PASSWORD_DEV'
else
  echo '⚠️  SNOWFLAKE_ROLE not found'
fi

# Migrate SNOWFLAKE_SCHEMA -> SOPHIA_SNOWFLAKE_PASSWORD_STG
if gh secret list --org ai-cherry | grep -q 'SNOWFLAKE_SCHEMA'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="SNOWFLAKE_SCHEMA") | .value')
  gh secret set SOPHIA_SNOWFLAKE_PASSWORD_STG --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated SNOWFLAKE_SCHEMA -> SOPHIA_SNOWFLAKE_PASSWORD_STG'
else
  echo '⚠️  SNOWFLAKE_SCHEMA not found'
fi

# Migrate SNOWFLAKE_SCHEMA -> SOPHIA_SNOWFLAKE_PASSWORD_DEV
if gh secret list --org ai-cherry | grep -q 'SNOWFLAKE_SCHEMA'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="SNOWFLAKE_SCHEMA") | .value')
  gh secret set SOPHIA_SNOWFLAKE_PASSWORD_DEV --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated SNOWFLAKE_SCHEMA -> SOPHIA_SNOWFLAKE_PASSWORD_DEV'
else
  echo '⚠️  SNOWFLAKE_SCHEMA not found'
fi

# Migrate SNOWFLAKE_USER -> SOPHIA_SNOWFLAKE_PASSWORD_STG
if gh secret list --org ai-cherry | grep -q 'SNOWFLAKE_USER'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="SNOWFLAKE_USER") | .value')
  gh secret set SOPHIA_SNOWFLAKE_PASSWORD_STG --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated SNOWFLAKE_USER -> SOPHIA_SNOWFLAKE_PASSWORD_STG'
else
  echo '⚠️  SNOWFLAKE_USER not found'
fi

# Migrate SNOWFLAKE_USER -> SOPHIA_SNOWFLAKE_PASSWORD_DEV
if gh secret list --org ai-cherry | grep -q 'SNOWFLAKE_USER'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="SNOWFLAKE_USER") | .value')
  gh secret set SOPHIA_SNOWFLAKE_PASSWORD_DEV --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated SNOWFLAKE_USER -> SOPHIA_SNOWFLAKE_PASSWORD_DEV'
else
  echo '⚠️  SNOWFLAKE_USER not found'
fi

# Migrate SNOWFLAKE_WAREHOUSE -> SOPHIA_SNOWFLAKE_PASSWORD_STG
if gh secret list --org ai-cherry | grep -q 'SNOWFLAKE_WAREHOUSE'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="SNOWFLAKE_WAREHOUSE") | .value')
  gh secret set SOPHIA_SNOWFLAKE_PASSWORD_STG --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated SNOWFLAKE_WAREHOUSE -> SOPHIA_SNOWFLAKE_PASSWORD_STG'
else
  echo '⚠️  SNOWFLAKE_WAREHOUSE not found'
fi

# Migrate SNOWFLAKE_WAREHOUSE -> SOPHIA_SNOWFLAKE_PASSWORD_DEV
if gh secret list --org ai-cherry | grep -q 'SNOWFLAKE_WAREHOUSE'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="SNOWFLAKE_WAREHOUSE") | .value')
  gh secret set SOPHIA_SNOWFLAKE_PASSWORD_DEV --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated SNOWFLAKE_WAREHOUSE -> SOPHIA_SNOWFLAKE_PASSWORD_DEV'
else
  echo '⚠️  SNOWFLAKE_WAREHOUSE not found'
fi

# Migrate VERCEL_ACCESS_TOKEN -> SOPHIA_VERCEL_TOKEN_STG
if gh secret list --org ai-cherry | grep -q 'VERCEL_ACCESS_TOKEN'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="VERCEL_ACCESS_TOKEN") | .value')
  gh secret set SOPHIA_VERCEL_TOKEN_STG --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated VERCEL_ACCESS_TOKEN -> SOPHIA_VERCEL_TOKEN_STG'
else
  echo '⚠️  VERCEL_ACCESS_TOKEN not found'
fi

# Migrate VERCEL_ACCESS_TOKEN -> SOPHIA_VERCEL_TOKEN_DEV
if gh secret list --org ai-cherry | grep -q 'VERCEL_ACCESS_TOKEN'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="VERCEL_ACCESS_TOKEN") | .value')
  gh secret set SOPHIA_VERCEL_TOKEN_DEV --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated VERCEL_ACCESS_TOKEN -> SOPHIA_VERCEL_TOKEN_DEV'
else
  echo '⚠️  VERCEL_ACCESS_TOKEN not found'
fi

# Migrate VERCEL_API_TOKEN -> SOPHIA_VERCEL_TOKEN_STG
if gh secret list --org ai-cherry | grep -q 'VERCEL_API_TOKEN'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="VERCEL_API_TOKEN") | .value')
  gh secret set SOPHIA_VERCEL_TOKEN_STG --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated VERCEL_API_TOKEN -> SOPHIA_VERCEL_TOKEN_STG'
else
  echo '⚠️  VERCEL_API_TOKEN not found'
fi

# Migrate VERCEL_API_TOKEN -> SOPHIA_VERCEL_TOKEN_DEV
if gh secret list --org ai-cherry | grep -q 'VERCEL_API_TOKEN'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="VERCEL_API_TOKEN") | .value')
  gh secret set SOPHIA_VERCEL_TOKEN_DEV --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated VERCEL_API_TOKEN -> SOPHIA_VERCEL_TOKEN_DEV'
else
  echo '⚠️  VERCEL_API_TOKEN not found'
fi

# Migrate VERCEL_ORG_ID -> SOPHIA_VERCEL_TOKEN_STG
if gh secret list --org ai-cherry | grep -q 'VERCEL_ORG_ID'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="VERCEL_ORG_ID") | .value')
  gh secret set SOPHIA_VERCEL_TOKEN_STG --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated VERCEL_ORG_ID -> SOPHIA_VERCEL_TOKEN_STG'
else
  echo '⚠️  VERCEL_ORG_ID not found'
fi

# Migrate VERCEL_ORG_ID -> SOPHIA_VERCEL_TOKEN_DEV
if gh secret list --org ai-cherry | grep -q 'VERCEL_ORG_ID'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="VERCEL_ORG_ID") | .value')
  gh secret set SOPHIA_VERCEL_TOKEN_DEV --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated VERCEL_ORG_ID -> SOPHIA_VERCEL_TOKEN_DEV'
else
  echo '⚠️  VERCEL_ORG_ID not found'
fi

# Migrate VERCEL_PROJECT_ID -> SOPHIA_VERCEL_TOKEN_STG
if gh secret list --org ai-cherry | grep -q 'VERCEL_PROJECT_ID'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="VERCEL_PROJECT_ID") | .value')
  gh secret set SOPHIA_VERCEL_TOKEN_STG --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated VERCEL_PROJECT_ID -> SOPHIA_VERCEL_TOKEN_STG'
else
  echo '⚠️  VERCEL_PROJECT_ID not found'
fi

# Migrate VERCEL_PROJECT_ID -> SOPHIA_VERCEL_TOKEN_DEV
if gh secret list --org ai-cherry | grep -q 'VERCEL_PROJECT_ID'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="VERCEL_PROJECT_ID") | .value')
  gh secret set SOPHIA_VERCEL_TOKEN_DEV --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated VERCEL_PROJECT_ID -> SOPHIA_VERCEL_TOKEN_DEV'
else
  echo '⚠️  VERCEL_PROJECT_ID not found'
fi

# Migrate VERCEL_PROJECT_ID_SOPHIA_PROD -> SOPHIA_VERCEL_TOKEN_STG
if gh secret list --org ai-cherry | grep -q 'VERCEL_PROJECT_ID_SOPHIA_PROD'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="VERCEL_PROJECT_ID_SOPHIA_PROD") | .value')
  gh secret set SOPHIA_VERCEL_TOKEN_STG --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated VERCEL_PROJECT_ID_SOPHIA_PROD -> SOPHIA_VERCEL_TOKEN_STG'
else
  echo '⚠️  VERCEL_PROJECT_ID_SOPHIA_PROD not found'
fi

# Migrate VERCEL_PROJECT_ID_SOPHIA_PROD -> SOPHIA_VERCEL_TOKEN_DEV
if gh secret list --org ai-cherry | grep -q 'VERCEL_PROJECT_ID_SOPHIA_PROD'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="VERCEL_PROJECT_ID_SOPHIA_PROD") | .value')
  gh secret set SOPHIA_VERCEL_TOKEN_DEV --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated VERCEL_PROJECT_ID_SOPHIA_PROD -> SOPHIA_VERCEL_TOKEN_DEV'
else
  echo '⚠️  VERCEL_PROJECT_ID_SOPHIA_PROD not found'
fi

# Migrate VERCEL_TEAM_ID -> SOPHIA_VERCEL_TOKEN_STG
if gh secret list --org ai-cherry | grep -q 'VERCEL_TEAM_ID'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="VERCEL_TEAM_ID") | .value')
  gh secret set SOPHIA_VERCEL_TOKEN_STG --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated VERCEL_TEAM_ID -> SOPHIA_VERCEL_TOKEN_STG'
else
  echo '⚠️  VERCEL_TEAM_ID not found'
fi

# Migrate VERCEL_TEAM_ID -> SOPHIA_VERCEL_TOKEN_DEV
if gh secret list --org ai-cherry | grep -q 'VERCEL_TEAM_ID'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="VERCEL_TEAM_ID") | .value')
  gh secret set SOPHIA_VERCEL_TOKEN_DEV --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated VERCEL_TEAM_ID -> SOPHIA_VERCEL_TOKEN_DEV'
else
  echo '⚠️  VERCEL_TEAM_ID not found'
fi

# Migrate VERCEL_TOKEN -> SOPHIA_VERCEL_TOKEN_STG
if gh secret list --org ai-cherry | grep -q 'VERCEL_TOKEN'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="VERCEL_TOKEN") | .value')
  gh secret set SOPHIA_VERCEL_TOKEN_STG --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated VERCEL_TOKEN -> SOPHIA_VERCEL_TOKEN_STG'
else
  echo '⚠️  VERCEL_TOKEN not found'
fi

# Migrate VERCEL_TOKEN -> SOPHIA_VERCEL_TOKEN_DEV
if gh secret list --org ai-cherry | grep -q 'VERCEL_TOKEN'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="VERCEL_TOKEN") | .value')
  gh secret set SOPHIA_VERCEL_TOKEN_DEV --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated VERCEL_TOKEN -> SOPHIA_VERCEL_TOKEN_DEV'
else
  echo '⚠️  VERCEL_TOKEN not found'
fi

# Migrate WEAVIATE_API_KEY -> SOPHIA_WEAVIATE_API_KEY_STG
if gh secret list --org ai-cherry | grep -q 'WEAVIATE_API_KEY'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="WEAVIATE_API_KEY") | .value')
  gh secret set SOPHIA_WEAVIATE_API_KEY_STG --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated WEAVIATE_API_KEY -> SOPHIA_WEAVIATE_API_KEY_STG'
else
  echo '⚠️  WEAVIATE_API_KEY not found'
fi

# Migrate WEAVIATE_API_KEY -> SOPHIA_WEAVIATE_API_KEY_DEV
if gh secret list --org ai-cherry | grep -q 'WEAVIATE_API_KEY'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="WEAVIATE_API_KEY") | .value')
  gh secret set SOPHIA_WEAVIATE_API_KEY_DEV --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated WEAVIATE_API_KEY -> SOPHIA_WEAVIATE_API_KEY_DEV'
else
  echo '⚠️  WEAVIATE_API_KEY not found'
fi

# Migrate WEAVIATE_GRPC_ENDPOINT -> SOPHIA_WEAVIATE_PASSWORD_STG
if gh secret list --org ai-cherry | grep -q 'WEAVIATE_GRPC_ENDPOINT'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="WEAVIATE_GRPC_ENDPOINT") | .value')
  gh secret set SOPHIA_WEAVIATE_PASSWORD_STG --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated WEAVIATE_GRPC_ENDPOINT -> SOPHIA_WEAVIATE_PASSWORD_STG'
else
  echo '⚠️  WEAVIATE_GRPC_ENDPOINT not found'
fi

# Migrate WEAVIATE_GRPC_ENDPOINT -> SOPHIA_WEAVIATE_PASSWORD_DEV
if gh secret list --org ai-cherry | grep -q 'WEAVIATE_GRPC_ENDPOINT'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="WEAVIATE_GRPC_ENDPOINT") | .value')
  gh secret set SOPHIA_WEAVIATE_PASSWORD_DEV --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated WEAVIATE_GRPC_ENDPOINT -> SOPHIA_WEAVIATE_PASSWORD_DEV'
else
  echo '⚠️  WEAVIATE_GRPC_ENDPOINT not found'
fi

# Migrate WEAVIATE_REST_ENDPOINT -> SOPHIA_WEAVIATE_PASSWORD_STG
if gh secret list --org ai-cherry | grep -q 'WEAVIATE_REST_ENDPOINT'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="WEAVIATE_REST_ENDPOINT") | .value')
  gh secret set SOPHIA_WEAVIATE_PASSWORD_STG --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated WEAVIATE_REST_ENDPOINT -> SOPHIA_WEAVIATE_PASSWORD_STG'
else
  echo '⚠️  WEAVIATE_REST_ENDPOINT not found'
fi

# Migrate WEAVIATE_REST_ENDPOINT -> SOPHIA_WEAVIATE_PASSWORD_DEV
if gh secret list --org ai-cherry | grep -q 'WEAVIATE_REST_ENDPOINT'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="WEAVIATE_REST_ENDPOINT") | .value')
  gh secret set SOPHIA_WEAVIATE_PASSWORD_DEV --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated WEAVIATE_REST_ENDPOINT -> SOPHIA_WEAVIATE_PASSWORD_DEV'
else
  echo '⚠️  WEAVIATE_REST_ENDPOINT not found'
fi

# Migrate WEAVIATE_URL -> SOPHIA_WEAVIATE_PASSWORD_STG
if gh secret list --org ai-cherry | grep -q 'WEAVIATE_URL'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="WEAVIATE_URL") | .value')
  gh secret set SOPHIA_WEAVIATE_PASSWORD_STG --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated WEAVIATE_URL -> SOPHIA_WEAVIATE_PASSWORD_STG'
else
  echo '⚠️  WEAVIATE_URL not found'
fi

# Migrate WEAVIATE_URL -> SOPHIA_WEAVIATE_PASSWORD_DEV
if gh secret list --org ai-cherry | grep -q 'WEAVIATE_URL'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="WEAVIATE_URL") | .value')
  gh secret set SOPHIA_WEAVIATE_PASSWORD_DEV --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated WEAVIATE_URL -> SOPHIA_WEAVIATE_PASSWORD_DEV'
else
  echo '⚠️  WEAVIATE_URL not found'
fi

# Migrate gong_access_key -> SOPHIA_GONG_API_KEY_STG
if gh secret list --org ai-cherry | grep -q 'gong_access_key'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="gong_access_key") | .value')
  gh secret set SOPHIA_GONG_API_KEY_STG --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated gong_access_key -> SOPHIA_GONG_API_KEY_STG'
else
  echo '⚠️  gong_access_key not found'
fi

# Migrate gong_access_key -> SOPHIA_GONG_API_KEY_DEV
if gh secret list --org ai-cherry | grep -q 'gong_access_key'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="gong_access_key") | .value')
  gh secret set SOPHIA_GONG_API_KEY_DEV --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated gong_access_key -> SOPHIA_GONG_API_KEY_DEV'
else
  echo '⚠️  gong_access_key not found'
fi

# Migrate gong_access_key_secret -> SOPHIA_GONG_CLIENT_SECRET_STG
if gh secret list --org ai-cherry | grep -q 'gong_access_key_secret'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="gong_access_key_secret") | .value')
  gh secret set SOPHIA_GONG_CLIENT_SECRET_STG --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated gong_access_key_secret -> SOPHIA_GONG_CLIENT_SECRET_STG'
else
  echo '⚠️  gong_access_key_secret not found'
fi

# Migrate gong_access_key_secret -> SOPHIA_GONG_CLIENT_SECRET_DEV
if gh secret list --org ai-cherry | grep -q 'gong_access_key_secret'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="gong_access_key_secret") | .value')
  gh secret set SOPHIA_GONG_CLIENT_SECRET_DEV --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated gong_access_key_secret -> SOPHIA_GONG_CLIENT_SECRET_DEV'
else
  echo '⚠️  gong_access_key_secret not found'
fi

# Migrate openai_api_key -> SOPHIA_OPENAI_API_KEY_STG
if gh secret list --org ai-cherry | grep -q 'openai_api_key'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="openai_api_key") | .value')
  gh secret set SOPHIA_OPENAI_API_KEY_STG --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated openai_api_key -> SOPHIA_OPENAI_API_KEY_STG'
else
  echo '⚠️  openai_api_key not found'
fi

# Migrate openai_api_key -> SOPHIA_OPENAI_API_KEY_DEV
if gh secret list --org ai-cherry | grep -q 'openai_api_key'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="openai_api_key") | .value')
  gh secret set SOPHIA_OPENAI_API_KEY_DEV --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated openai_api_key -> SOPHIA_OPENAI_API_KEY_DEV'
else
  echo '⚠️  openai_api_key not found'
fi

# Migrate slack_webhook_url -> SOPHIA_SLACK_BOT_TOKEN_STG
if gh secret list --org ai-cherry | grep -q 'slack_webhook_url'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="slack_webhook_url") | .value')
  gh secret set SOPHIA_SLACK_BOT_TOKEN_STG --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated slack_webhook_url -> SOPHIA_SLACK_BOT_TOKEN_STG'
else
  echo '⚠️  slack_webhook_url not found'
fi

# Migrate slack_webhook_url -> SOPHIA_SLACK_BOT_TOKEN_DEV
if gh secret list --org ai-cherry | grep -q 'slack_webhook_url'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="slack_webhook_url") | .value')
  gh secret set SOPHIA_SLACK_BOT_TOKEN_DEV --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated slack_webhook_url -> SOPHIA_SLACK_BOT_TOKEN_DEV'
else
  echo '⚠️  slack_webhook_url not found'
fi

# Migrate snowflake_account -> SOPHIA_SNOWFLAKE_PASSWORD_STG
if gh secret list --org ai-cherry | grep -q 'snowflake_account'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="snowflake_account") | .value')
  gh secret set SOPHIA_SNOWFLAKE_PASSWORD_STG --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated snowflake_account -> SOPHIA_SNOWFLAKE_PASSWORD_STG'
else
  echo '⚠️  snowflake_account not found'
fi

# Migrate snowflake_account -> SOPHIA_SNOWFLAKE_PASSWORD_DEV
if gh secret list --org ai-cherry | grep -q 'snowflake_account'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="snowflake_account") | .value')
  gh secret set SOPHIA_SNOWFLAKE_PASSWORD_DEV --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated snowflake_account -> SOPHIA_SNOWFLAKE_PASSWORD_DEV'
else
  echo '⚠️  snowflake_account not found'
fi

# Migrate snowflake_database -> SOPHIA_SNOWFLAKE_PASSWORD_STG
if gh secret list --org ai-cherry | grep -q 'snowflake_database'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="snowflake_database") | .value')
  gh secret set SOPHIA_SNOWFLAKE_PASSWORD_STG --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated snowflake_database -> SOPHIA_SNOWFLAKE_PASSWORD_STG'
else
  echo '⚠️  snowflake_database not found'
fi

# Migrate snowflake_database -> SOPHIA_SNOWFLAKE_PASSWORD_DEV
if gh secret list --org ai-cherry | grep -q 'snowflake_database'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="snowflake_database") | .value')
  gh secret set SOPHIA_SNOWFLAKE_PASSWORD_DEV --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated snowflake_database -> SOPHIA_SNOWFLAKE_PASSWORD_DEV'
else
  echo '⚠️  snowflake_database not found'
fi

# Migrate snowflake_password -> SOPHIA_SNOWFLAKE_PASSWORD_STG
if gh secret list --org ai-cherry | grep -q 'snowflake_password'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="snowflake_password") | .value')
  gh secret set SOPHIA_SNOWFLAKE_PASSWORD_STG --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated snowflake_password -> SOPHIA_SNOWFLAKE_PASSWORD_STG'
else
  echo '⚠️  snowflake_password not found'
fi

# Migrate snowflake_password -> SOPHIA_SNOWFLAKE_PASSWORD_DEV
if gh secret list --org ai-cherry | grep -q 'snowflake_password'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="snowflake_password") | .value')
  gh secret set SOPHIA_SNOWFLAKE_PASSWORD_DEV --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated snowflake_password -> SOPHIA_SNOWFLAKE_PASSWORD_DEV'
else
  echo '⚠️  snowflake_password not found'
fi

# Migrate snowflake_role -> SOPHIA_SNOWFLAKE_PASSWORD_STG
if gh secret list --org ai-cherry | grep -q 'snowflake_role'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="snowflake_role") | .value')
  gh secret set SOPHIA_SNOWFLAKE_PASSWORD_STG --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated snowflake_role -> SOPHIA_SNOWFLAKE_PASSWORD_STG'
else
  echo '⚠️  snowflake_role not found'
fi

# Migrate snowflake_role -> SOPHIA_SNOWFLAKE_PASSWORD_DEV
if gh secret list --org ai-cherry | grep -q 'snowflake_role'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="snowflake_role") | .value')
  gh secret set SOPHIA_SNOWFLAKE_PASSWORD_DEV --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated snowflake_role -> SOPHIA_SNOWFLAKE_PASSWORD_DEV'
else
  echo '⚠️  snowflake_role not found'
fi

# Migrate snowflake_schema -> SOPHIA_SNOWFLAKE_PASSWORD_STG
if gh secret list --org ai-cherry | grep -q 'snowflake_schema'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="snowflake_schema") | .value')
  gh secret set SOPHIA_SNOWFLAKE_PASSWORD_STG --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated snowflake_schema -> SOPHIA_SNOWFLAKE_PASSWORD_STG'
else
  echo '⚠️  snowflake_schema not found'
fi

# Migrate snowflake_schema -> SOPHIA_SNOWFLAKE_PASSWORD_DEV
if gh secret list --org ai-cherry | grep -q 'snowflake_schema'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="snowflake_schema") | .value')
  gh secret set SOPHIA_SNOWFLAKE_PASSWORD_DEV --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated snowflake_schema -> SOPHIA_SNOWFLAKE_PASSWORD_DEV'
else
  echo '⚠️  snowflake_schema not found'
fi

# Migrate snowflake_user -> SOPHIA_SNOWFLAKE_PASSWORD_STG
if gh secret list --org ai-cherry | grep -q 'snowflake_user'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="snowflake_user") | .value')
  gh secret set SOPHIA_SNOWFLAKE_PASSWORD_STG --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated snowflake_user -> SOPHIA_SNOWFLAKE_PASSWORD_STG'
else
  echo '⚠️  snowflake_user not found'
fi

# Migrate snowflake_user -> SOPHIA_SNOWFLAKE_PASSWORD_DEV
if gh secret list --org ai-cherry | grep -q 'snowflake_user'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="snowflake_user") | .value')
  gh secret set SOPHIA_SNOWFLAKE_PASSWORD_DEV --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated snowflake_user -> SOPHIA_SNOWFLAKE_PASSWORD_DEV'
else
  echo '⚠️  snowflake_user not found'
fi

# Migrate snowflake_warehouse -> SOPHIA_SNOWFLAKE_PASSWORD_STG
if gh secret list --org ai-cherry | grep -q 'snowflake_warehouse'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="snowflake_warehouse") | .value')
  gh secret set SOPHIA_SNOWFLAKE_PASSWORD_STG --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated snowflake_warehouse -> SOPHIA_SNOWFLAKE_PASSWORD_STG'
else
  echo '⚠️  snowflake_warehouse not found'
fi

# Migrate snowflake_warehouse -> SOPHIA_SNOWFLAKE_PASSWORD_DEV
if gh secret list --org ai-cherry | grep -q 'snowflake_warehouse'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="snowflake_warehouse") | .value')
  gh secret set SOPHIA_SNOWFLAKE_PASSWORD_DEV --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated snowflake_warehouse -> SOPHIA_SNOWFLAKE_PASSWORD_DEV'
else
  echo '⚠️  snowflake_warehouse not found'
fi

# Update Pulumi ESC environments
echo '📝 Updating Pulumi ESC configurations...'
# Update scoobyjava-org/sophia-ai-stg
pulumi env init scoobyjava-org/sophia-ai-stg --yes || true
echo '{"sophia": {"platform": {"name": "sophia-ai-platform", "version": "v2.0.0", "environment": "stg", "docker": {"token": "${SOPHIA_DOCKER_TOKEN_STG}"}, "github": {"token": "${SOPHIA_GITHUB_TOKEN_STG}", "password": "${SOPHIA_GITHUB_PASSWORD_STG}"}, "pulumi": {"token": "${SOPHIA_PULUMI_TOKEN_STG}"}}, "ai": {"anthropic": {"api_key": "${SOPHIA_ANTHROPIC_API_KEY_STG}"}, "openai": {"api_key": "${SOPHIA_OPENAI_API_KEY_STG}"}, "portkey": {"api_key": "${SOPHIA_PORTKEY_API_KEY_STG}"}}, "integration": {"gong": {"api_key": "${SOPHIA_GONG_API_KEY_STG}", "client_secret": "${SOPHIA_GONG_CLIENT_SECRET_STG}"}, "hubspot": {"token": "${SOPHIA_HUBSPOT_TOKEN_STG}", "api_key": "${SOPHIA_HUBSPOT_API_KEY_STG}"}, "linear": {"api_key": "${SOPHIA_LINEAR_API_KEY_STG}"}}, "infrastructure": {"lambda": {"api_key": "${SOPHIA_LAMBDA_API_KEY_STG}", "token": "${SOPHIA_LAMBDA_TOKEN_STG}"}, "namecheap": {"api_key": "${SOPHIA_NAMECHEAP_API_KEY_STG}", "token": "${SOPHIA_NAMECHEAP_TOKEN_STG}"}, "vercel": {"token": "${SOPHIA_VERCEL_TOKEN_STG}"}}, "data": {"pinecone": {"api_key": "${SOPHIA_PINECONE_API_KEY_STG}", "password": "${SOPHIA_PINECONE_PASSWORD_STG}"}, "weaviate": {"api_key": "${SOPHIA_WEAVIATE_API_KEY_STG}", "password": "${SOPHIA_WEAVIATE_PASSWORD_STG}"}, "snowflake": {"password": "${SOPHIA_SNOWFLAKE_PASSWORD_STG}"}}, "communication": {"slack": {"token": "${SOPHIA_SLACK_TOKEN_STG}", "bot_token": "${SOPHIA_SLACK_BOT_TOKEN_STG}", "client_secret": "${SOPHIA_SLACK_CLIENT_SECRET_STG}"}}}}' | pulumi env set scoobyjava-org/sophia-ai-stg --
echo '✅ Updated scoobyjava-org/sophia-ai-stg'

# Update scoobyjava-org/sophia-ai-dev
pulumi env init scoobyjava-org/sophia-ai-dev --yes || true
echo '{"sophia": {"platform": {"name": "sophia-ai-platform", "version": "v2.0.0", "environment": "dev", "docker": {"token": "${SOPHIA_DOCKER_TOKEN_DEV}"}, "github": {"token": "${SOPHIA_GITHUB_TOKEN_DEV}", "password": "${SOPHIA_GITHUB_PASSWORD_DEV}"}, "pulumi": {"token": "${SOPHIA_PULUMI_TOKEN_DEV}"}}, "ai": {"anthropic": {"api_key": "${SOPHIA_ANTHROPIC_API_KEY_DEV}"}, "openai": {"api_key": "${SOPHIA_OPENAI_API_KEY_DEV}"}, "portkey": {"api_key": "${SOPHIA_PORTKEY_API_KEY_DEV}"}}, "integration": {"gong": {"api_key": "${SOPHIA_GONG_API_KEY_DEV}", "client_secret": "${SOPHIA_GONG_CLIENT_SECRET_DEV}"}, "hubspot": {"token": "${SOPHIA_HUBSPOT_TOKEN_DEV}", "api_key": "${SOPHIA_HUBSPOT_API_KEY_DEV}"}, "linear": {"api_key": "${SOPHIA_LINEAR_API_KEY_DEV}"}}, "infrastructure": {"lambda": {"api_key": "${SOPHIA_LAMBDA_API_KEY_DEV}", "token": "${SOPHIA_LAMBDA_TOKEN_DEV}"}, "namecheap": {"api_key": "${SOPHIA_NAMECHEAP_API_KEY_DEV}", "token": "${SOPHIA_NAMECHEAP_TOKEN_DEV}"}, "vercel": {"token": "${SOPHIA_VERCEL_TOKEN_DEV}"}}, "data": {"pinecone": {"api_key": "${SOPHIA_PINECONE_API_KEY_DEV}", "password": "${SOPHIA_PINECONE_PASSWORD_DEV}"}, "weaviate": {"api_key": "${SOPHIA_WEAVIATE_API_KEY_DEV}", "password": "${SOPHIA_WEAVIATE_PASSWORD_DEV}"}, "snowflake": {"password": "${SOPHIA_SNOWFLAKE_PASSWORD_DEV}"}}, "communication": {"slack": {"token": "${SOPHIA_SLACK_TOKEN_DEV}", "bot_token": "${SOPHIA_SLACK_BOT_TOKEN_DEV}", "client_secret": "${SOPHIA_SLACK_CLIENT_SECRET_DEV}"}}}}' | pulumi env set scoobyjava-org/sophia-ai-dev --
echo '✅ Updated scoobyjava-org/sophia-ai-dev'

echo '🎉 Migration completed successfully!'
