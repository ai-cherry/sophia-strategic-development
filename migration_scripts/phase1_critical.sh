#!/bin/bash
# Phase 1: Critical Production Secrets
set -e

echo '🔐 Starting secret migration...'

# Migrate GONG_ACCESS_KEY -> SOPHIA_GONG_API_KEY_PROD
if gh secret list --org ai-cherry | grep -q 'GONG_ACCESS_KEY'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="GONG_ACCESS_KEY") | .value')
  gh secret set SOPHIA_GONG_API_KEY_PROD --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated GONG_ACCESS_KEY -> SOPHIA_GONG_API_KEY_PROD'
else
  echo '⚠️  GONG_ACCESS_KEY not found'
fi

# Migrate GONG_ACCESS_KEY_SECRET -> SOPHIA_GONG_CLIENT_SECRET_PROD
if gh secret list --org ai-cherry | grep -q 'GONG_ACCESS_KEY_SECRET'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="GONG_ACCESS_KEY_SECRET") | .value')
  gh secret set SOPHIA_GONG_CLIENT_SECRET_PROD --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated GONG_ACCESS_KEY_SECRET -> SOPHIA_GONG_CLIENT_SECRET_PROD'
else
  echo '⚠️  GONG_ACCESS_KEY_SECRET not found'
fi

# Migrate GONG_API_KEY -> SOPHIA_GONG_API_KEY_PROD
if gh secret list --org ai-cherry | grep -q 'GONG_API_KEY'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="GONG_API_KEY") | .value')
  gh secret set SOPHIA_GONG_API_KEY_PROD --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated GONG_API_KEY -> SOPHIA_GONG_API_KEY_PROD'
else
  echo '⚠️  GONG_API_KEY not found'
fi

# Migrate GONG_API_SECRET -> SOPHIA_GONG_CLIENT_SECRET_PROD
if gh secret list --org ai-cherry | grep -q 'GONG_API_SECRET'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="GONG_API_SECRET") | .value')
  gh secret set SOPHIA_GONG_CLIENT_SECRET_PROD --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated GONG_API_SECRET -> SOPHIA_GONG_CLIENT_SECRET_PROD'
else
  echo '⚠️  GONG_API_SECRET not found'
fi

# Migrate GONG_BASE_URL -> SOPHIA_GONG_API_KEY_PROD
if gh secret list --org ai-cherry | grep -q 'GONG_BASE_URL'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="GONG_BASE_URL") | .value')
  gh secret set SOPHIA_GONG_API_KEY_PROD --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated GONG_BASE_URL -> SOPHIA_GONG_API_KEY_PROD'
else
  echo '⚠️  GONG_BASE_URL not found'
fi

# Migrate GONG_CLIENT_ID -> SOPHIA_GONG_API_KEY_PROD
if gh secret list --org ai-cherry | grep -q 'GONG_CLIENT_ID'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="GONG_CLIENT_ID") | .value')
  gh secret set SOPHIA_GONG_API_KEY_PROD --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated GONG_CLIENT_ID -> SOPHIA_GONG_API_KEY_PROD'
else
  echo '⚠️  GONG_CLIENT_ID not found'
fi

# Migrate GONG_CLIENT_SECRET -> SOPHIA_GONG_CLIENT_SECRET_PROD
if gh secret list --org ai-cherry | grep -q 'GONG_CLIENT_SECRET'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="GONG_CLIENT_SECRET") | .value')
  gh secret set SOPHIA_GONG_CLIENT_SECRET_PROD --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated GONG_CLIENT_SECRET -> SOPHIA_GONG_CLIENT_SECRET_PROD'
else
  echo '⚠️  GONG_CLIENT_SECRET not found'
fi

# Migrate LLAMAINDEX_OPENAI_API_KEY -> SOPHIA_OPENAI_API_KEY_PROD
if gh secret list --org ai-cherry | grep -q 'LLAMAINDEX_OPENAI_API_KEY'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="LLAMAINDEX_OPENAI_API_KEY") | .value')
  gh secret set SOPHIA_OPENAI_API_KEY_PROD --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated LLAMAINDEX_OPENAI_API_KEY -> SOPHIA_OPENAI_API_KEY_PROD'
