#!/usr/bin/env bash
set -euo pipefail

# Configure these variables for your org/project/env
PULUMI_ENV="scoobyjava-org/default/sophia-ai-production"
OUTPUT_FILE=".env.local"

if ! command -v esc &> /dev/null; then
  echo "Error: Pulumi ESC CLI (esc) is not installed or not in PATH."
  exit 1
fi

echo "Fetching secrets from Pulumi ESC..."
esc env open "$PULUMI_ENV" --format dotenv > "$OUTPUT_FILE"
echo "Loaded secrets into $OUTPUT_FILE"
echo "Now you can run: docker compose up"
