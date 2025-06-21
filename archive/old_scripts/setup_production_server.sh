#!/bin/bash
# Set up production server for Sophia AI
# This script sets up a new production server for Sophia AI

echo "🚀 Setting up production server for Sophia AI..."

# Set environment variables
export DEPLOY_ENV="production"
export DEPLOY_TARGET="lambda-labs"
export DEPLOY_REGION="us-west-2"

# Step 1: Set up SSH connection to production server
echo "🔑 Setting up SSH connection to production server..."
SSH_KEY="~/.ssh/lambda_labs_key"
PROD_SERVER="sophia-prod.payready.ai"
PROD_USER="deploy"

# Step 2: Install required packages
echo "📦 Installing required packages..."
ssh -i $SSH_KEY $PROD_USER@$PROD_SERVER "sudo apt-get update && sudo apt-get install -y docker.io docker-compose git python3 python3-pip python3-venv"

# Step 3: Create directory structure
echo "📁 Creating directory structure..."
ssh -i $SSH_KEY $PROD_USER@$PROD_SERVER "sudo mkdir -p /opt/sophia && sudo chown -R $PROD_USER:$PROD_USER /opt/sophia"

# Step 4: Clone repository
echo "📥 Cloning repository..."
ssh -i $SSH_KEY $PROD_USER@$PROD_SERVER "cd /opt && git clone https://github.com/ai-cherry/sophia-main.git sophia"

# Step 5: Set up environment variables
echo "🔧 Setting up environment variables..."
ssh -i $SSH_KEY $PROD_USER@$PROD_SERVER "cd /opt/sophia && cp env.example .env"

# Step 6: Update environment variables with production values
echo "🔄 Updating environment variables with production values..."
ssh -i $SSH_KEY $PROD_USER@$PROD_SERVER "cd /opt/sophia && ./update_env.py"

# Step 7: Set up SSL certificates
echo "🔒 Setting up SSL certificates..."
ssh -i $SSH_KEY $PROD_USER@$PROD_SERVER "cd /opt/sophia && sudo mkdir -p /etc/ssl/sophia && sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/ssl/sophia/sophia.key -out /etc/ssl/sophia/sophia.crt -subj '/CN=sophia.payready.ai'"

# Step 8: Set up Nginx
echo "🌐 Setting up Nginx..."
ssh -i $SSH_KEY $PROD_USER@$PROD_SERVER "sudo apt-get install -y nginx"
ssh -i $SSH_KEY $PROD_USER@$PROD_SERVER "sudo bash -c 'cat > /etc/nginx/sites-available/sophia << EOF
server {
    listen 80;
    server_name sophia.payready.ai;
    return 301 https://\$host\$request_uri;
}

server {
    listen 443 ssl;
    server_name sophia.payready.ai;

    ssl_certificate /etc/ssl/sophia/sophia.crt;
    ssl_certificate_key /etc/ssl/sophia/sophia.key;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
    }
}
EOF'"
ssh -i $SSH_KEY $PROD_USER@$PROD_SERVER "sudo ln -sf /etc/nginx/sites-available/sophia /etc/nginx/sites-enabled/sophia && sudo nginx -t && sudo systemctl restart nginx"

# Step 9: Set up firewall
echo "🔥 Setting up firewall..."
ssh -i $SSH_KEY $PROD_USER@$PROD_SERVER "sudo ufw allow 22 && sudo ufw allow 80 && sudo ufw allow 443 && sudo ufw --force enable"

# Step 10: Run the setup script
echo "🔧 Running setup script..."
ssh -i $SSH_KEY $PROD_USER@$PROD_SERVER "cd /opt/sophia && make"

# Step 11: Set up systemd service
echo "⚙️ Setting up systemd service..."
ssh -i $SSH_KEY $PROD_USER@$PROD_SERVER "sudo bash -c 'cat > /etc/systemd/system/sophia.service << EOF
[Unit]
Description=Sophia AI Service
After=network.target

[Service]
User=$PROD_USER
WorkingDirectory=/opt/sophia
ExecStart=/usr/bin/make
Restart=always
RestartSec=10
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=sophia

[Install]
WantedBy=multi-user.target
EOF'"
ssh -i $SSH_KEY $PROD_USER@$PROD_SERVER "sudo systemctl daemon-reload && sudo systemctl enable sophia && sudo systemctl start sophia"

# Step 12: Verify setup
echo "✅ Verifying setup..."
ssh -i $SSH_KEY $PROD_USER@$PROD_SERVER "cd /opt/sophia && ./run_with_ssl_fix.py automated_health_check.py"

echo "✅ Production server has been set up successfully!"
echo "🌐 You can access the system at: https://sophia.payready.ai"
