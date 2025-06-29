# Sentry Configuration Setup for Sophia AI

## Provided Sentry Tokens

Based on the provided tokens, here's the mapping for the Sophia AI project:

### Token Analysis
- **SENTRY_PAT**: `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`
- **SENTRY_API_TOKEN**: `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`
- **SENTRY_CLIENT_SECRET**: `42c8dc1fbabb7668e5e2abf5a1bcd1ac94c2df91bb4450411f906571352c3f65`

### Decoded Information from API Token
From the SENTRY_API_TOKEN, we can extract:
- **Organization**: `pay-ready`
- **URL**: `https://sentry.io`
- **Region URL**: `https://us.sentry.io`

## GitHub Secrets Mapping

The following secrets need to be set in the GitHub organization (ai-cherry):

| GitHub Secret Name | Value | Description |
|-------------------|-------|-------------|
| `SENTRY_AUTH_TOKEN` | `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` | Sentry Personal Access Token |
| `SENTRY_API_TOKEN` | `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` | Sentry API Token |
| `SENTRY_CLIENT_SECRET` | `42c8dc1fbabb7668e5e2abf5a1bcd1ac94c2df91bb4450411f906571352c3f65` | Sentry Client Secret |
| `SENTRY_ORGANIZATION_SLUG` | `pay-ready` | Sentry Organization Slug |
| `SENTRY_PROJECT_SLUG` | `sophia-ai` | Sentry Project Slug (to be created) |
| `SENTRY_DSN` | `https://[key]@[org].ingest.sentry.io/[project-id]` | To be obtained after project creation |

## Next Steps

1. Create Sentry project for Sophia AI in the `pay-ready` organization
2. Obtain the DSN from the created project
3. Update GitHub organization secrets
4. Run the sync workflow to push secrets to Pulumi ESC
5. Test the integration

## Configuration Files to Update

- Update `auto_esc_config.py` to include Sentry configuration access
- Ensure `sentry_setup.py` can access the new configuration structure
- Update GitHub workflows if needed

