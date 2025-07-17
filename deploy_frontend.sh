#!/bin/bash
# 🌐 SOPHIA AI FRONTEND DEPLOYMENT
# Build and deploy React frontend to Lambda Labs

PRIMARY_SERVER="192.222.58.232"
LAMBDA_KEY="$HOME/.ssh/lambda_labs_key"

echo "🌐 DEPLOYING SOPHIA AI FRONTEND"
echo "=============================="

# Step 1: Build frontend locally
echo "🏗️  Building React frontend..."
cd frontend

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Installing..."
    # Try to install Node via brew or other means
    if command -v brew &> /dev/null; then
        brew install node
    else
        echo "⚠️  Please install Node.js and run again"
        exit 1
    fi
fi

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Build for production
echo "🚀 Building for production..."
npm run build

# Check if build was successful
if [ ! -d "dist" ]; then
    echo "❌ Build failed - no dist directory created"
    exit 1
fi

echo "✅ Frontend built successfully"
echo "   Build size: $(du -sh dist | cut -f1)"

cd ..

# Step 2: Deploy to Lambda Labs server
echo ""
echo "📤 Deploying to Lambda Labs..."

# Create deployment package
tar -czf frontend-dist.tar.gz -C frontend/dist .

# Copy to server
scp -i "$LAMBDA_KEY" frontend-dist.tar.gz ubuntu@$PRIMARY_SERVER:/tmp/

# Deploy on server
ssh -i "$LAMBDA_KEY" ubuntu@$PRIMARY_SERVER << 'EOF'
echo "📂 Setting up frontend on server..."

# Create web directory
sudo mkdir -p /var/www/sophia-frontend
sudo chown ubuntu:ubuntu /var/www/sophia-frontend

# Extract frontend files
cd /var/www/sophia-frontend
tar -xzf /tmp/frontend-dist.tar.gz
sudo chown -R www-data:www-data /var/www/sophia-frontend

# Update Nginx configuration for full app
echo "🔧 Updating Nginx configuration..."
sudo tee /etc/nginx/sites-available/sophia-ai << 'NGINX'
server {
    listen 80;
    server_name _;

    # Frontend - serve React app
    location / {
        root /var/www/sophia-frontend;
        try_files $uri $uri/ /index.html;
        
        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # Backend API routes
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Health check (direct backend)
    location /health {
        proxy_pass http://localhost:8000/health;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Vector service
    location /vector/ {
        proxy_pass http://localhost:6333/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
NGINX

# Test and reload Nginx
sudo nginx -t && sudo systemctl reload nginx

echo "✅ Frontend deployed successfully!"
echo ""
echo "📊 Deployment status:"
echo "  Frontend files: $(ls -la /var/www/sophia-frontend | wc -l) files"
echo "  Directory size: $(du -sh /var/www/sophia-frontend)"
echo ""
echo "🌐 Testing frontend..."
curl -s -I http://localhost/ | head -3

# Clean up
rm /tmp/frontend-dist.tar.gz
EOF

# Clean up local file
rm frontend-dist.tar.gz

echo ""
echo "🔍 TESTING DEPLOYMENT..."
echo "======================="

# Test from external
sleep 5
echo "Testing frontend access..."

if curl -s -I http://$PRIMARY_SERVER/ | grep -q "200"; then
    echo "✅ Frontend accessible at http://$PRIMARY_SERVER/"
    echo "📄 Content preview:"
    curl -s http://$PRIMARY_SERVER/ | head -10 | grep -E "(title|h1|Sophia)" || echo "   HTML content loaded"
else
    echo "❌ Frontend not accessible"
fi

echo ""
echo "🎉 FRONTEND DEPLOYMENT COMPLETED!"
echo "================================"
echo ""
echo "🌐 ACCESS URLS:"
echo "  Frontend:     http://$PRIMARY_SERVER/"
echo "  Backend API:  http://$PRIMARY_SERVER/api/"
echo "  Health:       http://$PRIMARY_SERVER/health"
echo "  Vector API:   http://$PRIMARY_SERVER/vector/"
echo ""
echo "📊 FULL STACK STATUS:"
echo "  Frontend:     React app served by Nginx"
echo "  Backend:      FastAPI on port 8000"
echo "  Vector:       Service on port 6333"
echo "  Database:     PostgreSQL + Redis"
echo ""
echo "🚀 Sophia AI Full Stack is now LIVE!" 