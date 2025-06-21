#!/usr/bin/env python3
"""Check that key AI service credentials are available."""
import os

REQUIRED_VARS = [
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "AGNO_API_KEY",
]


def main() -> None:
    missing = [var for var in REQUIRED_VARS if not os.getenv(var)]
    if missing:
        print("❌ Missing AI service credentials:", ", ".join(missing))
    else:
        print("✅ All required AI service credentials present")

if __name__ == "__main__":
    main()
