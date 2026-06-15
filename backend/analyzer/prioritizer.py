"""
Priority / effort enrichment layer — sits on top of existing check results.
Does not affect scoring; only adds presentation metadata.
"""

from typing import List, Literal

from models import Check, SiteIssue, CrawlResult

# ── Impact constants ──────────────────────────────────────────────────────────

_IMPACT = {"failed": 3, "warning": 1, "passed": 0}

# priority_score thresholds:  critical ≥ 9 | high ≥ 3 | medium ≥ 1 | low = 0
_THRESHOLDS = [(9, "critical"), (3, "high"), (1, "medium"), (0, "low")]

PriorityLabel = Literal["critical", "high", "medium", "low"]
EffortLabel = Literal["low", "medium", "high"]

# ── Effort map ────────────────────────────────────────────────────────────────
# How hard it is to fix a check (developer time / complexity estimate).

EFFORT_MAP: dict[str, EffortLabel] = {
    # Meta
    "meta_title":                   "low",
    "meta_description":             "low",
    # Headings
    "heading_h1":                   "low",
    "heading_h2":                   "low",
    "heading_hierarchy":            "low",
    "heading_breakdown":            "low",
    # Content
    "content_word_count":           "medium",
    "content_text_html_ratio":      "medium",
    "content_js_render":            "high",
    "content_desc_title_dupe":      "low",
    "content_title_h1_match":       "low",
    # URL
    "url_length":                   "low",
    "url_uppercase":                "low",
    "url_underscore":               "low",
    "url_spaces":                   "low",
    "url_query_params":             "medium",
    "url_tr_chars":                 "low",
    # Indexability
    "indexability_canonical":       "low",
    "indexability_noindex":         "low",
    "indexability_nofollow":        "low",
    "indexability_lang":            "low",
    # Schema
    "schema_json_ld":               "medium",
    # Images
    "image_alt":                    "low",
    "image_dimensions":             "medium",
    "image_modern_format":          "medium",
    "image_filename_length":        "low",
    "image_lazy_above_fold":        "medium",
    # Links
    "links_internal":               "medium",
    "links_external":               "low",
    "links_invalid":                "medium",
    # Social
    "social_og":                    "low",
    "social_twitter":               "low",
    # Structural
    "structural_viewport":          "low",
    "structural_favicon":           "low",
    "structural_hreflang":          "high",
    "structural_pagination":        "medium",
    "structural_rss":               "low",
    # HTTP / tech
    "http_hsts":                    "medium",
    "http_compression":             "low",
    "http_caching":                 "medium",
    "http_response_time":           "high",
    "http_content_type":            "low",
    "http_x_robots_tag":            "low",
    "http_x_robots_noindex":        "low",
    "http_x_robots_nofollow":       "low",
    # PageSpeed
    "pagespeed_performance":        "high",
    "pagespeed_lcp":                "high",
    "pagespeed_cls":                "high",
    "pagespeed_fcp":                "high",
    "pagespeed_tbt":                "high",
    "pagespeed_ttfb":               "high",
    "pagespeed_speed_index":        "high",
    "pagespeed_seo":                "medium",
    "pagespeed_accessibility":      "medium",
    "pagespeed_error":              "medium",
}

# ── Knowledge base ────────────────────────────────────────────────────────────
# (why_it_matters, how_to_fix) — shown only on failed / warning checks.

