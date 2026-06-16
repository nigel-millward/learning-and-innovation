# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A personal **"learning and innovation" monorepo** of independent sandbox projects, mostly exploring data-engineering, cloud, and AI tooling (much of it framed around BBC "learning and innovation days"). The BBC context shows up in code: Java packages are `com.bbc`, Snowpark connects to a `bbcstudios_test` account.

**Each top-level directory is a self-contained project.** There is no root build system, no CI, no shared dependencies, and no cross-project imports. Treat each subproject as its own repository: `cd` into it and use its own toolchain. Do not try to build or test the repo as a whole, and don't assume a change in one project affects another. Active language-tutorial work currently lives in `python/`.

## Per-project commands

Each Python project has its **own `requirements.txt`** and is meant to run in its own virtual env, launched **from that subproject's directory** (imports are rooted at the subproject dir, not the repo root).

| Project | Stack | Build / run / test |
|---|---|---|
| `aes_decryption/` | Python (AES utility), `src/main` + `src/test` layout | Run tests from `aes_decryption/`: `python -m unittest discover src/test`. Tests import as `from src.main.aes_decrypt import ...`, so CWD must be the project root. |
| `dagster_university/` | Dagster + DuckDB + pandas; installable package | `pip install -e ".[dev]"`, copy `.env.example`→`.env`, then `dagster dev`. Two code locations — run both with `dagster dev -m code_example -m dagster_university`. Tests: `pytest dagster_university_tests`. Linted with Ruff. Asset file paths in `assets/constants.py` are relative to the project root (`data/`). |
| `apache-flink/realtime-pipeline/` | Java 11, Maven, Flink 1.18.1, Lombok | `mvn package` → runnable jar in `target/`. Entry point: `com.bbc.ApplicationEntryPoint` → `WordCountPipeline`. Reads `src/main/resources/testdata/...`, writes to a `target/wordcount/...` file sink. |
| `amazon-q/` | Java (`java/`, Maven, Java 11) + Python (`python/`) demos | Example code only (incl. intentional "bad" vs "fixed-by-AI" samples). `mvn package` in `java/`. |
| `dbt_intro/` | dbt Core, `jaffle_shop`, profile `default` | Standard dbt: `dbt deps`, `dbt seed`, `dbt run`, `dbt test`, `dbt build`, `dbt docs generate/serve`. Models: `models/staging` (views) → `models/marts/core` (tables). Requires `~/.dbt/profiles.yml` (not in repo). See `README_DBT*.md`. |
| `terraform/` | Terraform, AWS provider 4.67.0 | `terraform init / plan / apply / destroy`. **`terraform.tfstate` is committed** — be careful editing or applying. |
| `localstack/` | LocalStack (AWS emulation) via Docker | `docker-compose up` (gateway on `127.0.0.1:4566`). Use the `awslocal` CLI. `testkinesis.py` is a Kinesis smoke test. |
| `prefect/` | Prefect 2.20.3 orchestration | Scripts in `src/main`. Full server → work-pool → deployment flow is in `prefect/README.MD`. |
| `snowpark/` | Snowflake Snowpark Python API | `SnowflakeSession` (`src/libs/session.py`) holds connection params with **placeholder creds** (`<user_account>`, `<password>`) — fill in locally to run; never commit real credentials. |
| `python/`, `python_versions/` | Plain Python tutorial scripts | Run a file directly: `python <file>.py`. No deps beyond stdlib for most. |
| `pandas/` | Single pivot-table script + `.xlsx` data | `python pivot_table/pivot_table.py`. |
| `snowflake_sql_commands/` | SnowPro exam-prep SQL (DDL/DQL/hands-on) | Not a runnable project — execute statements manually in Snowflake. |
| `architect/`, `docker/` | Reference notes only | `architect/` is markdown/text resources; `docker/` is command notes plus AWS-credential startup shell scripts. No build. |

## Conventions & gotchas

- **Secrets are stubbed, not stored.** Running `snowpark/`, `dbt_intro/`, or `dagster_university/` requires filling in placeholder creds / `~/.dbt/profiles.yml` / `.env` locally. `.env*` is gitignored.
- **Committed build/state artifacts.** `terraform.tfstate`, some Maven `target/` output, and `.idea/`/`__pycache__` files exist in history. `.gitignore` covers `.idea/`, `target/`, `dbt_packages/`, `logs/`, `.env*`, `.DS_Store` going forward — prefer not to add more generated files.
- **Java projects target Java 11** (both Maven `pom.xml` files).
