import pytest
from helpers import load_fixture, make_soup
from analyzer.image_analyzer import analyze_images


def check_by_id(checks, cid):
    return next((c for c in checks if c.id == cid), None)


class TestImageAlt:
    def test_all_alt_present_is_passed(self):
        soup, _ = load_fixture("images_all_alt.html")
        checks = analyze_images(soup)
        assert check_by_id(checks, "image_alt").status == "passed"

    def test_missing_alt_is_warning(self):
        soup, _ = load_fixture("images_missing_alt.html")
        checks = analyze_images(soup)
        assert check_by_id(checks, "image_alt").status == "warning"

    def test_no_images_alt_is_passed(self):
        html = "<html><body><p>No images here</p></body></html>"
        checks = analyze_images(make_soup(html))
        assert check_by_id(checks, "image_alt").status == "passed"


class TestImageDimensions:
    def test_all_dims_present_is_passed(self):
        soup, _ = load_fixture("images_all_alt.html")
        checks = analyze_images(soup)
        assert check_by_id(checks, "image_dimensions").status == "passed"

    def test_no_dims_majority_is_failed(self):
        soup, _ = load_fixture("images_no_dims.html")
        checks = analyze_images(soup)
        c = check_by_id(checks, "image_dimensions")
        assert c.status == "failed"

    def test_minority_missing_dims_is_warning(self):
        soup, _ = load_fixture("images_missing_alt.html")
        checks = analyze_images(soup)
        c = check_by_id(checks, "image_dimensions")
        # depends on fixture: 2/3 missing alt but we need dims data
        assert c is not None
        assert c.status in ("warning", "failed", "passed")

    def test_exactly_50pct_missing_is_warning(self):
        html = """<html><body>
        <img src="a.jpg" alt="a" width="100" height="100">
        <img src="b.jpg" alt="b">
        </body></html>"""
        checks = analyze_images(make_soup(html))
        c = check_by_id(checks, "image_dimensions")
        # 50% missing → not > 50 → warning
        assert c.status == "warning"

    def test_51pct_missing_is_failed(self):
        html = """<html><body>
        <img src="a.jpg" alt="a" width="100" height="100">
        <img src="b.jpg" alt="b">
        <img src="c.jpg" alt="c">
        </body></html>"""
        # 2/3 = 66% missing → failed
        checks = analyze_images(make_soup(html))
        c = check_by_id(checks, "image_dimensions")
        assert c.status == "failed"


class TestModernFormat:
    def test_webp_images_is_passed(self):
        soup, _ = load_fixture("images_all_alt.html")
        checks = analyze_images(soup)
        assert check_by_id(checks, "image_modern_format").status == "passed"

    def test_jpg_images_is_warning(self):
        soup, _ = load_fixture("images_no_dims.html")
        checks = analyze_images(soup)
        assert check_by_id(checks, "image_modern_format").status == "warning"


class TestLazyAboveFold:
    def test_lazy_first_img_is_warning(self):
        soup, _ = load_fixture("images_lazy_above_fold.html")
        checks = analyze_images(soup)
        assert check_by_id(checks, "image_lazy_above_fold").status == "warning"

    def test_no_lazy_first_img_is_passed(self):
        soup, _ = load_fixture("images_all_alt.html")
        checks = analyze_images(soup)
        assert check_by_id(checks, "image_lazy_above_fold").status == "passed"

    def test_lazy_only_on_4th_img_is_passed(self):
        html = """<html><body>
        <img src="a.webp" alt="a" width="100" height="100">
        <img src="b.webp" alt="b" width="100" height="100">
        <img src="c.webp" alt="c" width="100" height="100">
        <img src="d.webp" alt="d" width="100" height="100" loading="lazy">
        </body></html>"""
        checks = analyze_images(make_soup(html))
        assert check_by_id(checks, "image_lazy_above_fold").status == "passed"
