# Azure App Service 部署指南

## 前提条件
- Azure 账号已登录：`az login`
- 已创建 Resource Group

## 部署步骤

### 1. 创建 App Service Plan + Web App
```bash
# 设置变量
RESOURCE_GROUP="your-resource-group"
APP_NAME="food-nutrition-$(date +%s)"
LOCATION="eastasia"

# 创建 App Service Plan (Linux, Free Tier)
az appservice plan create \
  --name "${APP_NAME}-plan" \
  --resource-group "$RESOURCE_GROUP" \
  --location "$LOCATION" \
  --is-linux \
  --sku B1

# 创建 Web App (Python 3.11)
az webapp create \
  --name "$APP_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --plan "${APP_NAME}-plan" \
  --runtime "PYTHON:3.11"
```

### 2. 配置环境变量
```bash
az webapp config appsettings set \
  --name "$APP_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --settings \
    USDA_API_KEY="DEMO_KEY" \
    REDIS_HOST="" \
    REDIS_PORT="6379" \
    REDIS_PASSWORD="" \
    SCM_DO_BUILD_DURING_DEPLOYMENT="true"
```

### 3. 部署后端
```bash
cd backend
zip -r deploy.zip . -x "*.pyc" -x "__pycache__/*" -x "venv/*"

az webapp deployment source config-zip \
  --name "$APP_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --src deploy.zip
```

### 4. 构建前端并部署为静态资源
```bash
cd ../frontend

# 设置后端 API URL
echo "VITE_API_URL=https://${APP_NAME}.azurewebsites.net" > .env.production

# 构建
npm run build

# 将 dist/ 部署到 Azure Static Web Apps 或直接放在 backend/static/
# 方案 A: 集成到后端
cp -r dist ../backend/static
cd ../backend
zip -r deploy.zip . -x "*.pyc" -x "__pycache__/*" -x "venv/*"
az webapp deployment source config-zip \
  --name "$APP_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --src deploy.zip
```

### 5. 配置启动命令
```bash
az webapp config set \
  --name "$APP_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --startup-file "gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000"
```

### 6. 验证
```bash
echo "访问: https://${APP_NAME}.azurewebsites.net"
```

## Redis 配置 (可选)
如需 Redis 缓存，创建 Azure Cache for Redis:
```bash
az redis create \
  --name "${APP_NAME}-redis" \
  --resource-group "$RESOURCE_GROUP" \
  --location "$LOCATION" \
  --sku Basic \
  --vm-size c0

# 获取连接信息
az redis show \
  --name "${APP_NAME}-redis" \
  --resource-group "$RESOURCE_GROUP" \
  --query "[hostName,sslPort]" -o tsv
```

## 持续部署
使用 GitHub Actions（见 `.github/workflows/azure-deploy.yml`）

## 故障排查
```bash
# 查看日志
az webapp log tail --name "$APP_NAME" --resource-group "$RESOURCE_GROUP"

# SSH 进容器
az webapp ssh --name "$APP_NAME" --resource-group "$RESOURCE_GROUP"
```
