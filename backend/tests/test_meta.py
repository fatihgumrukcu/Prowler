import pytest
from helpers import load_fixture, make_soup
from analyzer.meta_analyzer import analyze_meta


def check_by_id(checks, cid):
    return next(c for c in checks if c.id == cid)


class TestMetaTitle:
    def test_missing_title_is_failed(self):
        soup, _ = load_fixture("meta_no_title.html")
        checks = analyze_meta(soup)
        c = check_by_id(checks, "meta_title")
        assert c.status == "failed"

    def test_short_title_is_warning(self):
        soup, _ = load_fixture("meta_short_title.html")
        checks = analyze_meta(soup)
        c = check_by_id(checks, "meta_title")
        assert c.status == "warning"
        assert "short" in c.message.lower() or "kısa" in c.message.lower() or "chars" in c.message.lower()

    def test_long_title_is_warning(self):
        soup, _ = load_fixture("meta_long_title.html")
        checks = analyze_meta(soup)
        c = check_by_id(checks, "meta_title")
        assert c.status == "warning"

    def test_ideal_title_is_passed(self):
        soup, _ = load_fixture("meta_ideal.html")
        checks = analyze_meta(soup)
        c = check_by_id(checks, "meta_title")
        assert c.status == "passed"

    def test_title_30_to_60_chars_passes(self):
        html = "<html><head><title>Exactly 30 characters long title!</title></head></html>"
        soup = make_soup(html)
        checks = analyze_meta(soup)
        c = check_by_id(checks, "meta_title")
        title_len = len("Exactly 30 characters long title!")
        if 30 <= title_len <= 60:
            assert c.status == "passed"

    def test_title_boundary_30_passes(self):
        title = "A" * 30
        html = f"<html><head><title>{title}</title></head></html>"
        checks = analyze_meta(make_soup(html))
        assert check_by_id(checks, "meta_title").status == "passed"

    def test_title_boundary_60_passes(self):
        title = "A" * 60
        html = f"<html><head><title>{title}</title></head></html>"
        checks = analyze_meta(make_soup(html))
        assert check_by_id(checks, "meta_title").status == "passed"

    def test_title_61_chars_is_warning(self):
        title = "A" * 61
        html = f"<html><head><title>{title}</title></head></html>"
        checks = analyze_meta(make_soup(html))
        assert check_by_id(checks, "meta_title").status == "warning"

    def test_title_29_chars_is_warning(self):
        title = "A" * 29
        html = f"<html><head><title>{title}</title></head></html>"
        checks = analyze_meta(make_soup(html))
        assert check_by_id(checks, "meta_title").status == "warning"


class TestMetaDescription:
    def test_missing_desc_is_failed(self):
        soup, _ = load_fixture("meta_no_desc.html")
        checks = analyze_meta(soup)
        c = check_by_id(checks, "meta_description")
        assert c.status == "failed"

    def test_ideal_desc_is_passed(self):
        soup, _ = load_fixture("meta_ideal.html")
        checks = analyze_meta(soup)
        c = check_by_id(checks, "meta_description")
        assert c.status == "passed"

    def test_short_desc_is_warning(self):
        html = '<html><head><title>Title</title><meta name="description" content="Too short"></head></html>'
        checks = analyze_meta(make_soup(html))
        assert check_by_id(checks, "meta_description").status == "warning"

    def test_long_desc_is_warning(self):
        desc = "A" * 161
        html = f'<html><head><title>Title</title><meta name="description" content="{desc}"></head></html>'
        checks = analyze_meta(make_soup(html))
        assert check_by_id(checks, "meta_description").status == "warning"

    def test_desc_boundary_120_passes(self):
        desc = "A" * 120
        html = f'<html><head><title>Title</title><meta name="description" content="{desc}"></head></html>'
        checks = analyze_meta(make_soup(html))
        assert check_by_id(checks, "meta_description").status == "passed"

    def test_desc_boundary_160_passes(self):
        desc = "A" * 160
        html = f'<html><head><title>Title</title><meta name="description" content="{desc}"></head></html>'
        checks = analyze_meta(make_soup(html))
        assert check_by_id(checks, "meta_description").status == "passed"
