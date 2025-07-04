# Sophia AI Development Aliases
# Add these to your ~/.zshrc or ~/.bashrc file
# IMPORTANT: Set PULUMI_ACCESS_TOKEN in your environment first

# Quick environment restoration
alias sophia="cd ~/sophia-main && source .venv/bin/activate && export ENVIRONMENT=prod && export PULUMI_ORG=scoobyjava-org && echo '🚀 Sophia AI Environment Ready! (Set PULUMI_ACCESS_TOKEN if needed)'"

# Quick app launches
alias sophia-api="cd ~/sophia-main && source .venv/bin/activate && export ENVIRONMENT=prod && export PULUMI_ORG=scoobyjava-org && uvicorn backend.app.stabilized_fastapi_app:app --host 0.0.0.0 --port 8001"

alias sophia-test="cd ~/sophia-main && source .venv/bin/activate && export ENVIRONMENT=prod && export PULUMI_ORG=scoobyjava-org && python backend/app/phase2_minimal_app.py"

alias sophia-status="cd ~/sophia-main && source .venv/bin/activate && export ENVIRONMENT=prod && export PULUMI_ORG=scoobyjava-org && git status && echo 'Dir: $(pwd)' && echo 'Python: $(which python)' && echo 'Env: $ENVIRONMENT'"

# Set your Pulumi token (add this to your ~/.zshrc):
# export PULUMI_ACCESS_TOKEN=your_pulumi_token_here

# Installation instructions:
# 1. Copy the aliases above
# 2. Add them to your ~/.zshrc file: echo "$(cat sophia_aliases.sh)" >> ~/.zshrc
# 3. Set your Pulumi token: export PULUMI_ACCESS_TOKEN=your_token
# 4. Reload your shell: source ~/.zshrc
# 5. Use: sophia (to restore environment), sophia-api (to run API), sophia-test (to test), sophia-status (to check)
