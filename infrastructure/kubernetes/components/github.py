import pulumi_github as github
from pulumi import Config, ResourceOptions

from .base_component import BaseComponent


class GitHubComponent(BaseComponent):
    def __init__(self, name: str, opts: ResourceOptions = None):
        super().__init__(name, opts)
        component_opts = ResourceOptions(parent=self)

        config = Config()
        env = config.require("environment")

        repo_name = f"sophia-{env}"
        self.repo = github.Repository(
            repo_name,
            name=repo_name,
            description=f"Sophia AI - Pay Ready's AI Assistant Orchestrator ({env})",
            visibility="private",
            auto_init=True,
            opts=component_opts,
        )

        self.branch_protection = github.BranchProtection(
            "main-branch-protection",
            repository_id=self.repo.node_id,
            pattern="main",
            enforce_admins=True,
            opts=component_opts,
        )

        team_name = f"sophia-{env}-team"
        self.team = github.Team(
            team_name,
            name=team_name,
            description=f"Team for the Sophia AI {env} environment",
            privacy="closed",
            opts=component_opts,
        )

        self.team_repository = github.TeamRepository(
            f"{team_name}-repo-access",
            team_id=self.team.id,
            repository=self.repo.name,
            permission="admin",
            opts=component_opts,
        )

        # A real implementation would have a more dynamic way to manage secrets
        secrets_to_create = {
            "PULUMI_ACCESS_TOKEN": config.require_secret("pulumi_access_token"),
            "SNOWFLAKE_PASSWORD": config.require_secret("snowflake_password"),
            # ... and so on for all other secrets
        }

        for name, value in secrets_to_create.items():
            github.ActionsSecret(
                f"{repo_name}-{name}-secret",
                repository=self.repo.name,
                secret_name=name,
                plaintext_value=value,
                opts=component_opts,
            )

        self.register_outputs(
            {
                "repository_name": self.repo.name,
                "repository_url": self.repo.html_url,
                "team_name": self.team.name,
            }
        )
