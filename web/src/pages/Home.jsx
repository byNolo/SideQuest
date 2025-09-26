import { useEffect, useState } from 'react'
import { useApi } from '../hooks/useApi'
import { useDebugUser } from '../context/DebugUserContext'

function DetailRow({ label, value }) {
  return (
    <div className="flex items-center justify-between gap-4 text-sm">
      <span className="text-slate-400">{label}</span>
      <span className="font-medium text-slate-100">{value ?? '—'}</span>
    </div>
  )
}

function formatCategories(preferences) {
  const categories = preferences?.categories || []
  if (!categories.length) return 'Open'
  return categories
    .map((item) => item.charAt(0).toUpperCase() + item.slice(1))
    .join(', ')
}

export default function HomePage() {
  const { request } = useApi()
  const { debugUser } = useDebugUser()
  const [profile, setProfile] = useState(null)
  const [quest, setQuest] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [refreshIndex, setRefreshIndex] = useState(0)

  useEffect(() => {
    if (!debugUser) {
      setProfile(null)
      setQuest(null)
      return
    }

    let cancelled = false
    setLoading(true)
    setError(null)

    Promise.all([
      request('/me'),
      request('/quests/today', { timeoutMs: 15000 }),
    ])
      .then(([profileData, questData]) => {
        if (cancelled) return
        setProfile(profileData)
        setQuest(questData?.quest || null)
      })
      .catch((err) => {
        if (cancelled) return
        console.error('Failed to load dashboard data', err)
        let message = err?.message || 'Failed to load dashboard data.'
        if (err.name === 'AbortError' || /timed out/i.test(message)) {
          message = 'Timed out waiting for the API. Ensure the backend container is running and reachable.'
        } else if (err.status === 401) {
          message = 'Unauthorized. Add a debug username in the overlay above to load sandbox data.'
        }
        setError(message)
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [debugUser, refreshIndex, request])

  if (!debugUser) {
    return (
      <section className="rounded-2xl border border-slate-900 bg-slate-900/40 p-8 text-center text-sm text-slate-400">
        Pick a debug user above to preview the daily quest.
      </section>
    )
  }

  return (
    <div className="space-y-6">
      <header>
        <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Dashboard</p>
        <h2 className="text-2xl font-semibold text-slate-100">Today&apos;s quest preview</h2>
        <p className="text-sm text-slate-400">
          Review the personalized quest and current profile snapshot for your sandbox account.
        </p>
      </header>

      {error && (
        <div className="rounded-xl border border-rose-500/40 bg-rose-500/10 px-4 py-3 text-sm text-rose-300">
          {error}
        </div>
      )}

      <div className="grid gap-6 md:grid-cols-2">
        <section className="rounded-2xl border border-slate-900 bg-slate-900/40 p-6">
          <header className="mb-4 flex items-center justify-between">
            <h3 className="text-lg font-semibold text-slate-100">Profile snapshot</h3>
            {loading && <span className="text-xs text-slate-500">Refreshing…</span>}
          </header>
          {profile ? (
            <div className="space-y-3">
              <DetailRow label="Username" value={profile.username} />
              <DetailRow label="Display name" value={profile.display_name || profile.username} />
              <DetailRow label="Onboarding" value={profile.onboarding.completed ? 'Complete' : 'In progress'} />
              <DetailRow
                label="Default location"
                value={profile.location ? profile.location.name || `${profile.location.lat?.toFixed(3)}, ${profile.location.lon?.toFixed(3)}` : 'Unset'}
              />
              <DetailRow label="Notifications" value={profile.webpush_registered ? 'Registered' : 'Not configured'} />
              <DetailRow
                label="Privacy mode"
                value={profile.privacy === 'friends_only' ? 'Friends only' : 'Public'}
              />
              <DetailRow label="Quest focus" value={formatCategories(profile.quest_preferences)} />
            </div>
          ) : (
            <p className="text-sm text-slate-500">{loading ? 'Loading profile…' : 'No profile data yet.'}</p>
          )}
        </section>

        <section className="flex h-full flex-col rounded-2xl border border-slate-900 bg-slate-900/40 p-6">
          <header className="mb-4 flex items-center justify-between">
            <h3 className="text-lg font-semibold text-slate-100">Quest details</h3>
            <button
              type="button"
              onClick={() => setRefreshIndex((value) => value + 1)}
              className="rounded-lg border border-blue-500/40 bg-blue-500/10 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-blue-200 transition hover:bg-blue-500/20"
            >
              Refresh
            </button>
          </header>
          {quest ? (
            <div className="flex flex-1 flex-col gap-4 text-sm">
              <div>
                <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Title</p>
                <p className="text-lg font-semibold text-slate-100">{quest.title}</p>
              </div>
              <div>
                <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Description</p>
                <p className="text-slate-200">{quest.description}</p>
              </div>
              {quest.hints && quest.hints.length > 0 && (
                <div>
                  <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Hints</p>
                  <ul className="mt-2 space-y-2 text-slate-200">
                    {quest.hints.map((hint, index) => (
                      <li key={index} className="rounded-lg border border-slate-800/60 bg-slate-900/50 px-3 py-2">
                        {hint}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              {quest.location && (
                <div>
                  <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Suggested zone</p>
                  <p className="text-slate-200">
                    {quest.location.name || 'Unnamed spot'} · radius {quest.location.radius_km ?? 2} km
                  </p>
                </div>
              )}
            </div>
          ) : (
            <p className="text-sm text-slate-500">{loading ? 'Loading quest…' : 'No quest available yet.'}</p>
          )}
        </section>
      </div>
    </div>
  )
}
