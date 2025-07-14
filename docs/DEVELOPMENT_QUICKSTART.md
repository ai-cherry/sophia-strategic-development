# Sophia AI Development Quickstart

## Prerequisites
- Python 3.12+
- UV package manager
- Docker Desktop
- Modern Stack account

## Quick Setup (5 minutes)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ai-cherry/sophia-main.git
   cd sophia-main
   ```

2. **Install dependencies:**
   ```bash
   uv pip install -e .
   ```

3. **Configure environment:**
   ```bash
   export PULUMI_ORG=scoobyjava-org
   export ENVIRONMENT=prod
   ```

4. **Run the application:**
   ```bash
   cd backend/app
   python app.py
   ```

5. **Verify it's working:**
   ```bash
   curl http://localhost:8000/health
   ```

## Architecture Overview
See the [System Handbook](system_handbook/00_SOPHIA_AI_SYSTEM_HANDBOOK.md) for detailed architecture.

## Common Tasks
- **Add an API endpoint:** See [API Documentation](API_DOCUMENTATION.md)
- **Deploy to production:** See [Deployment Checklist](DEPLOYMENT_CHECKLIST.md)
- **Understand the structure:** See [Application Structure](APPLICATION_STRUCTURE.md)

## Need Help?
- Check the [Remediation Summary](REMEDIATION_SUMMARY.md) for current status
- Review [Immediate Actions](IMMEDIATE_REMEDIATION_ACTIONS.md) for ongoing work
