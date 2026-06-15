import asyncio
from urllib.parse import urlparse

from dotenv import load_dotenv
load_dotenv()

from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from analyzer import analyze_html
from analyzer.fetcher import fetch_url
from analyzer.url_utils import normalize_url
from analyzer.pagespeed_analyzer import analyze_pagespeed
from crawler.crawler import crawl_site
from crawler.job_store import job_store
from crawler.site_aggregator import aggregate
from models import (
    AnalyzeRequest,
    AnalyzeResponse,
    CrawlJobResponse,
    CrawlRequest,
)

app = FastAPI(title="Prowler SEO Analyzer", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Health ────────────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    return {"name": "Prowler SEO Analyzer", "version": "2.0.0"}


# ── Single-URL analysis ───────────────────────────────────────────────────────

@app.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze(request: AnalyzeRequest):
    try:
        url = normalize_url(request.url)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    status_code, final_url, redirected, html, http_headers, response_time_ms, error = await fetch_url(url)

    if html is None:
        raise HTTPException(status_code=502, detail=error or "Failed to fetch page")

    soup = BeautifulSoup(html, "html.parser")
    checks, score, summary, metadata = analyze_html(
        soup,
        final_url,
        raw_html=html,
        http_headers=http_headers,
        response_time_ms=response_time_ms,
    )

    pagespeed_checks = await analyze_pagespeed(final_url)
    if pagespeed_checks:
        checks.extend(pagespeed_checks)
        from analyzer.scoring import calculate_score
        score = calculate_score(checks)
        summary = summary.__class__(
            passed=sum(1 for c in checks if c.status == "passed"),
            warnings=sum(1 for c in checks if c.status == "warning"),
            failed=sum(1 for c in checks if c.status == "failed"),
        )

    return AnalyzeResponse(
        url=url,
        final_url=final_url,
        status_code=status_code,
        redirected=redirected,
        score=score,
        summary=summary,
        checks=checks,
        metadata=metadata,
    )


# ── Site crawl ────────────────────────────────────────────────────────────────

async def _run_crawl_job(
    job_id: str,
    start_url: str,
    max_pages: int,
    max_depth: int,
    include_subdomains: bool,
) -> None:
    job_store.update(job_id, status="running")
    try:
        pages, pages_done, pages_failed, sitemap_urls_found = await crawl_site(
            start_url=start_url,
            max_pages=max_pages,
            max_depth=max_depth,
            include_subdomains=include_subdomains,
            job_id=job_id,
            job_store=job_store,
        )
        domain = urlparse(start_url).netloc
        result = aggregate(start_url, domain, pages, sitemap_urls_found)
        job_store.update(job_id, status="done", result=result)
    except Exception as exc:
        job_store.update(job_id, status="error", error=str(exc)[:500])


@app.post("/api/crawl", status_code=202)
async def start_crawl(request: CrawlRequest):
    try:
        url = normalize_url(request.url)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    job_id = job_store.create(url)
    asyncio.create_task(
        _run_crawl_job(
            job_id,
            url,
            request.max_pages,
            request.max_depth,
            request.include_subdomains,
        )
    )
    return {"job_id": job_id, "status": "queued"}


@app.get("/api/crawl/{job_id}", response_model=CrawlJobResponse)
async def get_crawl_job(job_id: str):
    job = job_store.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found")
    return job.to_response()


# ── Page source viewer ────────────────────────────────────────────────────────

@app.get("/api/source")
async def get_page_source(url: str):
    """Fetch and return the raw HTML of any URL (for the source viewer)."""
    try:
        normalized = normalize_url(url)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    _, final_url, _, html, _, _, error = await fetch_url(normalized)
    if html is None:
        raise HTTPException(status_code=502, detail=error or "Failed to fetch page")
    return {"url": final_url, "html": html}