else
  echo '⚠️  LLAMAINDEX_OPENAI_API_KEY not found'
fi

# Migrate OPENAI_API_KEY -> SOPHIA_OPENAI_API_KEY_PROD
if gh secret list --org ai-cherry | grep -q 'OPENAI_API_KEY'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="OPENAI_API_KEY") | .value')
  gh secret set SOPHIA_OPENAI_API_KEY_PROD --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated OPENAI_API_KEY -> SOPHIA_OPENAI_API_KEY_PROD'
else
  echo '⚠️  OPENAI_API_KEY not found'
fi

# Migrate PULUMI_ACCESS_TOKEN -> SOPHIA_PULUMI_TOKEN_PROD
if gh secret list --org ai-cherry | grep -q 'PULUMI_ACCESS_TOKEN'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="PULUMI_ACCESS_TOKEN") | .value')
  gh secret set SOPHIA_PULUMI_TOKEN_PROD --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated PULUMI_ACCESS_TOKEN -> SOPHIA_PULUMI_TOKEN_PROD'
else
  echo '⚠️  PULUMI_ACCESS_TOKEN not found'
fi

# Migrate PULUMI_BACKEND_URL_DEV -> SOPHIA_PULUMI_TOKEN_PROD
if gh secret list --org ai-cherry | grep -q 'PULUMI_BACKEND_URL_DEV'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="PULUMI_BACKEND_URL_DEV") | .value')
  gh secret set SOPHIA_PULUMI_TOKEN_PROD --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated PULUMI_BACKEND_URL_DEV -> SOPHIA_PULUMI_TOKEN_PROD'
else
  echo '⚠️  PULUMI_BACKEND_URL_DEV not found'
fi

# Migrate PULUMI_BACKEND_URL_PROD -> SOPHIA_PULUMI_TOKEN_PROD
if gh secret list --org ai-cherry | grep -q 'PULUMI_BACKEND_URL_PROD'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="PULUMI_BACKEND_URL_PROD") | .value')
  gh secret set SOPHIA_PULUMI_TOKEN_PROD --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated PULUMI_BACKEND_URL_PROD -> SOPHIA_PULUMI_TOKEN_PROD'
else
  echo '⚠️  PULUMI_BACKEND_URL_PROD not found'
fi

# Migrate PULUMI_BACKEND_URL_STAGING -> SOPHIA_PULUMI_TOKEN_PROD
if gh secret list --org ai-cherry | grep -q 'PULUMI_BACKEND_URL_STAGING'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="PULUMI_BACKEND_URL_STAGING") | .value')
  gh secret set SOPHIA_PULUMI_TOKEN_PROD --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated PULUMI_BACKEND_URL_STAGING -> SOPHIA_PULUMI_TOKEN_PROD'
else
  echo '⚠️  PULUMI_BACKEND_URL_STAGING not found'
fi

# Migrate PULUMI_CONFIG_PASSPHRASE -> SOPHIA_PULUMI_TOKEN_PROD
if gh secret list --org ai-cherry | grep -q 'PULUMI_CONFIG_PASSPHRASE'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="PULUMI_CONFIG_PASSPHRASE") | .value')
  gh secret set SOPHIA_PULUMI_TOKEN_PROD --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated PULUMI_CONFIG_PASSPHRASE -> SOPHIA_PULUMI_TOKEN_PROD'
else
  echo '⚠️  PULUMI_CONFIG_PASSPHRASE not found'
fi

# Migrate PULUMI_IP_ADDRESS -> SOPHIA_PULUMI_TOKEN_PROD
if gh secret list --org ai-cherry | grep -q 'PULUMI_IP_ADDRESS'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="PULUMI_IP_ADDRESS") | .value')
  gh secret set SOPHIA_PULUMI_TOKEN_PROD --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated PULUMI_IP_ADDRESS -> SOPHIA_PULUMI_TOKEN_PROD'
else
  echo '⚠️  PULUMI_IP_ADDRESS not found'
fi

