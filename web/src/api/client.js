const API_BASE = (() => {
  const base = import.meta.env.VITE_API_BASE_URL
  if (!base) return '/api'
  return `${base.replace(/\/$/, '')}/api`
})()

async function parseJson(response) {
  const text = await response.text()
  if (!text) return null
  try {
    return JSON.parse(text)
  } catch (err) {
    console.error('Failed to parse JSON response', err)
    throw new Error('Invalid server response')
  }
}

export async function apiFetch(
  path,
  { method = 'GET', body, debugUser, headers, signal, timeoutMs = 10000 } = {}
) {
  console.log(`[API] ${method} ${API_BASE}${path}`, { debugUser, timeoutMs })

  const controller = !signal ? new AbortController() : null
  const timeoutId = controller
    ? setTimeout(() => {
        const reason =
          typeof DOMException !== 'undefined'
            ? new DOMException('Request timed out', 'TimeoutError')
            : new Error('Request timed out')
        controller.abort(reason)
      }, timeoutMs)
    : null

  const init = {
    method,
    headers: {
      'Content-Type': 'application/json',
      ...(headers || {}),
    },
    signal: signal || controller?.signal,
  }

  if (body !== undefined) {
    init.body = typeof body === 'string' ? body : JSON.stringify(body)
  }

  if (debugUser) {
    init.headers['X-Debug-User'] = debugUser
  }

  let response
  try {
    response = await fetch(`${API_BASE}${path}`, init)
    console.log(`[API] Response ${response.status} for ${method} ${path}`)
  } finally {
    if (timeoutId) clearTimeout(timeoutId)
  }

  const data = await parseJson(response)

  if (!response.ok) {
    const message = (data && data.error) || `Request failed with status ${response.status}`
    const error = new Error(message)
    error.status = response.status
    error.payload = data
    console.error(`[API] Error ${response.status}:`, message, data)
    throw error
  }

  console.log(`[API] Success for ${method} ${path}:`, data)
  return data
}

export { API_BASE }
