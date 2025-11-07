#!/bin/bash
# Script to fix CSRF verification failed error

echo "🔧 LinkedRite CSRF Fix Script"
echo "============================="

cd ~/linkedrite 2>/dev/null || cd /root/linkedrite 2>/dev/null || { echo "Error: LinkedRite directory not found"; exit 1; }

# Function to get current server IP
get_server_ip() {
    # Try multiple methods to get the external IP
    SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || curl -s icanhazip.com 2>/dev/null || hostname -I | awk '{print $1}')
    echo "$SERVER_IP"
}

# Get current configuration
echo "Current configuration:"
echo "---------------------"
if [ -f .env ]; then
    echo "SITE_URL: $(grep '^SITE_URL=' .env || echo 'Not set')"
    echo "CSRF_TRUSTED_ORIGINS: $(grep '^CSRF_TRUSTED_ORIGINS=' .env || echo 'Not set')"
    echo "DEBUG: $(grep '^DEBUG=' .env || echo 'Not set')"
else
    echo "❌ .env file not found!"
    exit 1
fi

# Get server details
echo ""
echo "Server information:"
echo "------------------"
SERVER_IP=$(get_server_ip)
echo "Server IP: $SERVER_IP"
echo "Hostname: $(hostname)"

# Ask user for configuration
echo ""
echo "How do you access your LinkedRite application?"
echo "1. Using IP address (e.g., http://$SERVER_IP:8000)"
echo "2. Using domain name with HTTP (e.g., http://linkedrite.example.com)"
echo "3. Using domain name with HTTPS (e.g., https://linkedrite.example.com)"
read -p "Enter your choice (1-3): " CHOICE

case $CHOICE in
    1)
        SITE_URL="http://$SERVER_IP:8000"
        CSRF_ORIGINS="http://$SERVER_IP:8000"
        USE_HTTPS="False"
        ;;
    2)
        read -p "Enter your domain name (without http://): " DOMAIN
        SITE_URL="http://$DOMAIN"
        CSRF_ORIGINS="http://$DOMAIN,http://www.$DOMAIN"
        USE_HTTPS="False"
        ;;
    3)
        read -p "Enter your domain name (without https://): " DOMAIN
        SITE_URL="https://$DOMAIN"
        CSRF_ORIGINS="https://$DOMAIN,https://www.$DOMAIN"
        USE_HTTPS="True"
        ;;
    *)
        echo "Invalid choice!"
        exit 1
        ;;
esac

# Show what will be added
echo ""
echo "Will add/update these settings:"
echo "------------------------------"
echo "SITE_URL=$SITE_URL"
echo "CSRF_TRUSTED_ORIGINS=$CSRF_ORIGINS"
echo "USE_HTTPS=$USE_HTTPS"
echo "DEBUG=False"

# Confirm
read -p "Do you want to apply these settings? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 1
fi

# Backup .env file
cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
echo "✅ Backed up .env file"

# Update .env file
echo "Updating .env file..."

# Function to update or add a line in .env
update_env() {
    KEY=$1
    VALUE=$2
    if grep -q "^$KEY=" .env; then
        # Update existing
        sed -i "s|^$KEY=.*|$KEY=$VALUE|" .env
    else
        # Add new
        echo "$KEY=$VALUE" >> .env
    fi
}

# Update settings
update_env "SITE_URL" "$SITE_URL"
update_env "CSRF_TRUSTED_ORIGINS" "$CSRF_ORIGINS"
update_env "USE_HTTPS" "$USE_HTTPS"
update_env "DEBUG" "False"

echo "✅ Updated .env file"

# Restart web container
echo ""
echo "Restarting web container..."
if [ -f docker-compose.prod.yml ]; then
    docker-compose -f docker-compose.prod.yml restart web
else
    docker-compose restart web
fi

echo "✅ Web container restarted"

# Wait for container to be ready
echo "Waiting for application to be ready..."
sleep 10

# Test the application
echo ""
echo "Testing application..."
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$SITE_URL" || echo "Failed")
if [[ "$HTTP_STATUS" == "200" ]] || [[ "$HTTP_STATUS" == "302" ]]; then
    echo "✅ Application is responding (HTTP $HTTP_STATUS)"
else
    echo "⚠️  Application returned: $HTTP_STATUS"
fi

echo ""
echo "🎉 CSRF fix applied!"
echo ""
echo "Please try the following:"
echo "1. Clear your browser cookies/cache"
echo "2. Visit: $SITE_URL"
echo "3. Try to login/signup again"
echo ""
echo "If you still have issues:"
echo "- Use incognito/private browsing mode"
echo "- Check logs: docker-compose -f docker-compose.prod.yml logs web"