# Migrate PULUMI_ORG -> SOPHIA_PULUMI_TOKEN_PROD
if gh secret list --org ai-cherry | grep -q 'PULUMI_ORG'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="PULUMI_ORG") | .value')
  gh secret set SOPHIA_PULUMI_TOKEN_PROD --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated PULUMI_ORG -> SOPHIA_PULUMI_TOKEN_PROD'
else
  echo '⚠️  PULUMI_ORG not found'
fi

# Migrate PULUMI_STACK -> SOPHIA_PULUMI_TOKEN_PROD
if gh secret list --org ai-cherry | grep -q 'PULUMI_STACK'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="PULUMI_STACK") | .value')
  gh secret set SOPHIA_PULUMI_TOKEN_PROD --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated PULUMI_STACK -> SOPHIA_PULUMI_TOKEN_PROD'
else
  echo '⚠️  PULUMI_STACK not found'
fi

# Migrate SNOWFLAKE_ACCOUNT -> SOPHIA_SNOWFLAKE_PASSWORD_PROD
if gh secret list --org ai-cherry | grep -q 'SNOWFLAKE_ACCOUNT'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="SNOWFLAKE_ACCOUNT") | .value')
  gh secret set SOPHIA_SNOWFLAKE_PASSWORD_PROD --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated SNOWFLAKE_ACCOUNT -> SOPHIA_SNOWFLAKE_PASSWORD_PROD'
else
  echo '⚠️  SNOWFLAKE_ACCOUNT not found'
fi

# Migrate SNOWFLAKE_DATABASE -> SOPHIA_SNOWFLAKE_PASSWORD_PROD
if gh secret list --org ai-cherry | grep -q 'SNOWFLAKE_DATABASE'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="SNOWFLAKE_DATABASE") | .value')
  gh secret set SOPHIA_SNOWFLAKE_PASSWORD_PROD --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated SNOWFLAKE_DATABASE -> SOPHIA_SNOWFLAKE_PASSWORD_PROD'
else
  echo '⚠️  SNOWFLAKE_DATABASE not found'
fi

# Migrate SNOWFLAKE_PASSWORD -> SOPHIA_SNOWFLAKE_PASSWORD_PROD
if gh secret list --org ai-cherry | grep -q 'SNOWFLAKE_PASSWORD'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="SNOWFLAKE_PASSWORD") | .value')
  gh secret set SOPHIA_SNOWFLAKE_PASSWORD_PROD --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated SNOWFLAKE_PASSWORD -> SOPHIA_SNOWFLAKE_PASSWORD_PROD'
else
  echo '⚠️  SNOWFLAKE_PASSWORD not found'
fi

# Migrate SNOWFLAKE_PAT -> SOPHIA_SNOWFLAKE_PASSWORD_PROD
if gh secret list --org ai-cherry | grep -q 'SNOWFLAKE_PAT'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="SNOWFLAKE_PAT") | .value')
  gh secret set SOPHIA_SNOWFLAKE_PASSWORD_PROD --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated SNOWFLAKE_PAT -> SOPHIA_SNOWFLAKE_PASSWORD_PROD'
else
  echo '⚠️  SNOWFLAKE_PAT not found'
fi

# Migrate SNOWFLAKE_ROLE -> SOPHIA_SNOWFLAKE_PASSWORD_PROD
if gh secret list --org ai-cherry | grep -q 'SNOWFLAKE_ROLE'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="SNOWFLAKE_ROLE") | .value')
  gh secret set SOPHIA_SNOWFLAKE_PASSWORD_PROD --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated SNOWFLAKE_ROLE -> SOPHIA_SNOWFLAKE_PASSWORD_PROD'
else
  echo '⚠️  SNOWFLAKE_ROLE not found'
fi

# Migrate SNOWFLAKE_SCHEMA -> SOPHIA_SNOWFLAKE_PASSWORD_PROD
if gh secret list --org ai-cherry | grep -q 'SNOWFLAKE_SCHEMA'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="SNOWFLAKE_SCHEMA") | .value')
  gh secret set SOPHIA_SNOWFLAKE_PASSWORD_PROD --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated SNOWFLAKE_SCHEMA -> SOPHIA_SNOWFLAKE_PASSWORD_PROD'