KNOWLEDGE_BASE: dict[str, tuple[str, str]] = {
    "meta_title": (
        "Title tag is the strongest on-page signal for both rankings and SERP click-through rate.",
        "Write a unique, keyword-rich title of 50–60 characters. Place the primary keyword near the beginning.",
    ),
    "meta_description": (
        "Meta descriptions appear as SERP snippets and directly influence click-through rate, even though they don't affect rankings.",
        "Write a compelling 120–160 character summary with the target keyword and a clear call-to-action.",
    ),
    "heading_h1": (
        "The H1 is the clearest structural signal to search engines about the page's primary topic.",
        "Add exactly one H1 per page that includes the target keyword and accurately describes the content.",
    ),
    "heading_h2": (
        "H2 headings structure content into scannable sections and reinforce topical relevance for crawlers.",
        "Break long content into logical H2 sections with descriptive, keyword-relevant labels.",
    ),
    "heading_hierarchy": (
        "Skipping heading levels (e.g., H1 → H4) breaks the document outline that search engines and screen readers rely on.",
        "Ensure headings follow strict nesting order — never skip a level; demote or promote tags to restore hierarchy.",
    ),
    "heading_breakdown": (
        "Multiple H1 tags dilute the primary topic signal and confuse search engines about which topic is most important.",
        "Keep exactly one H1 per page; convert extra H1s to H2 or H3.",
    ),
    "content_word_count": (
        "Pages with too little content are considered thin by search engines and rank poorly for competitive queries.",
        "Aim for at least 300 words of unique, meaningful content; for competitive topics, 800+ words typically performs better.",
    ),
    "content_text_html_ratio": (
        "A very low text-to-HTML ratio signals a page bloated with markup relative to content, which can indicate poor content quality.",
        "Reduce unnecessary inline styles, scripts, and markup; increase the amount of visible, useful text content.",
    ),
    "content_js_render": (
        "Content visible only after JavaScript execution may not be indexed by search engines that don't fully render JS.",
        "Implement server-side rendering (SSR) or static generation (SSG) so critical content exists in the initial HTML response.",
    ),
    "content_desc_title_dupe": (
        "Identical title and meta description wastes the opportunity to communicate additional context in search snippets.",
        "Write a distinct meta description that expands on the title — the title names the page, the description sells the click.",
    ),
    "content_title_h1_match": (
        "When the title tag and H1 don't align, there's a missed opportunity to reinforce the page's primary keyword.",
        "Make title and H1 thematically consistent — they need not be identical but should target the same keyword intent.",
    ),
    "url_length": (
        "Overly long URLs get truncated in SERPs, are harder to share, and can dilute keyword relevance.",
        "Keep URLs under 100 characters; remove stop words, IDs, and unnecessary path segments.",
    ),
    "url_uppercase": (
        "Uppercase letters can cause duplicate content issues because some servers treat mixed-case paths as different URLs.",
        "Use all-lowercase URLs and set up 301 redirects from any uppercase variants.",
    ),
    "url_underscore": (
        "Google treats underscores as word joiners, so 'my_page' is read as 'mypage' rather than 'my page'.",
        "Replace underscores with hyphens in all URL slugs.",
    ),
    "url_spaces": (
        "Spaces in URLs get percent-encoded (%20), making them ugly, fragile across systems, and hard to share.",
        "Replace spaces with hyphens; keep URLs clean and human-readable.",
    ),
    "url_query_params": (
        "Excessive query parameters can create infinite crawl loops and canonicalization problems.",
        "Use URL parameters sparingly; handle parameter variants with canonical tags or Google Search Console parameter settings.",
    ),
    "url_tr_chars": (
        "Non-ASCII characters (e.g., ş, ğ, ı) get percent-encoded in URLs, making them unreadable and fragile.",
        "Transliterate special characters to ASCII equivalents in URL slugs (ş→s, ğ→g, ı→i).",
    ),
    "indexability_canonical": (
        "Without a canonical tag, search engines must guess which URL to index, potentially splitting link equity across duplicates.",
        "Add <link rel='canonical' href='...'> pointing to the preferred URL on every page.",
    ),
    "indexability_noindex": (
        "A noindex directive removes this page from search engine indexes, making it invisible to organic search.",
        "Remove the noindex directive if this page should appear in search results, or confirm it's intentionally excluded.",
    ),
    "indexability_nofollow": (
        "A page-level nofollow prevents search engines from following any links on the page, limiting crawl coverage.",
        "Remove the page-level nofollow if you want search engines to discover and crawl links on this page.",
    ),
    "indexability_lang": (
        "The lang attribute helps search engines serve content to users in the correct language.",
        "Add a lang attribute to the <html> element matching the page's primary language (e.g., <html lang='en'>).",
    ),
    "schema_json_ld": (
        "Structured data enables rich results in SERPs (star ratings, FAQs, breadcrumbs), significantly boosting click-through rates.",
        "Add JSON-LD structured data for your primary content type (Article, Product, LocalBusiness, FAQ, etc.) in the <head>.",
    ),
    "image_alt": (
        "Alt text is the primary signal for search engines to understand image content and is critical for image search rankings.",
        "Add descriptive alt attributes to all meaningful images; use empty alt='' for purely decorative images.",
    ),
    "image_dimensions": (
        "Images without explicit width/height cause layout shifts (CLS), hurting Core Web Vitals and user experience.",
        "Set explicit width and height attributes on all <img> tags so the browser can reserve space before the image loads.",
    ),
    "image_modern_format": (
        "Modern image formats (WebP, AVIF) are 25–50% smaller than JPEG/PNG, directly improving page load speed.",
        "Convert images to WebP or AVIF format and use <picture> elements for browser compatibility fallbacks.",
    ),
    "image_filename_length": (
        "Overly long image filenames add unnecessary URL weight and rarely provide SEO benefit.",
        "Use concise, descriptive filenames under 80 characters with hyphens separating meaningful keywords.",
    ),
    "image_lazy_above_fold": (
        "Lazy-loading above-the-fold images delays their rendering, directly hurting LCP (Largest Contentful Paint).",
        "Remove loading='lazy' from images visible on initial load; reserve lazy loading for below-the-fold images only.",
    ),
    "links_internal": (
        "Internal links distribute PageRank across your site and help users and crawlers discover related content.",
        "Add contextual internal links to related pages using descriptive, keyword-relevant anchor text.",
    ),
    "links_external": (
        "External links to authoritative sources signal topical credibility and provide value to users.",
        "Link to relevant, high-quality external sources where appropriate; add rel='noopener noreferrer' for security.",
    ),
    "links_invalid": (
        "Broken links create a poor user experience and waste crawl budget on dead-end URLs.",
        "Fix or remove all broken links; set up 301 redirects for pages that have moved.",
    ),
    "social_og": (
        "Open Graph tags control how your page appears when shared on social networks, affecting click-through rates.",
        "Add og:title, og:description, og:image, and og:url <meta> tags to the <head>.",
    ),
    "social_twitter": (
        "Twitter Card tags create rich link previews when content is shared on Twitter/X, improving social engagement.",
        "Add twitter:card, twitter:title, twitter:description, and twitter:image <meta> tags.",
    ),
    "structural_viewport": (
        "Without a viewport meta tag, mobile browsers render pages at desktop width, making them unusable on mobile.",
        "Add <meta name='viewport' content='width=device-width, initial-scale=1'> to the <head>.",
    ),
    "structural_favicon": (
        "Favicons appear in browser tabs and bookmarks; their absence makes the site look unfinished.",
        "Add a favicon.ico or SVG favicon and reference it with <link rel='icon'> in the <head>.",
    ),
    "structural_hreflang": (
        "Without hreflang tags, search engines may show the wrong language or regional variant to international users.",
        "Implement hreflang annotations for every language/region variant, including a self-referencing tag on each page.",
    ),
    "structural_pagination": (
        "Missing pagination signals leave search engines uncertain about paginated content series.",
        "Add rel='prev' and rel='next' link elements (or a canonical to page 1) for all paginated content.",
    ),
    "structural_rss": (
        "An RSS feed allows search engines and aggregators to discover new content faster.",
        "Create an RSS or Atom feed and reference it with <link rel='alternate' type='application/rss+xml'>.",
    ),
    "http_hsts": (
        "Without HSTS, browsers may make an initial unencrypted HTTP request before being redirected, leaving users exposed.",
        "Configure your server to send Strict-Transport-Security: max-age=31536000; includeSubDomains.",
    ),
    "http_compression": (
        "Uncompressed responses can be 5–10× larger, significantly slowing page loads, especially on mobile.",
        "Enable gzip or Brotli compression on your web server or CDN for all text-based responses.",
    ),
    "http_caching": (
        "Without proper cache headers, browsers re-download unchanged assets on every visit, wasting bandwidth and slowing repeat visits.",
        "Set Cache-Control headers with appropriate max-age values for static assets (images, CSS, JS).",
    ),
    "http_response_time": (
        "Slow server response time (TTFB) is a direct ranking signal and delays every subsequent step of page loading.",
        "Optimise server performance, use a CDN, enable server-side caching, and review slow database queries.",
    ),
    "http_content_type": (
        "A missing or incorrect Content-Type header can cause browsers to misinterpret the page, leading to rendering issues.",
        "Ensure your server returns Content-Type: text/html; charset=utf-8 for all HTML responses.",
    ),
    "http_x_robots_tag": (
        "The X-Robots-Tag HTTP header may be unintentionally restricting indexation at the server level.",
        "Audit the X-Robots-Tag response header and remove any unintended noindex or nofollow directives.",
    ),
    "http_x_robots_noindex": (
        "X-Robots-Tag: noindex makes this page invisible to search engines at the HTTP level, overriding meta tags.",
        "Remove the noindex directive from the X-Robots-Tag header if this page should be indexed.",
    ),
    "http_x_robots_nofollow": (
        "X-Robots-Tag: nofollow prevents search engines from following links on this page at the HTTP level.",
        "Remove the nofollow directive from the X-Robots-Tag header if you want links on this page to be crawled.",
    ),
    "pagespeed_performance": (
        "Google's Core Web Vitals performance score directly factors into search rankings, especially on mobile.",
        "Address the specific CWV issues flagged (LCP, CLS, FCP, TBT) to raise the overall performance score.",
    ),
    "pagespeed_lcp": (
        "Largest Contentful Paint measures how quickly the main content loads — a key Google ranking signal.",
        "Preload the hero image, use fast hosting, and minimise render-blocking resources to hit the <2.5s target.",
    ),
    "pagespeed_cls": (
        "Cumulative Layout Shift measures visual stability — unexpected shifts hurt user experience and are penalised by Google.",
        "Set explicit dimensions on images and embeds; avoid inserting content above existing content after the page loads.",
    ),
    "pagespeed_fcp": (
        "First Contentful Paint measures when users first see content — a slow FCP signals poor server or network performance.",
        "Eliminate render-blocking resources, inline critical CSS, and improve server response times.",
    ),
    "pagespeed_tbt": (
        "Total Blocking Time measures main-thread blockage during load — high TBT makes the page feel unresponsive.",
        "Break up long JavaScript tasks, defer non-critical JS, and use web workers for heavy computation.",
    ),
    "pagespeed_ttfb": (
        "Time to First Byte is the server's response latency and directly delays every subsequent loading step.",
        "Use a CDN, enable server caching, optimise database queries, and review your hosting infrastructure.",
    ),
    "pagespeed_speed_index": (
        "Speed Index measures how quickly content is visually populated — a slow score frustrates users and correlates with ranking drops.",
        "Prioritise loading above-the-fold content first, defer off-screen resources, and optimise the critical rendering path.",
    ),
    "pagespeed_seo": (
        "PageSpeed's SEO audit flags crawl blockers, missing viewport tags, and unoptimised links that hurt rankings.",
        "Review and fix the specific SEO issues reported by PageSpeed for this URL.",
    ),
    "pagespeed_accessibility": (
        "Accessibility issues affect users with disabilities and also limit search engine understanding of your content.",
        "Fix the flagged issues: add missing alt text, increase colour contrast, ensure all interactive elements are keyboard-accessible.",
    ),
    "pagespeed_error": (
        "A PageSpeed API error means Core Web Vitals data could not be retrieved, leaving performance blind spots.",
        "Verify the PageSpeed API key is valid and the page is publicly accessible, then re-run the analysis.",
    ),
}


