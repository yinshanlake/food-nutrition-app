#!/bin/bash
# 测试脚本

echo "🧪 测试 Food Nutrition API"
echo ""

# 测试 1: Health Check
echo "1. Health Check"
curl -s http://localhost:8000/api/health | python3 -m json.tool
echo ""

# 测试 2: 搜索鸡肉
echo "2. 搜索: chicken"
curl -s "http://localhost:8000/api/search?q=chicken" | python3 -m json.tool | head -50
echo ""

# 测试 3: 搜索牛肉
echo "3. 搜索: beef"
curl -s "http://localhost:8000/api/search?q=beef" | python3 -m json.tool | head -50
echo ""

# 测试 4: 搜索蔬菜
echo "4. 搜索: broccoli"
curl -s "http://localhost:8000/api/search?q=broccoli" | python3 -m json.tool | head -50
echo ""

echo "✅ 测试完成"
