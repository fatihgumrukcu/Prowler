import pytest
from models import Check
from analyzer.scoring import calculate_score


def make_check(status: str) -> Check:
    return Check(id="test", category="Test", label="Test", status=status, message="msg")


class TestCalculateScore:
    def test_all_passed_is_100(self):
        checks = [make_check("passed")] * 5
        assert calculate_score(checks) == 100

    def test_empty_checks_is_100(self):
        assert calculate_score([]) == 100

    def test_single_failed_deducts_15(self):
        checks = [make_check("failed")]
        assert calculate_score(checks) == 85

    def test_single_warning_deducts_5(self):
        checks = [make_check("warning")]
        assert calculate_score(checks) == 95

    def test_mixed_checks(self):
        checks = [
            make_check("failed"),   # -15
            make_check("warning"),  # -5
            make_check("passed"),   # 0
        ]
        assert calculate_score(checks) == 80

    def test_score_clamped_at_zero(self):
        checks = [make_check("failed")] * 10  # -150 → clamped to 0
        assert calculate_score(checks) == 0

    def test_score_clamped_at_100(self):
        checks = [make_check("passed")] * 100
        assert calculate_score(checks) == 100

    def test_seven_failures_is_zero(self):
        # 7 * 15 = 105 → clamped to 0
        checks = [make_check("failed")] * 7
        assert calculate_score(checks) == 0

    def test_six_failures_is_10(self):
        # 6 * 15 = 90 → score = 10
        checks = [make_check("failed")] * 6
        assert calculate_score(checks) == 10

    def test_known_set(self):
        # 2 failed (-30), 3 warning (-15) → 55
        checks = (
            [make_check("failed")] * 2
            + [make_check("warning")] * 3
            + [make_check("passed")] * 4
        )
        assert calculate_score(checks) == 55
