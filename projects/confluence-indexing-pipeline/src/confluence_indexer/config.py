"""Pipeline configuration.

All settings come from environment variables so the same code runs unchanged
under MWAA (env set by the startup script), self-managed Airflow, and local
`airflow standalone`. Secret values may be given directly (``CONFLUENCE_API_TOKEN``) or as an
AWS Secrets Manager reference (``CONFLUENCE_API_TOKEN_SECRET_ID``); the
reference form is the one to use anywhere other than a developer laptop.
"""

from __future__ import annotations

import json
import os
import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import timedelta
from functools import cache
from typing import Any
from urllib.parse import quote

_SPACE_KEY = re.compile(r"^[A-Za-z0-9~_-]+$")


class ConfigError(ValueError):
    """Raised when required configuration is missing or invalid."""


@dataclass(frozen=True)
class ConfluenceConfig:
    base_url: str  # e.g. https://example.atlassian.net/wiki
    api_token: str = field(repr=False)
    # Cloud authenticates with email + API token (basic auth). Leave unset for
    # Data Center, where api_token is a personal access token (bearer auth).
    username: str | None = None
    space_keys: tuple[str, ...] = ()  # empty = every space the service account can see
    # CQL compares lastmodified in the API user's profile timezone, not UTC.
    cql_timezone: str = "UTC"
    page_size: int = 50
    reconcile_page_size: int = 200
    timeout_seconds: float = 30.0
    max_retries: int = 5

    def __post_init__(self) -> None:
        for key in self.space_keys:
            if not _SPACE_KEY.match(key):
                raise ConfigError(f"Invalid Confluence space key: {key!r}")


@dataclass(frozen=True)
class LandingConfig:
    bucket: str
    prefix: str = "confluence-indexing"
    kms_key_id: str | None = None


@dataclass(frozen=True)
class ChunkingConfig:
    chunk_size_tokens: int = 800
    chunk_overlap_tokens: int = 120  # 15%
    encoding_name: str = "cl100k_base"  # tokenizer used by text-embedding-3-*
    boilerplate_patterns: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.chunk_size_tokens <= 0:
            raise ConfigError("CHUNK_SIZE_TOKENS must be positive")
        if not 0 <= self.chunk_overlap_tokens < self.chunk_size_tokens:
            raise ConfigError("CHUNK_OVERLAP_TOKENS must be >= 0 and < CHUNK_SIZE_TOKENS")


# Per-provider defaults, so switching EMBEDDING_PROVIDER alone gives a working setup.
DEFAULT_EMBEDDING_MODELS = {
    "ollama": ("nomic-embed-text", 768),
    "openai": ("text-embedding-3-large", 1536),
    "azure_openai": ("text-embedding-3-large", 1536),  # model = Azure deployment name
    "bedrock": ("amazon.titan-embed-text-v2:0", 1024),
}


@dataclass(frozen=True)
class EmbeddingConfig:
    provider: str  # ollama | openai | azure_openai | bedrock
    model: str  # model name, Azure deployment name, or Bedrock model id
    dimensions: int
    # Bump to force every chunk to be re-embedded even though its text is unchanged,
    # e.g. after a provider-side model update that kept the same name.
    revision: str = "1"
    batch_size: int = 64
    timeout_seconds: float = 120.0
    api_key: str | None = field(default=None, repr=False)
    ollama_base_url: str = "http://localhost:11434"
    azure_endpoint: str | None = None
    azure_api_version: str | None = None
    aws_region: str | None = None

    def __post_init__(self) -> None:
        if self.provider not in DEFAULT_EMBEDDING_MODELS:
            raise ConfigError(f"Unsupported EMBEDDING_PROVIDER: {self.provider!r}")
        if self.provider == "azure_openai" and not self.azure_endpoint:
            raise ConfigError("AZURE_OPENAI_ENDPOINT is required for azure_openai")

    @property
    def embedding_version(self) -> str:
        """Identity of the vector space a chunk's embedding lives in.

        Vectors are only comparable, and only reusable, within one version.
        """
        return f"{self.provider}:{self.model}:{self.dimensions}:r{self.revision}"


@dataclass(frozen=True)
class DatabaseConfig:
    database_connection_string: str = field(repr=False)


