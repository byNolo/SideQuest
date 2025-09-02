import { useEffect, useState } from 'react'

export default function App(){
  const [quest, setQuest] = useState(null)
  useEffect(()=>{
    fetch('/api/quests/today').then(r=>r.json()).then(setQuest)
  },[])
  return (
    <div className="max-w-3xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-2">Today’s SideQuest</h1>
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
