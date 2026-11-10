"""Confluence REST API client.

Uses the v1 content API, which both Confluence Cloud and Data Center serve
under ``{base_url}/rest/api``, and CQL for incremental search.
"""

from __future__ import annotations

import logging
import random
import time
from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass
from datetime import datetime
from email.utils import parsedate_to_datetime
from typing import Any
from zoneinfo import ZoneInfo

import httpx

from ..config import ConfluenceConfig

log = logging.getLogger(__name__)

PAGE_EXPAND = "body.storage,version,space,ancestors,metadata.labels"
_RETRYABLE_STATUS = frozenset({429, 500, 502, 503, 504})
_MAX_BACKOFF_SECONDS = 60.0


class ConfluenceError(RuntimeError):
    pass


@dataclass(frozen=True)
class PageHit:
    """A lightweight search result: enough to decide whether to fetch the page."""

    page_id: str
    version: int


class ConfluenceClient:
    def __init__(
        self,
        config: ConfluenceConfig,
        *,
        transport: httpx.BaseTransport | None = None,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self._config = config
        self._sleep = sleep
        auth: httpx.Auth | None = None
        headers = {"Accept": "application/json"}
        if config.username:
            auth = httpx.BasicAuth(config.username, config.api_token)
        else:
            headers["Authorization"] = f"Bearer {config.api_token}"
        self._http = httpx.Client(
            base_url=config.base_url,
            auth=auth,
            headers=headers,
            timeout=config.timeout_seconds,
            transport=transport,
        )

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> ConfluenceClient:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    # -- queries -----------------------------------------------------------

    def changed_pages(self, since: datetime | None) -> Iterator[PageHit]:
        """Pages created or updated at or after ``since`` (all pages when None).

        Deletions are not visible to CQL; ``list_page_ids`` supports detecting them.
        """
        clauses = ["type = page", *self._space_clause()]
        if since is not None:
            clauses.append(f'lastmodified >= "{self.format_cql_datetime(since)}"')
        cql = " AND ".join(clauses) + " ORDER BY lastmodified ASC"
        log.info("Searching Confluence: %s", cql)
        for result in self._search(cql, expand="version", limit=self._config.page_size):
            yield PageHit(page_id=str(result["id"]), version=int(result["version"]["number"]))

    def list_page_ids(self) -> set[str]:
        """Every current page ID in the configured spaces.

        Raises rather than returning a partial set: callers delete anything
        missing from this set, so an incomplete listing must never escape.
        """
        cql = " AND ".join(["type = page", *self._space_clause()])
        return {str(r["id"]) for r in self._search(cql, limit=self._config.reconcile_page_size)}

    def get_page(self, page_id: str) -> dict[str, Any] | None:
        """Full page payload, or None if the page no longer exists or is not visible."""
        response = self._get(f"/rest/api/content/{page_id}", params={"expand": PAGE_EXPAND})
        if response.status_code == 404:
            return None
        _raise_for_status(response)
        payload: dict[str, Any] = response.json()
        return payload

    def format_cql_datetime(self, ts: datetime) -> str:
        """Render a timestamp the way CQL expects: minute precision, user's timezone."""
        if ts.tzinfo is None:
            raise ValueError("Watermark timestamps must be timezone-aware")
        return ts.astimezone(ZoneInfo(self._config.cql_timezone)).strftime("%Y-%m-%d %H:%M")

    # -- transport ---------------------------------------------------------

    def _space_clause(self) -> Iterable[str]:
        if self._config.space_keys:
            keys = ", ".join(f'"{key}"' for key in self._config.space_keys)
            yield f"space IN ({keys})"

    def _search(
        self, cql: str, *, limit: int, expand: str | None = None
    ) -> Iterator[dict[str, Any]]:
        query: dict[str, Any] = {"cql": cql, "limit": limit}
        if expand:
            query["expand"] = expand
        url = "/rest/api/content/search"
        params: dict[str, Any] | None = query
        seen: set[str] = set()
        while True:
            response = self._get(url, params=params)
            _raise_for_status(response)
            body = response.json()
            yield from body.get("results", [])
            next_link = (body.get("_links") or {}).get("next")
            if not next_link:
                return
            if next_link in seen:
                raise ConfluenceError(f"Pagination loop: {next_link} was already fetched")
            seen.add(next_link)
            # The next link is relative to the context path and already carries
            # the cursor/start and the original query parameters. params must be
            # None, not {}: httpx replaces a URL's query string with any params given.
            url, params = next_link, None

    def _get(self, url: str, params: dict[str, Any] | None = None) -> httpx.Response:
        attempt = 0
        while True:
            attempt += 1
            try:
                response = self._http.get(url, params=params)
            except httpx.TransportError as exc:
                if attempt > self._config.max_retries:
                    raise ConfluenceError(f"GET {url} failed after {attempt} attempts") from exc
                delay = self._backoff(attempt)
                log.warning("GET %s transport error (%s); retrying in %.1fs", url, exc, delay)
            else:
                if response.status_code not in _RETRYABLE_STATUS:
                    return response
                if attempt > self._config.max_retries:
                    _raise_for_status(response)
                delay = _retry_after(response) or self._backoff(attempt)
                log.warning(
                    "GET %s returned %s; retrying in %.1fs", url, response.status_code, delay
                )
            self._sleep(delay)

    @staticmethod
    def _backoff(attempt: int) -> float:
        # Full jitter keeps parallel workers from retrying in lockstep.
        return random.uniform(0, min(_MAX_BACKOFF_SECONDS, 2.0**attempt))  # noqa: S311


def _retry_after(response: httpx.Response) -> float | None:
    value = response.headers.get("Retry-After")
    if not value:
        return None
    try:
        return min(_MAX_BACKOFF_SECONDS, max(0.0, float(value)))
    except ValueError:
        pass
    try:
        when = parsedate_to_datetime(value)
    except (TypeError, ValueError):
        return None
    return min(_MAX_BACKOFF_SECONDS, max(0.0, when.timestamp() - time.time()))


def _raise_for_status(response: httpx.Response) -> None:
    if response.is_success:
        return
    raise ConfluenceError(
        f"{response.request.method} {response.request.url} -> {response.status_code}: "
        f"{response.text[:500]}"
    )
