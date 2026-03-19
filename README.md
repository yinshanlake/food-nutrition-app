# 食物营养查询网站 - 快速开始

## 项目概览
一个帮助减脂人群快速查询食物营养信息的 Web 应用。

**核心功能**:
- 🔍 快速搜索食物营养数据（USDA 官方数据源）
- 💡 智能减脂建议（能不能吃 + 怎么健康吃）
- 🍳 菜谱推荐
- 📊 折叠式卡片展示（核心信息 + 详情）
- ⚡ Redis 缓存加速（可选）

**技术栈**:
- 后端: FastAPI + Python 3.11+
- 前端: React + Vite
- 部署: Azure App Service
- 数据源: USDA FoodData Central API

## 本地运行

### 1. 克隆项目
```bash
git clone https://github.com/yinshanlake/food-nutrition-app.git
cd food-nutrition-app
```

### 2. 启动后端
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload
```

后端运行在 http://localhost:8000

### 3. 启动前端（新终端）
```bash
cd frontend
npm install
npm run dev
```

前端运行在 http://localhost:5173

### 4. 测试
打开浏览器访问 http://localhost:5173，输入 "chicken" 或 "鸡肉" 测试。

## 部署到 Azure

### 前提条件
- Azure 账号
- 已安装 Azure CLI：`az login`

### 一键部署
```bash
cd deployment
./deploy.sh
```

部署完成后会显示访问链接，例如：
```
https://food-nutrition-1710234567.azurewebsites.net
```

详细部署文档见 `DEPLOY.md`。

## 项目结构
```
food-nutrition-app/
├── backend/          # FastAPI 后端
│   ├── main.py      # 主应用
│   ├── requirements.txt
│   └── .env.example
├── frontend/         # React 前端
│   ├── src/
│   │   ├── App.jsx  # 主组件
│   │   └── App.css
│   └── package.json
├── deployment/       # Azure 部署配置
│   ├── deploy.sh    # 一键部署脚本
│   └── README.md
├── DEPLOY.md        # 部署指南
└── README.md
```

## API 文档

### GET /api/search
查询食物营养信息

**参数**:
- `q` (string, required): 食物名称（中英文）

**响应示例**:
```json
{
  "query": "chicken",
  "nutrition": [
    {
      "name": "Chicken, breast, meat only, cooked, roasted",
      "calories": 165,
      "protein": 31.0,
      "fat": 3.6,
      "carbs": 0,
      "fiber": 0,
      "source": "USDA",
      "serving_size": "100g"
    }
  ],
  "advice": {
    "is_suitable": true,
    "rating": 5,
    "reason": "热量165kcal，蛋白质31.0g，脂肪3.6g",
    "tips": [
      "热量适中，适合减脂期",
      "蛋白质含量丰富，有助于维持肌肉"
    ],
    "recipes": [
      "清蒸Chicken（少油少盐）",
      "水煮Chicken + 西兰花"
    ]
  }
}
```

### GET /api/health
健康检查

## 下一步开发

当前为 MVP 版本，后续可扩展功能：
- [ ] 中文食物数据源接入（薄荷健康 API）
- [ ] 收藏夹功能
- [ ] 每日营养摄入记录
- [ ] LLM 增强的个性化建议（DeepSeek API）
- [ ] 移动端适配优化

## 贡献
欢迎提 Issue 和 PR！

## License
MIT
