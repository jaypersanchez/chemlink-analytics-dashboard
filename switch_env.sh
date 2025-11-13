#!/bin/bash

# Environment switcher for ChemLink Analytics Dashboard
# Usage: ./switch_env.sh [uat|prod|dev]

if [ -z "$1" ]; then
    echo "Usage: ./switch_env.sh [uat|prod|dev]"
    echo ""
    echo "Current environment:"
    grep "^APP_ENV=" .env | sed 's/APP_ENV=/  /'
    exit 1
fi

ENV=$1

if [ "$ENV" != "uat" ] && [ "$ENV" != "prod" ] && [ "$ENV" != "dev" ]; then
    echo "❌ Invalid environment: $ENV"
    echo "Valid options: uat, prod, dev"
    exit 1
fi

# Update .env file
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    sed -i '' "s/^APP_ENV=.*/APP_ENV=$ENV/" .env
else
    # Linux
    sed -i "s/^APP_ENV=.*/APP_ENV=$ENV/" .env
fi

echo "✅ Environment switched to: $ENV"
echo ""
echo "Database connections:"
case $ENV in
    uat)
        echo "  ChemLink: chemlink-service-stg"
        echo "  Engagement: engagement-platform-stg"
        ;;
    prod)
        echo "  ChemLink: chemlink-service-prd (READ-ONLY)"
        echo "  Engagement: engagement-platform-prd (needs connection)"
        ;;
    dev)
        echo "  ChemLink: chemlink-service-dev (K8s cluster - may not work)"
        ;;
esac
echo ""
echo "🔄 Restart the server for changes to take effect:"
echo "   ./stop.sh && ./start.sh"
