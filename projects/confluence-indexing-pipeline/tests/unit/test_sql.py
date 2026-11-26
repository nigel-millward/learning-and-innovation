"""Tests for the SQL files and how the vector store uses them."""

import re
from pathlib import Path

from confluence_indexer import sql
from confluence_indexer.integrations import vector_store


def test_every_query_used_by_the_store_exists():
    source = Path(vector_store.__file__).read_text()
    used = set(re.findall(r'(?:query|_one|_all|_execute)\(\s*"(\w+)"', source))
    assert used, "no query names found"
    for name in used:
        assert sql.query(name).strip()


def test_schema_management_scripts_are_ordered_and_templated():
    files = sql.schema_management()
    assert [f.name for f in files] == sorted(f.name for f in files)
    assert ":embedding_dimensions" in files[0].read_text()


def test_schema_management_creates_are_rerunnable():
    # The scripts run at the start of every pipeline run.
    for f in sql.schema_management():
        creates = re.findall(r"\bCREATE\s+(?:UNIQUE\s+)?\w+\s+(?!IF NOT EXISTS)\S+", f.read_text())
        assert creates == [], f"{f.name}: add IF NOT EXISTS to {creates}"
