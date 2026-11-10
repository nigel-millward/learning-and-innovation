import json

import boto3
import pytest
from moto import mock_aws

from confluence_indexer.config import ConfigError, PipelineConfig

BASE = {
    "CONFLUENCE_BASE_URL": "https://example.atlassian.net/wiki/",
    "CONFLUENCE_API_TOKEN": "conf-secret-1",
    "CONFLUENCE_SPACE_KEYS": "ENG, OPS",
    "LANDING_BUCKET": "bucket",
    "OPENAI_API_KEY": "openai-secret-2",
    "PG_DSN": "postgresql://u:p@h/db",
    "AWS_REGION": "eu-west-2",
}


def test_defaults_from_minimal_env():
    config = PipelineConfig.from_env(BASE)
    assert config.confluence.base_url == "https://example.atlassian.net/wiki"
    assert config.confluence.space_keys == ("ENG", "OPS")
    assert config.chunking.chunk_size_tokens == 800
    assert config.chunking.chunk_overlap_tokens == 120
    # Local-first: Ollama needs no key, so OPENAI_API_KEY above is simply unused.
    assert config.embedding.embedding_version == "ollama:nomic-embed-text:768:r1"
    assert config.embedding.ollama_base_url == "http://localhost:11434"
    assert config.database.dsn == "postgresql://u:p@h/db"


def test_secrets_are_not_in_repr():
    text = repr(PipelineConfig.from_env(BASE))
    assert not any(s in text for s in ("conf-secret-1", "openai-secret-2", "u:p@h"))


def test_missing_required_values_fail_fast():
    env = {k: v for k, v in BASE.items() if k != "LANDING_BUCKET"}
    with pytest.raises(ConfigError, match="LANDING_BUCKET"):
        PipelineConfig.from_env(env)


def test_invalid_overlap_is_rejected():
    with pytest.raises(ConfigError):
        PipelineConfig.from_env({**BASE, "CHUNK_OVERLAP_TOKENS": "900"})


def test_hosted_provider_defaults_and_key_requirement():
    config = PipelineConfig.from_env({**BASE, "EMBEDDING_PROVIDER": "openai"})
    assert config.embedding.embedding_version == "openai:text-embedding-3-large:1536:r1"
    assert config.embedding.api_key == "openai-secret-2"

    env = {k: v for k, v in BASE.items() if k != "OPENAI_API_KEY"}
    with pytest.raises(ConfigError, match="OPENAI_API_KEY"):
        PipelineConfig.from_env({**env, "EMBEDDING_PROVIDER": "openai"})


def test_bedrock_needs_no_api_key():
    env = {k: v for k, v in BASE.items() if k != "OPENAI_API_KEY"}
    config = PipelineConfig.from_env(
        {
            **env,
            "EMBEDDING_PROVIDER": "bedrock",
            "EMBEDDING_MODEL": "amazon.titan-embed-text-v2:0",
            "EMBEDDING_DIMENSIONS": "1024",
        }
    )
    assert config.embedding.api_key is None
    assert config.embedding.aws_region == "eu-west-2"


def test_secrets_manager_references_including_rds_secret_json():
    with mock_aws():
        sm = boto3.client("secretsmanager", region_name="eu-west-2")
        sm.create_secret(Name="confluence-token", SecretString="from-sm")
        sm.create_secret(
            Name="rds",
            SecretString=json.dumps(
                {
                    "username": "indexer",
                    "password": "p@ss/word",
                    "host": "db.internal",
                    "port": 5432,
                    "dbname": "rag",
                }
            ),
        )
        env = {k: v for k, v in BASE.items() if k not in ("CONFLUENCE_API_TOKEN", "PG_DSN")}
        config = PipelineConfig.from_env(
            {**env, "CONFLUENCE_API_TOKEN_SECRET_ID": "confluence-token", "PG_DSN_SECRET_ID": "rds"}
        )

    assert config.confluence.api_token == "from-sm"
    assert config.database.dsn == (
        "postgresql://indexer:p%40ss%2Fword@db.internal:5432/rag?sslmode=verify-full"
    )
