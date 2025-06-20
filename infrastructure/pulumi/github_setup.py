"""
Pulumi script for setting up GitHub resources using the native Pulumi provider.
"""
import pulumi
import pulumi_github as github
from infrastructure.esc.github_secrets import github_secret_manager

# --- Configuration ---
config = pulumi.Config("github")
repo_name = config.get("repo_name", "sophia-main")
repo_description = config.get("repo_description", "The official repository for the Sophia AI project.")

# Get the GitHub PAT from our secret manager
# This is needed to authenticate the provider
github_token = github_secret_manager.get_pat()

# Configure the GitHub provider with the token
github_provider = github.Provider("github-provider",
    token=github_token
)

# --- Resource Definitions ---

# 1. Get a reference to our existing repository
# We are managing an existing repo, not creating a new one.
sophia_repo = github.get_repository(
    name=repo_name,
    opts=pulumi.ResourceOptions(provider=github_provider)
)

# 2. Define a branch protection rule for the 'main' branch
main_branch_protection = github.BranchProtection("main-branch-protection",
    repository_id=sophia_repo.node_id,
    pattern="main",
    enforce_admins=True,
    requires_status_checks=github.BranchProtectionRequiresStatusChecksArgs(
        strict=True,
        contexts=["ci-checks"], # Placeholder for a real CI check context
    ),
    required_pull_request_reviews=github.BranchProtectionRequiredPullRequestReviewsArgs(
        required_approving_review_count=1,
    ),
    opts=pulumi.ResourceOptions(provider=github_provider)
)

# 3. Add a repository secret (example)
# This securely adds a secret to the GitHub repository for use in Actions.
example_secret = github.ActionsSecret("example-repo-secret",
    repository=sophia_repo.name,
    secret_name="EXAMPLE_SECRET",
    plaintext_value=config.require_secret("example_secret_value"),
    opts=pulumi.ResourceOptions(provider=github_provider)
)


# --- Outputs ---
pulumi.export("github_repository_name", sophia_repo.full_name)
pulumi.export("github_main_branch_protection_status", "Enabled")
pulumi.export("github_example_secret_name", example_secret.secret_name) 