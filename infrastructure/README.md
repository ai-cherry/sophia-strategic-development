# Sophia AI Infrastructure as Code

This directory contains the Infrastructure as Code (IaC) implementation for the Sophia AI platform using Pulumi.

## Overview

The Sophia AI platform uses Pulumi to manage infrastructure resources across multiple environments (development, staging, production). This includes:

- **Lambda Labs**: GPU instances and Kubernetes clusters for core AI services.
- **Modern Stack**: Core configurations for data warehousing.
- **Portkey**: API key management for AI gateway.

**Note on SSH Key Management:** SSH keys for Lambda Labs currently require manual configuration due to Pulumi CLI limitations with multi-line secrets. This is a known area for future automation.

## Prerequisites

- [Pulumi CLI](https://www.pulumi.com/docs/get-started/install/)
- [Python 3.11+](https://www.python.org/downloads/)
- [pip](https://pip.pypa.io/en/stable/installation/)
- [virtualenv](https://virtualenv.pypa.io/en/latest/installation.html)

## Getting Started

### 1. Initialize Pulumi Stacks

Run the initialization script to create Pulumi stacks for different environments:

```bash
./init_stacks.sh
```

This will create three stacks:
- `development`
- `staging`
- `production`

### 2. Deploy Infrastructure

Deploy the infrastructure to the selected stack:

```bash
pulumi stack select development
pulumi up
```

## Project Structure

- `infrastructure/index.py`: Python Pulumi program for Lambda Labs and Modern Stack configurations.
- `infrastructure/pulumi/clean-architecture-stack.ts`: TypeScript Pulumi program for Kubernetes deployments on Lambda Labs.
- `Pulumi.yaml`: Pulumi project configuration.
- `requirements.txt`: Python dependencies.
- `init_stacks.sh`: Script to initialize Pulumi stacks.

## Environment-Specific Configuration

Each environment (development, staging, production) has its own configuration values defined in the respective Pulumi stack. These values can be set using the Pulumi CLI:

```bash
pulumi stack select <stack-name>
pulumi config set <key> <value>
```

For secrets, use the `--secret` flag:

```bash
pulumi config set --secret <key> <value>
```

## Secret Management

Secrets are managed using Pulumi ESC (Environments, Secrets, and Configuration). This provides a secure way to manage sensitive information across different environments.

To view the current configuration:

```bash
pulumi stack select <stack-name>
pulumi config
```

## CI/CD Integration

The infrastructure deployment can be integrated into a CI/CD pipeline using GitHub Actions. See the `.github/workflows/production_deployment.yml` file for an example.

## Monitoring and Alerting

Infrastructure monitoring and alerting are configured using Pulumi. This includes:

- Resource health monitoring
- Performance monitoring
- Cost monitoring
- Security monitoring

## Troubleshooting

If you encounter issues with the infrastructure deployment, check the Pulumi logs:

```bash
pulumi stack select <stack-name>
pulumi logs
```

For more detailed information, use the `--verbose` flag:

```bash
pulumi up --verbose
```

## Contributing

1. Create a new branch for your changes
2. Make your changes
3. Test your changes locally
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
