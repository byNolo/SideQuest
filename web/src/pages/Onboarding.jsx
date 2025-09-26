import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { useApi } from '../hooks/useApi'
import { useDebugUser } from '../context/DebugUserContext'

function StepBadge({ step }) {
  const base = 'flex items-center gap-2 rounded-xl border px-3 py-2 text-xs'
  if (step.completed) {
    return (
      <div className={`${base} border-emerald-500/40 bg-emerald-500/10 text-emerald-200`}>
        <span className="inline-flex h-4 w-4 items-center justify-center rounded-full border border-emerald-400/80 text-[10px]">✓</span>
        {step.label}
      </div>
    )
  }
  return (
    <div className={`${base} border-slate-800 bg-slate-900/50 text-slate-300`}>{step.label}</div>
  )
}

function Feedback({ message, tone = 'info' }) {
  if (!message) return null
  const styles = {
    info: 'border-blue-500/30 bg-blue-500/10 text-blue-200',
    success: 'border-emerald-500/30 bg-emerald-500/10 text-emerald-200',
    error: 'border-rose-500/30 bg-rose-500/10 text-rose-200',
  }
  return <p className={`rounded-lg border px-3 py-2 text-xs ${styles[tone] || styles.info}`}>{message}</p>
}

function LocationCard({ profile, status, onStepComplete }) {
  const { request } = useApi()
  const [query, setQuery] = useState('')
  const [radius, setRadius] = useState(() => profile?.location?.radius_km ?? 2)
  const [results, setResults] = useState([])
  const [searching, setSearching] = useState(false)
  const [saving, setSaving] = useState(false)
  const [geoWorking, setGeoWorking] = useState(false)
  const [feedback, setFeedback] = useState(null)

  const hasLocation = Boolean(profile?.location)

  const searchLocations = async (event) => {
    event.preventDefault()
    if (!query.trim()) return
    setSearching(true)
    setFeedback(null)
    try {
      const data = await request(`/geocode?q=${encodeURIComponent(query.trim())}`)
      setResults(data?.locations || [])
      if ((data?.locations || []).length === 0) {
        setFeedback({ tone: 'info', message: 'No matches found. Try a broader search.' })
      }
    } catch (err) {
      setFeedback({ tone: 'error', message: err.message })
    } finally {
      setSearching(false)
    }
  }

  const applyLocation = async (location, options = {}) => {
    setSaving(true)
    setFeedback(null)
    try {
      const precisionM = options.precisionM ?? null
      const source = options.source ?? 'geocode'
      await request('/me/location', {
        method: 'POST',
        body: {
          lat: Number(location.lat),
          lon: Number(location.lon),
          name: options.nameOverride || location.display_name || query.trim(),
          radius_km: Number(radius),
          source,
          precision_m: precisionM,
        },
      })
      await onStepComplete('location')
      setFeedback({ tone: 'success', message: 'Location saved successfully.' })
    } catch (err) {
      setFeedback({ tone: 'error', message: err.message })
    } finally {
      setSaving(false)
    }
  }

  const useCurrentLocation = () => {
    if (!('geolocation' in navigator)) {
      setFeedback({ tone: 'error', message: 'Your browser does not support geolocation.' })
      return
    }

    setGeoWorking(true)
    setFeedback(null)

    navigator.geolocation.getCurrentPosition(
      async (position) => {
        const { latitude, longitude, accuracy } = position.coords
        const baseName = `${latitude.toFixed(4)}, ${longitude.toFixed(4)}`

        try {
          let resolvedName = baseName
          try {
            const reverse = await request(
              `/geocode/reverse?lat=${encodeURIComponent(latitude)}&lon=${encodeURIComponent(longitude)}`
            )
            resolvedName = reverse?.location?.display_name || baseName
          } catch (reverseErr) {
            console.warn('Reverse geocode failed', reverseErr)
          }

          await applyLocation(
            { lat: latitude, lon: longitude, display_name: resolvedName },
            {
              source: 'geolocation',
              precisionM: typeof accuracy === 'number' ? accuracy : undefined,
              nameOverride: resolvedName,
            }
          )
        } catch (err) {
          setFeedback({ tone: 'error', message: err.message })
        } finally {
          setGeoWorking(false)
        }
      },
      (error) => {
        let message = 'Unable to retrieve your location.'
        if (error.code === error.PERMISSION_DENIED) {
          message = 'Location permission denied. Please allow access or use search instead.'
        } else if (error.code === error.POSITION_UNAVAILABLE) {
          message = 'Location information is unavailable. Try again in a moment.'
        } else if (error.code === error.TIMEOUT) {
          message = 'Location request timed out. Try again or use search.'
        }
        setGeoWorking(false)
        setFeedback({ tone: 'error', message })
      },
      {
        enableHighAccuracy: true,
        timeout: 1000 * 10,
        maximumAge: 1000 * 60,
      }
    )
  }

  return (
    <section className="rounded-2xl border border-slate-900 bg-slate-900/50 p-6">
      <header className="mb-4 flex flex-col gap-1">
        <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Step 1</p>
        <h3 className="text-lg font-semibold text-slate-100">Choose your home base</h3>
        <p className="text-sm text-slate-400">
          Set a default location so quests can adapt to your surroundings.
        </p>
      </header>

      <div className="space-y-4">
        {hasLocation && (
          <div className="rounded-xl border border-blue-500/30 bg-blue-500/10 px-4 py-3 text-sm text-blue-100">
            Current: {profile.location.name || 'Unnamed'} · radius {profile.location.radius_km ?? 2} km
          </div>
        )}

        <form onSubmit={searchLocations} className="space-y-3">
          <label className="text-xs font-semibold uppercase tracking-wide text-slate-400">
            Search for a place
          </label>
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Downtown Portland, OR"
            className="w-full rounded-lg border border-slate-800 bg-slate-950 px-3 py-2 text-sm text-slate-100 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/30"
          />
          <div className="flex items-center gap-3 text-xs">
            <label className="text-slate-500" htmlFor="radius-input">
              Radius (km)
            </label>
            <input
              id="radius-input"
              type="number"
              min="1"
              max="30"
              step="1"
              value={radius}
              onChange={(event) => setRadius(event.target.value)}
              className="w-20 rounded border border-slate-800 bg-slate-950 px-2 py-1 text-right text-sm text-slate-100"
            />
          </div>
          <button
            type="submit"
            disabled={searching}
            className="rounded-lg bg-blue-500 px-4 py-2 text-sm font-semibold text-blue-50 transition hover:bg-blue-400 disabled:cursor-not-allowed disabled:bg-blue-500/40"
          >
            {searching ? 'Searching…' : 'Find locations'}
          </button>
        </form>

        <div className="flex flex-wrap items-center gap-3">
          <button
            type="button"
            onClick={useCurrentLocation}
            disabled={geoWorking}
            className="rounded-lg border border-emerald-500/40 bg-emerald-500/10 px-3 py-2 text-xs font-semibold uppercase tracking-wide text-emerald-200 transition hover:bg-emerald-500/20 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {geoWorking ? 'Locating…' : 'Use current location'}
          </button>
          <p className="text-xs text-slate-500">We&apos;ll try to pinpoint you automatically, then you can adjust the radius.</p>
        </div>

        {results.length > 0 && (
          <ul className="space-y-3 text-sm">
            {results.map((location) => (
              <li key={`${location.lat}-${location.lon}-${location.display_name}`}
                className="rounded-xl border border-slate-800 bg-slate-950/60 p-4">
                <p className="font-medium text-slate-100">{location.display_name}</p>
                <p className="text-xs text-slate-500">
                  {Number(location.lat).toFixed(4)}, {Number(location.lon).toFixed(4)} · {location.type}
                </p>
                <button
                  type="button"
                  onClick={() => applyLocation(location)}
                  disabled={saving}
                  className="mt-3 rounded-lg border border-blue-500/40 bg-blue-500/10 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-blue-200 transition hover:bg-blue-500/20 disabled:cursor-not-allowed disabled:bg-blue-500/10"
                >
                  {saving ? 'Saving…' : 'Use this location'}
                </button>
              </li>
            ))}
          </ul>
        )}

        <Feedback message={feedback?.message} tone={feedback?.tone} />

        {status?.steps?.find((step) => step.id === 'location')?.completed && (
          <p className="text-xs text-emerald-300">Location step complete ✓</p>
        )}
      </div>
    </section>
  )
}

