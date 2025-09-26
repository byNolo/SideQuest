import { BrowserRouter, NavLink, Navigate, Route, Routes } from 'react-router-dom'

import { DebugUserProvider, useDebugUser } from './context/DebugUserContext'
import DebugUserSelector from './components/DebugUserSelector'
import DebugUserPrompt from './components/DebugUserPrompt'
import HomePage from './pages/Home'
import OnboardingPage from './pages/Onboarding'

function NavigationLink({ to, children }) {
  return (
    <NavLink
      to={to}
      end
      className={({ isActive }) =>
        `rounded-lg px-3 py-2 transition ${
          isActive ? 'bg-blue-500/10 text-blue-300' : 'text-slate-400 hover:text-slate-200'
        }`
      }
    >
      {children}
    </NavLink>
  )
}

function Layout({ children }) {
  const { debugUser } = useDebugUser()

  return (
    <div className="flex min-h-screen flex-col bg-slate-950 text-slate-100">
      <header className="border-b border-slate-900 bg-slate-900/60">
        <div className="mx-auto flex w-full max-w-6xl flex-col gap-4 px-6 py-5 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.3em] text-blue-400/80">SideQuest</p>
            <h1 className="text-2xl font-semibold tracking-tight text-slate-100">Creator Console</h1>
            <p className="text-xs text-slate-500">
              Map your onboarding flow, tweak preferences, and preview today&apos;s quest.
            </p>
          </div>
          <DebugUserSelector />
        </div>
      </header>

      <div className="mx-auto flex w-full max-w-6xl flex-1 flex-col gap-6 px-6 py-8 lg:flex-row lg:items-start">
        <aside className="flex flex-row gap-2 overflow-x-auto pb-2 text-sm lg:w-60 lg:flex-col lg:gap-3 lg:pb-0">
          <NavigationLink to="/">Daily quest</NavigationLink>
          <NavigationLink to="/onboarding">Onboarding setup</NavigationLink>
        </aside>

        <main className="flex-1">
          {children}
        </main>
      </div>

      {!debugUser && (
        <div className="fixed inset-0 flex items-center justify-center bg-slate-950/90 px-6">
          <div className="max-w-md rounded-2xl border border-slate-800 bg-slate-900/90 p-8 text-center shadow-xl">
            <h2 className="text-lg font-semibold text-slate-100">Choose a debug username to get started</h2>
            <p className="mt-2 text-sm text-slate-400">
              We&apos;ll auto-provision a sandbox user for any name you enter, so you can experiment freely
              without OAuth.
            </p>
            <DebugUserPrompt />
          </div>
        </div>
      )}
    </div>
  )
}

function AppShell() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/onboarding" element={<OnboardingPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  )
}

export default function App() {
  return (
    <DebugUserProvider>
      <AppShell />
    </DebugUserProvider>
  )
}
