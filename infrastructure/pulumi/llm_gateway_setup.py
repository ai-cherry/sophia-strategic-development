"""
Pulumi script for managing OpenRouter resources using its CLI.
"""
import pulumi
import pulumi_command as command
from infrastructure.esc.llm_gateway_secrets import llm_gateway_secret_manager

# --- Configuration ---
config = pulumi.Config("openrouter")
# Example: We can manage which models are enabled or disabled.
disabled_models = config.get("disabled_models", "[]") # Expects a JSON array string

# Get the OpenRouter API key from our secret manager
openrouter_api_key = llm_gateway_secret_manager.get_openrouter_api_key()

# --- Resource Definition using the Command Provider ---

# This is a conceptual example. If the OpenRouter CLI had a command like
# `openrouter models disable <model_name>`, we could use it like this.
# Since the primary interaction is via SDK, this serves as a placeholder for
# any future CLI-based management tasks.

disable_command = pulumi.Output.concat(
    "echo 'Simulating OpenRouter CLI command. A real command would disable models: ' && echo ",
    disabled_models
)

openrouter_config = command.local.Command("openrouter-cli-config",
    create=disable_command,
    update=disable_command, # Run on updates as well
    environment={
        "OPENROUTER_API_KEY": openrouter_api_key
    }
)

# --- Outputs ---
pulumi.export("openrouter_cli_status", "OpenRouter configuration managed via Pulumi Command resource (simulation).")
pulumi.export("openrouter_simulated_command_stdout", openrouter_config.stdout) 