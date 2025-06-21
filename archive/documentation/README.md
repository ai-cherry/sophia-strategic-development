# Sophia AI

Sophia AI is an AI assistant orchestrator for Pay Ready company, serving as the central "Pay Ready Brain" that orchestrates multiple AI agents and integrates with business systems.

## Automatic Setup

**Sophia AI now sets up automatically!** You don't need to run any scripts or remember any commands.

### When cloning the repository:

```bash
git clone <repository-url>
cd sophia-main
```

The system will automatically set up everything for you. No additional steps required!

### If you already have the repository:

Simply run:

```bash
make
```

This will automatically:
- Set up all environment variables
- Fix SSL certificate issues
- Resolve Python package dependencies
- Configure Docker and start MCP servers
- Run health checks and system status verification

## System Components

- **Multi-agent AI orchestrator** with flat-to-hierarchical evolution
- **Primary Role:** Business intelligence and automation for Pay Ready
- **Core Integrations:** HubSpot CRM, Gong.io call analysis, Slack communication
- **Data Stack:** PostgreSQL, Redis, Pinecone, Weaviate
- **Infrastructure:** Lambda Labs servers, Vercel frontend deployment

## Key Features

- **Call Analysis Agent:** Process Gong.io recordings for insights
- **CRM Sync Agent:** Maintain HubSpot data quality and synchronization
- **Notification Agent:** Send intelligent Slack updates
- **Business Intelligence Agent:** Generate revenue and performance reports

## Advanced Usage

If you need to run specific components manually:

```bash
# Check system status
make command

# Run health check
make health

# Update environment variables
make env

# Fix SSL certificate issues
make ssl

# Fix Python package dependencies
make deps

# Start MCP servers
make docker

# Clean up
make clean
```

For more detailed information, see:
- [Setup Instructions](SETUP_INSTRUCTIONS.md)
- [Fixes Summary](SOPHIA_FIXES_SUMMARY.md)
- [Secrets Management Guide](SECRETS_MANAGEMENT_GUIDE.md)
