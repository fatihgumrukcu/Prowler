"""
FastAPI endpoint tests — uses TestClient (sync) + monkeypatching to avoid
real HTTP requests and real background crawl tasks.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch

from main import app
from crawler.job_store import JobStore
from models import (
    AnalyzeResponse,
    CrawlResult,
    PageResult,
    Summary,
    Check,
    SiteIssue,
)


SAMPLE_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <title>Test Page Title Tag SEO Analysis</title>
  <meta name="description" content="Test page description with enough characters to meet the 120 minimum.">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="canonical" href="https://example.com/">
</head>
<body>
  <h1>Test Heading</h1>
  <h2>Subheading</h2>
  <p>Content words here for word count purposes during SEO analysis testing.</p>
</body>
</html>"""


def make_sample_page(url="https://example.com/") -> PageResult:
    return PageResult(
        url=url,
        final_url=url,
        status_code=200,
        score=80,
        summary=Summary(passed=8, warnings=2, failed=0),
        checks=[
            Check(
                id="meta_title", category="Meta", label="Title Tag",
                status="passed", message="Good title"
            )
        ],
        discovery_source="crawl",
    )


def make_sample_crawl_result() -> CrawlResult:
    page = make_sample_page()
    return CrawlResult(
        start_url="https://example.com",
        domain="example.com",
        pages=[page],
        pages_crawled=1,
        pages_failed=0,
        sitemap_urls_found=0,
        site_score=80,
        site_summary=Summary(passed=8, warnings=2, failed=0),
        site_issues=[],
        top_issues=[],
    )


@pytest.fixture()
def client(monkeypatch):
    """TestClient with a fresh isolated JobStore."""
    store = JobStore()
    monkeypatch.setattr("main.job_store", store)
    monkeypatch.setattr("crawler.job_store.job_store", store)
    return TestClient(app), store


class TestHealthEndpoint:
    def test_root_returns_200(self, client):
        tc, _ = client
        resp = tc.get("/")
        assert resp.status_code == 200

    def test_root_returns_name(self, client):
        tc, _ = client
        data = tc.get("/").json()
        assert "Prowler" in data.get("name", "")


class TestAnalyzeEndpoint:
    def test_analyze_returns_200(self, client, monkeypatch):
        tc, store = client

        async def fake_fetch(url):
            return 200, url, False, SAMPLE_HTML, {"content-type": "text/html; charset=utf-8"}, 300, None

        monkeypatch.setattr("main.fetch_url", fake_fetch)

        resp = tc.post("/api/analyze", json={"url": "https://example.com"})
        assert resp.status_code == 200

    def test_analyze_response_has_score(self, client, monkeypatch):
        tc, _ = client

        async def fake_fetch(url):
            return 200, url, False, SAMPLE_HTML, {"content-type": "text/html; charset=utf-8"}, 300, None

        monkeypatch.setattr("main.fetch_url", fake_fetch)

        data = tc.post("/api/analyze", json={"url": "https://example.com"}).json()
        assert "score" in data
        assert isinstance(data["score"], int)

    def test_analyze_response_has_checks(self, client, monkeypatch):
        tc, _ = client

        async def fake_fetch(url):
            return 200, url, False, SAMPLE_HTML, {}, 200, None

        monkeypatch.setattr("main.fetch_url", fake_fetch)

        data = tc.post("/api/analyze", json={"url": "https://example.com"}).json()
        assert "checks" in data
        assert len(data["checks"]) > 0

    def test_analyze_empty_url_returns_422(self, client):
        tc, _ = client
        resp = tc.post("/api/analyze", json={"url": ""})
        assert resp.status_code == 422

    def test_analyze_fetch_failure_returns_502(self, client, monkeypatch):
        tc, _ = client

        async def fake_fetch(url):
            return None, url, False, None, {}, 0, "Connection refused"

        monkeypatch.setattr("main.fetch_url", fake_fetch)

        resp = tc.post("/api/analyze", json={"url": "https://unreachable.example.com"})
        assert resp.status_code == 502

    def test_analyze_adds_https_prefix(self, client, monkeypatch):
        tc, _ = client

        async def fake_fetch(url):
            return 200, url, False, SAMPLE_HTML, {}, 200, None

        monkeypatch.setattr("main.fetch_url", fake_fetch)

        resp = tc.post("/api/analyze", json={"url": "example.com"})
        # Should not raise 422 — url_utils adds https://
        assert resp.status_code in (200, 502)


