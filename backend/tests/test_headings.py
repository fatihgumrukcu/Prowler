import pytest
from helpers import load_fixture, make_soup
from analyzer.heading_analyzer import analyze_headings


def check_by_id(checks, cid):
    return next((c for c in checks if c.id == cid), None)


class TestH1:
    def test_no_h1_is_failed(self):
        soup, _ = load_fixture("headings_no_h1.html")
        checks = analyze_headings(soup)
        assert check_by_id(checks, "heading_h1").status == "failed"

    def test_single_h1_is_passed(self):
        soup, _ = load_fixture("headings_single_h1.html")
        checks = analyze_headings(soup)
        assert check_by_id(checks, "heading_h1").status == "passed"

    def test_multiple_h1_is_warning(self):
        soup, _ = load_fixture("headings_multiple_h1.html")
        checks = analyze_headings(soup)
        assert check_by_id(checks, "heading_h1").status == "warning"

    def test_multiple_h1_message_contains_count(self):
        soup, _ = load_fixture("headings_multiple_h1.html")
        checks = analyze_headings(soup)
        c = check_by_id(checks, "heading_h1")
        assert "3" in c.message or "birden" in c.message.lower()


class TestH2:
    def test_no_h2_is_warning(self):
        html = "<html><body><h1>Only H1 Here</h1><p>Some content text here for the page.</p></body></html>"
        checks = analyze_headings(make_soup(html))
        c = check_by_id(checks, "heading_h2")
        assert c.status == "warning"

    def test_h2_present_is_passed(self):
        soup, _ = load_fixture("headings_single_h1.html")
        checks = analyze_headings(soup)
        c = check_by_id(checks, "heading_h2")
        assert c.status == "passed"


class TestHeadingHierarchy:
    def test_correct_hierarchy_is_passed(self):
        soup, _ = load_fixture("headings_single_h1.html")
        checks = analyze_headings(soup)
        c = check_by_id(checks, "heading_hierarchy")
        assert c.status == "passed"

    def test_skipped_level_is_warning(self):
        soup, _ = load_fixture("headings_hierarchy_skip.html")
        checks = analyze_headings(soup)
        c = check_by_id(checks, "heading_hierarchy")
        assert c.status == "warning"

    def test_skip_message_mentions_levels(self):
        soup, _ = load_fixture("headings_hierarchy_skip.html")
        checks = analyze_headings(soup)
        c = check_by_id(checks, "heading_hierarchy")
        assert "H" in c.message

    def test_single_heading_no_hierarchy_check(self):
        html = "<html><body><h1>Only Heading</h1></body></html>"
        checks = analyze_headings(make_soup(html))
        c = check_by_id(checks, "heading_hierarchy")
        assert c is None
