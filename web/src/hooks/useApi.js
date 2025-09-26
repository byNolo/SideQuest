import { useCallback } from 'react'
import { apiFetch } from '../api/client'
import { useDebugUser } from '../context/DebugUserContext'

export function useApi() {
  const { debugUser } = useDebugUser()

  const request = useCallback(
    (path, options) =>
      apiFetch(path, {
        timeoutMs: 10000,
        ...(options || {}),
        debugUser,
      }),
    [debugUser]
  )

  return { request, debugUser }
}
