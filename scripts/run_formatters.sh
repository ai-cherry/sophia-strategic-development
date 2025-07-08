#!/usr/bin/env bash
set -e
python -m venv .venv
source .venv/bin/activate
pip install --break-system-packages black ruff
black . -q
ruff check . --fix
