import { createContext, useContext, useEffect, useMemo, useState } from 'react'

const DebugUserContext = createContext({ debugUser: '', setDebugUser: () => {} })

export function DebugUserProvider({ children }) {
  const [debugUser, setDebugUser] = useState(() => localStorage.getItem('sq-debug-user') || '')

  useEffect(() => {
    if (debugUser) {
      localStorage.setItem('sq-debug-user', debugUser)
    } else {
      localStorage.removeItem('sq-debug-user')
    }
  }, [debugUser])

  const value = useMemo(() => ({ debugUser, setDebugUser }), [debugUser])

  return <DebugUserContext.Provider value={value}>{children}</DebugUserContext.Provider>
}

export function useDebugUser() {
  return useContext(DebugUserContext)
}