function PreferencesCard({ profile, onStepComplete }) {
  const { request } = useApi()
  const categories = useMemo(
    () => [
      { id: 'art', label: 'Creative & Art' },
      { id: 'outdoor', label: 'Outdoor Exploration' },
      { id: 'social', label: 'Social & Connection' },
      { id: 'mindful', label: 'Mindfulness & Reflection' },
    ],
    []
  )

  const initialCategories = useMemo(() => new Set(profile?.quest_preferences?.categories || []), [profile])
  const [selectedCategories, setSelectedCategories] = useState(initialCategories)
  const [preferredTime, setPreferredTime] = useState(profile?.quest_preferences?.preferred_time || 'any')
  const [spendLevel, setSpendLevel] = useState(profile?.quest_preferences?.spend_level || 'free')
  const [privacy, setPrivacy] = useState(profile?.privacy || 'public')
  const [saving, setSaving] = useState(false)
  const [feedback, setFeedback] = useState(null)

  useEffect(() => {
    setSelectedCategories(new Set(profile?.quest_preferences?.categories || []))
    setPreferredTime(profile?.quest_preferences?.preferred_time || 'any')
    setSpendLevel(profile?.quest_preferences?.spend_level || 'free')
    setPrivacy(profile?.privacy || 'public')
  }, [profile])

  const toggleCategory = (id) => {
    setSelectedCategories((prev) => {
      const next = new Set(prev)
      if (next.has(id)) {
        next.delete(id)
      } else {
        next.add(id)
      }
      return next
    })
  }

  const handleSave = async (event) => {
    event.preventDefault()
    setSaving(true)
    setFeedback(null)
    try {
      const questPreferences = {
        categories: Array.from(selectedCategories),
        preferred_time: preferredTime,
        spend_level: spendLevel,
      }
      await request('/me/preferences', {
        method: 'PATCH',
        body: {
          quest_preferences: questPreferences,
          privacy,
        },
      })
      await onStepComplete('preferences')
      setFeedback({ tone: 'success', message: 'Preferences updated.' })
    } catch (err) {
      setFeedback({ tone: 'error', message: err.message })
    } finally {
      setSaving(false)
    }
  }

  return (
    <section className="rounded-2xl border border-slate-900 bg-slate-900/50 p-6">
      <header className="mb-4 flex flex-col gap-1">
        <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Step 2</p>
        <h3 className="text-lg font-semibold text-slate-100">Tune your quest style</h3>
        <p className="text-sm text-slate-400">
          Highlight the types of adventures you&apos;re eager to receive.
        </p>
      </header>

      <form onSubmit={handleSave} className="space-y-5 text-sm">
        <div className="space-y-2">
          <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">Activity vibes</p>
          <div className="flex flex-wrap gap-2">
            {categories.map((category) => {
              const active = selectedCategories.has(category.id)
              return (
                <button
                  key={category.id}
                  type="button"
                  onClick={() => toggleCategory(category.id)}
                  className={`rounded-full px-3 py-1 text-xs font-semibold transition ${
                    active
                      ? 'bg-fuchsia-500/20 text-fuchsia-200 shadow-inner'
                      : 'bg-slate-900/70 text-slate-300 hover:text-slate-100'
                  }`}
                >
                  {category.label}
                </button>
              )
            })}
          </div>
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          <label className="flex flex-col gap-2">
            <span className="text-xs font-semibold uppercase tracking-wide text-slate-400">Preferred time</span>
            <select
              value={preferredTime}
              onChange={(event) => setPreferredTime(event.target.value)}
              className="rounded-lg border border-slate-800 bg-slate-950 px-3 py-2 text-sm text-slate-100 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/30"
            >
              <option value="any">Anytime</option>
              <option value="morning">Morning</option>
              <option value="afternoon">Afternoon</option>
              <option value="evening">Evening</option>
            </select>
          </label>

          <label className="flex flex-col gap-2">
            <span className="text-xs font-semibold uppercase tracking-wide text-slate-400">Spend level</span>
            <select
              value={spendLevel}
              onChange={(event) => setSpendLevel(event.target.value)}
              className="rounded-lg border border-slate-800 bg-slate-950 px-3 py-2 text-sm text-slate-100 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/30"
            >
              <option value="free">Free / Zero spend</option>
              <option value="under-20">Under $20</option>
              <option value="splurge">Let&apos;s splurge</option>
            </select>
          </label>
        </div>

        <div className="space-y-2">
          <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">Privacy mode</p>
          <div className="grid gap-3 sm:grid-cols-2">
            <button
              type="button"
              onClick={() => setPrivacy('public')}
              className={`rounded-xl border px-4 py-3 text-left text-xs transition ${
                privacy === 'public'
                  ? 'border-emerald-500/40 bg-emerald-500/10 text-emerald-100 shadow-inner'
                  : 'border-slate-800 bg-slate-950/60 text-slate-300 hover:border-slate-700 hover:text-slate-100'
              }`}
            >
              <span className="block text-sm font-semibold">Public</span>
              <span className="mt-1 block text-[11px] text-slate-400">
                Share your completed quests to the global feed once submissions launch.
              </span>
            </button>
            <button
              type="button"
              onClick={() => setPrivacy('friends_only')}
              className={`rounded-xl border px-4 py-3 text-left text-xs transition ${
                privacy === 'friends_only'
                  ? 'border-indigo-500/40 bg-indigo-500/10 text-indigo-100 shadow-inner'
                  : 'border-slate-800 bg-slate-950/60 text-slate-300 hover:border-slate-700 hover:text-slate-100'
              }`}
            >
              <span className="block text-sm font-semibold">Friends only</span>
              <span className="mt-1 block text-[11px] text-slate-400">
                Keep your adventures private except for people you approve.
              </span>
            </button>
          </div>
        </div>

        <button
          type="submit"
          disabled={saving}
          className="rounded-lg bg-fuchsia-500 px-4 py-2 text-sm font-semibold text-fuchsia-50 transition hover:bg-fuchsia-400 disabled:cursor-not-allowed disabled:bg-fuchsia-500/40"
        >
          {saving ? 'Saving…' : 'Save preferences'}
        </button>

        <Feedback message={feedback?.message} tone={feedback?.tone} />
      </form>
    </section>
  )
}

