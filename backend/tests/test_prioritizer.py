import pytest
from models import Check, SiteIssue
from analyzer.prioritizer import (
    enrich_check,
    enrich_checks,
    get_top_issues,
    _priority_label,
    EFFORT_MAP,
)


def make_check(cid: str, status: str) -> Check:
    return Check(id=cid, category="Test", label="Test", status=status, message="msg")


class TestPriorityLabel:
    def test_failed_single_page_is_high(self):
        # impact=3, scope=1 → score=3 → high
        assert _priority_label("failed", 1) == "high"

    def test_failed_3_pages_is_critical(self):
        # impact=3, scope=3 → score=9 → critical
        assert _priority_label("failed", 3) == "critical"

    def test_warning_single_page_is_medium(self):
        # impact=1, scope=1 → score=1 → medium
        assert _priority_label("warning", 1) == "medium"

    def test_warning_3_pages_is_high(self):
        # impact=1, scope=3 → score=3 → high
        assert _priority_label("warning", 3) == "high"

    def test_passed_is_low(self):
        assert _priority_label("passed", 100) == "low"

    def test_critical_threshold_9(self):
        # impact=3, scope=3 → score=9 → critical (boundary)
        assert _priority_label("failed", 3) == "critical"

    def test_high_threshold_3(self):
        # impact=1, scope=3 → score=3 → high (boundary)
        assert _priority_label("warning", 3) == "high"

    def test_medium_threshold_1(self):
        # impact=1, scope=1 → score=1 → medium (boundary)
        assert _priority_label("warning", 1) == "medium"


class TestEnrichCheck:
    def test_failed_check_gets_why_and_fix(self):
        c = enrich_check(make_check("meta_title", "failed"))
        assert c.why_it_matters is not None
        assert c.how_to_fix is not None

    def test_passed_check_gets_no_why(self):
        c = enrich_check(make_check("meta_title", "passed"))
        assert c.why_it_matters is None
        assert c.how_to_fix is None

    def test_effort_populated(self):
        c = enrich_check(make_check("meta_title", "failed"))
        assert c.effort == "low"

    def test_unknown_check_id_gets_medium_effort(self):
        c = enrich_check(make_check("unknown_check_xyz", "failed"))
        assert c.effort == "medium"

    def test_priority_label_populated(self):
        c = enrich_check(make_check("meta_title", "failed"), scope=1)
        assert c.priority_label in ("critical", "high", "medium", "low")


class TestGetTopIssues:
    def test_passed_checks_excluded(self):
        checks = [
            make_check("meta_title", "passed"),
            make_check("heading_h1", "failed"),
        ]
        enriched = enrich_checks(checks)
        top = get_top_issues(enriched)
        assert all(c.status != "passed" for c in top)

    def test_critical_first(self):
        checks = enrich_checks([
            make_check("meta_title", "warning"),
            make_check("heading_h1", "failed"),
        ], scope=5)
        top = get_top_issues(checks)
        assert top[0].priority_label in ("critical", "high")

    def test_top_n_respected(self):
        checks = enrich_checks([make_check("meta_title", "failed")] * 10)
        top = get_top_issues(checks, n=3)
        assert len(top) == 3

    def test_all_passed_returns_empty(self):
        checks = enrich_checks([make_check("meta_title", "passed")] * 5)
        top = get_top_issues(checks)
        assert top == []


class TestEffortMap:
    def test_known_low_effort_checks(self):
        for cid in ["meta_title", "meta_description", "heading_h1", "url_length"]:
            assert EFFORT_MAP.get(cid) == "low"

    def test_known_high_effort_checks(self):
        for cid in ["content_js_render", "http_response_time", "pagespeed_lcp"]:
            assert EFFORT_MAP.get(cid) == "high"