# ── Core helpers ──────────────────────────────────────────────────────────────

def _priority_label(status: str, scope: int) -> PriorityLabel:
    score = _IMPACT.get(status, 0) * scope
    for threshold, label in _THRESHOLDS:
        if score >= threshold:
            return label  # type: ignore[return-value]
    return "low"


def _enrich_fields(check_id: str, status: str, scope: int) -> dict:
    label = _priority_label(status, scope)
    effort: EffortLabel = EFFORT_MAP.get(check_id, "medium")
    why, how = KNOWLEDGE_BASE.get(check_id, ("", ""))
    return {
        "priority_label": label,
        "effort": effort,
        "why_it_matters": why if status != "passed" else None,
        "how_to_fix": how if status != "passed" else None,
    }


# ── Public API ────────────────────────────────────────────────────────────────

def enrich_check(check: Check, scope: int = 1) -> Check:
    """Return a copy of *check* with priority/effort/knowledge fields filled in."""
    return check.model_copy(update=_enrich_fields(check.id, check.status, scope))


def enrich_checks(checks: list[Check], scope: int = 1) -> list[Check]:
    return [enrich_check(c, scope) for c in checks]


def get_top_issues(checks: list[Check], n: int = 5) -> list[Check]:
    """Return the top *n* failed/warning checks sorted by priority (critical first)."""
    _order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    issues = [c for c in checks if c.status in ("failed", "warning")]
    return sorted(issues, key=lambda c: _order.get(c.priority_label or "low", 3))[:n]


def enrich_site_issue(issue: SiteIssue) -> SiteIssue:
    """Return a copy of *issue* with priority/effort/knowledge fields, scope = page_count."""
    fields = _enrich_fields(issue.check_id, issue.status, issue.page_count)
    return issue.model_copy(update=fields)


def enrich_crawl_result(result: CrawlResult) -> CrawlResult:
    """Enrich all site_issues and attach a top_issues list to the crawl result."""
    enriched = [enrich_site_issue(si) for si in result.site_issues]
    _order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    top = sorted(enriched, key=lambda si: _order.get(si.priority_label or "low", 3))[:5]
    return result.model_copy(update={"site_issues": enriched, "top_issues": top})
