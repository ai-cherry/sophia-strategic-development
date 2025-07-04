#!/bin/bash
# Sophia AI Quick Deployment Script for Lambda Labs
# This script sets up and deploys the complete Sophia AI stack on Lambda Labs

set -e

echo "🚀 SOPHIA AI LAMBDA LABS DEPLOYMENT STARTING..."
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root"
   exit 1
fi

# Check for required environment variables
print_header "0. Checking required environment variables..."
if [ -z "$DOCKER_USER_NAME" ] || [ -z "$DOCKER_PERSONAL_ACCESS_TOKEN" ]; then
    print_error "Required environment variables not set!"
    print_error "Please set DOCKER_USER_NAME and DOCKER_PERSONAL_ACCESS_TOKEN"
    print_error "Example: export DOCKER_USER_NAME=your_username"
    print_error "Example: export DOCKER_PERSONAL_ACCESS_TOKEN=your_token"
    exit 1
fi

if [ -z "$LAMBDA_LABS_API_KEY" ]; then
    print_warning "LAMBDA_LABS_API_KEY not set. Some features may not work."
fi

print_status "Environment variables validated successfully"

# Step 1: Update system and install dependencies
print_header "1. Installing system dependencies..."
sudo apt-get update -y
sudo apt-get install -y \
    curl \
    wget \
    git \
    python3 \
    python3-pip \
    python3-venv \
    build-essential \
    libpq-dev \
    redis-server \
    postgresql \
    postgresql-contrib \
    nginx \
    htop \
    tree

# Step 2: Install Docker
print_header "2. Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    print_status "Docker installed successfully"
else
    print_status "Docker already installed"
fi

# Step 3: Install Docker Compose
print_header "3. Installing Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    print_status "Docker Compose installed successfully"
else
    print_status "Docker Compose already installed"
fi

# Step 4: Clone or update repository
print_header "4. Setting up Sophia AI repository..."
if [ ! -d "sophia-main" ]; then
    git clone https://github.com/ai-cherry/sophia-main.git
    cd sophia-main
else
    cd sophia-main
    git pull origin main
fi

# Step 5: Set up Python environment
print_header "5. Setting up Python environment..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Step 6: Configure Docker authentication
print_header "6. Configuring Docker authentication..."
echo "$DOCKER_PERSONAL_ACCESS_TOKEN" | docker login --username "$DOCKER_USER_NAME" --password-stdin

# Step 7: Set up environment variables
print_header "7. Setting up environment variables..."
cat > .env << EOF
# Sophia AI Environment Configuration
SOPHIA_ENV=production
SOPHIA_VERSION=2.0.0
DATABASE_URL=postgresql://sophia:sophia_password@localhost:5432/sophia_ai
REDIS_URL=redis://localhost:6379
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET=$(openssl rand -hex 32)

# Docker Configuration
DOCKER_USER_NAME=${DOCKER_USER_NAME}
DOCKER_PERSONAL_ACCESS_TOKEN=${DOCKER_PERSONAL_ACCESS_TOKEN}

# Lambda Labs Configuration
LAMBDA_LABS_API_KEY=${LAMBDA_LABS_API_KEY}
EOF

# Step 8: Set up PostgreSQL database
print_header "8. Setting up PostgreSQL database..."
sudo systemctl start postgresql
sudo systemctl enable postgresql
sudo -u postgres psql -c "CREATE USER sophia WITH PASSWORD 'sophia_password';" || true
sudo -u postgres psql -c "CREATE DATABASE sophia_ai OWNER sophia;" || true
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE sophia_ai TO sophia;" || true

# Step 9: Start Redis
print_header "9. Starting Redis..."
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Step 10: Build Docker images
print_header "10. Building Docker images..."
docker build -t ${DOCKER_USER_NAME}/sophia-ai:latest .

# Build MCP servers
for server in mcp-servers/*/; do
    if [ -f "$server/Dockerfile" ]; then
        server_name=$(basename "$server")
        print_status "Building MCP server: $server_name"
        docker build -t ${DOCKER_USER_NAME}/sophia-mcp-$server_name:latest "$server"
    fi
done

# Step 11: Push images to Docker Hub
print_header "11. Pushing images to Docker Hub..."
docker push ${DOCKER_USER_NAME}/sophia-ai:latest

for server in mcp-servers/*/; do
    if [ -f "$server/Dockerfile" ]; then
        server_name=$(basename "$server")
        print_status "Pushing MCP server: $server_name"
        docker push ${DOCKER_USER_NAME}/sophia-mcp-$server_name:latest
    fi
done

# Step 12: Start services with Docker Compose
print_header "12. Starting services with Docker Compose..."
docker-compose up -d

# Step 13: Configure Nginx reverse proxy
print_header "13. Configuring Nginx..."
sudo tee /etc/nginx/sites-available/sophia-ai << EOF
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /api/ {
        proxy_pass http://localhost:8000/api/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/sophia-ai /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl enable nginx

# Step 14: Final health checks
print_header "14. Running health checks..."
sleep 30

# Check if services are running
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    print_status "✅ Sophia AI main service is healthy"
else
    print_warning "⚠️ Sophia AI main service health check failed"
fi

if redis-cli ping | grep -q PONG; then
    print_status "✅ Redis is running"
else
    print_warning "⚠️ Redis health check failed"
fi

if sudo -u postgres psql -c "SELECT 1;" > /dev/null 2>&1; then
    print_status "✅ PostgreSQL is running"
else
    print_warning "⚠️ PostgreSQL health check failed"
fi

# Display final status
print_header "🎉 DEPLOYMENT COMPLETED!"
echo "=================================================="
print_status "Sophia AI is now deployed and running on Lambda Labs"
print_status "Main application: http://$(curl -s ifconfig.me):80"
print_status "Default credentials and API keys are set via environment variables"
echo ""
print_status "Services status:"
docker-compose ps
echo ""
print_status "To view logs: docker-compose logs -f"
print_status "To stop services: docker-compose down"
print_status "To restart services: docker-compose restart"
echo "=================================================="
