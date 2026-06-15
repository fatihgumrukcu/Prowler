import pytest
from helpers import load_fixture, make_soup
from analyzer.social_analyzer import analyze_social


def check_by_id(checks, cid):
    return next((c for c in checks if c.id == cid), None)


class TestOpenGraph:
    def test_all_og_present_is_passed(self):
        soup, _ = load_fixture("social_full.html")
        checks = analyze_social(soup)
        assert check_by_id(checks, "social_og").status == "passed"

    def test_no_og_is_warning(self):
        soup, _ = load_fixture("social_missing.html")
        checks = analyze_social(soup)
        assert check_by_id(checks, "social_og").status == "warning"

    def test_missing_og_image_is_warning(self):
        html = """<html><head>
        <meta property="og:title" content="Title">
        <meta property="og:description" content="Description">
        </head><body></body></html>"""
        checks = analyze_social(make_soup(html))
        assert check_by_id(checks, "social_og").status == "warning"

    def test_og_warning_message_lists_missing(self):
        soup, _ = load_fixture("social_missing.html")
        checks = analyze_social(soup)
        c = check_by_id(checks, "social_og")
        assert "og:" in c.message


class TestTwitterCard:
    def test_twitter_card_present_is_passed(self):
        soup, _ = load_fixture("social_full.html")
        checks = analyze_social(soup)
        assert check_by_id(checks, "social_twitter").status == "passed"

    def test_no_twitter_card_is_warning(self):
        soup, _ = load_fixture("social_missing.html")
        checks = analyze_social(soup)
        assert check_by_id(checks, "social_twitter").status == "warning"

    def test_twitter_card_value_returned(self):
        soup, _ = load_fixture("social_full.html")
        checks = analyze_social(soup)
        c = check_by_id(checks, "social_twitter")
        assert c.value == "summary_large_image"
