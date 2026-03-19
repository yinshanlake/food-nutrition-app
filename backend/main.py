from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional, Dict
import httpx
import redis
import json
import os
from dotenv import load_dotenv
import hashlib
from pathlib import Path

load_dotenv()

app = FastAPI(title="Food Nutrition API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis
try:
    redis_client = redis.Redis(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", 6379)),
        password=os.getenv("REDIS_PASSWORD", None),
        decode_responses=True
    )
    redis_client.ping()
    REDIS_ENABLED = True
except:
    REDIS_ENABLED = False
    print("⚠️  Redis not available, running without cache")

USDA_API_KEY = os.getenv("USDA_API_KEY", "DEMO_KEY")

# Models
class NutritionData(BaseModel):
    name: str
    calories: float
    protein: float
    fat: float
    carbs: float
    fiber: Optional[float] = None
    source: str
    serving_size: str

class FoodAdvice(BaseModel):
    is_suitable: bool
    rating: int  # 1-5
    reason: str
    tips: List[str]
    recipes: List[str]

class FoodResponse(BaseModel):
    query: str
    nutrition: List[NutritionData]
    advice: FoodAdvice

# Cache helper
def get_cache_key(query: str) -> str:
    return f"food:{hashlib.md5(query.lower().encode()).hexdigest()}"

def get_from_cache(key: str) -> Optional[dict]:
    if not REDIS_ENABLED:
        return None
    try:
        data = redis_client.get(key)
        return json.loads(data) if data else None
    except:
        return None

def set_cache(key: str, data: dict, ttl: int = 3600):
    if not REDIS_ENABLED:
        return
    try:
        redis_client.setex(key, ttl, json.dumps(data))
    except:
        pass

# USDA API
async def search_usda(query: str) -> List[NutritionData]:
    url = "https://api.nal.usda.gov/fdc/v1/foods/search"
    params = {
        "api_key": USDA_API_KEY,
        "query": query,
        "pageSize": 3,
        "dataType": ["Foundation", "SR Legacy"]
    }
    
    try:
        # Use proxy only in dev environment
        client_kwargs = {"timeout": 10.0}
        if os.getenv("USE_PROXY", "false").lower() == "true":
            client_kwargs["proxy"] = "http://127.0.0.1:7890"
        
        async with httpx.AsyncClient(**client_kwargs) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            results = []
            for food in data.get("foods", [])[:3]:
                nutrients = {n["nutrientName"]: n["value"] for n in food.get("foodNutrients", [])}
                
                results.append(NutritionData(
                    name=food.get("description", "Unknown"),
                    calories=nutrients.get("Energy", 0),
                    protein=nutrients.get("Protein", 0),
                    fat=nutrients.get("Total lipid (fat)", 0),
                    carbs=nutrients.get("Carbohydrate, by difference", 0),
                    fiber=nutrients.get("Fiber, total dietary"),
                    source="USDA",
                    serving_size="100g"
                ))
            
            return results
    except Exception as e:
        print(f"USDA API error: {e}")
        return []

# Advice engine (rule-based)
def generate_advice(nutrition_list: List[NutritionData]) -> FoodAdvice:
    if not nutrition_list:
        return FoodAdvice(
            is_suitable=False,
            rating=0,
            reason="无法找到营养信息",
            tips=[],
            recipes=[]
        )
    
    # Use first result for evaluation
    food = nutrition_list[0]
    
    # Simple scoring rules
    score = 5
    tips = []
    recipes = []
    
    # High calorie penalty
    if food.calories > 300:
        score -= 1
        tips.append("热量较高，建议控制摄入量")
    else:
        tips.append("热量适中，适合减脂期")
    
    # High protein bonus
    if food.protein > 15:
        score = min(5, score + 1)
        tips.append("蛋白质含量丰富，有助于维持肌肉")
    
    # High fat penalty
    if food.fat > 15:
        score -= 1
        tips.append("脂肪含量较高，建议搭配蔬菜食用")
    
    # High fiber bonus
    if food.fiber and food.fiber > 3:
        score = min(5, score + 1)
        tips.append("膳食纤维丰富，增强饱腹感")
    
    is_suitable = score >= 3
    
    if is_suitable:
        recipes = [
            f"清蒸{food.name.split(',')[0]}（少油少盐）",
            f"水煮{food.name.split(',')[0]} + 西兰花",
            f"{food.name.split(',')[0]}沙拉（低脂酱汁）"
        ]
    
    reason = f"热量{food.calories:.0f}kcal，蛋白质{food.protein:.1f}g，脂肪{food.fat:.1f}g"
    
    return FoodAdvice(
        is_suitable=is_suitable,
        rating=max(1, score),
        reason=reason,
        tips=tips[:3],
        recipes=recipes[:2]
    )

@app.get("/api/search", response_model=FoodResponse)
async def search_food(q: str):
    if not q or len(q.strip()) < 2:
        raise HTTPException(status_code=400, detail="Query too short")
    
    # Check cache
    cache_key = get_cache_key(q)
    cached = get_from_cache(cache_key)
    if cached:
        return cached
    
    # Fetch from USDA
    nutrition_data = await search_usda(q)
    
    if not nutrition_data:
        raise HTTPException(status_code=404, detail="Food not found")
    
    # Generate advice
    advice = generate_advice(nutrition_data)
    
    response = FoodResponse(
        query=q,
        nutrition=nutrition_data,
        advice=advice
    )
    
    # Cache result
    set_cache(cache_key, response.model_dump())
    
    return response

@app.get("/api/health")
async def health():
    return {
        "status": "healthy",
        "redis": REDIS_ENABLED
    }

# Serve frontend static files
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/assets", StaticFiles(directory=static_dir / "assets"), name="assets")
    
    @app.get("/")
    async def serve_frontend():
        return FileResponse(static_dir / "index.html")
