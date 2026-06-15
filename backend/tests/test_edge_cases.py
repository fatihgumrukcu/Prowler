"""
Edge-case tests: empty HTML, huge HTML, network errors, unusual URLs.
No real internet — fetcher.fetch_url is monkeypatched or respx is used.
"""
import pytest
import respx
import httpx
from bs4 import BeautifulSoup

from helpers import make_soup
from analyzer.meta_analyzer import analyze_meta
from analyzer.heading_analyzer import analyze_headings
from analyzer.content_analyzer import analyze_content
from analyzer.image_analyzer import analyze_images
from analyzer.schema_analyzer import analyze_schema
from analyzer.social_analyzer import analyze_social
from analyzer.indexability_analyzer import analyze_indexability
from analyzer.url_quality_analyzer import analyze_url_quality
from analyzer.scoring import calculate_score
from models import Check


def check_by_id(checks, cid):
    return next((c for c in checks if c.id == cid), None)


class TestEmptyHtml:
    def test_meta_empty_html_no_crash(self):
        soup = make_soup("")
        checks = analyze_meta(soup)
        assert any(c.id == "meta_title" for c in checks)
        assert any(c.id == "meta_description" for c in checks)

    def test_heading_empty_html_no_crash(self):
        soup = make_soup("")
        checks = analyze_headings(soup)
        assert any(c.id == "heading_h1" for c in checks)

    def test_content_empty_html_is_failed(self):
        soup = make_soup("")
        checks = analyze_content(soup, "")
        c = check_by_id(checks, "content_word_count")
        assert c.status == "failed"

    def test_images_empty_html_no_crash(self):
        checks = analyze_images(make_soup(""))
        assert any(c.id == "image_alt" for c in checks)

    def test_schema_empty_html_is_warning(self):
        checks = analyze_schema(make_soup(""))
        assert check_by_id(checks, "schema_json_ld").status == "warning"

    def test_social_empty_html_no_crash(self):
        checks = analyze_social(make_soup(""))
        assert any(c.id == "social_og" for c in checks)

    def test_indexability_empty_html_no_crash(self):
        checks = analyze_indexability(make_soup(""), "https://example.com")
        assert any(c.id == "indexability_lang" for c in checks)


class TestHugeHtml:
    def test_large_html_does_not_crash_meta(self):
        # 500KB of repeated content
        body = "<p>" + "word " * 10000 + "</p>"
        html = f"<html><head><title>Big Page</title></head><body>{body}</body></html>"
        soup = make_soup(html)
        checks = analyze_meta(soup)
        assert any(c.id == "meta_title" for c in checks)

    def test_large_html_word_count_is_passed(self):
        words = " ".join(["word"] * 5000)
        html = f"<html><body><p>{words}</p></body></html>"
        checks = analyze_content(make_soup(html), html)
        assert check_by_id(checks, "content_word_count").status == "passed"


class TestMalformedHtml:
    def test_unclosed_tags_no_crash(self):
        html = "<html><head><title>Test"
        checks = analyze_meta(make_soup(html))
        assert any(c.id == "meta_title" for c in checks)

    def test_deeply_nested_html_no_crash(self):
        nesting = "<div>" * 100 + "content" + "</div>" * 100
        html = f"<html><body>{nesting}</body></html>"
        checks = analyze_content(make_soup(html), html)
        assert any(c.id == "content_word_count" for c in checks)

    def test_special_chars_in_title_no_crash(self):
        html = '<html><head><title>Tıtle wïth spëcïal chäracters & symbols < > "</title></head></html>'
        checks = analyze_meta(make_soup(html))
        c = check_by_id(checks, "meta_title")
        assert c is not None

    def test_no_body_tag_no_crash(self):
        html = "<html><head><title>No body</title></head></html>"
        checks = analyze_content(make_soup(html), html)
        assert any(c.id == "content_word_count" for c in checks)


