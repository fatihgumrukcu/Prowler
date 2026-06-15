const TTL_MS = 24 * 60 * 60 * 1000 // 24 saat

interface Entry<T> {
  data: T
  ts: number
}

function storageKey(type: string, url: string) {
  return `prowler:${type}:${url}`
}

export function cacheSet<T>(type: string, url: string, data: T): void {
  try {
    localStorage.setItem(storageKey(type, url), JSON.stringify({ data, ts: Date.now() }))
    localStorage.setItem('prowler:lastUrl', url)
    localStorage.setItem('prowler:lastMode', type)
  } catch {}
}

export function cacheGet<T>(type: string, url: string): T | null {
  try {
    const raw = localStorage.getItem(storageKey(type, url))
    if (!raw) return null
    const entry: Entry<T> = JSON.parse(raw)
    if (Date.now() - entry.ts > TTL_MS) {
      localStorage.removeItem(storageKey(type, url))
      return null
    }
    return entry.data
  } catch {
    return null
  }
}

export function cacheGetLast(): { url: string; mode: string } | null {
  try {
    const url = localStorage.getItem('prowler:lastUrl')
    const mode = localStorage.getItem('prowler:lastMode')
    if (url && mode) return { url, mode }
  } catch {}
  return null
}

export function cacheClear(type: string, url: string): void {
  try {
    localStorage.removeItem(storageKey(type, url))
  } catch {}
}
