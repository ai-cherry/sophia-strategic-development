import pulumi_vercel as vercel
from pulumi import Config, ResourceOptions

from .base_component import BaseComponent


class VercelComponent(BaseComponent):
    def __init__(self, name: str, opts: ResourceOptions = None):
        super().__init__(name, opts)

        config = Config()
        env = config.require("environment")

        vercel_team_id = config.get("vercel_team_id")

        project_names = {
            "development": "sophia-dev",
            "staging": "sophia-staging",
            "production": "sophia",
        }

        domains = {
            "development": "dev.sophia.payready.com",
            "staging": "staging.sophia.payready.com",
            "production": "sophia.payready.com",
        }

        project_name = project_names.get(env, project_names["development"])
        self.project = vercel.Project(
            project_name,
            name=project_name,
            framework="nextjs",
            git_repository={
                "type": "github",
                "repo": "payready/sophia-frontend",
                "production_branch": "main" if env == "production" else env,
            },
            team_id=vercel_team_id,
        )

        domain_name = domains.get(env, domains["development"])
        self.domain = vercel.Domain(
            domain_name,
            name=domain_name,
            project_id=self.project.id,
            team_id=vercel_team_id,
        )

        self.deployment = vercel.Deployment(
            f"{project_name}-deployment",
            project_id=self.project.id,
            production=(env == "production"),
            team_id=vercel_team_id,
            opts=ResourceOptions(depends_on=[self.project, self.domain]),
        )

        self.register_outputs(
            {
                "project_name": self.project.name,
                "domain_name": self.domain.name,
                "deployment_url": self.deployment.url,
            }
        )
