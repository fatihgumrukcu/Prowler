"""
Async crawl tests — mock HTTP via respx so no real network is needed.
"""
import asyncio
import pytest
import respx
import httpx

from crawler.crawler import crawl_site
from crawler.job_store import JobStore, job_store as _global_store


HOME_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <title>Mock Home Page Title Tag Here</title>
  <meta name="description" content="This is the home page description with enough characters to pass.">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="canonical" href="https://mock.example.com/">
</head>
<body>
  <h1>Home Page</h1>
  <h2>Section One</h2>
  <p>{'word ' * 50}</p>
  <a href="/about">About</a>
  <a href="/contact">Contact</a>
</body>
</html>""".replace("{'word ' * 50}", " ".join(["word"] * 50))

ABOUT_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <title>About Page Title Tag Exactly Here</title>
  <meta name="description" content="About page description with enough length to meet the minimum requirement characters.">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="canonical" href="https://mock.example.com/about">
</head>
<body>
  <h1>About Us</h1>
  <p>{'word ' * 60}</p>
  <a href="/">Home</a>
</body>
</html>""".replace("{'word ' * 60}", " ".join(["word"] * 60))

CONTACT_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <title>Contact Page Title Tag For Test</title>
  <meta name="description" content="Contact page description with sufficient length to pass the meta description check minimum.">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="canonical" href="https://mock.example.com/contact">
</head>
<body>
  <h1>Contact Us</h1>
  <p>{'word ' * 40}</p>
</body>
</html>""".replace("{'word ' * 40}", " ".join(["word"] * 40))

ORPHAN_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <title>Orphan Page — No Inbound Links</title>
  <meta name="description" content="This orphan page is not linked from anywhere in the crawled site.">
</head>
<body>
  <h1>Orphan Page</h1>
  <p>Content here but no inbound links from site.</p>
</body>
</html>"""

SITEMAP_XML = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://mock.example.com/</loc></url>
  <url><loc>https://mock.example.com/about</loc></url>
  <url><loc>https://mock.example.com/contact</loc></url>
  <url><loc>https://mock.example.com/orphan</loc></url>
</urlset>"""

ROBOTS_TXT = "User-agent: *\nAllow: /"


@pytest.fixture()
def store():
    return JobStore()


def _crawl_kwargs(job_id: str, store: JobStore, **overrides) -> dict:
    return dict(
        job_id=job_id,
        start_url="https://mock.example.com/",
        max_pages=overrides.get("max_pages", 10),
        max_depth=overrides.get("max_depth", 3),
        include_subdomains=False,
        job_store=store,
    )


@pytest.mark.asyncio
async def test_crawl_visits_linked_pages(store):
    job_id = store.create("https://mock.example.com")

    with respx.mock(assert_all_called=False) as mock:
        mock.get("https://mock.example.com/robots.txt").mock(
            return_value=httpx.Response(200, text=ROBOTS_TXT)
        )
        mock.get("https://mock.example.com/sitemap.xml").mock(
            return_value=httpx.Response(404, text="")
        )
        mock.get("https://mock.example.com/").mock(
            return_value=httpx.Response(200, text=HOME_HTML)
        )
        mock.get("https://mock.example.com/about").mock(
            return_value=httpx.Response(200, text=ABOUT_HTML)
        )
        mock.get("https://mock.example.com/contact").mock(
            return_value=httpx.Response(200, text=CONTACT_HTML)
        )

        pages, done, failed, sitemap_count, edges = await crawl_site(
            **_crawl_kwargs(job_id, store)
        )

    assert any("mock.example.com" in p.url for p in pages)
    assert done >= 1


@pytest.mark.asyncio
async def test_crawl_returns_five_tuple(store):
    job_id = store.create("https://mock.example.com")

    with respx.mock(assert_all_called=False) as mock:
        mock.get("https://mock.example.com/robots.txt").mock(
            return_value=httpx.Response(200, text=ROBOTS_TXT)
        )
        mock.get("https://mock.example.com/sitemap.xml").mock(
            return_value=httpx.Response(404)
        )
        mock.get("https://mock.example.com/").mock(
            return_value=httpx.Response(200, text=HOME_HTML)
        )

        result = await crawl_site(**_crawl_kwargs(job_id, store, max_pages=5, max_depth=2))

    assert len(result) == 5
    page_results, done, failed, sitemap_count, edges = result
    assert isinstance(page_results, list)
    assert isinstance(done, int)
    assert isinstance(failed, int)
    assert isinstance(sitemap_count, int)
    assert isinstance(edges, list)


@pytest.mark.asyncio
async def test_crawl_404_page_increments_failed(store):
    job_id = store.create("https://mock.example.com")

    broken_html = HOME_HTML.replace(
        '<a href="/contact">Contact</a>',
        '<a href="/broken">Broken</a>'
    )

    with respx.mock(assert_all_called=False) as mock:
        mock.get("https://mock.example.com/robots.txt").mock(
            return_value=httpx.Response(200, text=ROBOTS_TXT)
        )
        mock.get("https://mock.example.com/sitemap.xml").mock(
            return_value=httpx.Response(404)
        )
        mock.get("https://mock.example.com/").mock(
            return_value=httpx.Response(200, text=broken_html)
        )
        mock.get("https://mock.example.com/about").mock(
            return_value=httpx.Response(200, text=ABOUT_HTML)
        )
        mock.get("https://mock.example.com/broken").mock(
            return_value=httpx.Response(404, text="Not Found")
        )

        _, done, failed, _, _ = await crawl_site(
            **_crawl_kwargs(job_id, store, max_depth=2)
        )

    assert failed >= 1


@pytest.mark.asyncio
async def test_crawl_collects_edges(store):
    job_id = store.create("https://mock.example.com")

    with respx.mock(assert_all_called=False) as mock:
        mock.get("https://mock.example.com/robots.txt").mock(
            return_value=httpx.Response(200, text=ROBOTS_TXT)
        )
        mock.get("https://mock.example.com/sitemap.xml").mock(
            return_value=httpx.Response(404)
        )
        mock.get("https://mock.example.com/").mock(
            return_value=httpx.Response(200, text=HOME_HTML)
        )
        mock.get("https://mock.example.com/about").mock(
            return_value=httpx.Response(200, text=ABOUT_HTML)
        )
        mock.get("https://mock.example.com/contact").mock(
            return_value=httpx.Response(200, text=CONTACT_HTML)
        )

        _, _, _, _, edges = await crawl_site(
            **_crawl_kwargs(job_id, store, max_depth=2)
        )

    assert isinstance(edges, list)
    if edges:
        assert all(isinstance(e, tuple) and len(e) == 2 for e in edges)


@pytest.mark.asyncio
async def test_crawl_respects_max_pages(store):
    job_id = store.create("https://mock.example.com")

    with respx.mock(assert_all_called=False) as mock:
        mock.get("https://mock.example.com/robots.txt").mock(
            return_value=httpx.Response(200, text=ROBOTS_TXT)
        )
        mock.get("https://mock.example.com/sitemap.xml").mock(
            return_value=httpx.Response(404)
        )
        mock.get("https://mock.example.com/").mock(
            return_value=httpx.Response(200, text=HOME_HTML)
        )
        mock.get("https://mock.example.com/about").mock(
            return_value=httpx.Response(200, text=ABOUT_HTML)
        )
        mock.get("https://mock.example.com/contact").mock(
            return_value=httpx.Response(200, text=CONTACT_HTML)
        )

        page_results, done, failed, _, _ = await crawl_site(
            **_crawl_kwargs(job_id, store, max_pages=1, max_depth=3)
        )

    assert (done + failed) <= 1
