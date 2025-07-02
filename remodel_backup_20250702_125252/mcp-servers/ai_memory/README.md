# AI Memory MCP Server

This directory packages the AI Memory MCP server for containerized deployment.

## Build

```
docker build -t ai-memory-mcp .
```

## Environment Variables

- `OPENAI_API_KEY` - optional, for generating embeddings
- `PINECONE_API_KEY` - optional, enables vector search
- `PINECONE_ENVIRONMENT` - pinecone environment name, default `us-east1-gcp`

## Usage

Run the container exposing port `9000`:

```
docker run -p 9000:9000 ai-memory-mcp
```
