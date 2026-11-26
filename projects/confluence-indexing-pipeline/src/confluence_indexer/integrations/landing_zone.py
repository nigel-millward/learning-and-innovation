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
    """Reads and writes the pipeline's objects in the S3 landing zone."""

    def __init__(self, s3_client: Any, config: LandingConfig) -> None:
        """Store the client and choose server-side encryption.

        Args:
            s3_client: boto3 S3 client.
            config: Bucket, prefix and optional KMS key. Objects use SSE-KMS
                when a key is set, else SSE-S3 (AES256).
        """
        self._s3 = s3_client
        self._bucket = config.bucket
        self._prefix = config.prefix
        if config.kms_key_id:
            self._encryption = {"ServerSideEncryption": "aws:kms", "SSEKMSKeyId": config.kms_key_id}
        else:
            self._encryption = {"ServerSideEncryption": "AES256"}

    # -- raw pages ---------------------------------------------------------

    def put_raw_page(self, payload: dict[str, Any], run_id: str) -> str:
        """Write a raw page payload, wrapped in a versioned envelope.

        Args:
            payload: Page JSON from the Confluence API.
            run_id: Airflow run ID that extracted the page, recorded in the envelope.

        Returns:
            The ``s3://`` URI of the object, keyed by space, page ID and version.
        """
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
        """Read a raw page written by ``put_raw_page``.

        Args:
            uri: ``s3://`` URI of the object.

        Returns:
            The Confluence page payload from inside the envelope.

        Raises:
            ValueError: If the envelope's schema version is not supported.
        """
        envelope = self.get_json(uri)
        if envelope.get("schema_version") != RAW_SCHEMA_VERSION:
            raise ValueError(f"Unsupported raw schema version in {uri}")
        payload: dict[str, Any] = envelope["payload"]
        return payload

    # -- run artefacts -----------------------------------------------------

    def run_uri(self, run_id: str, name: str) -> str:
        """Return the URI of a run artefact, without reading or writing it.

        Args:
            run_id: Airflow run ID.
            name: File name within the run's folder.

        Returns:
            The ``s3://`` URI.
        """
        return f"s3://{self._bucket}/{self._run_key(run_id, name)}"

    def put_run_json(self, run_id: str, name: str, data: dict[str, Any]) -> str:
        """Write a JSON artefact into the run's folder.

        Args:
            run_id: Airflow run ID.
            name: File name within the run's folder.
            data: Object to serialise.

        Returns:
            The ``s3://`` URI of the object.
        """
        return self._put_json(self._run_key(run_id, name), data)

    def put_run_jsonl(self, run_id: str, name: str, records: Iterable[dict[str, Any]]) -> str:
        """Stream records to a temp file and upload, so memory stays flat for large runs.

        Args:
            run_id: Airflow run ID.
            name: File name within the run's folder.
            records: Records to write, one JSON object per line.

        Returns:
            The ``s3://`` URI of the object.
        """
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
        """Stream records from a JSON Lines object, skipping blank lines.

        Args:
            uri: ``s3://`` URI of the object.

        Yields:
            Each record, in file order.

        Raises:
            ValueError: If ``uri`` is not an S3 URI.
        """
        bucket, key = _split_uri(uri)
        body = self._s3.get_object(Bucket=bucket, Key=key)["Body"]
        for line in body.iter_lines():
            if line.strip():
                yield json.loads(line)

    def get_json(self, uri: str) -> dict[str, Any]:
        """Read a JSON object from S3.

        Args:
            uri: ``s3://`` URI of the object.

        Returns:
            The parsed object.

        Raises:
            ValueError: If ``uri`` is not an S3 URI.
        """
        bucket, key = _split_uri(uri)
        data: dict[str, Any] = json.loads(
            self._s3.get_object(Bucket=bucket, Key=key)["Body"].read()
        )
        return data

    # -- internals ---------------------------------------------------------

    def _run_key(self, run_id: str, name: str) -> str:
        """Return the S3 key of a run artefact.

        Args:
            run_id: Airflow run ID; made safe for S3 with ``safe_run_id``.
            name: File name within the run's folder.

        Returns:
            The key, relative to the bucket.
        """
        return f"{self._prefix}/runs/run_id={safe_run_id(run_id)}/{name}"

    def _put_json(self, key: str, data: dict[str, Any]) -> str:
        """Write an object as UTF-8 JSON with the configured encryption.

        Args:
            key: S3 key, relative to the bucket.
            data: Object to serialise.

        Returns:
            The ``s3://`` URI of the object.
        """
        self._s3.put_object(
            Bucket=self._bucket,
            Key=key,
            Body=json.dumps(data, ensure_ascii=False).encode("utf-8"),
            ContentType="application/json",
            **self._encryption,
        )
        return f"s3://{self._bucket}/{key}"


def safe_run_id(run_id: str) -> str:
    """Replace characters outside ``[A-Za-z0-9._-]`` in a run ID with ``_``.

    Airflow run IDs contain ':' and '+', which are awkward in S3 keys.

    Args:
        run_id: Airflow run ID.

    Returns:
        The run ID, safe to use in an S3 key.
    """
    return re.sub(r"[^A-Za-z0-9._-]", "_", run_id)


def _split_uri(uri: str) -> tuple[str, str]:
    """Split an ``s3://bucket/key`` URI.

    Args:
        uri: S3 URI.

    Returns:
        The bucket and key.

    Raises:
        ValueError: If ``uri`` does not start with ``s3://``.
    """
    if not uri.startswith("s3://"):
        raise ValueError(f"Not an S3 URI: {uri}")
    bucket, _, key = uri[5:].partition("/")
    return bucket, key
