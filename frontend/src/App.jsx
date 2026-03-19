import { useState } from 'react'
import './App.css'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function App() {
  const [query, setQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [expandedCards, setExpandedCards] = useState({})

  const handleSearch = async (e) => {
    e.preventDefault()
    if (!query.trim()) return

    setLoading(true)
    setError('')
    setResult(null)

    try {
      const response = await fetch(`${API_BASE}/api/search?q=${encodeURIComponent(query)}`)
      if (!response.ok) {
        throw new Error('食物未找到')
      }
      const data = await response.json()
      setResult(data)
      setExpandedCards({})
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const toggleCard = (index) => {
    setExpandedCards(prev => ({
      ...prev,
      [index]: !prev[index]
    }))
  }

  const getRatingColor = (rating) => {
    if (rating >= 4) return '#4CAF50'
    if (rating >= 3) return '#FF9800'
    return '#f44336'
  }

  return (
    <div className="app">
      <header className="header">
        <h1>🥗 减脂食物查询</h1>
        <p>快速查询食物营养 + 减脂建议</p>
      </header>

      <main className="main">
        <form onSubmit={handleSearch} className="search-form">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="输入食物名称（中英文）"
            className="search-input"
          />
          <button type="submit" disabled={loading} className="search-button">
            {loading ? '查询中...' : '搜索'}
          </button>
        </form>

        {error && (
          <div className="error">
            ❌ {error}
          </div>
        )}

        {result && (
          <div className="results">
            {/* Advice Card */}
            <div className="advice-card" style={{ borderColor: getRatingColor(result.advice.rating) }}>
              <div className="advice-header">
                <h2>
                  {result.advice.is_suitable ? '✅ 适合减脂' : '⚠️ 谨慎食用'}
                  <span className="rating" style={{ color: getRatingColor(result.advice.rating) }}>
                    {'⭐'.repeat(result.advice.rating)}
                  </span>
                </h2>
                <p className="reason">{result.advice.reason}</p>
              </div>

              <div className="advice-tips">
                <h3>💡 建议</h3>
                <ul>
                  {result.advice.tips.map((tip, i) => (
                    <li key={i}>{tip}</li>
                  ))}
                </ul>
              </div>

              {result.advice.recipes.length > 0 && (
                <div className="advice-recipes">
                  <h3>🍳 健康做法</h3>
                  <ul>
                    {result.advice.recipes.map((recipe, i) => (
                      <li key={i}>{recipe}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

            {/* Nutrition Cards */}
            <div className="nutrition-cards">
              <h3>📊 营养数据（多源对比）</h3>
              {result.nutrition.map((item, index) => (
                <div key={index} className="nutrition-card">
                  <div 
                    className="card-header"
                    onClick={() => toggleCard(index)}
                  >
                    <div>
                      <strong>{item.name}</strong>
                      <span className="source-badge">{item.source}</span>
                    </div>
                    <span className="expand-icon">
                      {expandedCards[index] ? '▼' : '▶'}
                    </span>
                  </div>

                  <div className="card-quick-info">
                    <div className="nutrient">
                      <span className="label">热量</span>
                      <span className="value">{item.calories.toFixed(0)} kcal</span>
                    </div>
                    <div className="nutrient">
                      <span className="label">蛋白质</span>
                      <span className="value">{item.protein.toFixed(1)}g</span>
                    </div>
                    <div className="nutrient">
                      <span className="label">脂肪</span>
                      <span className="value">{item.fat.toFixed(1)}g</span>
                    </div>
                  </div>

                  {expandedCards[index] && (
                    <div className="card-details">
                      <div className="nutrient">
                        <span className="label">碳水化合物</span>
                        <span className="value">{item.carbs.toFixed(1)}g</span>
                      </div>
                      {item.fiber && (
                        <div className="nutrient">
                          <span className="label">膳食纤维</span>
                          <span className="value">{item.fiber.toFixed(1)}g</span>
                        </div>
                      )}
                      <div className="nutrient">
                        <span className="label">参考份量</span>
                        <span className="value">{item.serving_size}</span>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </main>

      <footer className="footer">
        <p>数据来源: USDA FoodData Central | 建议仅供参考，请咨询专业营养师</p>
      </footer>
    </div>
  )
}

export default App
