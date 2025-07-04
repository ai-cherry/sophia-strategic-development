# Docker Hub Deployment Guide

## Overview

This guide documents the Docker Hub deployment process for Sophia AI backend services.

## Docker Hub Repository

- **Registry**: Docker Hub (docker.io)
- **Username**: scoobyjava15
- **Repository**: scoobyjava15/sophia-backend
- **URL**: https://hub.docker.com/r/scoobyjava15/sophia-backend

## Building the Docker Image

### Prerequisites
- Docker Desktop installed and running
- Access to the Sophia AI repository
- Docker Hub account with push permissions

### Build Commands

```bash
# Build the production image
docker build -t scoobyjava15/sophia-backend:latest -f Dockerfile.simple .

# Build with a specific tag
docker build -t scoobyjava15/sophia-backend:v1.0.0 -f Dockerfile.simple .
```

## Pushing to Docker Hub

### Method 1: Using the Push Script

```bash
# Set the Docker token as environment variable
export DOCKER_TOKEN="your-docker-personal-access-token"

# Run the push script
./scripts/docker_push.sh

# Or provide token inline (less secure)
DOCKER_TOKEN="your-token" ./scripts/docker_push.sh
```

### Method 2: Manual Push

```bash
# Login to Docker Hub
echo "$DOCKER_TOKEN" | docker login -u scoobyjava15 --password-stdin

# Push the image
docker push scoobyjava15/sophia-backend:latest

# Logout for security
docker logout
```

## Using the Image

### On Lambda Labs or Production

```bash
# Pull the latest image
docker pull scoobyjava15/sophia-backend:latest

# Run the container
docker run -d \
  --name sophia-backend \
  -p 8000:8000 \
  -e ENVIRONMENT=prod \
  -e PULUMI_ORG=scoobyjava-org \
  scoobyjava15/sophia-backend:latest

# View logs
docker logs sophia-backend

# Stop the container
docker stop sophia-backend
```

### Docker Compose Example

```yaml
version: '3.8'

services:
  sophia-backend:
    image: scoobyjava15/sophia-backend:latest
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=prod
      - PULUMI_ORG=scoobyjava-org
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

## Security Best Practices

### Docker Personal Access Token (PAT)

1. **Never commit tokens to Git**
   - Use environment variables
   - Store in secure password managers
   - Rotate tokens regularly

2. **Token Permissions**
   - Use minimal required permissions
   - Create separate tokens for different uses
   - Delete unused tokens

3. **Secure Storage**
   ```bash
   # Store in environment file (not in Git)
   echo "export DOCKER_TOKEN='your-token'" >> ~/.docker_env
   source ~/.docker_env
   ```

### Image Security

1. **Scan for vulnerabilities**
   ```bash
   docker scout cves scoobyjava15/sophia-backend:latest
   ```

2. **Use specific tags**
   - Avoid using `latest` in production
   - Tag with version numbers: `v1.0.0`, `v1.0.1`

3. **Multi-stage builds**
   - Minimize final image size
   - Don't include build tools in production

## Troubleshooting

### Common Issues

1. **Login Failed**
   ```
   Error: unauthorized: incorrect username or password
   ```
   - Verify token is correct
   - Check token hasn't expired
   - Ensure username is correct

2. **Push Denied**
   ```
   denied: requested access to the resource is denied
   ```
   - Verify you're logged in
   - Check repository permissions
   - Ensure image is tagged correctly

3. **Image Not Found**
   ```
   Error: Image not found: scoobyjava15/sophia-backend:latest
   ```
   - Build the image first
   - Check image name and tag

### Debug Commands

```bash
# List local images
docker images | grep sophia

# Check login status
docker info | grep Username

# Verify image details
docker inspect scoobyjava15/sophia-backend:latest
```

## CI/CD Integration

### GitHub Actions Example

```yaml
- name: Login to Docker Hub
  uses: docker/login-action@v3
  with:
    username: scoobyjava15
    password: ${{ secrets.DOCKER_TOKEN }}

- name: Build and push
  uses: docker/build-push-action@v5
  with:
    context: .
    file: ./Dockerfile.simple
    push: true
    tags: scoobyjava15/sophia-backend:latest
```

## Monitoring

### Docker Hub Dashboard
- View pull statistics
- Monitor image sizes
- Check vulnerability scans

### Container Monitoring
```bash
# Resource usage
docker stats sophia-backend

# Health status
docker inspect sophia-backend | jq '.[0].State.Health'
```

## Maintenance

### Regular Tasks
1. Update base images monthly
2. Scan for vulnerabilities weekly
3. Rotate access tokens quarterly
4. Clean up old images

### Cleanup Commands
```bash
# Remove old images locally
docker image prune -a

# Remove specific versions
docker rmi scoobyjava15/sophia-backend:old-version
```
