from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from models import Check


def analyze_meta(soup: BeautifulSoup) -> List[Check]:
    checks = []

    title_tag = soup.find("title")
    title = title_tag.get_text().strip() if title_tag else None

    if not title:
        checks.append(Check(
            id="meta_title", category="Meta", label="Title Tag",
            status="failed", message="Title tag is missing",
            recommendation="Add a descriptive title tag between 30–60 characters",
        ))
    else:
        n = len(title)
        if 30 <= n <= 60:
            checks.append(Check(id="meta_title", category="Meta", label="Title Tag",
                status="passed", message=f"Title is {n} characters (optimal: 30–60)", value=title))
        elif n < 30:
            checks.append(Check(id="meta_title", category="Meta", label="Title Tag",
                status="warning", message=f"Title is too short ({n} chars)", value=title,
                recommendation="Expand your title to 30–60 characters"))
        else:
            checks.append(Check(id="meta_title", category="Meta", label="Title Tag",
                status="warning", message=f"Title is too long ({n} chars)", value=title[:200],
                recommendation="Shorten your title to 30–60 characters to avoid SERP truncation"))

    desc_tag = soup.find("meta", attrs={"name": "description"})
    desc = desc_tag.get("content", "").strip() if desc_tag else None

    if not desc:
        checks.append(Check(
            id="meta_description", category="Meta", label="Meta Description",
            status="failed", message="Meta description is missing",
            recommendation="Add a meta description between 120–160 characters",
        ))
    else:
        n = len(desc)
        if 120 <= n <= 160:
            checks.append(Check(id="meta_description", category="Meta", label="Meta Description",
                status="passed", message=f"Description is {n} characters (optimal: 120–160)", value=desc))
        elif n < 120:
            checks.append(Check(id="meta_description", category="Meta", label="Meta Description",
                status="warning", message=f"Description is too short ({n} chars)", value=desc,
                recommendation="Expand your meta description to 120–160 characters"))
        else:
            checks.append(Check(id="meta_description", category="Meta", label="Meta Description",
                status="warning", message=f"Description is too long ({n} chars)", value=desc[:200],
                recommendation="Shorten your meta description to 120–160 characters"))

    return checks


def get_meta_metadata(soup: BeautifulSoup) -> Dict[str, Optional[str]]:
    title_tag = soup.find("title")
    title = title_tag.get_text().strip() if title_tag else None

    desc_tag = soup.find("meta", attrs={"name": "description"})
    desc = desc_tag.get("content", "").strip() if desc_tag else None

    return {"title": title or None, "description": desc or None}
