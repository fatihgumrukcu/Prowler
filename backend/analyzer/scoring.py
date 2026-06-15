from typing import List
from models import Check

FAILED_PENALTY = 15
WARNING_PENALTY = 5


def calculate_score(checks: List[Check]) -> int:
    score = 100
    for check in checks:
        if check.status == "failed":
            score -= FAILED_PENALTY
        elif check.status == "warning":
            score -= WARNING_PENALTY
    return max(0, min(100, score))
