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
    """Raised when a Confluence request fails or the API misbehaves."""


@dataclass(frozen=True)
class PageHit:
    """A lightweight search result: enough to decide whether to fetch the page.

    Attributes:
        page_id: Confluence content ID.
        version: Current version number of the page.
    """

    page_id: str
    version: int


class ConfluenceClient:
    """Read-only client for the Confluence v1 content API, with retries and backoff.

    Use as a context manager, or call ``close`` when done.
    """

    def __init__(
        self,
        config: ConfluenceConfig,
        *,
        transport: httpx.BaseTransport | None = None,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        """Create the HTTP client with basic auth (Cloud) or bearer auth (Data Center).

        Args:
            config: Confluence connection settings. A ``username`` selects basic
                auth; without one, the token is sent as a bearer token.
            transport: httpx transport to use instead of the network, for tests.
            sleep: Function used to wait between retries, replaceable in tests.
        """
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
        """Close the underlying HTTP connection pool."""
        self._http.close()

    def __enter__(self) -> ConfluenceClient:
        """Return the client itself."""
        return self

    def __exit__(self, *exc: object) -> None:
        """Close the client."""
        self.close()

    # -- queries -----------------------------------------------------------

    def changed_pages(self, since: datetime | None) -> Iterator[PageHit]:
        """Yield pages created or updated at or after ``since``, oldest first.

        Deletions are not visible to CQL; ``list_page_ids`` supports detecting them.

        Args:
            since: Earliest modification time to include; None returns every page.

        Yields:
            The ID and current version of each matching page.

        Raises:
            ConfluenceError: If a request fails after retries.
            ValueError: If ``since`` is not timezone-aware.
        """
        clauses = ["type = page", *self._space_clause()]
        if since is not None:
            clauses.append(f'lastmodified >= "{self.format_cql_datetime(since)}"')
        cql = " AND ".join(clauses) + " ORDER BY lastmodified ASC"
        log.info("Searching Confluence: %s", cql)
        for result in self._search(cql, expand="version", limit=self._config.page_size):
            yield PageHit(page_id=str(result["id"]), version=int(result["version"]["number"]))

    def list_page_ids(self) -> set[str]:
        """Return every current page ID in the configured spaces.

        Raises rather than returning a partial set: callers delete anything
        missing from this set, so an incomplete listing must never escape.

        Returns:
            The IDs of all pages visible to the service account.

        Raises:
            ConfluenceError: If any request fails after retries.
        """
        cql = " AND ".join(["type = page", *self._space_clause()])
        return {str(r["id"]) for r in self._search(cql, limit=self._config.reconcile_page_size)}

    def get_page(self, page_id: str) -> dict[str, Any] | None:
        """Fetch a page with its body, version, space, ancestors and labels.

        Args:
            page_id: Confluence content ID.

        Returns:
            The page payload, or None if the page no longer exists or is not visible.

        Raises:
            ConfluenceError: If the request fails with any status other than 404.
        """
        response = self._get(f"/rest/api/content/{page_id}", params={"expand": PAGE_EXPAND})
        if response.status_code == 404:
            return None
        _raise_for_status(response)
        payload: dict[str, Any] = response.json()
        return payload

    def format_cql_datetime(self, ts: datetime) -> str:
        """Render a timestamp the way CQL expects: minute precision, user's timezone.

        Args:
            ts: Timezone-aware timestamp.

        Returns:
            The time in ``cql_timezone`` as ``YYYY-MM-DD HH:MM``.

        Raises:
            ValueError: If ``ts`` is naive.
        """
        if ts.tzinfo is None:
            raise ValueError("Watermark timestamps must be timezone-aware")
        return ts.astimezone(ZoneInfo(self._config.cql_timezone)).strftime("%Y-%m-%d %H:%M")

    # -- transport ---------------------------------------------------------

    def _space_clause(self) -> Iterable[str]:
        """Yield a CQL ``space IN (...)`` clause when spaces are configured.

        Yields:
            At most one clause; nothing when every space is indexed.
        """
        if self._config.space_keys:
            keys = ", ".join(f'"{key}"' for key in self._config.space_keys)
            yield f"space IN ({keys})"

    def _search(
        self, cql: str, *, limit: int, expand: str | None = None
    ) -> Iterator[dict[str, Any]]:
        """Run a CQL search and follow its ``next`` links until the last page.

        Args:
            cql: CQL query.
            limit: Results requested per page.
            expand: Fields to expand on each result, if any.

        Yields:
            Each search result, in the order returned.

        Raises:
            ConfluenceError: If a request fails, or a ``next`` link repeats.
        """
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
        """Send a GET, retrying transport errors and retryable statuses with backoff.

        Waits for ``Retry-After`` when the server sends it, else uses jittered
        exponential backoff, for up to ``max_retries`` retries.

        Args:
            url: URL or path relative to the base URL.
            params: Query parameters; None keeps any query string already in ``url``.

        Returns:
            The first response whose status is not retryable.

        Raises:
            ConfluenceError: If retries run out.
        """
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
        """Return a random delay up to ``2 ** attempt`` seconds, capped at 60.

        Args:
            attempt: Number of the attempt that just failed, from 1.

        Returns:
            The delay in seconds.
        """
        # Full jitter keeps parallel workers from retrying in lockstep.
        return random.uniform(0, min(_MAX_BACKOFF_SECONDS, 2.0**attempt))  # noqa: S311


def _retry_after(response: httpx.Response) -> float | None:
    """Parse a ``Retry-After`` header given in seconds or as an HTTP date.

    Args:
        response: Response that may carry the header.

    Returns:
        The delay in seconds, clamped to 0-60, or None if the header is missing
        or unparseable.
    """
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
    """Raise for a non-2xx response, including the start of the body.

    Args:
        response: Response to check.

    Raises:
        ConfluenceError: If the status is not a success.
    """
    if response.is_success:
        return
    raise ConfluenceError(
        f"{response.request.method} {response.request.url} -> {response.status_code}: "
        f"{response.text[:500]}"
    )
