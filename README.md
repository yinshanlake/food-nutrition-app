# Food Nutrition App - 减脂食物营养查询

## 功能
- 快速查询食物营养信息（热量/蛋白质/脂肪）
- 多源数据聚合（USDA + 薄荷健康）
- 减脂建议（能不能吃 + 健康吃法 + 菜谱推荐）
- 折叠式卡片 UI
- Redis 缓存加速

## 技术栈
- Backend: FastAPI + Redis
- Frontend: React + Vite
- Deployment: Azure App Service

## 开发

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## 部署
见 `deployment/README.md`
