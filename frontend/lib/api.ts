import type { AnalyzeResponse, CrawlJobResponse, GraphResponse } from './types'

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new Error(typeof body?.detail === 'string' ? body.detail : `Sunucu hatası ${res.status}`)
  }
  return res.json() as Promise<T>
}

export async function analyzeUrl(url: string): Promise<AnalyzeResponse> {
  const res = await fetch(`${API_URL}/api/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url }),
  })
  return handleResponse<AnalyzeResponse>(res)
}

export async function startCrawl(
  url: string,
  maxPages = 100,
  maxDepth = 3,
): Promise<{ job_id: string; status: string }> {
  const res = await fetch(`${API_URL}/api/crawl`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url, max_pages: maxPages, max_depth: maxDepth }),
  })
  return handleResponse(res)
}

export async function getCrawlJob(jobId: string): Promise<CrawlJobResponse> {
  const res = await fetch(`${API_URL}/api/crawl/${jobId}`)
  return handleResponse<CrawlJobResponse>(res)
}

export async function fetchPageSource(url: string): Promise<{ url: string; html: string }> {
  const res = await fetch(`${API_URL}/api/source?url=${encodeURIComponent(url)}`)
  return handleResponse(res)
}

export async function fetchGraph(jobId: string): Promise<GraphResponse> {
  const res = await fetch(`${API_URL}/api/crawl/${jobId}/graph`)
  return handleResponse<GraphResponse>(res)
}

export async function exportCrawl(jobId: string, format: 'csv' | 'json'): Promise<void> {
  const res = await fetch(`${API_URL}/api/crawl/${jobId}/export?format=${format}`)
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new Error(typeof body?.detail === 'string' ? body.detail : `Sunucu hatası ${res.status}`)
  }
  const blob = await res.blob()
  const disposition = res.headers.get('Content-Disposition') ?? ''
  const match = disposition.match(/filename="?([^";\n]+)"?/)
  const filename = match?.[1] ?? `prowler-export.${format}`
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}
