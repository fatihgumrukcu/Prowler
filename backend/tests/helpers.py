from pathlib import Path
from bs4 import BeautifulSoup

FIXTURES = Path(__file__).parent / "fixtures"


def load_fixture(name: str):
    """Return (soup, raw_html) for a fixture file."""
    html = (FIXTURES / name).read_text(encoding="utf-8")
    return BeautifulSoup(html, "html.parser"), html


def make_soup(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "html.parser")
