#!/bin/bash

# Sophia AI Quick Deployment Fix Script
# Applies standard fixes for common deployment issues

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [[ ! -f "backend/app/simple_fastapi.py" ]]; then
    log_error "Please run this script from the sophia-main-2 root directory"
    exit 1
fi

log_info "🚀 Starting Sophia AI Quick Deployment Fix"

# Kill existing processes
log_info "🔪 Killing existing processes..."
pkill -f "uvicorn" 2>/dev/null || log_warning "No uvicorn processes to kill"
pkill -f "npm" 2>/dev/null || log_warning "No npm processes to kill"
pkill -f "vite" 2>/dev/null || log_warning "No vite processes to kill"
sleep 3

# Backend fixes
log_info "🔧 Fixing Backend Issues..."
cd backend

# Install missing Python dependencies
log_info "📦 Installing Python dependencies..."
pip3 install -q \
    sqlalchemy \
    pyjwt \
    passlib[bcrypt] \
    aiofiles \
    python-multipart \
    email-validator \
    qdrant-client \
    uvicorn[standard] \
    fastapi \
    redis \
    psycopg2-binary \
    asyncpg 2>/dev/null || log_warning "Some dependencies may have failed to install"

log_success "✅ Backend dependencies updated"

# Start backend
log_info "🚀 Starting Backend..."
nohup python3 -m uvicorn app.simple_fastapi:app --host 0.0.0.0 --port 8000 --reload > ../backend.log 2>&1 &
BACKEND_PID=$!

cd ..

# Frontend fixes
log_info "🔧 Fixing Frontend Issues..."
cd frontend

# Clear npm cache and reinstall
log_info "🧹 Clearing npm cache..."
npm cache clean --force 2>/dev/null || log_warning "npm cache clean failed"

log_info "🗑️ Removing node_modules..."
rm -rf node_modules package-lock.json 2>/dev/null || log_warning "Cleanup had issues"

log_info "📦 Reinstalling npm dependencies..."
npm install --no-package-lock --silent 2>/dev/null || {
    log_warning "npm install failed, trying with legacy peer deps..."
    npm install --legacy-peer-deps --silent 2>/dev/null || log_error "npm install failed completely"
}

log_info "🔍 Fixing package vulnerabilities..."
npm audit fix --force --silent 2>/dev/null || log_warning "npm audit fix had issues"

log_success "✅ Frontend dependencies updated"

# Start frontend
log_info "🚀 Starting Frontend..."
nohup npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!

cd ..

# Health checks
log_info "🏥 Running Health Checks..."
sleep 15  # Give services time to start

# Check backend health
log_info "🔍 Checking Backend Health..."
for i in {1..6}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        log_success "✅ Backend is healthy (http://localhost:8000)"
        BACKEND_HEALTHY=true
        break
    else
        log_warning "Backend not ready, waiting... (attempt $i/6)"
        sleep 5
    fi
done

if [[ "$BACKEND_HEALTHY" != "true" ]]; then
    log_error "❌ Backend health check failed"
    log_info "📋 Backend logs:"
    tail -10 backend.log 2>/dev/null || log_warning "No backend logs available"
fi

# Check frontend health
log_info "🔍 Checking Frontend Health..."
for i in {1..6}; do
    if curl -s http://localhost:5173 > /dev/null 2>&1; then
        log_success "✅ Frontend is healthy (http://localhost:5173)"
        FRONTEND_HEALTHY=true
        break
    elif curl -s http://localhost:5174 > /dev/null 2>&1; then
        log_success "✅ Frontend is healthy (http://localhost:5174)"
        FRONTEND_HEALTHY=true
        break
    else
        log_warning "Frontend not ready, waiting... (attempt $i/6)"
        sleep 5
    fi
done

if [[ "$FRONTEND_HEALTHY" != "true" ]]; then
    log_error "❌ Frontend health check failed"
    log_info "📋 Frontend logs:"
    tail -10 frontend.log 2>/dev/null || log_warning "No frontend logs available"
fi

# MCP Servers (optional)
log_info "🔧 Starting MCP Servers..."
if [[ -f "scripts/run_all_mcp_servers.py" ]]; then
    nohup python3 scripts/run_all_mcp_servers.py > mcp.log 2>&1 &
    MCP_PID=$!
    log_success "✅ MCP servers started"
else
    log_warning "⚠️ MCP server script not found, skipping"
fi

# Summary
echo ""
log_info "📊 Deployment Fix Summary:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [[ "$BACKEND_HEALTHY" == "true" ]]; then
    log_success "Backend: ✅ Healthy (PID: $BACKEND_PID)"
else
    log_error "Backend: ❌ Unhealthy"
fi

if [[ "$FRONTEND_HEALTHY" == "true" ]]; then
    log_success "Frontend: ✅ Healthy (PID: $FRONTEND_PID)"
else
    log_error "Frontend: ❌ Unhealthy"
fi

if [[ -n "$MCP_PID" ]]; then
    log_success "MCP Servers: ✅ Started (PID: $MCP_PID)"
else
    log_warning "MCP Servers: ⚠️ Skipped"
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# URLs
log_info "🌐 Service URLs:"
echo "  • Backend:  http://localhost:8000"
echo "  • Frontend: http://localhost:5173 or http://localhost:5174"
echo "  • API Docs: http://localhost:8000/docs"

# Log files
log_info "📋 Log Files:"
echo "  • Backend:  backend.log"
echo "  • Frontend: frontend.log"
echo "  • MCP:      mcp.log"

# Commands for manual management
echo ""
log_info "🛠️ Manual Commands:"
echo "  • Stop Backend:  kill $BACKEND_PID"
echo "  • Stop Frontend: kill $FRONTEND_PID"
[[ -n "$MCP_PID" ]] && echo "  • Stop MCP:      kill $MCP_PID"
echo "  • View Logs:     tail -f backend.log frontend.log"
echo "  • Re-run Fix:    bash scripts/quick_deployment_fix.sh"

# Overall success
if [[ "$BACKEND_HEALTHY" == "true" && "$FRONTEND_HEALTHY" == "true" ]]; then
    log_success "🎉 Deployment fix completed successfully!"
    exit 0
else
    log_error "💥 Some services are unhealthy. Check logs for details."
    exit 1
fi 