import { useEffect, useState } from 'react'

export default function App(){
  const [quest, setQuest] = useState(null)
  const [me, setMe] = useState(null)
  const [loading, setLoading] = useState(true)
  
  useEffect(()=>{
    Promise.all([
      fetch('/api/quests/today').then(r=>r.json()),
      fetch('/api/auth/me', { credentials: 'include' })
        .then(r=> r.ok ? r.json() : { authenticated:false })
    ]).then(([questData, userData]) => {
      setQuest(questData)
      setMe(userData)
      setLoading(false)
    })
  },[])
  
  const startLogin = async () => {
    const r = await fetch('/api/auth/login-url')
    const data = await r.json()
    if (data.url) window.location.href = data.url
  }
  
  const logout = async () => {
    await fetch('/api/auth/logout', { method:'POST', credentials:'include' })
    setMe({ authenticated:false })
    // Refresh quest to get generic version
    const questData = await fetch('/api/quests/today').then(r=>r.json())
    setQuest(questData)
  }

  const getDifficultyColor = (difficulty) => {
    if (difficulty <= 2) return 'text-green-400'
    if (difficulty <= 3) return 'text-yellow-400'
    return 'text-red-400'
  }

  const getRarityColor = (rarity) => {
    switch(rarity) {
      case 'common': return 'text-gray-400'
      case 'rare': return 'text-blue-400'
      case 'legendary': return 'text-purple-400'
      default: return 'text-gray-400'
    }
  }
  
  if (loading) {
    return (
      <div className="max-w-3xl mx-auto p-6">
        <div className="opacity-60">Loading your quest...</div>
      </div>
    )
  }
  
  return (
    <div className="max-w-3xl mx-auto p-6">
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-3xl font-bold">Today's SideQuest</h1>
        <div>
          {me?.authenticated ? (
            <div className="flex items-center gap-3">
              <span className="opacity-80">{me.user?.display_name || me.user?.username}</span>
              <button onClick={logout} className="px-3 py-1 rounded bg-zinc-800 border border-zinc-700">Logout</button>
            </div>
          ) : (
            <button onClick={startLogin} className="px-3 py-1 rounded bg-emerald-600">Login with KeyN</button>
          )}
        </div>
      </div>
      
      {quest ? (
        <div className="space-y-4">
          <div className="rounded-2xl p-6 bg-zinc-900 border border-zinc-800">
            <div className="flex items-start justify-between mb-3">
              <div>
                <h2 className="text-xl font-semibold mb-1">{quest.title}</h2>
                <div className="flex items-center gap-3 text-sm opacity-75">
                  <span className={getDifficultyColor(quest.difficulty)}>
                    Difficulty: {quest.difficulty}/5
                  </span>
                  {quest.rarity && (
                    <span className={getRarityColor(quest.rarity)}>
                      {quest.rarity.charAt(0).toUpperCase() + quest.rarity.slice(1)}
                    </span>
                  )}
                  <span className="text-zinc-400">{quest.date}</span>
                </div>
              </div>
            </div>
            
            <p className="text-zinc-300 mb-4 leading-relaxed">{quest.details}</p>
            
            {quest.weather && (
              <div className="mb-4 p-3 rounded-lg bg-zinc-800/50 border border-zinc-700/50">
                <div className="text-sm text-zinc-400 mb-1">Current Weather</div>
                <div className="flex items-center gap-2">
                  <span className="text-zinc-200">{quest.weather.description}</span>
                  {quest.weather.tags && quest.weather.tags.length > 0 && (
                    <div className="flex gap-1">
                      {quest.weather.tags.slice(0, 3).map(tag => (
                        <span key={tag} className="px-2 py-0.5 text-xs rounded bg-zinc-700 text-zinc-300">
                          {tag}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            )}
            
            {quest.context && Object.keys(quest.context).length > 0 && (
              <div className="mb-4 p-3 rounded-lg bg-zinc-800/50 border border-zinc-700/50">
                <div className="text-sm text-zinc-400 mb-2">Quest Details</div>
                <div className="grid grid-cols-2 gap-2 text-sm">
                  {quest.context.place && (
                    <div>
                      <span className="text-zinc-400">Suggested location:</span>
                      <div className="text-zinc-200">{quest.context.place.name}</div>
                    </div>
                  )}
                  {quest.context.radius_km && (
                    <div>
                      <span className="text-zinc-400">Within:</span>
                      <div className="text-zinc-200">{quest.context.radius_km} km</div>
                    </div>
                  )}
                  {quest.context.modifier && (
                    <div className="col-span-2">
                      <span className="text-zinc-400">Focus on:</span>
                      <div className="text-zinc-200">{quest.context.modifier}</div>
                    </div>
                  )}
                </div>
              </div>
            )}
            
            {quest.tags && quest.tags.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {quest.tags.map(tag => (
                  <span key={tag} className="px-2 py-1 text-xs rounded bg-zinc-700 text-zinc-300">
                    {tag.replace('_', ' ')}
                  </span>
                ))}
              </div>
            )}
            
            {quest.note && (
              <div className="mt-4 p-3 rounded bg-blue-900/20 border border-blue-700/30 text-blue-200 text-sm">
                💡 {quest.note}
              </div>
            )}
          </div>
          
          {quest.id && (
            <div className="text-center">
              <button className="px-6 py-3 rounded-xl bg-emerald-600 hover:bg-emerald-700 font-semibold transition-colors">
                Start Quest
              </button>
            </div>
          )}
        </div>
      ) : (
        <div className="opacity-60">No quest available today</div>
      )}
    </div>
  )
}
