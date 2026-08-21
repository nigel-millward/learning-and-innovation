# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A personal **"learning and innovation" monorepo** of independent sandbox projects, mostly exploring data-engineering, cloud, and AI tooling (much of it framed around BBC "learning and innovation days"). The BBC context shows up in code: Java packages are `com.bbc`, Snowpark and dbt connect to a `bbcstudios_test` account.

Work is grouped by **maturity**, not by technology. `README.md` is the authoritative description of the scheme; in short:

| Group | Contains |
|---|---|
| `training/` | Courses, tutorials, labs, vendor docs — reproducing existing material |
| `experiments/` | Proof-of-concepts answering "can this work?" |
| `projects/` | Maintained solutions someone depends on (currently empty) |
| `templates/` | Boilerplate for starting new work (currently empty) |
| `shared/` | Reference notes and utilities used across the above |

**Each project directory inside those groups is self-contained.** There is no root build system, no CI, no shared dependencies, and no cross-project imports. Treat each subproject as its own repository: `cd` into it and use its own toolchain. Do not try to build or test the repo as a whole, and don't assume a change in one project affects another.

## Per-project commands

Each Python project has its **own `requirements.txt`** and is meant to run in its own virtual env, launched **from that subproject's directory** (imports are rooted at the subproject dir, not the repo root).

| Project | Stack | Build / run / test |
|---|---|---|
| `training/aes_decryption/` | Python (AES utility), `src/main` + `src/test` layout | Run tests from `training/aes_decryption/`: `python -m unittest discover src/test`. Single test: `python -m unittest src.test.test_aes_decrypt.TestAES.test_aes_decrypt_hex_string`. CWD must be the project root. The repo's only real test suite, but it **currently fails to import** (see "IDE-rewritten imports" below). |
| `training/ai/` | — | Scaffold only: empty `01-call-an-llm` … `06-multi-agent-experiment` directories. Nothing to run yet. |
| `training/apache-flink/realtime-pipeline/` | Java 11, Maven, Flink 1.18.1, Lombok | `mvn package` → runnable jar in `target/`. Entry point: `com.bbc.ApplicationEntryPoint` → `WordCountPipeline`. Input/output paths resolve **relative to the working directory**, so run from `realtime-pipeline/`; override with `-Dwordcount.input=` / `-Dwordcount.output=`. |
| `training/dagster_university/` | Dagster + DuckDB + pandas; installable package | `pip install -e ".[dev]"`, copy `.env.example`→`.env`, then `dagster dev`. Two code locations — run both with `dagster dev -m code_example -m dagster_university`. Tests: `pytest dagster_university_tests` — but `test_assets.py` is empty, so this collects nothing. Single test once populated: `pytest dagster_university_tests/test_assets.py::test_name`. `ruff check .` is configured but **currently fails** (see gotchas). Asset file paths in `assets/constants.py` are relative to the project root (`data/`). |
| `training/dbt_intro/` | dbt Core, `jaffle_shop`, profile `default` | Standard dbt: `dbt deps`, `dbt seed`, `dbt run`, `dbt test`, `dbt build`, `dbt docs generate/serve`. Models: `models/staging` (views) → `models/marts/core` (tables). Requires `~/.dbt/profiles.yml` (not in repo). See `README_DBT*.md`. |
| `training/dbt_sql_optimisations_examples/`<br>`  dbt_sql_optimisations_examples/` | dbt Core + Snowflake, profile `dbt_sql_optimisations_examples` | **The dbt project root is the doubled inner directory** — run `dbt deps`, `dbt run`, `dbt test` from there, not the outer one. Ships its own `profiles.yml` (silver/gold models). Credentials come from `DBT_SNOWFLAKE_*` env vars, or the `local_runner` target which uses `externalbrowser` SSO. |
| `training/dbt_transformation_examples/`<br>`  dbt_transformation_examples/` | dbt Core + Snowflake, profile `dbt_transformation_examples` | As above — doubled inner directory is the project root; own `profiles.yml`, `silver`/`gold` model layers, env-var or SSO credentials. Also carries `.sqlfluff`, `seeds/`, and `snapshots/`. |
| `training/localstack/` | LocalStack (AWS emulation) via Docker | `docker-compose up` (gateway on `127.0.0.1:4566`). Use the `awslocal` CLI. `testkinesis.py` is a Kinesis smoke test. |
| `training/pandas/` | Single pivot-table script + `.xlsx` data | `python pivot_table/pivot_table.py`. |
| `training/prefect/` | Prefect 2.20.3 orchestration | Scripts in `src/main`. Full server → work-pool → deployment flow is in `prefect/README.MD`. |
| `training/python/`, `training/python_versions/` | Plain Python tutorial scripts | Run a file directly: `python <file>.py`. No deps beyond stdlib for most. `python/src` is chaptered 1–9; `python_versions` is split by release, 3.8–3.13. |
| `training/python_sandbox/` | Polars, PySpark, log parsing, CSV/JSON | Own `requirements.txt`. Run a file directly. `polars_basics/` and `pyspark_basics/` have their own READMEs (PySpark needs a local Java/Spark setup). |
| `training/snowflake_sql_commands/` | SnowPro exam-prep SQL (DDL/DML/DQL/hands-on) | Not a runnable project — execute statements manually in Snowflake. |
| `training/snowpark/` | Snowflake Snowpark Python API | `SnowflakeSession` (`src/libs/session.py`) holds connection params with **placeholder creds** (`<user_account>`, `<password>`) — fill in locally to run; never commit real credentials. |
| `training/terraform/` | Terraform, AWS provider 4.67.0 | `terraform init / plan / apply / destroy`. State is **no longer committed** (`*.tfstate` is gitignored); `.terraform.lock.hcl` **is** committed deliberately. |
| `experiments/amazon-q/` | Java (`java/`, Maven, Java 11) + Python (`python/`) demos | Example code only (incl. intentional "bad" vs "fixed-by-AI" samples). `mvn package` in `java/`. |
| `shared/architect/`, `shared/docker/` | Reference notes only | `architect/` is markdown/text resources; `docker/` is command notes plus AWS-credential startup shell scripts. No build. |

