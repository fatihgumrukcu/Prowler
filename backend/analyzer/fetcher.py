import time
import httpx
from typing import Tuple, Optional, Dict

USER_AGENT = "Mozilla/5.0 (compatible; ProwlerSEO/1.0)"
TIMEOUT = 15.0


async def _do_fetch(
    url: str, verify: bool
) -> Tuple[Optional[int], str, bool, Optional[str], Dict[str, str], int]:
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
    }
    async with httpx.AsyncClient(
        follow_redirects=True,
        timeout=httpx.Timeout(TIMEOUT),
        headers=headers,
        verify=verify,
    ) as client:
        t0 = time.monotonic()
        response = await client.get(url)
        response_time_ms = int((time.monotonic() - t0) * 1000)
        redirected = len(response.history) > 0
        return (
            response.status_code,
            str(response.url),
            redirected,
            response.text,
            dict(response.headers),
            response_time_ms,
        )


async def fetch_url(
    url: str,
) -> Tuple[Optional[int], str, bool, Optional[str], Dict[str, str], int, Optional[str]]:
    """Returns (status_code, final_url, redirected, html, headers, response_time_ms, error)."""
    try:
        status_code, final_url, redirected, html, headers, rt = await _do_fetch(url, verify=True)
        return status_code, final_url, redirected, html, headers, rt, None
    except httpx.SSLError:
        try:
            status_code, final_url, redirected, html, headers, rt = await _do_fetch(url, verify=False)
            return status_code, final_url, redirected, html, headers, rt, None
        except Exception as e:
            return None, url, False, None, {}, 0, f"SSL error: {e}"
    except httpx.TimeoutException:
        return None, url, False, None, {}, 0, "Request timed out"
    except httpx.ConnectError as e:
        return None, url, False, None, {}, 0, f"Connection failed: {e}"
    except Exception as e:
        return None, url, False, None, {}, 0, f"Fetch error: {e}"
