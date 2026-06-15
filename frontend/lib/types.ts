export type CheckStatus = 'passed' | 'warning' | 'failed'
export type PriorityLabel = 'critical' | 'high' | 'medium' | 'low'
export type EffortLabel = 'low' | 'medium' | 'high'

export interface Check {
  id: string
  category: string
  label: string
  status: CheckStatus
  message: string
  value: string | null
  recommendation: string | null
  priority_label: PriorityLabel | null
  effort: EffortLabel | null
  why_it_matters: string | null
  how_to_fix: string | null
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
  click_depth: number
  inlinks_count: number
}

export interface SiteIssue {
  check_id: string
  category: string
  label: string
  status: CheckStatus
  page_count: number
  example_urls: string[]
  priority_label: PriorityLabel | null
  effort: EffortLabel | null
  why_it_matters: string | null
  how_to_fix: string | null
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
  top_issues: SiteIssue[]
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
  top_issues: Check[]
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

// ── Graph types ───────────────────────────────────────────────────────────────

export interface GraphNode {
  id: string
  url: string
  score: number
  click_depth: number
  inlinks_count: number
  status_code: number | null
  is_orphan: boolean
  discovery_source: string
}

export interface GraphEdge {
  source: string
  target: string
}

export interface GraphResponse {
  nodes: GraphNode[]
  edges: GraphEdge[]
}