class TestCrawlEndpoints:
    def test_start_crawl_returns_202(self, client, monkeypatch):
        tc, store = client

        async def fake_run(*args, **kwargs):
            pass

        monkeypatch.setattr("main._run_crawl_job", fake_run)

        resp = tc.post("/api/crawl", json={"url": "https://example.com"})
        assert resp.status_code == 202

    def test_start_crawl_returns_job_id(self, client, monkeypatch):
        tc, _ = client

        async def fake_run(*args, **kwargs):
            pass

        monkeypatch.setattr("main._run_crawl_job", fake_run)

        data = tc.post("/api/crawl", json={"url": "https://example.com"}).json()
        assert "job_id" in data
        assert len(data["job_id"]) > 0

    def test_get_crawl_job_not_found_returns_404(self, client):
        tc, _ = client
        resp = tc.get("/api/crawl/nonexistent-job-id")
        assert resp.status_code == 404

    def test_get_crawl_job_returns_status(self, client, monkeypatch):
        tc, store = client

        async def fake_run(*args, **kwargs):
            pass

        monkeypatch.setattr("main._run_crawl_job", fake_run)

        job_id = tc.post("/api/crawl", json={"url": "https://example.com"}).json()["job_id"]
        resp = tc.get(f"/api/crawl/{job_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] in ("queued", "running", "done", "error")

    def test_crawl_invalid_url_returns_422(self, client):
        tc, _ = client
        resp = tc.post("/api/crawl", json={"url": ""})
        assert resp.status_code == 422


class TestGraphEndpoint:
    def _setup_done_job(self, store):
        job_id = store.create("https://example.com")
        result = make_sample_crawl_result()
        store.update(job_id, status="done", result=result, graph_edges=[])
        return job_id

    def test_graph_unknown_job_returns_404(self, client):
        tc, _ = client
        resp = tc.get("/api/crawl/no-such-job/graph")
        assert resp.status_code == 404

    def test_graph_queued_job_returns_409(self, client, monkeypatch):
        tc, store = client

        async def fake_run(*args, **kwargs):
            pass

        monkeypatch.setattr("main._run_crawl_job", fake_run)

        job_id = tc.post("/api/crawl", json={"url": "https://example.com"}).json()["job_id"]
        resp = tc.get(f"/api/crawl/{job_id}/graph")
        assert resp.status_code == 409

    def test_graph_done_job_returns_200(self, client):
        tc, store = client
        job_id = self._setup_done_job(store)
        resp = tc.get(f"/api/crawl/{job_id}/graph")
        assert resp.status_code == 200

    def test_graph_response_has_nodes_and_edges(self, client):
        tc, store = client
        job_id = self._setup_done_job(store)
        data = tc.get(f"/api/crawl/{job_id}/graph").json()
        assert "nodes" in data
        assert "edges" in data

    def test_graph_nodes_have_required_fields(self, client):
        tc, store = client
        job_id = self._setup_done_job(store)
        data = tc.get(f"/api/crawl/{job_id}/graph").json()
        for node in data["nodes"]:
            assert "id" in node
            assert "url" in node
            assert "score" in node
            assert "is_orphan" in node


class TestExportEndpoint:
    def _setup_done_job(self, store):
        job_id = store.create("https://example.com")
        result = make_sample_crawl_result()
        store.update(job_id, status="done", result=result, graph_edges=[])
        return job_id

    def test_export_csv_returns_200(self, client):
        tc, store = client
        job_id = self._setup_done_job(store)
        resp = tc.get(f"/api/crawl/{job_id}/export?format=csv")
        assert resp.status_code == 200
        assert "text/csv" in resp.headers["content-type"]

    def test_export_json_returns_200(self, client):
        tc, store = client
        job_id = self._setup_done_job(store)
        resp = tc.get(f"/api/crawl/{job_id}/export?format=json")
        assert resp.status_code == 200

    def test_export_unknown_job_returns_404(self, client):
        tc, _ = client
        resp = tc.get("/api/crawl/no-such-job/export")
        assert resp.status_code == 404

    def test_export_queued_job_returns_409(self, client, monkeypatch):
        tc, store = client

        async def fake_run(*args, **kwargs):
            pass

        monkeypatch.setattr("main._run_crawl_job", fake_run)

        job_id = tc.post("/api/crawl", json={"url": "https://example.com"}).json()["job_id"]
        resp = tc.get(f"/api/crawl/{job_id}/export")
        assert resp.status_code == 409
