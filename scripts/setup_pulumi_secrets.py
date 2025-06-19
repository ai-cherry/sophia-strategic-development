import os
import subprocess
import logging


def sync_github_secrets_to_pulumi_esc(env_file: str = ".env", pulumi_stack: str = "pulumi-esc-environment.yaml"):
    """
    Sync secrets from a .env file to Pulumi ESC using the Pulumi CLI.
    Args:
        env_file (str): Path to the .env file containing secrets.
        pulumi_stack (str): Path to the Pulumi ESC stack YAML file.
    """
    logging.basicConfig(level=logging.INFO)
    if not os.path.exists(env_file):
        logging.error(f"{env_file} not found.")
        return

    with open(env_file) as f:
        for line in f:
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.strip().split("=", 1)
                cmd = [
                    "pulumi", "config", "set", k, v,
                    "--secret", "--path", pulumi_stack
                ]
                try:
                    subprocess.run(cmd, check=True)
                    logging.info(f"Set secret: {k}")
                except subprocess.CalledProcessError as e:
                    logging.error(f"Failed to set secret {k}: {e}")

    logging.info("Secrets synced to Pulumi ESC.")


if __name__ == "__main__":
    sync_github_secrets_to_pulumi_esc() 