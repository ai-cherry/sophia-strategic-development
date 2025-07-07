# Codacy_V2 MCP Server

Production-ready MCP server for codacy_v2 integration with Sophia AI platform.

## Features

- ✅ Async/await architecture with FastAPI
- ✅ Production-ready logging (JSON format)
- ✅ Prometheus metrics
- ✅ Health checks and monitoring
- ✅ Docker support
- ✅ Comprehensive error handling
- ✅ AI-powered data processing (Snowflake Cortex)
- ✅ Automated testing

## Quick Start

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export CODACY_V2_API_KEY=your_api_key
export CODACY_V2_LOG_LEVEL=DEBUG

# Run the server
python -m infrastructure.mcp_servers.codacy_v2.server
```

### Docker

```bash
# Build and run with docker-compose
docker-compose up --build

# Server will be available at http://localhost:9001
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /health | Health check endpoint |
| GET | /capabilities | Server capabilities |
| POST | /sync | Trigger data synchronization |
| GET | /data | Get codacy_v2 data |
| GET | /docs | OpenAPI documentation |

## Configuration

See `.env.example` for all available environment variables.

## Testing

```bash
# Run tests
pytest tests -v

# With coverage
pytest --cov=codacy_v2 --cov-report=html
```

## License

Proprietary - Sophia AI Platform
