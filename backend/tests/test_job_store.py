import pytest
from crawler.job_store import JobStore


@pytest.fixture()
def store():
    return JobStore()


class TestJobStoreCreate:
    def test_create_returns_job_id(self, store):
        job_id = store.create("https://example.com")
        assert job_id is not None
        assert len(job_id) > 0

    def test_create_two_jobs_different_ids(self, store):
        id1 = store.create("https://a.com")
        id2 = store.create("https://b.com")
        assert id1 != id2

    def test_created_job_status_is_queued(self, store):
        job_id = store.create("https://example.com")
        job = store.get(job_id)
        assert job.status == "queued"

    def test_created_job_has_correct_start_url(self, store):
        job_id = store.create("https://example.com/start")
        job = store.get(job_id)
        assert job.start_url == "https://example.com/start"


class TestJobStoreGet:
    def test_get_unknown_id_returns_none(self, store):
        assert store.get("nonexistent-id") is None

    def test_get_created_job_returns_job(self, store):
        job_id = store.create("https://example.com")
        job = store.get(job_id)
        assert job is not None
        assert job.job_id == job_id


class TestJobStoreUpdate:
    def test_update_status(self, store):
        job_id = store.create("https://example.com")
        store.update(job_id, status="running")
        assert store.get(job_id).status == "running"

    def test_update_pages_found(self, store):
        job_id = store.create("https://example.com")
        store.update(job_id, pages_found=5)
        assert store.get(job_id).pages_found == 5

    def test_update_multiple_fields(self, store):
        job_id = store.create("https://example.com")
        store.update(job_id, status="done", pages_done=10, pages_failed=2)
        job = store.get(job_id)
        assert job.status == "done"
        assert job.pages_done == 10
        assert job.pages_failed == 2

    def test_update_unknown_id_no_error(self, store):
        store.update("no-such-id", status="done")


class TestJobStoreCompletedUrls:
    def test_add_completed_url(self, store):
        job_id = store.create("https://example.com")
        store.add_completed_url(job_id, "https://example.com/page1")
        assert "https://example.com/page1" in store.get(job_id).completed_urls

    def test_add_multiple_completed_urls(self, store):
        job_id = store.create("https://example.com")
        for i in range(5):
            store.add_completed_url(job_id, f"https://example.com/page{i}")
        assert len(store.get(job_id).completed_urls) == 5


class TestJobStoreAll:
    def test_all_returns_list(self, store):
        assert isinstance(store.all(), list)

    def test_all_contains_created_jobs(self, store):
        store.create("https://a.com")
        store.create("https://b.com")
        assert len(store.all()) == 2


class TestJobStoreToResponse:
    def test_to_response_fields(self, store):
        job_id = store.create("https://example.com")
        resp = store.get(job_id).to_response()
        assert resp.job_id == job_id
        assert resp.status == "queued"
        assert resp.progress["pages_found"] == 0

    def test_live_urls_only_when_running(self, store):
        job_id = store.create("https://example.com")
        store.update(job_id, status="running")
        store.add_completed_url(job_id, "https://example.com/page1")
        resp = store.get(job_id).to_response()
        assert "https://example.com/page1" in resp.live_urls

    def test_live_urls_empty_when_done(self, store):
        job_id = store.create("https://example.com")
        store.add_completed_url(job_id, "https://example.com/page1")
        store.update(job_id, status="done")
        resp = store.get(job_id).to_response()
        assert resp.live_urls == []
