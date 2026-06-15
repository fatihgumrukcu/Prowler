import pytest
from analyzer.http_tech_analyzer import analyze_http_tech


def check_by_id(checks, cid):
    return next((c for c in checks if c.id == cid), None)


BASE_URL = "https://example.com/page"
HTTP_URL = "http://example.com/page"


class TestXRobotsTag:
    def test_noindex_header_is_warning(self):
        headers = {"X-Robots-Tag": "noindex"}
        checks = analyze_http_tech(headers, 200, BASE_URL)
        assert check_by_id(checks, "http_x_robots_noindex").status == "warning"

    def test_nofollow_header_is_warning(self):
        headers = {"X-Robots-Tag": "nofollow"}
        checks = analyze_http_tech(headers, 200, BASE_URL)
        assert check_by_id(checks, "http_x_robots_nofollow").status == "warning"

    def test_harmless_x_robots_is_passed(self):
        headers = {"X-Robots-Tag": "all"}
        checks = analyze_http_tech(headers, 200, BASE_URL)
        assert check_by_id(checks, "http_x_robots_tag").status == "passed"

    def test_no_x_robots_no_check(self):
        checks = analyze_http_tech({}, 200, BASE_URL)
        assert check_by_id(checks, "http_x_robots_tag") is None
        assert check_by_id(checks, "http_x_robots_noindex") is None


class TestContentType:
    def test_correct_content_type_is_passed(self):
        headers = {"Content-Type": "text/html; charset=utf-8"}
        checks = analyze_http_tech(headers, 200, BASE_URL)
        assert check_by_id(checks, "http_content_type").status == "passed"

    def test_missing_content_type_is_warning(self):
        checks = analyze_http_tech({}, 200, BASE_URL)
        assert check_by_id(checks, "http_content_type").status == "warning"

    def test_wrong_content_type_is_warning(self):
        headers = {"Content-Type": "application/json"}
        checks = analyze_http_tech(headers, 200, BASE_URL)
        assert check_by_id(checks, "http_content_type").status == "warning"

    def test_html_without_charset_is_warning(self):
        headers = {"Content-Type": "text/html"}
        checks = analyze_http_tech(headers, 200, BASE_URL)
        assert check_by_id(checks, "http_content_type").status == "warning"


class TestCompression:
    def test_gzip_is_passed(self):
        headers = {"Content-Encoding": "gzip", "Content-Type": "text/html; charset=utf-8"}
        checks = analyze_http_tech(headers, 200, BASE_URL)
        assert check_by_id(checks, "http_compression").status == "passed"

    def test_brotli_is_passed(self):
        headers = {"Content-Encoding": "br", "Content-Type": "text/html; charset=utf-8"}
        checks = analyze_http_tech(headers, 200, BASE_URL)
        assert check_by_id(checks, "http_compression").status == "passed"

    def test_no_compression_is_warning(self):
        headers = {"Content-Type": "text/html; charset=utf-8"}
        checks = analyze_http_tech(headers, 200, BASE_URL)
        assert check_by_id(checks, "http_compression").status == "warning"


class TestResponseTime:
    def test_fast_response_is_passed(self):
        checks = analyze_http_tech({}, 500, BASE_URL)
        assert check_by_id(checks, "http_response_time").status == "passed"

    def test_slow_response_is_warning(self):
        checks = analyze_http_tech({}, 2000, BASE_URL)
        assert check_by_id(checks, "http_response_time").status == "warning"

    def test_very_slow_response_is_failed(self):
        checks = analyze_http_tech({}, 3500, BASE_URL)
        assert check_by_id(checks, "http_response_time").status == "failed"

    def test_zero_response_time_no_check(self):
        checks = analyze_http_tech({}, 0, BASE_URL)
        assert check_by_id(checks, "http_response_time") is None

    def test_boundary_1500ms_is_passed(self):
        checks = analyze_http_tech({}, 1500, BASE_URL)
        assert check_by_id(checks, "http_response_time").status == "passed"

    def test_boundary_1501ms_is_warning(self):
        checks = analyze_http_tech({}, 1501, BASE_URL)
        assert check_by_id(checks, "http_response_time").status == "warning"


class TestCaching:
    def test_cache_control_is_passed(self):
        headers = {"Cache-Control": "max-age=86400"}
        checks = analyze_http_tech(headers, 200, BASE_URL)
        assert check_by_id(checks, "http_caching").status == "passed"

    def test_etag_is_passed(self):
        headers = {"ETag": '"abc123"'}
        checks = analyze_http_tech(headers, 200, BASE_URL)
        assert check_by_id(checks, "http_caching").status == "passed"

    def test_no_caching_headers_is_warning(self):
        checks = analyze_http_tech({}, 200, BASE_URL)
        assert check_by_id(checks, "http_caching").status == "warning"


class TestHsts:
    def test_hsts_on_https_is_passed(self):
        headers = {"Strict-Transport-Security": "max-age=31536000; includeSubDomains"}
        checks = analyze_http_tech(headers, 200, BASE_URL)
        assert check_by_id(checks, "http_hsts").status == "passed"

    def test_missing_hsts_on_https_is_warning(self):
        checks = analyze_http_tech({}, 200, BASE_URL)
        assert check_by_id(checks, "http_hsts").status == "warning"

    def test_no_hsts_check_on_http(self):
        checks = analyze_http_tech({}, 200, HTTP_URL)
        assert check_by_id(checks, "http_hsts") is None
