#!/bin/bash
set -e

# 配置
RESOURCE_GROUP="${AZURE_RESOURCE_GROUP:-rg-food-nutrition}"
APP_NAME="food-nutrition-$(date +%s)"
LOCATION="eastasia"

echo "🚀 开始部署到 Azure App Service"
echo "Resource Group: $RESOURCE_GROUP"
echo "App Name: $APP_NAME"

# 1. 创建资源组（如果不存在）
echo "1. 检查/创建资源组..."
if ! az group show --name "$RESOURCE_GROUP" &>/dev/null; then
    az group create --name "$RESOURCE_GROUP" --location "$LOCATION"
    echo "✅ 资源组已创建"
else
    echo "✅ 资源组已存在"
fi

# 2. 创建 App Service Plan
echo "2. 创建 App Service Plan..."
az appservice plan create \
    --name "${APP_NAME}-plan" \
    --resource-group "$RESOURCE_GROUP" \
    --location "$LOCATION" \
    --is-linux \
    --sku B1

# 3. 创建 Web App
echo "3. 创建 Web App..."
az webapp create \
    --name "$APP_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --plan "${APP_NAME}-plan" \
    --runtime "PYTHON:3.11"

# 4. 配置环境变量
echo "4. 配置环境变量..."
az webapp config appsettings set \
    --name "$APP_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --settings \
        USDA_API_KEY="DEMO_KEY" \
        SCM_DO_BUILD_DURING_DEPLOYMENT="true"

# 5. 配置启动命令
echo "5. 配置启动命令..."
az webapp config set \
    --name "$APP_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --startup-file "gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000"

# 6. 构建前端
echo "6. 构建前端..."
cd frontend
echo "VITE_API_URL=https://${APP_NAME}.azurewebsites.net" > .env.production
npm install
npm run build
cd ..

# 7. 整合前端到后端
echo "7. 整合前端到后端..."
rm -rf backend/static
cp -r frontend/dist backend/static

# 8. 部署
echo "8. 打包并部署..."
cd backend
zip -r deploy.zip . -x "*.pyc" -x "__pycache__/*" -x "venv/*"

az webapp deployment source config-zip \
    --name "$APP_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --src deploy.zip

rm deploy.zip
cd ..

echo "✅ 部署完成！"
echo "🌐 访问网站: https://${APP_NAME}.azurewebsites.net"
echo "📊 查看日志: az webapp log tail --name $APP_NAME --resource-group $RESOURCE_GROUP"

# 保存部署信息
echo "$APP_NAME" > .deployment-info
echo "APP_NAME=$APP_NAME" >> .deployment-info
echo "RESOURCE_GROUP=$RESOURCE_GROUP" >> .deployment-info
