import asyncio
import csv
import io
import re
from datetime import date
from typing import Literal
from urllib.parse import urlparse

from dotenv import load_dotenv
load_dotenv()

from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from analyzer import analyze_html
from analyzer.fetcher import fetch_url
from analyzer.url_utils import normalize_url
from analyzer.pagespeed_analyzer import analyze_pagespeed
from crawler.crawler import crawl_site
from crawler.job_store import job_store
from crawler.site_aggregator import aggregate
from analyzer.prioritizer import enrich_checks, enrich_crawl_result, get_top_issues
from models import (
    AnalyzeRequest,
    AnalyzeResponse,
    CrawlJobResponse,
    CrawlRequest,
    GraphNode,
    GraphEdge,
    GraphResponse,
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

    checks = enrich_checks(checks, scope=1)

    return AnalyzeResponse(
        url=url,
        final_url=final_url,
        status_code=status_code,
        redirected=redirected,
        score=score,
        summary=summary,
        checks=checks,
        metadata=metadata,
        top_issues=get_top_issues(checks),
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
        pages, pages_done, pages_failed, sitemap_urls_found, crawl_edges = await crawl_site(
            start_url=start_url,
            max_pages=max_pages,
            max_depth=max_depth,
            include_subdomains=include_subdomains,
            job_id=job_id,
            job_store=job_store,
        )
        # Compute inlinks_count per page from edge list
        inlinks: dict[str, int] = {}
        for _from, _to in crawl_edges:
            inlinks[_to] = inlinks.get(_to, 0) + 1
        for page in pages:
            page.inlinks_count = inlinks.get(page.url, 0)
        # Per-page priority enrichment (scope=1 per page)
        for page in pages:
            page.checks = enrich_checks(page.checks, scope=1)
        domain = urlparse(start_url).netloc
        result = aggregate(start_url, domain, pages, sitemap_urls_found)
        # Site-level priority enrichment (scope=page_count per issue)
        result = enrich_crawl_result(result)
        job_store.update(job_id, status="done", result=result, graph_edges=crawl_edges)
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


# ── Crawl export ──────────────────────────────────────────────────────────────

_PRIORITY_RANK = {"critical": 0, "high": 1, "medium": 2, "low": 3}


@app.get("/api/crawl/{job_id}/export")
async def export_crawl(
    job_id: str,
    format: Literal["csv", "json"] = Query(default="csv"),
):
    job = job_store.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found")
    if job.status != "done" or job.result is None:
        raise HTTPException(
            status_code=409,
            detail=f"Crawl henüz tamamlanmadı (durum: {job.status})",
        )

    result = job.result
    domain_safe = re.sub(r"[^\w\-]", "-", result.domain)
    today = date.today().isoformat()

    # ── JSON export ───────────────────────────────────────────────────────────
    if format == "json":
        filename = f"prowler-{domain_safe}-{today}.json"
        return Response(
            content=result.model_dump_json(indent=2).encode("utf-8"),
            media_type="application/json",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )

    # ── CSV export ────────────────────────────────────────────────────────────
    buf = io.StringIO()
    writer = csv.writer(buf, quoting=csv.QUOTE_MINIMAL)
    writer.writerow(["url", "status_code", "score", "passed", "warnings", "failed", "top_issue", "top_priority"])

    for page in result.pages:
        issues = [c for c in page.checks if c.status != "passed"]
        issues.sort(key=lambda c: _PRIORITY_RANK.get(c.priority_label or "low", 3))
        top_issue    = issues[0].label         if issues else ""
        top_priority = issues[0].priority_label if issues else ""

        writer.writerow([
            page.url,
            page.status_code if page.status_code is not None else "",
            page.score,
            page.summary.passed,
            page.summary.warnings,
            page.summary.failed,
            top_issue,
            top_priority,
        ])

    filename = f"prowler-{domain_safe}-{today}.csv"
    # utf-8-sig prepends UTF-8 BOM so Excel opens Turkish chars correctly
    return Response(
        content=buf.getvalue().encode("utf-8-sig"),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# ── Site architecture graph ───────────────────────────────────────────────────

_NODE_CAP = 300
_EDGE_CAP = 800


@app.get("/api/crawl/{job_id}/graph", response_model=GraphResponse)
async def get_crawl_graph(job_id: str):
    job = job_store.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found")
    if job.status != "done" or job.result is None:
        raise HTTPException(
            status_code=409,
            detail=f"Crawl henüz tamamlanmadı (durum: {job.status})",
        )

    result = job.result
    pages = result.pages
    start_url = result.start_url

    # Sort: start URL first, then by inlinks_count DESC, then score DESC
    sorted_pages = sorted(
        pages,
        key=lambda p: (0 if p.url == start_url else 1, -p.inlinks_count, -p.score),
    )
    node_pages = sorted_pages[:_NODE_CAP]
    node_urls = {p.url for p in node_pages}

    nodes = [
        GraphNode(
            id=p.url,
            url=p.url,
            score=p.score,
            click_depth=p.click_depth,
            inlinks_count=p.inlinks_count,
            status_code=p.status_code,
            is_orphan=(p.inlinks_count == 0 and p.url != start_url),
            discovery_source=p.discovery_source,
        )
        for p in node_pages
    ]

    edges = [
        GraphEdge(source=f, target=t)
        for f, t in job.graph_edges
        if f in node_urls and t in node_urls
    ][:_EDGE_CAP]

    return GraphResponse(nodes=nodes, edges=edges)


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
