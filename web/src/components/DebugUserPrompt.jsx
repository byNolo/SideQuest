import { useState } from 'react'
import { useDebugUser } from '../context/DebugUserContext'

export default function DebugUserPrompt() {
  const { setDebugUser } = useDebugUser()
  const [value, setValue] = useState('')

  return (
    <form
      onSubmit={(event) => {
        event.preventDefault()
        if (!value.trim()) return
        setDebugUser(value.trim())
      }}
      className="mt-6 flex flex-col gap-3 text-left"
    >
      <label htmlFor="debug-user-overlay" className="text-xs font-semibold uppercase tracking-wide text-slate-300">
        Debug username
      </label>
      <input
        id="debug-user-overlay"
        autoFocus
        value={value}
        onChange={(event) => setValue(event.target.value)}
        placeholder="e.g. explorer-dev"
        className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 focus:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-400/40"
      />
      <button
        type="submit"
        className="rounded-lg bg-blue-500 px-4 py-2 text-sm font-semibold uppercase tracking-wide text-blue-100 transition hover:bg-blue-400 disabled:cursor-not-allowed disabled:bg-blue-500/40"
        disabled={!value.trim()}
      >
        Start exploring
      </button>
    </form>
  )
}
