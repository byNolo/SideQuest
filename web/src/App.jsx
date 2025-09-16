import { useEffect, useState } from 'react'

export default function App(){
  const [quest, setQuest] = useState(null)
  const [me, setMe] = useState(null)
  useEffect(()=>{
    fetch('/api/quests/today').then(r=>r.json()).then(setQuest)
    fetch('/api/auth/me', { credentials: 'include' })
      .then(r=> r.ok ? r.json() : { authenticated:false })
      .then(setMe)
  },[])
  const startLogin = async () => {
    const r = await fetch('/api/auth/login-url')
    const data = await r.json()
    if (data.url) window.location.href = data.url
  }
  const logout = async () => {
    await fetch('/api/auth/logout', { method:'POST', credentials:'include' })
    setMe({ authenticated:false })
  }
  return (
    <div className="max-w-3xl mx-auto p-6">
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-3xl font-bold">Today’s SideQuest</h1>
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
        <div className="rounded-2xl p-4 bg-zinc-900 border border-zinc-800">
          <div className="text-xl font-semibold">{quest.title}</div>
          <p className="opacity-75">{quest.details}</p>
        </div>
      ) : (
        <div className="opacity-60">Loading…</div>
      )}
    </div>
  )
}
