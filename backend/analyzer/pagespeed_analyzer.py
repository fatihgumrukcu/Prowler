"""
Google PageSpeed Insights analyzer (v5).

Env var: PAGESPEED_API_KEY
Docs:    https://developers.google.com/speed/docs/insights/v5/get-started
"""

import os
from typing import List, Optional, Tuple

import httpx

from models import Check

PAGESPEED_API_KEY = os.getenv("PAGESPEED_API_KEY", "")
PAGESPEED_API_URL = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"


def _status(score: Optional[float], good: float = 0.9, ok: float = 0.5) -> str:
    if score is None:
        return "warning"
    if score >= good:
        return "passed"
    if score >= ok:
        return "warning"
    return "failed"


def _audit(audits: dict, key: str) -> Tuple[Optional[float], str, Optional[float]]:
    """Returns (score 0-1, displayValue, numericValue)."""
    a = audits.get(key, {})
    return (
        a.get("score"),
        a.get("displayValue", "—"),
        a.get("numericValue"),
    )


async def analyze_pagespeed(url: str, strategy: str = "mobile") -> List[Check]:
    """
    Returns PageSpeed checks. Returns [] if key missing or API fails.
    strategy: "mobile" | "desktop"
    """
    if not PAGESPEED_API_KEY:
        return []

    params = [
        ("url", url),
        ("key", PAGESPEED_API_KEY),
        ("strategy", strategy),
        ("category", "performance"),
        ("category", "seo"),
        ("category", "accessibility"),
    ]

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(PAGESPEED_API_URL, params=params)
            resp.raise_for_status()
            data = resp.json()
    except Exception as exc:
        return [Check(
            id="pagespeed_error",
            category="PageSpeed",
            label="PageSpeed Insights",
            status="warning",
            message=f"PageSpeed API request failed: {exc}",
            recommendation="Check your PAGESPEED_API_KEY and network connection",
        )]

    lr = data.get("lighthouseResult", {})
    categories = lr.get("categories", {})
    audits = lr.get("audits", {})
    strat_label = strategy.capitalize()
    checks: List[Check] = []

    # ── Category scores ───────────────────────────────────────────────────────

    perf_score = categories.get("performance", {}).get("score")
    if perf_score is not None:
        pct = int(perf_score * 100)
        checks.append(Check(
            id="pagespeed_performance",
            category="PageSpeed",
            label=f"Performance Score ({strat_label})",
            status=_status(perf_score),
            message=f"Lighthouse performance score: {pct}/100",
            value=str(pct),
            recommendation=None if perf_score >= 0.9 else "Optimise images, reduce unused JS/CSS, enable caching",
        ))

    seo_score = categories.get("seo", {}).get("score")
    if seo_score is not None:
        pct = int(seo_score * 100)
        checks.append(Check(
            id="pagespeed_seo",
            category="PageSpeed",
            label=f"Lighthouse SEO Score ({strat_label})",
            status=_status(seo_score),
            message=f"Lighthouse SEO score: {pct}/100",
            value=str(pct),
            recommendation=None if seo_score >= 0.9 else "Check Lighthouse SEO audits for specific issues",
        ))

    a11y_score = categories.get("accessibility", {}).get("score")
    if a11y_score is not None:
        pct = int(a11y_score * 100)
        checks.append(Check(
            id="pagespeed_accessibility",
            category="PageSpeed",
            label=f"Accessibility Score ({strat_label})",
            status=_status(a11y_score),
            message=f"Lighthouse accessibility score: {pct}/100",
            value=str(pct),
            recommendation=None if a11y_score >= 0.9 else "Add ARIA labels, improve colour contrast, fix form labels",
        ))

    # ── Core Web Vitals ───────────────────────────────────────────────────────

    # LCP — good < 2.5s, ok < 4s
    lcp_score, lcp_val, lcp_ms = _audit(audits, "largest-contentful-paint")
    if lcp_score is not None:
        checks.append(Check(
            id="pagespeed_lcp",
            category="PageSpeed",
            label=f"LCP — Largest Contentful Paint ({strat_label})",
            status=_status(lcp_score),
            message=f"LCP: {lcp_val}",
            value=lcp_val,
            recommendation=None if lcp_score >= 0.9 else "Optimise server response, preload hero images, use a CDN",
        ))

    # CLS — good < 0.1, ok < 0.25
    cls_score, cls_val, _ = _audit(audits, "cumulative-layout-shift")
    if cls_score is not None:
        checks.append(Check(
            id="pagespeed_cls",
            category="PageSpeed",
            label=f"CLS — Cumulative Layout Shift ({strat_label})",
            status=_status(cls_score),
            message=f"CLS: {cls_val}",
            value=cls_val,
            recommendation=None if cls_score >= 0.9 else "Set explicit size on images/embeds, avoid inserting content above existing content",
        ))

    # TBT — proxy for FID/INP; good < 200ms, ok < 600ms
    tbt_score, tbt_val, _ = _audit(audits, "total-blocking-time")
    if tbt_score is not None:
        checks.append(Check(
            id="pagespeed_tbt",
            category="PageSpeed",
            label=f"TBT — Total Blocking Time ({strat_label})",
            status=_status(tbt_score),
            message=f"TBT: {tbt_val}",
            value=tbt_val,
            recommendation=None if tbt_score >= 0.9 else "Reduce long JS tasks, split code bundles, defer non-critical scripts",
        ))

    # FCP — good < 1.8s, ok < 3s
    fcp_score, fcp_val, _ = _audit(audits, "first-contentful-paint")
    if fcp_score is not None:
        checks.append(Check(
            id="pagespeed_fcp",
            category="PageSpeed",
            label=f"FCP — First Contentful Paint ({strat_label})",
            status=_status(fcp_score),
            message=f"FCP: {fcp_val}",
            value=fcp_val,
            recommendation=None if fcp_score >= 0.9 else "Reduce server response time, eliminate render-blocking resources",
        ))

    # TTFB
    ttfb_score, ttfb_val, _ = _audit(audits, "server-response-time")
    if ttfb_score is not None:
        checks.append(Check(
            id="pagespeed_ttfb",
            category="PageSpeed",
            label=f"TTFB — Server Response Time ({strat_label})",
            status=_status(ttfb_score),
            message=f"TTFB: {ttfb_val}",
            value=ttfb_val,
            recommendation=None if ttfb_score >= 0.9 else "Optimise server, use caching, consider a CDN",
        ))

    # Speed Index
    si_score, si_val, _ = _audit(audits, "speed-index")
    if si_score is not None:
        checks.append(Check(
            id="pagespeed_speed_index",
            category="PageSpeed",
            label=f"Speed Index ({strat_label})",
            status=_status(si_score),
            message=f"Speed Index: {si_val}",
            value=si_val,
            recommendation=None if si_score >= 0.9 else "Reduce render-blocking resources, optimise critical rendering path",
        ))

    return checks