function NotificationsCard({ status, onStepComplete, onRefresh }) {
  const { request } = useApi()
  const [working, setWorking] = useState(false)
  const [feedback, setFeedback] = useState(null)

  const notificationsStep = status?.steps?.find((step) => step.id === 'notifications')
  const registered = Boolean(notificationsStep?.completed)

  const simulateRegistration = async () => {
    setWorking(true)
    setFeedback(null)
    try {
      await request('/me/notifications/register', {
        method: 'POST',
        body: {
          endpoint: `debug-simulated-${Date.now()}`,
          keys: {
            auth: 'debug-auth',
            p256dh: 'debug-p256',
          },
        },
      })
      await onStepComplete('notifications')
      setFeedback({
        tone: 'success',
        message: 'Simulated push subscription saved. Replace with the real service worker when ready.',
      })
    } catch (err) {
      setFeedback({ tone: 'error', message: err.message })
    } finally {
      setWorking(false)
    }
  }

  const clearRegistration = async () => {
    setWorking(true)
    setFeedback(null)
    try {
      await request('/me/notifications/register', {
        method: 'DELETE',
      })
      await onRefresh()
      setFeedback({ tone: 'success', message: 'Notification preference cleared.' })
    } catch (err) {
      setFeedback({ tone: 'error', message: err.message })
    } finally {
      setWorking(false)
    }
  }

  return (
    <section className="rounded-2xl border border-slate-900 bg-slate-900/50 p-6">
      <header className="mb-4 flex flex-col gap-1">
        <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Step 3</p>
        <h3 className="text-lg font-semibold text-slate-100">Enable quest pings</h3>
        <p className="text-sm text-slate-400">
          Register a web push subscription so SideQuest can nudge you when fresh adventures arrive.
        </p>
      </header>

      <div className="space-y-4 text-sm text-slate-300">
        <p>
          We don&apos;t have the full notification worker wired up yet, so for now we store a simulated
          push subscription. This keeps the backend data model in sync while we finish the browser
          integration.
        </p>

        <div className={`rounded-xl border px-4 py-3 text-xs ${registered ? 'border-emerald-500/40 bg-emerald-500/10 text-emerald-200' : 'border-slate-800 bg-slate-950/70 text-slate-300'}`}>
          Status: {registered ? 'Notifications registered' : 'Not registered yet'}
        </div>

        <div className="flex flex-wrap gap-3">
          <button
            type="button"
            onClick={simulateRegistration}
            disabled={working}
            className="rounded-lg bg-indigo-500 px-4 py-2 text-xs font-semibold uppercase tracking-wide text-indigo-50 transition hover:bg-indigo-400 disabled:cursor-not-allowed disabled:bg-indigo-500/40"
          >
            {working ? 'Saving…' : registered ? 'Re-register debug push' : 'Simulate push registration'}
          </button>
          <button
            type="button"
            onClick={clearRegistration}
            disabled={working || !registered}
            className="rounded-lg border border-slate-700 px-4 py-2 text-xs font-semibold uppercase tracking-wide text-slate-300 transition hover:border-slate-500 hover:text-slate-100 disabled:cursor-not-allowed disabled:opacity-50"
          >
            Clear registration
          </button>
        </div>

        <Feedback message={feedback?.message} tone={feedback?.tone} />
      </div>
    </section>
  )
}