else
  echo '⚠️  SNOWFLAKE_SCHEMA not found'
fi

# Migrate SNOWFLAKE_USER -> SOPHIA_SNOWFLAKE_PASSWORD_PROD
if gh secret list --org ai-cherry | grep -q 'SNOWFLAKE_USER'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="SNOWFLAKE_USER") | .value')
  gh secret set SOPHIA_SNOWFLAKE_PASSWORD_PROD --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated SNOWFLAKE_USER -> SOPHIA_SNOWFLAKE_PASSWORD_PROD'
else
  echo '⚠️  SNOWFLAKE_USER not found'
fi

# Migrate SNOWFLAKE_WAREHOUSE -> SOPHIA_SNOWFLAKE_PASSWORD_PROD
if gh secret list --org ai-cherry | grep -q 'SNOWFLAKE_WAREHOUSE'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="SNOWFLAKE_WAREHOUSE") | .value')
  gh secret set SOPHIA_SNOWFLAKE_PASSWORD_PROD --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated SNOWFLAKE_WAREHOUSE -> SOPHIA_SNOWFLAKE_PASSWORD_PROD'
else
  echo '⚠️  SNOWFLAKE_WAREHOUSE not found'
fi

# Migrate VERCEL_ACCESS_TOKEN -> SOPHIA_VERCEL_TOKEN_PROD
if gh secret list --org ai-cherry | grep -q 'VERCEL_ACCESS_TOKEN'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="VERCEL_ACCESS_TOKEN") | .value')
  gh secret set SOPHIA_VERCEL_TOKEN_PROD --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated VERCEL_ACCESS_TOKEN -> SOPHIA_VERCEL_TOKEN_PROD'
else
  echo '⚠️  VERCEL_ACCESS_TOKEN not found'
fi

# Migrate VERCEL_API_TOKEN -> SOPHIA_VERCEL_TOKEN_PROD
if gh secret list --org ai-cherry | grep -q 'VERCEL_API_TOKEN'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="VERCEL_API_TOKEN") | .value')
  gh secret set SOPHIA_VERCEL_TOKEN_PROD --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated VERCEL_API_TOKEN -> SOPHIA_VERCEL_TOKEN_PROD'
else
  echo '⚠️  VERCEL_API_TOKEN not found'
fi

# Migrate VERCEL_ORG_ID -> SOPHIA_VERCEL_TOKEN_PROD
if gh secret list --org ai-cherry | grep -q 'VERCEL_ORG_ID'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="VERCEL_ORG_ID") | .value')
  gh secret set SOPHIA_VERCEL_TOKEN_PROD --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated VERCEL_ORG_ID -> SOPHIA_VERCEL_TOKEN_PROD'
else
  echo '⚠️  VERCEL_ORG_ID not found'
fi

# Migrate VERCEL_PROJECT_ID -> SOPHIA_VERCEL_TOKEN_PROD
if gh secret list --org ai-cherry | grep -q 'VERCEL_PROJECT_ID'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="VERCEL_PROJECT_ID") | .value')
  gh secret set SOPHIA_VERCEL_TOKEN_PROD --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated VERCEL_PROJECT_ID -> SOPHIA_VERCEL_TOKEN_PROD'
else
  echo '⚠️  VERCEL_PROJECT_ID not found'
fi

# Migrate VERCEL_PROJECT_ID_SOPHIA_PROD -> SOPHIA_VERCEL_TOKEN_PROD
if gh secret list --org ai-cherry | grep -q 'VERCEL_PROJECT_ID_SOPHIA_PROD'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="VERCEL_PROJECT_ID_SOPHIA_PROD") | .value')
  gh secret set SOPHIA_VERCEL_TOKEN_PROD --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated VERCEL_PROJECT_ID_SOPHIA_PROD -> SOPHIA_VERCEL_TOKEN_PROD'
else
  echo '⚠️  VERCEL_PROJECT_ID_SOPHIA_PROD not found'
fi

# Migrate VERCEL_TEAM_ID -> SOPHIA_VERCEL_TOKEN_PROD
if gh secret list --org ai-cherry | grep -q 'VERCEL_TEAM_ID'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="VERCEL_TEAM_ID") | .value')
  gh secret set SOPHIA_VERCEL_TOKEN_PROD --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated VERCEL_TEAM_ID -> SOPHIA_VERCEL_TOKEN_PROD'
