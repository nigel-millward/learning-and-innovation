"""SQL lives in ``.sql`` files in this package; Python only loads and executes it.

    queries/     one statement per file, with psycopg named parameters (%(name)s)
    migrations/  schema DDL, applied in file-name order by ``apply_migrations``

Files ship as package data, so an installed wheel can run and migrate itself.
"""

from __future__ import annotations

from functools import cache
from importlib.resources import files
from importlib.resources.abc import Traversable

_ROOT = files(__name__)


@cache
def query(name: str) -> str:
    """The text of ``queries/{name}.sql``."""
    return _ROOT.joinpath("queries", f"{name}.sql").read_text(encoding="utf-8")


def migrations() -> list[Traversable]:
    """Migration files, in the order they must be applied."""
    found = [f for f in _ROOT.joinpath("migrations").iterdir() if f.name.endswith(".sql")]
    return sorted(found, key=lambda f: f.name)