function CompletionCard({ status, onStepComplete }) {
  const [finishing, setFinishing] = useState(false)
  const [feedback, setFeedback] = useState(null)

  const finishOnboarding = async () => {
    setFinishing(true)
    setFeedback(null)
    try {
      await onStepComplete('complete')
      setFeedback({ tone: 'success', message: 'Onboarding marked complete—nice work!' })
    } catch (err) {
      setFeedback({ tone: 'error', message: err.message })
    } finally {
      setFinishing(false)
    }
  }

  const completed = Boolean(status?.completed)

  return (
    <section className="rounded-2xl border border-slate-900 bg-slate-900/50 p-6">
      <header className="mb-4 flex flex-col gap-1">
  <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Step 4</p>
        <h3 className="text-lg font-semibold text-slate-100">Wrap up &amp; preview next steps</h3>
        <p className="text-sm text-slate-400">
          Lock in your setup so you can focus on daily adventures.
        </p>
      </header>

      <div className="space-y-4 text-sm text-slate-300">
        <p>
          You&apos;re almost ready! Once you mark onboarding complete, today&apos;s quest will adapt to your
          preferences and future steps (like notifications) can build on this foundation.
        </p>

        <button
          type="button"
          onClick={finishOnboarding}
          disabled={finishing || completed}
          className="rounded-lg bg-emerald-500 px-4 py-2 text-sm font-semibold text-emerald-950 transition hover:bg-emerald-400 disabled:cursor-not-allowed disabled:bg-emerald-500/40"
        >
          {completed ? 'Onboarding complete' : finishing ? 'Marking complete…' : 'Mark onboarding complete'}
        </button>

        <Feedback message={feedback?.message} tone={feedback?.tone} />
      </div>
    </section>
  )
}