else
  echo '⚠️  VERCEL_TEAM_ID not found'
fi

# Migrate VERCEL_TOKEN -> SOPHIA_VERCEL_TOKEN_PROD
if gh secret list --org ai-cherry | grep -q 'VERCEL_TOKEN'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="VERCEL_TOKEN") | .value')
  gh secret set SOPHIA_VERCEL_TOKEN_PROD --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated VERCEL_TOKEN -> SOPHIA_VERCEL_TOKEN_PROD'
else
  echo '⚠️  VERCEL_TOKEN not found'
fi

# Migrate gong_access_key -> SOPHIA_GONG_API_KEY_PROD
if gh secret list --org ai-cherry | grep -q 'gong_access_key'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="gong_access_key") | .value')
  gh secret set SOPHIA_GONG_API_KEY_PROD --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated gong_access_key -> SOPHIA_GONG_API_KEY_PROD'
else
  echo '⚠️  gong_access_key not found'
fi

# Migrate gong_access_key_secret -> SOPHIA_GONG_CLIENT_SECRET_PROD
if gh secret list --org ai-cherry | grep -q 'gong_access_key_secret'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="gong_access_key_secret") | .value')
  gh secret set SOPHIA_GONG_CLIENT_SECRET_PROD --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated gong_access_key_secret -> SOPHIA_GONG_CLIENT_SECRET_PROD'
else
  echo '⚠️  gong_access_key_secret not found'
fi

# Migrate openai_api_key -> SOPHIA_OPENAI_API_KEY_PROD
if gh secret list --org ai-cherry | grep -q 'openai_api_key'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="openai_api_key") | .value')
  gh secret set SOPHIA_OPENAI_API_KEY_PROD --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated openai_api_key -> SOPHIA_OPENAI_API_KEY_PROD'
else
  echo '⚠️  openai_api_key not found'
fi

# Migrate snowflake_account -> SOPHIA_SNOWFLAKE_PASSWORD_PROD
if gh secret list --org ai-cherry | grep -q 'snowflake_account'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="snowflake_account") | .value')
  gh secret set SOPHIA_SNOWFLAKE_PASSWORD_PROD --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated snowflake_account -> SOPHIA_SNOWFLAKE_PASSWORD_PROD'
else
  echo '⚠️  snowflake_account not found'
fi

# Migrate snowflake_database -> SOPHIA_SNOWFLAKE_PASSWORD_PROD
if gh secret list --org ai-cherry | grep -q 'snowflake_database'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="snowflake_database") | .value')
  gh secret set SOPHIA_SNOWFLAKE_PASSWORD_PROD --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated snowflake_database -> SOPHIA_SNOWFLAKE_PASSWORD_PROD'
else
  echo '⚠️  snowflake_database not found'
fi

# Migrate snowflake_password -> SOPHIA_SNOWFLAKE_PASSWORD_PROD
if gh secret list --org ai-cherry | grep -q 'snowflake_password'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="snowflake_password") | .value')
  gh secret set SOPHIA_SNOWFLAKE_PASSWORD_PROD --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated snowflake_password -> SOPHIA_SNOWFLAKE_PASSWORD_PROD'
else
  echo '⚠️  snowflake_password not found'
fi

# Migrate snowflake_role -> SOPHIA_SNOWFLAKE_PASSWORD_PROD
if gh secret list --org ai-cherry | grep -q 'snowflake_role'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="snowflake_role") | .value')
  gh secret set SOPHIA_SNOWFLAKE_PASSWORD_PROD --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated snowflake_role -> SOPHIA_SNOWFLAKE_PASSWORD_PROD'
else
  echo '⚠️  snowflake_role not found'
fi

# Migrate snowflake_schema -> SOPHIA_SNOWFLAKE_PASSWORD_PROD
if gh secret list --org ai-cherry | grep -q 'snowflake_schema'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="snowflake_schema") | .value')
  gh secret set SOPHIA_SNOWFLAKE_PASSWORD_PROD --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated snowflake_schema -> SOPHIA_SNOWFLAKE_PASSWORD_PROD'
