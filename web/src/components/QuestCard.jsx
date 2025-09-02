export default function QuestCard({ quest }){
  return (
    <div className="rounded-2xl p-4 bg-zinc-900 border border-zinc-800">
      <div className="text-lg font-semibold">{quest.title}</div>
      <div className="opacity-70">Difficulty: {quest.difficulty}/5</div>
    </div>
  )
}
