import pytest
from analyzer.url_quality_analyzer import analyze_url_quality


def check_by_id(checks, cid):
    return next((c for c in checks if c.id == cid), None)


class TestTrChars:
    def test_turkish_char_in_url_is_warning(self):
        checks = analyze_url_quality("https://example.com/ürün/şeker")
        assert check_by_id(checks, "url_tr_chars").status == "warning"

    def test_ascii_url_no_tr_warning(self):
        checks = analyze_url_quality("https://example.com/urun/seker")
        assert check_by_id(checks, "url_tr_chars").status == "passed"

    def test_encoded_tr_chars_is_warning(self):
        # %C3%BC is 'ü' decoded
        checks = analyze_url_quality("https://example.com/%C3%BCr%C3%BCn")
        assert check_by_id(checks, "url_tr_chars").status == "warning"


class TestUrlSpaces:
    def test_space_encoded_is_warning(self):
        checks = analyze_url_quality("https://example.com/my%20page")
        assert check_by_id(checks, "url_spaces").status == "warning"

    def test_no_space_is_passed(self):
        checks = analyze_url_quality("https://example.com/my-page")
        assert check_by_id(checks, "url_spaces").status == "passed"


class TestUrlUppercase:
    def test_uppercase_path_is_warning(self):
        checks = analyze_url_quality("https://example.com/MyPage")
        assert check_by_id(checks, "url_uppercase").status == "warning"

    def test_lowercase_path_is_passed(self):
        checks = analyze_url_quality("https://example.com/my-page")
        assert check_by_id(checks, "url_uppercase").status == "passed"

    def test_uppercase_in_host_not_path_is_passed(self):
        # Domain case doesn't matter for path check
        checks = analyze_url_quality("https://Example.com/my-page")
        assert check_by_id(checks, "url_uppercase").status == "passed"


class TestUrlLength:
    def test_short_url_is_passed(self):
        checks = analyze_url_quality("https://example.com/page")
        assert check_by_id(checks, "url_length").status == "passed"

    def test_long_url_is_warning(self):
        long_path = "a" * 100
        checks = analyze_url_quality(f"https://example.com/{long_path}")
        assert check_by_id(checks, "url_length").status == "warning"

    def test_boundary_115_is_passed(self):
        # Build exactly 115 char URL
        base = "https://example.com/"
        path = "a" * (115 - len(base))
        url = base + path
        assert len(url) == 115
        checks = analyze_url_quality(url)
        assert check_by_id(checks, "url_length").status == "passed"

    def test_boundary_116_is_warning(self):
        base = "https://example.com/"
        path = "a" * (116 - len(base))
        url = base + path
        checks = analyze_url_quality(url)
        assert check_by_id(checks, "url_length").status == "warning"


class TestQueryParams:
    def test_no_query_params_no_check(self):
        checks = analyze_url_quality("https://example.com/page")
        c = check_by_id(checks, "url_query_params")
        assert c is None

    def test_few_params_is_passed(self):
        checks = analyze_url_quality("https://example.com/page?a=1&b=2")
        c = check_by_id(checks, "url_query_params")
        assert c.status == "passed"

    def test_many_params_is_warning(self):
        checks = analyze_url_quality("https://example.com/page?a=1&b=2&c=3&d=4")
        c = check_by_id(checks, "url_query_params")
        assert c.status == "warning"


class TestUrlUnderscore:
    def test_underscore_in_path_is_warning(self):
        checks = analyze_url_quality("https://example.com/my_page")
        assert check_by_id(checks, "url_underscore").status == "warning"

    def test_no_underscore_is_passed(self):
        checks = analyze_url_quality("https://example.com/my-page")
        assert check_by_id(checks, "url_underscore").status == "passed"
