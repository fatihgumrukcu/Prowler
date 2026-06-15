import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional

from models import CrawlJobResponse, CrawlResult


@dataclass
class CrawlJob:
    job_id: str
    start_url: str
    status: str = "queued"      # queued | running | done | error
    pages_found: int = 0        # URLs discovered
    pages_done: int = 0         # successfully analyzed
    pages_failed: int = 0       # fetch/parse failures
    completed_urls: List[str] = field(default_factory=list)  # live URL feed
    result: Optional[CrawlResult] = None
    error: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_response(self) -> CrawlJobResponse:
        return CrawlJobResponse(
            job_id=self.job_id,
            status=self.status,  # type: ignore[arg-type]
            progress={
                "pages_found": self.pages_found,
                "pages_done": self.pages_done,
                "pages_failed": self.pages_failed,
            },
            live_urls=list(self.completed_urls) if self.status == "running" else [],
            result=self.result,
            error=self.error,
        )


class JobStore:
    def __init__(self) -> None:
        self._jobs: Dict[str, CrawlJob] = {}

    def create(self, start_url: str) -> str:
        job_id = str(uuid.uuid4())
        self._jobs[job_id] = CrawlJob(job_id=job_id, start_url=start_url)
        return job_id

    def get(self, job_id: str) -> Optional[CrawlJob]:
        return self._jobs.get(job_id)

    def update(self, job_id: str, **kwargs) -> None:
        job = self._jobs.get(job_id)
        if job:
            for key, val in kwargs.items():
                setattr(job, key, val)

    def add_completed_url(self, job_id: str, url: str) -> None:
        job = self._jobs.get(job_id)
        if job:
            job.completed_urls.append(url)

    def all(self) -> List[CrawlJob]:
        return list(self._jobs.values())


# Singleton — shared across requests
job_store = JobStore()
