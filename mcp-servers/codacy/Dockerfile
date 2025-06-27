FROM python:3.11-slim

WORKDIR /app

# Copy only necessary files
COPY mcp-servers/codacy/requirements.txt .
COPY backend/ /app/backend
COPY mcp-servers/codacy/ /app/mcp-servers/codacy/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables for production-first operation
ENV ENVIRONMENT="prod"
ENV PULUMI_ORG="scoobyjava-org"
ENV LOG_LEVEL="INFO"
ENV PYTHONPATH="/app"

# Expose the port the server will run on
EXPOSE 3008

CMD ["uvicorn", "mcp-servers.codacy.codacy_mcp_server:app", "--host", "0.0.0.0", "--port", "3008"] 