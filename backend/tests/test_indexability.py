import pytest
from helpers import load_fixture, make_soup
from analyzer.indexability_analyzer import analyze_indexability


def check_by_id(checks, cid):
    return next((c for c in checks if c.id == cid), None)


PAGE_URL = "https://example.com/test"


class TestNoindex:
    def test_noindex_meta_is_warning(self):
        soup, _ = load_fixture("indexability_noindex.html")
        checks = analyze_indexability(soup, PAGE_URL)
        assert check_by_id(checks, "indexability_noindex").status == "warning"

    def test_no_robots_meta_is_passed(self):
        soup, _ = load_fixture("indexability_no_lang.html")
        checks = analyze_indexability(soup, PAGE_URL)
        assert check_by_id(checks, "indexability_noindex").status == "passed"

    def test_index_robots_is_passed(self):
        html = '<html lang="en"><head><meta name="robots" content="index, follow"></head></html>'
        checks = analyze_indexability(make_soup(html), PAGE_URL)
        assert check_by_id(checks, "indexability_noindex").status == "passed"


class TestCanonical:
    def test_canonical_different_url_is_warning(self):
        soup, _ = load_fixture("indexability_canonical_diff.html")
        checks = analyze_indexability(soup, PAGE_URL)
        assert check_by_id(checks, "indexability_canonical").status == "warning"

    def test_no_canonical_is_warning(self):
        html = '<html lang="en"><head><title>Test</title></head><body></body></html>'
        checks = analyze_indexability(make_soup(html), PAGE_URL)
        assert check_by_id(checks, "indexability_canonical").status == "warning"

    def test_matching_canonical_is_passed(self):
        html = f'<html lang="en"><head><link rel="canonical" href="{PAGE_URL}"></head></html>'
        checks = analyze_indexability(make_soup(html), PAGE_URL)
        assert check_by_id(checks, "indexability_canonical").status == "passed"

    def test_canonical_trailing_slash_matches(self):
        html = f'<html lang="en"><head><link rel="canonical" href="{PAGE_URL}/"></head></html>'
        checks = analyze_indexability(make_soup(html), PAGE_URL)
        assert check_by_id(checks, "indexability_canonical").status == "passed"


class TestLang:
    def test_no_lang_is_warning(self):
        soup, _ = load_fixture("indexability_no_lang.html")
        checks = analyze_indexability(soup, PAGE_URL)
        assert check_by_id(checks, "indexability_lang").status == "warning"

    def test_lang_present_is_passed(self):
        html = '<html lang="tr"><head><title>Test</title></head></html>'
        checks = analyze_indexability(make_soup(html), PAGE_URL)
        assert check_by_id(checks, "indexability_lang").status == "passed"
        assert check_by_id(checks, "indexability_lang").value == "tr"