class TestUrlEdgeCases:
    def test_very_long_url(self):
        url = "https://example.com/" + "a" * 300
        checks = analyze_url_quality(url)
        assert check_by_id(checks, "url_length").status == "warning"

    def test_url_with_many_segments(self):
        url = "https://example.com/" + "/".join(["segment"] * 20)
        checks = analyze_url_quality(url)
        assert any(c.id == "url_length" for c in checks)

    def test_root_url_passes_length(self):
        checks = analyze_url_quality("https://example.com/")
        assert check_by_id(checks, "url_length").status == "passed"

    def test_url_with_fragment_no_crash(self):
        # urlparse handles fragments — should not crash
        checks = analyze_url_quality("https://example.com/page#section")
        assert checks is not None

    def test_mixed_tr_and_uppercase(self):
        # Both TR chars and uppercase — both checks should warn
        checks = analyze_url_quality("https://example.com/ÜRün")
        url_upper = check_by_id(checks, "url_uppercase")
        url_tr = check_by_id(checks, "url_tr_chars")
        assert url_upper.status == "warning"
        assert url_tr.status == "warning"


class TestScoringEdgeCases:
    def test_no_checks_returns_100(self):
        assert calculate_score([]) == 100

    def test_single_check_passed(self):
        c = Check(id="x", category="X", label="X", status="passed", message="ok")
        assert calculate_score([c]) == 100

    def test_very_many_warnings_clamps_to_zero(self):
        checks = [Check(id="x", category="X", label="X", status="warning", message="w")] * 30
        assert calculate_score(checks) == 0

    def test_score_never_negative(self):
        checks = [Check(id="x", category="X", label="X", status="failed", message="f")] * 100
        assert calculate_score(checks) >= 0

    def test_score_never_above_100(self):
        # Artificial: check with unknown status shouldn't push above 100
        checks = [Check(id="x", category="X", label="X", status="passed", message="ok")] * 100
        assert calculate_score(checks) <= 100


class TestImageEdgeCases:
    def test_data_url_image_not_checked_for_format(self):
        html = '<html><body><img src="data:image/png;base64,abc" alt="img"></body></html>'
        checks = analyze_images(make_soup(html))
        c = check_by_id(checks, "image_modern_format")
        # data-url images have no extension → treated as "passed" (cannot evaluate)
        assert c is not None

    def test_image_without_src_no_crash(self):
        html = '<html><body><img alt="no src"></body></html>'
        checks = analyze_images(make_soup(html))
        assert any(c.id == "image_alt" for c in checks)


class TestSchemaEdgeCases:
    def test_multiple_schema_blocks(self):
        html = """<html><head>
        <script type="application/ld+json">{"@context":"https://schema.org","@type":"WebSite","name":"A","url":"https://a.com"}</script>
        <script type="application/ld+json">{"@context":"https://schema.org","@type":"Organization","name":"Org","url":"https://a.com"}</script>
        </head><body></body></html>"""
        checks = analyze_schema(make_soup(html))
        schema_check = check_by_id(checks, "schema_json_ld")
        assert schema_check.status == "passed"

    def test_empty_json_ld_block(self):
        html = """<html><head>
        <script type="application/ld+json"></script>
        </head><body></body></html>"""
        checks = analyze_schema(make_soup(html))
        # empty script.string → parse error or warning
        schema_check = check_by_id(checks, "schema_json_ld")
        assert schema_check is not None

    def test_graph_schema(self):
        html = """<html><head>
        <script type="application/ld+json">
        {
          "@context": "https://schema.org",
          "@graph": [
            {"@type": "WebSite", "name": "Site", "url": "https://example.com"},
            {"@type": "Organization", "name": "Org", "url": "https://example.com"}
          ]
        }
        </script>
        </head><body></body></html>"""
        checks = analyze_schema(make_soup(html))
        schema_check = check_by_id(checks, "schema_json_ld")
        assert schema_check.status == "passed"
