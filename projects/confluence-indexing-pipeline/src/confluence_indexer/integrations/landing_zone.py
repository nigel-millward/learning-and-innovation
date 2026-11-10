"""S3 landing zone: immutable raw pages plus per-run manifests and staging files.

Layout under ``s3://{bucket}/{prefix}/``::

    raw/space={KEY}/page_id={ID}/version={N}.json   one object per page version
    runs/run_id={RUN}/extract_manifest.json         pages extracted by a run
    runs/run_id={RUN}/transform_manifest.json
    runs/run_id={RUN}/documents.jsonl               cleaned + chunked pages

Raw objects are keyed by page version, so they are written once and give a
complete edit history for audit. Replaying a run means re-running transform
and load against its extract manifest; nothing needs re-fetching from Confluence.
"""

from __future__ import annotations

import json
import re
import tempfile
from collections.abc import Iterable, Iterator
from datetime import UTC, datetime
from typing import Any

from ..config import LandingConfig

RAW_SCHEMA_VERSION = 1


class LandingZone:
    def __init__(self, s3_client: Any, config: LandingConfig) -> None:
        self._s3 = s3_client
        self._bucket = config.bucket
        self._prefix = config.prefix
        if config.kms_key_id:
            self._encryption = {"ServerSideEncryption": "aws:kms", "SSEKMSKeyId": config.kms_key_id}
        else:
            self._encryption = {"ServerSideEncryption": "AES256"}

    # -- raw pages ---------------------------------------------------------

    def put_raw_page(self, payload: dict[str, Any], run_id: str) -> str:
        space = (payload.get("space") or {}).get("key", "_unknown")
        version = (payload.get("version") or {}).get("number", 0)
        key = f"{self._prefix}/raw/space={space}/page_id={payload['id']}/version={version}.json"
        envelope = {
            "schema_version": RAW_SCHEMA_VERSION,
            "source": "confluence",
            "run_id": run_id,
            "extracted_at": datetime.now(UTC).isoformat(),
            "payload": payload,
        }
        return self._put_json(key, envelope)

    def get_raw_page(self, uri: str) -> dict[str, Any]:
        envelope = self.get_json(uri)
        if envelope.get("schema_version") != RAW_SCHEMA_VERSION:
            raise ValueError(f"Unsupported raw schema version in {uri}")
        payload: dict[str, Any] = envelope["payload"]
        return payload

    # -- run artefacts -----------------------------------------------------

    def run_uri(self, run_id: str, name: str) -> str:
        return f"s3://{self._bucket}/{self._run_key(run_id, name)}"

    def put_run_json(self, run_id: str, name: str, data: dict[str, Any]) -> str:
        return self._put_json(self._run_key(run_id, name), data)

    def put_run_jsonl(self, run_id: str, name: str, records: Iterable[dict[str, Any]]) -> str:
        """Stream records to a temp file and upload, so memory stays flat for large runs."""
        key = self._run_key(run_id, name)
        with tempfile.TemporaryFile("w+b") as handle:
            for record in records:
                handle.write(json.dumps(record, ensure_ascii=False).encode("utf-8") + b"\n")
            handle.seek(0)
            self._s3.upload_fileobj(
                handle,
                self._bucket,
                key,
                ExtraArgs={"ContentType": "application/x-ndjson", **self._encryption},
            )
        return f"s3://{self._bucket}/{key}"

    def iter_jsonl(self, uri: str) -> Iterator[dict[str, Any]]:
        bucket, key = _split_uri(uri)
        body = self._s3.get_object(Bucket=bucket, Key=key)["Body"]
        for line in body.iter_lines():
            if line.strip():
                yield json.loads(line)

    def get_json(self, uri: str) -> dict[str, Any]:
        bucket, key = _split_uri(uri)
        data: dict[str, Any] = json.loads(
            self._s3.get_object(Bucket=bucket, Key=key)["Body"].read()
        )
        return data

    # -- internals ---------------------------------------------------------

    def _run_key(self, run_id: str, name: str) -> str:
        return f"{self._prefix}/runs/run_id={safe_run_id(run_id)}/{name}"

    def _put_json(self, key: str, data: dict[str, Any]) -> str:
        self._s3.put_object(
            Bucket=self._bucket,
            Key=key,
            Body=json.dumps(data, ensure_ascii=False).encode("utf-8"),
            ContentType="application/json",
            **self._encryption,
        )
        return f"s3://{self._bucket}/{key}"


def safe_run_id(run_id: str) -> str:
    """Airflow run IDs contain ':' and '+', which are awkward in S3 keys."""
    return re.sub(r"[^A-Za-z0-9._-]", "_", run_id)


def _split_uri(uri: str) -> tuple[str, str]:
    if not uri.startswith("s3://"):
        raise ValueError(f"Not an S3 URI: {uri}")
    bucket, _, key = uri[5:].partition("/")
    return bucket, key
