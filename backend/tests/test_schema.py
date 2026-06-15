import pytest
from helpers import load_fixture, make_soup
from analyzer.schema_analyzer import analyze_schema


def check_by_id(checks, cid):
    return next((c for c in checks if c.id == cid), None)


class TestSchemaJsonLd:
    def test_valid_schema_is_passed(self):
        soup, _ = load_fixture("schema_valid.html")
        checks = analyze_schema(soup)
        c = check_by_id(checks, "schema_json_ld")
        assert c.status == "passed"

    def test_broken_json_is_warning(self):
        soup, _ = load_fixture("schema_broken.html")
        checks = analyze_schema(soup)
        c = check_by_id(checks, "schema_json_ld")
        assert c.status == "warning"

    def test_no_schema_is_warning(self):
        soup, _ = load_fixture("schema_none.html")
        checks = analyze_schema(soup)
        c = check_by_id(checks, "schema_json_ld")
        assert c.status == "warning"

    def test_valid_schema_type_in_value(self):
        soup, _ = load_fixture("schema_valid.html")
        checks = analyze_schema(soup)
        c = check_by_id(checks, "schema_json_ld")
        assert c.value is not None

    def test_empty_page_no_schema(self):
        html = "<html><body><p>No schema here</p></body></html>"
        checks = analyze_schema(make_soup(html))
        c = check_by_id(checks, "schema_json_ld")
        assert c.status == "warning"

    def test_article_valid_fields(self):
        html = """<html><head>
        <script type="application/ld+json">
        {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": "Test Headline",
            "author": {"@type": "Person", "name": "Author"},
            "datePublished": "2024-01-01",
            "image": "https://example.com/img.jpg"
        }
        </script>
        </head><body></body></html>"""
        checks = analyze_schema(make_soup(html))
        field_check = check_by_id(checks, "schema_article_fields")
        assert field_check is not None
        assert field_check.status == "passed"

    def test_article_missing_field_is_warning(self):
        html = """<html><head>
        <script type="application/ld+json">
        {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": "Test Headline"
        }
        </script>
        </head><body></body></html>"""
        checks = analyze_schema(make_soup(html))
        field_check = check_by_id(checks, "schema_article_fields")
        assert field_check is not None
        assert field_check.status == "warning"
