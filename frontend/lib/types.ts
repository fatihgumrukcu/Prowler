export type CheckStatus = 'passed' | 'warning' | 'failed'

export interface Check {
  id: string
  category: string
  label: string
  status: CheckStatus
  message: string
  value: string | null
  recommendation: string | null
}

export interface Summary {
  passed: number
  warnings: number
  failed: number
}

export interface Metadata {
  title: string | null
  description: string | null
  canonical: string | null
  robots: string | null
  lang: string | null
  h1: string[]
  h2_count: number
  schema_types: string[]
  internal_links: number
  external_links: number
  images_total: number
  images_missing_alt: number
}

export interface AnalyzeResponse {
  url: string
  final_url: string
  status_code: number | null
  redirected: boolean
  score: number
  summary: Summary
  checks: Check[]
  metadata: Metadata
}

// ── Crawl types ───────────────────────────────────────────────────────────────

export interface PageResult {
  url: string
  final_url: string
  status_code: number | null
  score: number
  summary: Summary
  checks: Check[]
  discovery_source: string   // "start" | "sitemap" | "crawl"
  error: string | null
}

export interface SiteIssue {
  check_id: string
  category: string
  label: string
  status: CheckStatus
  page_count: number
  example_urls: string[]
}

export interface CrawlResult {
  start_url: string
  domain: string
  pages_crawled: number
  pages_failed: number
  site_score: number
  site_summary: Summary
  site_issues: SiteIssue[]
  sitemap_urls_found: number
  sitemap_urls_crawled: number
  sitemap_urls_unreachable: number
  pages: PageResult[]
}

export interface CrawlProgress {
  pages_found: number
  pages_done: number
  pages_failed: number
}

export interface CrawlJobResponse {
  job_id: string
  status: 'queued' | 'running' | 'done' | 'error'
  progress: CrawlProgress
  live_urls: string[]
  result: CrawlResult | null
  error: string | null
}