else
  echo '⚠️  snowflake_schema not found'
fi

# Migrate snowflake_user -> SOPHIA_SNOWFLAKE_PASSWORD_PROD
if gh secret list --org ai-cherry | grep -q 'snowflake_user'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="snowflake_user") | .value')
  gh secret set SOPHIA_SNOWFLAKE_PASSWORD_PROD --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated snowflake_user -> SOPHIA_SNOWFLAKE_PASSWORD_PROD'
else
  echo '⚠️  snowflake_user not found'
fi

# Migrate snowflake_warehouse -> SOPHIA_SNOWFLAKE_PASSWORD_PROD
if gh secret list --org ai-cherry | grep -q 'snowflake_warehouse'; then
  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name=="snowflake_warehouse") | .value')
  gh secret set SOPHIA_SNOWFLAKE_PASSWORD_PROD --body "$OLD_VALUE" --org ai-cherry
  echo '✅ Migrated snowflake_warehouse -> SOPHIA_SNOWFLAKE_PASSWORD_PROD'
else
  echo '⚠️  snowflake_warehouse not found'
fi

# Update Pulumi ESC environments
echo '📝 Updating Pulumi ESC configurations...'
# Update scoobyjava-org/sophia-ai-prod
pulumi env init scoobyjava-org/sophia-ai-prod --yes || true
echo '{"sophia": {"platform": {"name": "sophia-ai-platform", "version": "v2.0.0", "environment": "prod", "docker": {"token": "${SOPHIA_DOCKER_TOKEN_PROD}"}, "github": {"token": "${SOPHIA_GITHUB_TOKEN_PROD}", "password": "${SOPHIA_GITHUB_PASSWORD_PROD}"}, "pulumi": {"token": "${SOPHIA_PULUMI_TOKEN_PROD}"}}, "ai": {"anthropic": {"api_key": "${SOPHIA_ANTHROPIC_API_KEY_PROD}"}, "openai": {"api_key": "${SOPHIA_OPENAI_API_KEY_PROD}"}, "portkey": {"api_key": "${SOPHIA_PORTKEY_API_KEY_PROD}"}}, "integration": {"gong": {"api_key": "${SOPHIA_GONG_API_KEY_PROD}", "client_secret": "${SOPHIA_GONG_CLIENT_SECRET_PROD}"}, "hubspot": {"token": "${SOPHIA_HUBSPOT_TOKEN_PROD}", "api_key": "${SOPHIA_HUBSPOT_API_KEY_PROD}"}, "linear": {"api_key": "${SOPHIA_LINEAR_API_KEY_PROD}"}}, "infrastructure": {"lambda": {"api_key": "${SOPHIA_LAMBDA_API_KEY_PROD}", "token": "${SOPHIA_LAMBDA_TOKEN_PROD}"}, "namecheap": {"api_key": "${SOPHIA_NAMECHEAP_API_KEY_PROD}", "token": "${SOPHIA_NAMECHEAP_TOKEN_PROD}"}, "vercel": {"token": "${SOPHIA_VERCEL_TOKEN_PROD}"}}, "data": {"pinecone": {"api_key": "${SOPHIA_PINECONE_API_KEY_PROD}", "password": "${SOPHIA_PINECONE_PASSWORD_PROD}"}, "weaviate": {"api_key": "${SOPHIA_WEAVIATE_API_KEY_PROD}", "password": "${SOPHIA_WEAVIATE_PASSWORD_PROD}"}, "snowflake": {"password": "${SOPHIA_SNOWFLAKE_PASSWORD_PROD}"}}, "communication": {"slack": {"token": "${SOPHIA_SLACK_TOKEN_PROD}", "bot_token": "${SOPHIA_SLACK_BOT_TOKEN_PROD}", "client_secret": "${SOPHIA_SLACK_CLIENT_SECRET_PROD}"}}}}' | pulumi env set scoobyjava-org/sophia-ai-prod --
echo '✅ Updated scoobyjava-org/sophia-ai-prod'

echo '🎉 Migration completed successfully!'
