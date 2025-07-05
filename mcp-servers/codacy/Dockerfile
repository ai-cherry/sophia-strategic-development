# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Install uv for fast dependency management
RUN pip install uv

# Copy only the dependency files to leverage Docker layer caching
COPY pyproject.toml uv.lock ./

# Install project dependencies using uv
# --system flag installs into the system python, which is fine for our container
RUN uv pip install --system --no-cache -r requirements.txt

# Copy the rest of the application's code into the container
COPY . .

# Expose the port the app runs on
EXPOSE 3008

# Define the command to run the application
CMD ["uv", "run", "python", "mcp-servers/codacy/enhanced_codacy_mcp_server.py"]
