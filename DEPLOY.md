# 部署指南

## 本地测试

### 后端
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload
```

访问 http://localhost:8000/api/health

### 前端
```bash
cd frontend
npm install
npm run dev
```

访问 http://localhost:5173

## Azure 部署

### 前提条件
- Azure CLI 已安装并登录：`az login`
- Node.js 和 npm 已安装

### 一键部署
```bash
cd deployment
./deploy.sh
```

部署完成后会显示访问链接，例如：
```
https://food-nutrition-1710234567.azurewebsites.net
```

### 手动部署
见 `deployment/README.md` 详细步骤。

### 配置 Redis（可选）
如需启用缓存：
```bash
RESOURCE_GROUP="rg-food-nutrition"
APP_NAME="your-app-name"

# 创建 Redis
az redis create \
  --name "${APP_NAME}-redis" \
  --resource-group "$RESOURCE_GROUP" \
  --location "eastasia" \
  --sku Basic \
  --vm-size c0

# 获取连接信息
REDIS_HOST=$(az redis show --name "${APP_NAME}-redis" --resource-group "$RESOURCE_GROUP" --query "hostName" -o tsv)
REDIS_KEY=$(az redis list-keys --name "${APP_NAME}-redis" --resource-group "$RESOURCE_GROUP" --query "primaryKey" -o tsv)

# 更新环境变量
az webapp config appsettings set \
  --name "$APP_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --settings \
    REDIS_HOST="$REDIS_HOST" \
    REDIS_PORT="6380" \
    REDIS_PASSWORD="$REDIS_KEY"
```

## 故障排查

### 查看日志
```bash
az webapp log tail --name <APP_NAME> --resource-group rg-food-nutrition
```

### 重启应用
```bash
az webapp restart --name <APP_NAME> --resource-group rg-food-nutrition
```

### SSH 进入容器
```bash
az webapp ssh --name <APP_NAME> --resource-group rg-food-nutrition
```

## 更新部署
```bash
# 拉取最新代码
git pull

# 重新部署
cd deployment
./deploy.sh
```
