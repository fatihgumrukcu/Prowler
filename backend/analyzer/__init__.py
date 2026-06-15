from typing import Dict, List, Optional, Tuple

from bs4 import BeautifulSoup

from models import Check, Metadata, Summary
from analyzer.meta_analyzer import analyze_meta, get_meta_metadata
from analyzer.indexability_analyzer import analyze_indexability, get_indexability_metadata
from analyzer.heading_analyzer import analyze_headings, get_heading_metadata
from analyzer.schema_analyzer import analyze_schema, get_schema_metadata
from analyzer.image_analyzer import analyze_images, get_image_metadata
from analyzer.link_analyzer import analyze_links, get_link_metadata
from analyzer.social_analyzer import analyze_social
from analyzer.content_analyzer import analyze_content, get_content_metadata
from analyzer.url_quality_analyzer import analyze_url_quality
from analyzer.http_tech_analyzer import analyze_http_tech, get_http_metadata
from analyzer.structural_analyzer import analyze_structural, get_structural_metadata
from analyzer.scoring import calculate_score


def analyze_html(
    soup: BeautifulSoup,
    page_url: str,
    raw_html: str = "",
    http_headers: Optional[Dict[str, str]] = None,
    response_time_ms: int = 0,
) -> Tuple[List[Check], int, Summary, Metadata]:
    """Run all analyzers. Returns (checks, score, summary, metadata).

    http_headers: pass for single-URL analysis to enable HTTP-level checks.
                  Omit (None) for crawl mode to skip per-page HTTP headers.
    raw_html:     full HTML string for text-to-HTML ratio and content analysis.
    """
    checks: List[Check] = []
    checks.extend(analyze_meta(soup))
    checks.extend(analyze_content(soup, raw_html))
    checks.extend(analyze_url_quality(page_url))
    checks.extend(analyze_indexability(soup, page_url))
    checks.extend(analyze_headings(soup))
    checks.extend(analyze_schema(soup))
    checks.extend(analyze_images(soup))
    checks.extend(analyze_links(soup, page_url))
    checks.extend(analyze_social(soup))
    checks.extend(analyze_structural(soup, page_url))
    if http_headers is not None:
        checks.extend(analyze_http_tech(http_headers, response_time_ms, page_url))

    http_meta = get_http_metadata(http_headers, response_time_ms) if http_headers is not None else {}

    metadata = Metadata(
        **get_meta_metadata(soup),
        **get_indexability_metadata(soup),
        **get_heading_metadata(soup),
        **get_schema_metadata(soup),
        **get_image_metadata(soup),
        **get_link_metadata(soup, page_url),
        **get_content_metadata(soup, raw_html),
        **get_structural_metadata(soup),
        **http_meta,
    )

    score = calculate_score(checks)
    summary = Summary(
        passed=sum(1 for c in checks if c.status == "passed"),
        warnings=sum(1 for c in checks if c.status == "warning"),
        failed=sum(1 for c in checks if c.status == "failed"),
    )

    return checks, score, summary, metadata
