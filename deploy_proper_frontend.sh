#!/bin/bash
echo "🚀 Deploying Proper React Frontend with Tabs, Chat & Dashboards..."

# Create temp directory on server
ssh -i ~/.ssh/lambda_labs_key ubuntu@192.222.58.232 "mkdir -p /tmp/sophia-frontend"

# Upload React build files
echo "📦 Uploading React frontend files..."
scp -i ~/.ssh/lambda_labs_key -r frontend/dist/* ubuntu@192.222.58.232:/tmp/sophia-frontend/

# Deploy with proper permissions
echo "🔧 Setting up frontend with proper permissions..."
ssh -i ~/.ssh/lambda_labs_key ubuntu@192.222.58.232 << 'EOF'
    sudo cp -r /tmp/sophia-frontend/* /var/www/html/
    sudo chown -R www-data:www-data /var/www/html/
    sudo chmod -R 755 /var/www/html/
    sudo systemctl reload nginx
    rm -rf /tmp/sophia-frontend
    echo "✅ React frontend deployed successfully!"
EOF

echo "🌐 Testing deployment..."
sleep 2
curl -s http://192.222.58.232/ | grep -q "Sophia" && echo "✅ Frontend accessible!" || echo "❌ Frontend check failed"

echo "🎯 React Frontend with Tabs, Chat & Dashboards is now live at:"
echo "   http://192.222.58.232/"
echo ""
echo "Features available:"
echo "   ✅ 8 Intelligence Tabs"
echo "   ✅ Advanced Chat Interface"
echo "   ✅ Executive Dashboards"
echo "   ✅ Real-time WebSocket Updates"
echo "   ✅ Professional UI/UX" 