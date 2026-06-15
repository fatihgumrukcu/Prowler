import pytest
from analyzer.url_utils import normalize_url, get_netloc


class TestNormalizeUrl:
    def test_adds_https_prefix(self):
        assert normalize_url("example.com") == "https://example.com"

    def test_keeps_https(self):
        url = "https://example.com/page"
        assert normalize_url(url) == url

    def test_keeps_http(self):
        url = "http://example.com/page"
        assert normalize_url(url) == url

    def test_strips_leading_whitespace(self):
        assert normalize_url("  https://example.com  ") == "https://example.com"

    def test_empty_string_raises(self):
        with pytest.raises(ValueError, match="empty"):
            normalize_url("")

    def test_whitespace_only_raises(self):
        with pytest.raises(ValueError):
            normalize_url("   ")

    def test_empty_string_raises_value_error(self):
        with pytest.raises(ValueError):
            normalize_url("")

    def test_url_with_path(self):
        url = "https://example.com/path/to/page"
        assert normalize_url(url) == url

    def test_url_with_query(self):
        url = "https://example.com/search?q=seo"
        assert normalize_url(url) == url


class TestGetNetloc:
    def test_returns_domain(self):
        assert get_netloc("https://example.com/page") == "example.com"

    def test_returns_domain_with_subdomain(self):
        assert get_netloc("https://www.example.com/page") == "www.example.com"

    def test_returns_domain_with_port(self):
        assert get_netloc("http://localhost:8000/api") == "localhost:8000"

    def test_empty_url_returns_empty(self):
        assert get_netloc("") == ""
