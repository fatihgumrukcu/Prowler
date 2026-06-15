"""
Aggregates per-page PageResult list into a site-wide CrawlResult.
"""

from collections import defaultdict
from typing import Dict, List, Tuple

from models import CrawlResult, PageResult, SiteIssue, Summary


def aggregate(
    start_url: str,
    domain: str,
    pages: List[PageResult],
    sitemap_urls_found: int = 0,
) -> CrawlResult:
    successful = [p for p in pages if not p.error]
    failed_count = sum(1 for p in pages if p.error)

    # Site score: mean of successful page scores (0 if none)
    site_score = (
        round(sum(p.score for p in successful) / len(successful))
        if successful
        else 0
    )

    # Aggregate check counts across all pages
    total_passed = sum(p.summary.passed for p in successful)
    total_warnings = sum(p.summary.warnings for p in successful)
    total_failed = sum(p.summary.failed for p in successful)

    # ── Sitemap stats ─────────────────────────────────────────────────────────
    sitemap_pages = [p for p in pages if p.discovery_source == "sitemap"]
    sitemap_crawled = sum(
        1 for p in sitemap_pages
        if not p.error and p.status_code is not None and p.status_code < 400
    )
    sitemap_unreachable = sum(
        1 for p in sitemap_pages
        if p.error or (p.status_code is not None and p.status_code >= 400)
    )

    # ── Site issues ───────────────────────────────────────────────────────────
    issue_map: Dict[Tuple[str, str], dict] = defaultdict(
        lambda: {"check_id": "", "category": "", "label": "", "status": "", "pages": []}
    )

    for page in successful:
        for check in page.checks:
            if check.status in ("warning", "failed"):
                key = (check.id, check.status)
                entry = issue_map[key]
                entry["check_id"] = check.id
                entry["category"] = check.category
                entry["label"] = check.label
                entry["status"] = check.status
                entry["pages"].append(page.url)

    def sort_key(item: dict) -> Tuple[int, int]:
        return (0 if item["status"] == "failed" else 1, -len(item["pages"]))

    site_issues = [
        SiteIssue(
            check_id=entry["check_id"],
            category=entry["category"],
            label=entry["label"],
            status=entry["status"],  # type: ignore[arg-type]
            page_count=len(entry["pages"]),
            example_urls=entry["pages"][:5],
        )
        for entry in sorted(issue_map.values(), key=sort_key)
    ]

    return CrawlResult(
        start_url=start_url,
        domain=domain,
        pages_crawled=len(successful),
        pages_failed=failed_count,
        site_score=site_score,
        site_summary=Summary(
            passed=total_passed,
            warnings=total_warnings,
            failed=total_failed,
        ),
        site_issues=site_issues[:25],
        sitemap_urls_found=sitemap_urls_found,
        sitemap_urls_crawled=sitemap_crawled,
        sitemap_urls_unreachable=sitemap_unreachable,
        pages=pages,
    )
