# Deep Dive: GitHub Strategy & Operations

> **Version:** 1.0
> **Status:** Implemented
> **Parent:** [SOPHIA_AI_SYSTEM_HANDBOOK.md](./00_SOPHIA_AI_SYSTEM_HANDBOOK.md)

---

## 1. Repository Structure: A Unified Monorepo

The Sophia AI platform is developed within a single, unified repository (`sophia-main`). This "monorepo" approach was chosen for several strategic reasons:

-   **Atomic Commits:** Changes that span multiple services (e.g., updating the MCP gateway and an N8N workflow simultaneously) can be committed as a single, atomic unit. This eliminates versioning conflicts and simplifies rollbacks.
-   **Simplified Dependency Management:** All services share a single `uv.lock` file, ensuring perfect dependency alignment across the entire platform.
-   **Seamless Refactoring:** Code can be moved between services and shared libraries with ease, encouraging a cleaner, more modular architecture.
-   **Single Source of Truth:** All code, documentation, scripts, and infrastructure definitions live in one place, providing a holistic view of the project.

### **Key Directories:**

-   `docs/system_handbook/`: The master documentation for the platform.
-   `n8n-integration/`: The heart of our new architecture, containing the MCP gateway and all N8N workflows and scripts.
-   `scripts/`: Houses all operational scripts for analysis, health checks, deployment, etc.
-   `mcp-servers/`: **(Legacy)** Contains the original FastAPI services. These are now considered internal service backends, wrapped by N8N.
-   `external/`: Our curated collection of strategic third-party repositories, used as a knowledge base by our AI Pattern Selector.
-   `config/`: Contains static configuration files, but **not secrets**.
-   `backend/` & `frontend/`: Code for specific services and UI components. **(Note: Subject to refactoring into more granular services).**

## 2. Branching Strategy: Trunk-Based Development

We follow a simple, high-velocity, trunk-based development model.

-   **`main`:** The `main` branch is the single source of truth. It must **always** be stable and deployable.
-   **Feature Branches:** All new work is done on short-lived feature branches, typically named `[user]/[feature-name]` (e.g., `lynn/add-salesforce-tool`).
-   **Pull Requests:** When a feature is complete, a Pull Request is opened against `main`. Automated checks (linting, testing, security scans) are run via GitHub Actions.
-   **Merge:** Once the PR is reviewed and approved, it is squashed and merged into `main`, keeping our commit history clean and linear.

## 3. Commit Message Convention

We adhere to the [Conventional Commits](https://www.conventionalcommits.org/) specification. This provides a clear, machine-readable history, which is invaluable for automated changelog generation and understanding the impact of changes.

**Format:** `<type>(<scope>): <subject>`

-   **`<type>`:**
    -   `feat`: A new feature (e.g., adding a new MCP tool).
    -   `fix`: A bug fix.
    -   `docs`: Documentation changes only.
    -   `style`: Code style changes (formatting, etc.).
    -   `refactor`: A code change that neither fixes a bug nor adds a feature.
    -   `perf`: A code change that improves performance.
    -   `test`: Adding missing tests or correcting existing tests.
    -   `ci`: Changes to our CI configuration and scripts.
    -   `chore`: Routine tasks, dependency updates, etc.

-   **`<scope>` (optional):** The part of the codebase affected (e.g., `mcp`, `n8n`, `docs`).

**Example:**
`feat(mcp): Integrate Project Management Suite via N8N`

## 4. Deployment Strategy

Our deployment strategy is centered around **continuous integration and continuous delivery (CI/CD)**, automated via GitHub Actions.

1.  **Push to `main`:** Every push to the `main` branch triggers our primary deployment workflow.
2.  **Automated Testing:** The workflow runs a comprehensive suite of tests:
    -   UV dependency check.
    -   Ruff linting and formatting checks.
    -   Unit and integration tests.
3.  **Infrastructure Sync (Pulumi):** The workflow runs `pulumi up` to ensure our cloud infrastructure (defined in the `infrastructure/` directory) matches the state defined in the code.
4.  **Secret Sync (Pulumi ESC):** Our GitHub Actions are configured to automatically sync secrets from the `ai-cherry` GitHub organization to Pulumi ESC, ensuring our services always have the credentials they need.
5.  **Service Deployment:** Once tests and infrastructure checks pass, services are deployed.
    -   **N8N Workflows:** Workflows are automatically deployed to the N8N instance.
    -   **Internal Services:** Our internal FastAPI services (from `mcp-servers/`) are containerized and deployed as Docker images.
    -   **Frontend:** The frontend is deployed to Vercel.

This automated pipeline ensures that every change pushed to `main` is rigorously tested and deployed rapidly, allowing for high-velocity development without sacrificing stability.