@dataclass(frozen=True)
class ObservabilityConfig:
    metrics_namespace: str = "ConfluenceIndexing"
    alert_topic_arn: str | None = None
    notify_on_success: bool = False


@dataclass(frozen=True)
class GuardrailConfig:
    # Re-read this far behind the stored load_date: CQL dates have minute
    # precision and the Confluence search index is eventually consistent.
    load_date_overlap: timedelta = timedelta(minutes=30)
    # A stage fails (and Airflow retries it) when more than this fraction of
    # its pages fail. Below it, failures are dead-lettered and retried next run.
    max_failure_ratio: float = 0.1
    # A dead-lettered page is retried this many times before it is parked.
    max_page_attempts: int = 5
    # Refuse to delete more than this fraction of the index in one run, which
    # protects against a permissions change or API fault emptying the listing.
    # Deletions of up to mass_delete_min_pages are always allowed.
    max_delete_ratio: float = 0.2
    mass_delete_min_pages: int = 10
    load_batch_pages: int = 50


@dataclass(frozen=True)
class PipelineConfig:
    pipeline_name: str
    environment: str
    aws_region: str | None
    confluence: ConfluenceConfig
    landing: LandingConfig
    chunking: ChunkingConfig
    embedding: EmbeddingConfig
    database: DatabaseConfig
    observability: ObservabilityConfig
    guardrails: GuardrailConfig

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> PipelineConfig:
        e = _Env(os.environ if env is None else env)
        region = e.get("AWS_REGION") or e.get("AWS_DEFAULT_REGION")
        provider = e.get("EMBEDDING_PROVIDER", "ollama")
        default_model, default_dimensions = DEFAULT_EMBEDDING_MODELS.get(provider, ("", 0))
        return cls(
            pipeline_name=e.get("PIPELINE_NAME", "confluence-indexing"),
            environment=e.get("ENVIRONMENT", "dev"),
            aws_region=region,
            confluence=ConfluenceConfig(
                base_url=e.require("CONFLUENCE_BASE_URL").rstrip("/"),
                api_token=e.secret("CONFLUENCE_API_TOKEN", region, required=True),
                username=e.get("CONFLUENCE_USERNAME") or None,
                space_keys=e.csv("CONFLUENCE_SPACE_KEYS"),
                cql_timezone=e.get("CONFLUENCE_CQL_TIMEZONE", "UTC"),
                page_size=e.int_("CONFLUENCE_PAGE_SIZE", 50),
                reconcile_page_size=e.int_("CONFLUENCE_RECONCILE_PAGE_SIZE", 200),
                timeout_seconds=e.float_("CONFLUENCE_TIMEOUT_SECONDS", 30.0),
                max_retries=e.int_("CONFLUENCE_MAX_RETRIES", 5),
            ),
            landing=LandingConfig(
                bucket=e.require("LANDING_BUCKET"),
                prefix=e.get("LANDING_PREFIX", "confluence-indexing").strip("/"),
                kms_key_id=e.get("LANDING_KMS_KEY_ID") or None,
            ),
            chunking=ChunkingConfig(
                chunk_size_tokens=e.int_("CHUNK_SIZE_TOKENS", 800),
                chunk_overlap_tokens=e.int_("CHUNK_OVERLAP_TOKENS", 120),
                encoding_name=e.get("TOKENIZER_ENCODING", "cl100k_base"),
                boilerplate_patterns=tuple(e.json_list("BOILERPLATE_PATTERNS")),
            ),
            embedding=EmbeddingConfig(
                provider=provider,
                model=e.get("EMBEDDING_MODEL", default_model),
                dimensions=e.int_("EMBEDDING_DIMENSIONS", default_dimensions),
                revision=e.get("EMBEDDING_REVISION", "1"),
                batch_size=e.int_("EMBEDDING_BATCH_SIZE", 64),
                timeout_seconds=e.float_("EMBEDDING_TIMEOUT_SECONDS", 120.0),
                api_key=_embedding_api_key(e, provider, region),
                ollama_base_url=e.get("OLLAMA_BASE_URL", "http://localhost:11434"),
                azure_endpoint=e.get("AZURE_OPENAI_ENDPOINT") or None,
                azure_api_version=e.get("AZURE_OPENAI_API_VERSION", "2024-10-21"),
                aws_region=e.get("BEDROCK_REGION") or region,
            ),
            database=DatabaseConfig(
                database_connection_string=_database_connection_string(e, region)
            ),
            observability=ObservabilityConfig(
                metrics_namespace=e.get("METRICS_NAMESPACE", "ConfluenceIndexing"),
                alert_topic_arn=e.get("ALERT_TOPIC_ARN") or None,
                notify_on_success=e.bool_("NOTIFY_ON_SUCCESS", False),
            ),
            guardrails=GuardrailConfig(
                load_date_overlap=timedelta(minutes=e.int_("WATERMARK_OVERLAP_MINUTES", 30)),
                max_failure_ratio=e.float_("MAX_FAILURE_RATIO", 0.1),
                max_page_attempts=e.int_("MAX_PAGE_ATTEMPTS", 5),
                max_delete_ratio=e.float_("MAX_DELETE_RATIO", 0.2),
                mass_delete_min_pages=e.int_("MASS_DELETE_MIN_PAGES", 10),
                load_batch_pages=e.int_("LOAD_BATCH_PAGES", 50),
            ),
        )


