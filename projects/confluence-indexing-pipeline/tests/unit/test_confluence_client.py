from datetime import UTC, datetime

import httpx
import pytest

from confluence_indexer.config import ConfluenceConfig
from confluence_indexer.integrations.confluence import ConfluenceClient, ConfluenceError, PageHit


def client(handler, *, space_keys=("ENG", "OPS"), tz="UTC", username="svc@example.com"):
    config = ConfluenceConfig(
        base_url="https://example.atlassian.net/wiki",
        api_token="secret",
        username=username,
        space_keys=space_keys,
        cql_timezone=tz,
        max_retries=3,
    )
    sleeps: list[float] = []
    c = ConfluenceClient(config, transport=httpx.MockTransport(handler), sleep=sleeps.append)
    return c, sleeps


def test_incremental_search_builds_cql_and_follows_cursor_pagination():
    seen = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        if "cursor" not in request.url.params:
            return httpx.Response(
                200,
                json={
                    "results": [{"id": "1", "version": {"number": 4}}],
                    "_links": {"next": "/rest/api/content/search?cursor=abc&limit=50&cql=x"},
                },
            )
        return httpx.Response(200, json={"results": [{"id": "2", "version": {"number": 1}}]})

    c, _ = client(handler, tz="Europe/London")
    since = datetime(2026, 7, 1, 8, 30, 59, tzinfo=UTC)
    changed_pages = list(c.changed_pages(since))

    assert changed_pages == [PageHit("1", 4), PageHit("2", 1)]
    first, second = seen
    assert first.url.path == "/wiki/rest/api/content/search"
    # BST: 08:30 UTC is 09:30 local, truncated to the minute.
    assert first.url.params["cql"] == (
        'type = page AND space IN ("ENG", "OPS") AND lastmodified >= "2026-07-01 09:30" '
        "ORDER BY lastmodified ASC"
    )
    assert first.url.params["expand"] == "version"
    assert second.url.path == "/wiki/rest/api/content/search"
    assert second.url.params["cursor"] == "abc"
    assert first.headers["Authorization"].startswith("Basic ")


def test_full_search_has_no_date_clause_and_bearer_auth_without_username():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["Authorization"] == "Bearer secret"
        assert request.url.params["cql"] == "type = page ORDER BY lastmodified ASC"
        return httpx.Response(200, json={"results": []})

    c, _ = client(handler, space_keys=(), username=None)
    assert list(c.changed_pages(None)) == []


def test_naive_datetimes_are_rejected():
    c, _ = client(lambda r: httpx.Response(200, json={}))
    with pytest.raises(ValueError):
        c.format_cql_datetime(datetime(2026, 1, 1))


def test_retries_honour_retry_after_then_succeed():
    responses = iter(
        [
            httpx.Response(429, headers={"Retry-After": "7"}),
            httpx.Response(503),
            httpx.Response(200, json={"id": "9"}),
        ]
    )
    c, sleeps = client(lambda r: next(responses))

    assert c.get_page("9") == {"id": "9"}
    assert sleeps[0] == 7.0
    assert len(sleeps) == 2


def test_retries_are_bounded():
    c, sleeps = client(lambda r: httpx.Response(500, text="nope"))
    with pytest.raises(ConfluenceError, match="500"):
        c.get_page("9")
    assert len(sleeps) == 3


def test_transport_errors_are_retried():
    calls = {"n": 0}

    def handler(request):
        calls["n"] += 1
        if calls["n"] == 1:
            raise httpx.ConnectError("reset")
        return httpx.Response(200, json={"id": "9"})

    c, sleeps = client(handler)
    assert c.get_page("9") == {"id": "9"}
    assert len(sleeps) == 1


def test_missing_page_returns_none_and_client_errors_raise():
    c, _ = client(lambda r: httpx.Response(404))
    assert c.get_page("1") is None

    c, sleeps = client(lambda r: httpx.Response(403, text="forbidden"))
    with pytest.raises(ConfluenceError, match="403"):
        c.get_page("1")
    assert sleeps == []


def test_list_page_ids_collects_all_pages():
    pages = iter(
        [
            {
                "results": [{"id": "1"}, {"id": "2"}],
                "_links": {"next": "/rest/api/content/search?start=2"},
            },
            {"results": [{"id": "3"}]},
        ]
    )
    c, _ = client(lambda r: httpx.Response(200, json=next(pages)))
    assert c.list_page_ids() == {"1", "2", "3"}


def test_list_page_ids_raises_rather_than_returning_partial_results():
    pages = iter(
        [
            httpx.Response(200, json={"results": [{"id": "1"}], "_links": {"next": "/x?start=1"}}),
            httpx.Response(400, text="bad"),
        ]
    )
    c, _ = client(lambda r: next(pages))
    with pytest.raises(ConfluenceError):
        c.list_page_ids()


def test_invalid_space_keys_are_rejected_before_reaching_cql():
    with pytest.raises(ValueError):
        ConfluenceConfig(base_url="x", api_token="t", space_keys=('ENG") OR (1=1',))


def test_repeated_next_link_raises_instead_of_looping():
    page = {"results": [{"id": "1"}], "_links": {"next": "/rest/api/content/search?cursor=same"}}
    c, _ = client(lambda r: httpx.Response(200, json=page))
    with pytest.raises(ConfluenceError, match="Pagination loop"):
        c.list_page_ids()
