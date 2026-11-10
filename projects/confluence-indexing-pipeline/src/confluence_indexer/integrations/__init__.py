"""Adapters to external systems: everything here does I/O.

Confluence REST, the S3 landing zone, PostgreSQL/pgvector, embedding models,
and CloudWatch/SNS. Stages depend on these; tests replace them with fakes.
"""
