#!/bin/bash

# Quick Frontend Deployment Script for Sophia AI

echo "Building frontend..."
cd frontend
npm run build

echo "Creating deployment package..."
cd dist
tar -czf ../../frontend-deploy.tar.gz .
cd ../..

echo "Frontend package created: frontend-deploy.tar.gz"
echo ""
echo "Now run these commands to deploy:"
echo ""
echo "1. Copy to server:"
echo "   scp -i ~/.ssh/lambda_labs_private_key frontend-deploy.tar.gz ubuntu@192.222.58.232:/tmp/"
echo ""
echo "2. SSH to server:"
echo "   ssh -i ~/.ssh/lambda_labs_private_key ubuntu@192.222.58.232"
echo ""
echo "3. On the server, run:"
echo "   sudo rm -rf /var/www/sophia-frontend/*"
echo "   cd /var/www/sophia-frontend"
echo "   sudo tar -xzf /tmp/frontend-deploy.tar.gz"
echo "   sudo chown -R www-data:www-data /var/www/sophia-frontend"
echo "   sudo nginx -t && sudo systemctl reload nginx"
echo ""
echo "4. Test the deployment:"
echo "   curl -I https://sophia-intel.ai" 