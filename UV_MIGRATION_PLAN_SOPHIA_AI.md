# UV Implementation Guide and Migration Plan for Sophia AI Ecosystem

## 1. Installation and Setup

### Install UV
- macOS/Linux:
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
  Fix permission errors if any:
  ```bash
  sudo chown -R $USER ~/.local/share/uv
  ```
- Homebrew (macOS):
  ```bash
  brew install uv
  ```
- Windows (PowerShell admin):
  ```powershell
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```
- Verify installation:
  ```bash
  uv version
  ```
- Ensure `~/.local/bin` is in PATH:
  ```bash
  export PATH=$HOME/.local/bin:$PATH
  ```

### Initialize Project
```bash
uv init sophia-ai
cd sophia-ai
```
Creates `pyproject.toml`, `.python-version`, `.venv`.

### Add Core Dependencies
```bash
uv add snowflake-connector-python pulumi langchain openai anthropic pinecone-client weaviate-client redis fastapi pydantic structlog prometheus-client
uv add transformers torch tensorflow sentence-transformers scikit-learn numpy pandas
```

### Manage Python Versions
- Use `uv python install <version>` to install specific Python versions.
- Set version in `.python-version`:
  ```bash
  echo "3.12" > .python-version
  uv sync
  ```

---

## 2. Dependency Management

### Organize Dependencies in `pyproject.toml`
```toml
[project]
name = "sophia-ai"
version = "0.1.0"
dependencies = [
  "snowflake-connector-python>=3.0.0",
  "pulumi>=3.0.0",
  "langchain>=0.2.0",
  "openai>=1.0.0",
  "anthropic>=0.3.0",
  "pinecone-client>=3.0.0",
  "weaviate-client>=4.0.0",
  "redis>=5.0.0",
  "fastapi>=0.115.0",
  "pydantic>=2.0.0",
  "structlog>=24.0.0",
  "prometheus-client>=0.20.0",
  "transformers>=4.40.0",
  "torch>=2.0.0",
  "tensorflow>=2.15.0",
  "sentence-transformers>=3.0.0",
  "scikit-learn>=1.5.0",
  "numpy>=2.0.0",
  "pandas>=2.2.0",
]

[dependency-groups]
dev = ["pytest>=8.0.0", "ruff>=0.6.0"]
test = ["pytest-cov>=5.0.0"]
docs = ["mkdocs>=1.5.0"]
```

### Install Specific Groups
```bash
uv sync --group prod --no-group dev
```

### Platform-Specific Dependencies
- GPU-enabled PyTorch for Lambda Labs:
  ```bash
  uv add "torch>=2.0.0; sys_platform == 'linux'"
  ```
- CPU-only for M1/M2 Macs:
  ```bash
  uv add "torch[cpu]>=2.0.0"
  ```

### Editable Installs for MCP Servers
```bash
uv add --editable ./backend/mcp_servers/base
```
- Hot reload supported; native modules require rebuild with `uv sync`.

### Lock File Management
- Commit `uv.lock` for reproducibility.
- Generate lock file:
  ```bash
  uv lock
  ```
- Export for Docker:
  ```bash
  uv export -o requirements.txt
  ```

---

## 3. Pulumi Integration

### Configure `Pulumi.yaml`
```yaml
runtime:
  name: python
  options:
    toolchain: uv
    virtualenv: .venv
```

### ESC Variables
- Store secrets (e.g., Snowflake credentials) in Pulumi ESC.
- Set in CI environment:
  ```bash
  export PULUMI_CONFIG_PASSPHRASE=$(cat secrets/passphrase)
  uv run pulumi up
  ```

### Stack-Specific Dependencies
```toml
[dependency-groups]
prod-stack = ["snowflake-connector-python>=3.0.0"]
dev-stack = ["snowflake-connector-python>=2.0.0"]
```
- Sync with:
  ```bash
  uv sync --group prod-stack
  ```

### Performance Benefits
- UV caches dependencies globally.
- Expect ~20-30% faster `pulumi up` execution on large stacks.

---

## 4. Docker Optimization

### Multi-Stage Build Example
```dockerfile
# Build stage
FROM python:3.12-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-cache

# Runtime stage
FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY . .
CMD ["/app/.venv/bin/uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
```

### Build Optimizations
- Copy `pyproject.toml` and `uv.lock` early for layer caching.
- Use `docker buildx` with `--platform linux/amd64,linux/arm64` for multi-arch.
- UV reduces image size by ~80% via global cache and hard links.

---

## 5. CI/CD with GitHub Actions

### Workflow Snippet
```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install uv
        run: curl -LsSf https://astral.sh/uv/install.sh | sh
      - name: Sync prod dependencies
        run: uv sync --no-group dev --group prod
      - name: Run tests
        run: uv run pytest
      - uses: actions/cache@v4
        with:
          path: ~/.cache/uv
          key: uv-${{ hashFiles('uv.lock') }}
```
- Expect 2–5x faster dependency resolution.

---

## 6. Security and Compliance

### Scanning
- Compatible with Dependabot, Snyk, Safety.
- Run security checks:
  ```bash
  uv run safety check
  ```

### Private PyPI Configuration
```toml
[[tool.uv.sources]]
name = "internal-pypi"
url = "https://internal.pypi.company.com/simple"
token = "${PYPI_TOKEN}"
```

### SBOM Generation
```bash
uv run cyclonedx-bom -o sbom.json
```

---

## 7. Common Errors and Fixes

- **Permission Denied**: Fix with `sudo chown -R $USER ~/.local/share/uv`.
- **Unsatisfiable Dependencies**: Use `uv lock --verbose` to debug.
- **ModuleNotFoundError**: Run `uv add <package>`.
- **Pulumi Failures**: Ensure `toolchain: uv` in `Pulumi.yaml` and `.venv` exists.

---

## 8. Issues to Avoid

- Avoid system-wide `pip install uv`; use `pipx` or installer.
- Do not manually edit `uv.lock`.
- Sync `.python-version` with `pyproject.toml`.
- Always commit `uv.lock`.
- Set `PULUMI_CONFIG_PASSPHRASE` in CI for Pulumi.

---

## 9. Migration from Poetry

### Group Conversion
- Map Poetry groups to UV `[dependency-groups]` in `pyproject.toml`.

### Lock File Conversion
- Convert `poetry.lock` using:
  ```bash
  uvx pdm import pyproject.toml
  uv lock
  ```

### Monorepo Support
- Use UV workspace:
  ```bash
  uv workspace add backend
  uv workspace add mcp-servers/server1
  uv sync --workspace
  ```

### Rollback Plan
- Keep Poetry files in a separate branch.
- Test UV in isolated branch.
- Revert if issues arise.

---

This plan ensures a smooth, performant migration to UV, leveraging its speed and modern features while maintaining Sophia AI’s complex multi-repo, AI-heavy infrastructure.
