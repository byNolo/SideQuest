import { useEffect, useState } from 'react'
import { useDebugUser } from '../context/DebugUserContext'

export default function DebugUserSelector() {
  const { debugUser, setDebugUser } = useDebugUser()
  const [value, setValue] = useState(debugUser)

  useEffect(() => {
    setValue(debugUser)
  }, [debugUser])

  return (
    <form
      onSubmit={(event) => {
        event.preventDefault()
        setDebugUser(value.trim())
      }}
      className="flex w-full flex-col gap-2 text-sm sm:w-auto sm:flex-row sm:items-center"
    >
      <label htmlFor="debug-user" className="text-xs font-semibold uppercase tracking-wide text-slate-400">
        Debug user
      </label>
      <div className="flex flex-1 items-center gap-2 sm:w-72">
        <input
          id="debug-user"
          value={value}
          onChange={(event) => setValue(event.target.value)}
          placeholder="e.g. explorer-dev"
          className="flex-1 rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-xs text-slate-100 transition focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/40"
        />
        <button
          type="submit"
          className="rounded-lg bg-blue-500 px-3 py-2 text-xs font-semibold uppercase tracking-wide text-blue-50 transition hover:bg-blue-400"
        >
          Save
        </button>
      </div>
    </form>
  )
}
