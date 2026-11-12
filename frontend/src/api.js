const BASE = import.meta.env.VITE_API_URL || ''

// Read JSON from the FastAPI backend with useful errors.
export async function api(path, options = {}) {
  const response = await fetch(`${BASE}/api${path}`, options)
  const body = await response.json().catch(() => ({}))

  if (!response.ok) {
    throw new Error(body.detail || `Request failed: ${response.status}`)
  }

  return body
}

export function newThreadId() {
  return crypto.randomUUID()
}