export default function OnboardingPage() {
  const { request } = useApi()
  const { debugUser } = useDebugUser()
  const [status, setStatus] = useState(null)
  const [profile, setProfile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [welcomeDismissed, setWelcomeDismissed] = useState(false)
  const locationSectionRef = useRef(null)

  const refresh = useCallback(async () => {
    if (!debugUser) {
      setStatus(null)
      setProfile(null)
      return
    }

    setLoading(true)
    setError(null)
    try {
      const [statusData, profileData] = await Promise.all([
        request('/me/onboarding/status'),
        request('/me'),
      ])
      setStatus(statusData)
      setProfile(profileData)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [debugUser, request])

  useEffect(() => {
    refresh().catch(() => {})
  }, [refresh])

  const anyStepCompleted = Boolean(status?.steps?.some((step) => step.completed))
  const showWelcome = Boolean(status?.steps?.length) && !welcomeDismissed && !anyStepCompleted

  useEffect(() => {
    if (anyStepCompleted) {
      setWelcomeDismissed(true)
    }
  }, [anyStepCompleted])

  useEffect(() => {
    setWelcomeDismissed(false)
  }, [debugUser])

  const startOnboarding = () => {
    setWelcomeDismissed(true)
    locationSectionRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }

  const skipWelcome = () => {
    setWelcomeDismissed(true)
  }

  const handleStepComplete = useCallback(
    async (step, options = {}) => {
      if (!options.skipCompleteStep) {
        await request('/me/onboarding/complete-step', {
          method: 'POST',
          body: { step },
        })
      }
      await refresh()
    },
    [refresh, request]
  )

  if (!debugUser) {
    return (
      <section className="rounded-2xl border border-slate-900 bg-slate-900/40 p-8 text-center text-sm text-slate-400">
        Add a debug username above to configure onboarding.
      </section>
    )
  }

  return (
    <div className="space-y-6">
      <header className="space-y-2">
        <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Onboarding</p>
        <h2 className="text-2xl font-semibold text-slate-100">Guide new explorers</h2>
        <p className="text-sm text-slate-400">
          Walk through the foundational steps SideQuest asks from every adventurer.
        </p>
        {loading && <p className="text-xs text-slate-500">Loading latest status…</p>}
      </header>

      {error && (
        <div className="rounded-xl border border-rose-500/40 bg-rose-500/10 px-4 py-3 text-sm text-rose-300">
          {error}
        </div>
      )}

      {status?.steps && (
        <div className="flex flex-wrap gap-2">
          {status.steps.map((step) => (
            <StepBadge key={step.id} step={step} />
          ))}
        </div>
      )}

      {showWelcome && (
        <section className="rounded-2xl border border-blue-500/30 bg-blue-500/10 p-6 text-slate-100">
          <header className="mb-4 space-y-2">
            <p className="text-xs uppercase tracking-[0.25em] text-blue-200/80">New explorer setup</p>
            <h3 className="text-2xl font-semibold">Let&apos;s get you ready for your first quest</h3>
            <p className="text-sm text-blue-100/80">
              We&apos;ll walk through a few quick steps: pick a home base, tailor quest preferences, and choose how visible your adventures should be. You can tweak everything later from the dashboard.
            </p>
          </header>
          <div className="flex flex-wrap items-center gap-3 text-sm">
            <button
              type="button"
              onClick={startOnboarding}
              className="rounded-lg bg-blue-500 px-4 py-2 font-semibold text-blue-50 transition hover:bg-blue-400"
            >
              Start with location
            </button>
            <button
              type="button"
              onClick={skipWelcome}
              className="rounded-lg border border-blue-400/40 px-4 py-2 font-semibold text-blue-100 transition hover:border-blue-300/60"
            >
              Jump to steps
            </button>
            <p className="text-xs text-blue-100/70">We&apos;ll check off each badge above as you finish.</p>
          </div>
        </section>
      )}

      <div className="grid gap-6 xl:grid-cols-2">
        <div ref={locationSectionRef}>
          <LocationCard profile={profile} status={status} onStepComplete={handleStepComplete} />
        </div>
        <PreferencesCard profile={profile} onStepComplete={handleStepComplete} />
        <NotificationsCard status={status} onStepComplete={handleStepComplete} onRefresh={refresh} />
        <CompletionCard status={status} onStepComplete={handleStepComplete} />
      </div>
    </div>
  )
}