def _embedding_api_key(e: _Env, provider: str, region: str | None) -> str | None:
    if provider == "openai":
        return e.secret("OPENAI_API_KEY", region, required=True)
    if provider == "azure_openai":
        return e.secret("AZURE_OPENAI_API_KEY", region, required=True)
    return None  # Ollama needs no key; Bedrock uses the task's IAM role


def _database_connection_string(e: _Env, region: str | None) -> str:
    """Resolve the PostgreSQL connection string.

    ``PG_DSN_SECRET_ID`` may point at an RDS-managed secret (JSON with
    username/password/host/port/dbname) or at a plain connection string.
    """
    raw = e.secret("PG_DSN", region, required=True)
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return raw
    if not isinstance(parsed, dict):
        raise ConfigError("PG_DSN secret must be a connection string or an RDS secret JSON object")
    sslmode = e.get("PG_SSLMODE", "verify-full")
    return (
        f"postgresql://{quote(parsed['username'], safe='')}:{quote(parsed['password'], safe='')}"
        f"@{parsed['host']}:{parsed.get('port', 5432)}/{parsed.get('dbname', 'postgres')}"
        f"?sslmode={sslmode}"
    )


class _Env:
    def __init__(self, env: Mapping[str, str]) -> None:
        self._env = env

    def get(self, name: str, default: Any = None) -> Any:
        value = self._env.get(name)
        return default if value is None or value == "" else value

    def require(self, name: str) -> str:
        value = self.get(name)
        if value is None:
            raise ConfigError(f"Missing required environment variable {name}")
        return str(value)

    def int_(self, name: str, default: int) -> int:
        return int(self.get(name, default))

    def float_(self, name: str, default: float) -> float:
        return float(self.get(name, default))

    def bool_(self, name: str, default: bool) -> bool:
        value = self.get(name)
        return default if value is None else str(value).lower() in {"1", "true", "yes", "on"}

    def csv(self, name: str) -> tuple[str, ...]:
        value = self.get(name, "")
        return tuple(part.strip() for part in value.split(",") if part.strip())

    def json_list(self, name: str) -> list[str]:
        value = self.get(name)
        if value is None:
            return []
        parsed = json.loads(value)
        if not isinstance(parsed, list) or not all(isinstance(p, str) for p in parsed):
            raise ConfigError(f"{name} must be a JSON array of strings")
        return parsed

    def secret(self, name: str, region: str | None, *, required: bool = False) -> Any:
        """Read ``NAME`` directly, else fetch the secret named by ``NAME_SECRET_ID``."""
        value = self.get(name)
        if value is None and (secret_id := self.get(f"{name}_SECRET_ID")):
            value = _fetch_secret(secret_id, region)
        if value is None and required:
            raise ConfigError(f"Set {name} or {name}_SECRET_ID")
        return value


@cache
def _fetch_secret(secret_id: str, region: str | None) -> str:
    import boto3

    response = boto3.client("secretsmanager", region_name=region).get_secret_value(
        SecretId=secret_id
    )
    return str(response["SecretString"])
