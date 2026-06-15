from pydantic import BaseModel, Field
from typing import Optional, List, Literal, Dict


class AnalyzeRequest(BaseModel):
    url: str


class Check(BaseModel):
    id: str
    category: str
    label: str
    status: Literal["passed", "warning", "failed"]
    message: str
    value: Optional[str] = None
    recommendation: Optional[str] = None


class Summary(BaseModel):
    passed: int
    warnings: int
    failed: int


class Metadata(BaseModel):
    # Meta
    title: Optional[str] = None
    description: Optional[str] = None
    # Indexability
    canonical: Optional[str] = None
    robots: Optional[str] = None
    lang: Optional[str] = None
    # Headings
    h1: List[str] = Field(default_factory=list)
    h2_count: int = 0
    # Schema
    schema_types: List[str] = Field(default_factory=list)
    # Links
    internal_links: int = 0
    external_links: int = 0
    # Images
    images_total: int = 0
    images_missing_alt: int = 0
    # Content (new)
    word_count: int = 0
    text_html_ratio: float = 0.0
    # HTTP (new)
    response_time_ms: int = 0
    compression: Optional[str] = None
    # Structural (new)
    hreflang_langs: List[str] = Field(default_factory=list)
    has_favicon: bool = False
    has_rss: bool = False
    has_viewport: bool = False


class AnalyzeResponse(BaseModel):
    url: str
    final_url: str
    status_code: Optional[int] = None
    redirected: bool = False
    score: int
    summary: Summary
    checks: List[Check]
    metadata: Metadata


# ── Crawl models ──────────────────────────────────────────────────────────────

class CrawlRequest(BaseModel):
    url: str
    max_pages: int = Field(default=100, ge=1, le=1000)
    max_depth: int = Field(default=3, ge=0, le=10)
    include_subdomains: bool = False


class PageResult(BaseModel):
    url: str
    final_url: str = ""
    status_code: Optional[int] = None
    score: int = 0
    summary: Summary = Field(default_factory=lambda: Summary(passed=0, warnings=0, failed=0))
    checks: List[Check] = Field(default_factory=list)
    discovery_source: str = "crawl"   # "start" | "sitemap" | "crawl"
    error: Optional[str] = None


class SiteIssue(BaseModel):
    check_id: str
    category: str
    label: str
    status: Literal["passed", "warning", "failed"]
    page_count: int
    example_urls: List[str]


class CrawlResult(BaseModel):
    start_url: str
    domain: str
    pages_crawled: int
    pages_failed: int
    site_score: int
    site_summary: Summary
    site_issues: List[SiteIssue]
    sitemap_urls_found: int = 0
    sitemap_urls_crawled: int = 0
    sitemap_urls_unreachable: int = 0
    pages: List[PageResult]


class CrawlJobResponse(BaseModel):
    job_id: str
    status: Literal["queued", "running", "done", "error"]
    progress: Dict[str, int] = Field(default_factory=dict)
    live_urls: List[str] = Field(default_factory=list)
    result: Optional[CrawlResult] = None
    error: Optional[str] = None