## Architecture notes

Most subprojects are single-purpose scripts. Two have structure that spans enough files to be worth knowing up front.

**`training/dagster_university/`** serves **two independent Dagster code locations** from one repo: `dagster_university/` (the real course project) and `code_example/`. `dagster dev` alone loads only the module named in `pyproject.toml`'s `[tool.dagster] module_name`; use `dagster dev -m code_example -m dagster_university` to get both. Within the main package, definitions are split by Dagster concept rather than by feature — `assets/`, `jobs/`, `partitions/`, `resources/`, `schedules/`, `sensors/` — and wired together in `__init__.py`, so tracing one asset end-to-end means reading across several of those. All on-disk data paths are indirected through `assets/constants.py` and are relative to the project root, so the CWD must be `training/dagster_university/`.

**`training/dbt_sql_optimisations_examples/` and `training/dbt_transformation_examples/`** are near-identical in shape. Both are **nested one level deeper than they look**: the real dbt project root is a doubled directory (`training/dbt_transformation_examples/dbt_transformation_examples/`), so every dbt command must run from the inner path. Both use a `models/silver/` → `models/gold/` layering against Snowflake, and both differ from `dbt_intro/` in a way that matters — they ship their **own `profiles.yml` in the project directory** rather than relying on `~/.dbt/profiles.yml`. Each defines two targets: a default that reads `DBT_SNOWFLAKE_*` env vars, and a `local_runner` target that uses `externalbrowser` SSO. The profile name must match the project name in `dbt_project.yml`.

## Conventions & gotchas

- **Secrets are stubbed, not stored.** Running `training/snowpark/`, the dbt projects, or `training/dagster_university/` requires filling in placeholder creds / `~/.dbt/profiles.yml` / `.env` locally. The dbt `profiles.yml` files in-repo reference `DBT_SNOWFLAKE_*` env vars rather than literal credentials.
- **`.gitignore` patterns are deliberately unanchored** (`.idea/`, not `.idea/*`). The earlier anchored patterns silently stopped matching when projects were nested one level deeper under `training/`. Keep new patterns unanchored unless depth genuinely matters.
- **`.env` is ignored but `.env.example` is not** — the `!.env.example` negation must stay after `.env.*`, or `dagster_university`'s template disappears.
- **Dagster writes `tmp*/` instance directories** (schedules, history, compute logs) when `DAGSTER_HOME` is unset. These are ignored via `training/dagster_university/.gitignore`.
- **IDE-rewritten imports are broken.** Six files carry absolute imports prefixed with a grouping directory (`from experiments.snowpark.src.libs.session import ...`, `import training.python_versions...`), left behind by PyCharm rewriting imports when the directories were dragged between groups. Imports here are meant to be rooted at the **subproject** directory, with no grouping prefix — `git show HEAD:snowpark/src/scripts/session_sql.py` shows the intended form. Affected: `training/aes_decryption/src/{main/main.py,test/test_aes_decrypt.py}`, `training/snowpark/src/scripts/{session_sql,session_table,session_table_specify_columns}.py`, `training/python/src/4.modules/3.packages.py`. Expect this class of breakage after any future move; grep for `^(from|import) (training|experiments|projects|shared)\.` to find it.
- **Ruff is configured but broken.** `training/dagster_university/pyproject.toml` sets `[tool.ruff] extend = "../../pyproject.toml"`, which now resolves to a repo-root `pyproject.toml` that does not exist, so `ruff check` exits with a config error. Either create that root file or drop the `extend` line. This is the same class of breakage as the `.gitignore` anchoring below — a relative path that silently changed meaning when projects moved a level deeper.
- **Java projects target Java 11** (both Maven `pom.xml` files), though a newer JDK is installed locally.
- **Naming is inconsistent by history.** New work should be lowercase-with-hyphens; existing underscore names (`aes_decryption`, `dbt_intro`, `python_versions`) are being left alone. See the README's naming guidelines.
- **Empty directories are held open with `.gitkeep`.** Git tracks no empty directory, so `projects/`, `templates/`, `training/ai/*` and other intentional scaffolds each carry an empty `.gitkeep`. Keep it when adding real files to one of those directories is still pending; delete it once the directory has content.
- **`.user.yml` is ignored, `.test_env` is not.** Both dbt projects generate `.user.yml` (a local anonymous-usage id) — ignored repo-wide. `.test_env` holds non-secret Snowflake account/warehouse/role names and is committed deliberately.
