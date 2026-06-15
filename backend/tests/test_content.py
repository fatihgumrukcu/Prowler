import pytest
from helpers import load_fixture, make_soup
from analyzer.content_analyzer import analyze_content, _is_js_render


def check_by_id(checks, cid):
    return next((c for c in checks if c.id == cid), None)


class TestWordCount:
    def test_thin_content_is_failed(self):
        soup, html = load_fixture("content_thin.html")
        checks = analyze_content(soup, html)
        c = check_by_id(checks, "content_word_count")
        assert c.status == "failed"

    def test_adequate_content_is_passed(self):
        soup, html = load_fixture("content_adequate.html")
        checks = analyze_content(soup, html)
        c = check_by_id(checks, "content_word_count")
        assert c.status == "passed"

    def test_soft_404_is_failed(self):
        soup, html = load_fixture("soft_404.html")
        checks = analyze_content(soup, html)
        c = check_by_id(checks, "content_word_count")
        assert c.status == "failed"

    def test_boundary_exactly_100_is_warning(self):
        words = " ".join(["word"] * 100)
        html = f"<html><body><p>{words}</p></body></html>"
        checks = analyze_content(make_soup(html), html)
        c = check_by_id(checks, "content_word_count")
        assert c.status == "warning"

    def test_boundary_exactly_300_is_passed(self):
        words = " ".join(["word"] * 300)
        html = f"<html><body><p>{words}</p></body></html>"
        checks = analyze_content(make_soup(html), html)
        c = check_by_id(checks, "content_word_count")
        assert c.status == "passed"

    def test_zero_words_is_failed(self):
        html = "<html><body></body></html>"
        checks = analyze_content(make_soup(html), html)
        c = check_by_id(checks, "content_word_count")
        assert c.status == "failed"


class TestTextHtmlRatio:
    def test_low_ratio_is_warning(self):
        # A very small text inside a large HTML blob
        padding = "<!-- " + ("X" * 5000) + " -->"
        html = f"<html><head></head><body>{padding}<p>hi</p></body></html>"
        checks = analyze_content(make_soup(html), html)
        c = check_by_id(checks, "content_text_html_ratio")
        assert c is not None
        assert c.status == "warning"

    def test_adequate_ratio_is_passed(self):
        soup, html = load_fixture("content_adequate.html")
        checks = analyze_content(soup, html)
        c = check_by_id(checks, "content_text_html_ratio")
        assert c.status == "passed"

    def test_no_raw_html_skips_ratio(self):
        soup, _ = load_fixture("content_adequate.html")
        checks = analyze_content(soup, "")  # no raw_html
        c = check_by_id(checks, "content_text_html_ratio")
        assert c is None


class TestJsRender:
    def test_js_render_fixture_triggers_warning(self):
        soup, html = load_fixture("content_js_render.html")
        checks = analyze_content(soup, html)
        c = check_by_id(checks, "content_js_render")
        assert c is not None
        assert c.status == "warning"

    def test_adequate_content_no_js_render(self):
        soup, html = load_fixture("content_adequate.html")
        checks = analyze_content(soup, html)
        c = check_by_id(checks, "content_js_render")
        assert c is None

    def test_is_js_render_root_id(self):
        html = '<html><body><div id="root"></div></body></html>'
        soup = make_soup(html)
        assert _is_js_render(soup, 0) is True

    def test_is_js_render_many_scripts_few_words(self):
        html = "<html><body><script></script><script></script><script></script><p>hi</p></body></html>"
        soup = make_soup(html)
        assert _is_js_render(soup, 1) is True

    def test_is_js_render_enough_words_returns_false(self):
        html = "<html><body><div id='root'></div></body></html>"
        soup = make_soup(html)
        assert _is_js_render(soup, 100) is False


class TestTitleH1Match:
    def test_matching_title_h1_is_passed(self):
        html = "<html><head><title>Prowler SEO Analiz Aracı</title></head><body><h1>Prowler SEO Analiz</h1><p>" + " word" * 50 + "</p></body></html>"
        checks = analyze_content(make_soup(html), html)
        c = check_by_id(checks, "content_title_h1_match")
        assert c is not None
        assert c.status == "passed"

    def test_very_different_title_h1_is_warning(self):
        html = "<html><head><title>Shop Online Best Prices</title></head><body><h1>Cooking Recipes Daily</h1><p>" + " word" * 50 + "</p></body></html>"
        checks = analyze_content(make_soup(html), html)
        c = check_by_id(checks, "content_title_h1_match")
        assert c is not None
        assert c.status == "warning"
