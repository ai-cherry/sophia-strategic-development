---
title: Local Development & Testing Guide
description: **Date:** December 20, 2024 **Status:** The Official Guide for Running Sophia AI Services Locally
tags: security, onboarding, gong, docker, agent
last_updated: 2025-06-23
dependencies: none
related_docs: none
---

# Local Development & Testing Guide


## Table of Contents

- [1. The Goal: Secure, Simple, and Powerful Local Development](#1.-the-goal:-secure,-simple,-and-powerful-local-development)
- [2. Prerequisites](#2.-prerequisites)
- [3. The Core Pattern: `esc run`](#3.-the-core-pattern:-`esc-run`)
- [4. How to Run Any Agent Locally](#4.-how-to-run-any-agent-locally)
  - [Example: Running the "Analyst Agent"](#example:-running-the-"analyst-agent")
  - [Breakdown of the Command:](#breakdown-of-the-command:)
- [5. Advanced Usage: Dynamic Configuration Files](#5.-advanced-usage:-dynamic-configuration-files)
  - [Example: Providing a `settings.yaml` to a service](#example:-providing-a-`settings.yaml`-to-a-service)
  - [Breakdown:](#breakdown:)
- [Conclusion: The New Standard for Local Development](#conclusion:-the-new-standard-for-local-development)

**Date:** December 20, 2024
**Status:** The Official Guide for Running Sophia AI Services Locally

## 1. The Goal: Secure, Simple, and Powerful Local Development

This guide outlines the standardized, secure, and simple method for running any Sophia AI agent or service on your local machine for development and testing.

The core principle is the use of the **`esc run` command**, provided by the Pulumi ESC CLI. This approach completely eliminates the need for manual secret management (e.g., `.env` files) and ensures that your local environment perfectly mirrors the configuration of our production services.

---

## 2. Prerequisites

Before you begin, ensure you have the following installed:

1.  **The Pulumi ESC CLI:** [Installation Guide](https://www.pulumi.com/docs/esc/install/)
2.  **Docker Desktop:** [Installation Guide](https://docs.docker.com/get-docker/)
3.  **An active login to Pulumi Cloud:** Run `esc login` and follow the prompts.

---

## 3. The Core Pattern: `esc run`

The `esc run` command works by opening a secure session with our central Pulumi ESC environment (`scoobyjava-org/default/sophia-ai-production`), populating the current shell's environment with all the secrets and configurations defined there, and then executing a command you specify.

**The secrets never touch your local disk.** They exist only in the memory of the process you run.

---

## 4. How to Run Any Agent Locally

This process assumes you have built the Docker image for the agent you wish to run. For example, to build the `analyst-agent`:

```bash
# Example usage:
bash
```python

Once the image is built, you can run the agent with a **single command**.

### Example: Running the "Analyst Agent"

```bash
# Example usage:
bash
```python

### Breakdown of the Command:

1.  **`esc run scoobyjava-org/default/sophia-ai-production --`**
    -   This is the magic part. It connects to our ESC environment. The `--` separates the `esc` command from the command it will execute.

2.  **`docker run --rm -it -p 8080:8080`**
    -   This is a standard Docker command to run a container interactively and map a port.

3.  **`-e PERSONA="..." -e TOOLS="..."`**
    -   This passes the *non-secret* configuration to the agent, such as its persona and the list of tools it should activate.

**What `esc run` is doing automatically:**
Inside the container, `esc run` has already populated the environment with `AGNO_API_KEY`, `ARIZE_API_KEY`, `GONG_ACCESS_KEY`, and all other necessary secrets before the agent code starts. Your agent's `auto_esc_config.py` will find these environment variables and everything will work seamlessly.

---

## 5. Advanced Usage: Dynamic Configuration Files

As outlined in the Pulumi ESC documentation, we can also use the `files` directive to generate temporary configuration files.

### Example: Providing a `settings.yaml` to a service

Let's say a service needs a `config/settings.yaml` file to start. We can define this in our ESC environment:

```yaml
# Example usage:
yaml
```python

Now, we can run a service that needs this file:

```bash
# Example usage:
bash
```python

### Breakdown:

-   `esc run` creates a temporary file (e.g., `/tmp/esc-12345`) and sets the environment variable `AGENT_SETTINGS_YAML` to its path.
-   The `-v $AGENT_SETTINGS_YAML:/app/config/settings.yaml` command is a standard Docker volume mount. It mounts the temporary file created by `esc` into the expected location inside the container.

---

## Conclusion: The New Standard for Local Development

This `esc run` workflow is now the **official and required** method for local development and testing of all Sophia AI services.

-   **No more `.env` files.**
-   **No more manual secret management.**
-   **Perfect parity** between local and production configuration.
-   **Enhanced security** by keeping secrets off local disks.

This allows every developer to be productive within minutes, confident that their local environment is a perfect replica of the secure, configured production environment.
