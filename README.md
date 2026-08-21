# Repository Structure

## Introduction

This repository is organised to support learning, experimentation, and delivery of software solutions, particularly in emerging areas such as Data Engineering, AI, Agentic AI, Snowflake, AWS, and platform engineering.

A common challenge when learning new technologies is that proof-of-concepts, course exercises, production code, and personal notes become mixed together. This structure provides a clear separation between:

- Learning existing concepts
- Exploring new ideas
- Delivering maintainable solutions

The goal is to make it easy to understand the purpose and maturity of any piece of work at a glance.

Each subdirectory is a **self-contained project** with its own toolchain and dependencies. There is no root build system and no cross-project imports — work in a project by changing into its directory first. See `CLAUDE.md` for per-project build and test commands.

---

## Repository Layout

```text
/
├── training/
├── experiments/
├── projects/
├── templates/
└── shared/
```

`projects/` and `templates/` exist but are currently empty.

---

## Repository Contents

### training/

| Directory | Focus |
|---|---|
| `aes_decryption/` | AES decryption exercise with unit tests |
| `ai/` | LLM and agent exercises, 01-06 (scaffold only, no code yet) |
| `apache-flink/` | Flink streaming word-count pipeline (Java 11, Maven) |
| `dagster_university/` | Dagster University course - Dagster, DuckDB, pandas |
| `dbt_intro/` | dbt Core introduction using `jaffle_shop` |
| `dbt_sql_optimisations_examples/` | dbt and Snowflake SQL optimisation examples (dbt project root is the doubled inner directory) |
| `dbt_transformation_examples/` | dbt transformation patterns against Snowflake (dbt project root is the doubled inner directory) |
| `localstack/` | AWS emulation with LocalStack via Docker Compose |
| `pandas/` | Pivot table generation from an Excel workbook |
| `prefect/` | Prefect orchestration - flows, deployments, work pools |
| `python/` | Python language tutorial, chapters 1-9 |
| `python_sandbox/` | Polars, PySpark, log parsing, CSV/JSON handling |
| `python_versions/` | Language features by release, Python 3.8-3.13 |
| `snowflake_sql_commands/` | SnowPro exam preparation SQL (DDL/DML/DQL and labs) |
| `snowpark/` | Snowflake Snowpark Python API |
| `terraform/` | Terraform against the AWS provider |

### experiments/

| Directory | Focus |
|---|---|
| `amazon-q/` | Amazon Q evaluation - deliberately poor vs AI-corrected Java and Python |

### shared/

| Directory | Focus |
|---|---|
| `architect/` | AWS and Snowflake architecture reference notes |
| `docker/` | Docker command notes and AWS credential startup scripts |

### projects/

Empty. Nothing has yet been promoted from `experiments/`.

---

## Training

**Purpose:** Learn and reproduce concepts from courses, tutorials, books, vendor labs, and documentation.

### Definition

Training focuses on understanding existing knowledge rather than creating something new.

Typical activities include:

- Following online courses
- Completing labs and tutorials
- Taking notes
- Building sample implementations
- Reproducing vendor demonstrations

### Examples

```text
training/
├── snowflake-generative-ai/
├── snowflake-cortex-agents/
├── aws-bedrock-fundamentals/
└── dbt-core-training/
```

### Characteristics

- Educational
- Short-lived
- Based on external material
- Not intended for production use
- May contain notes, screenshots, notebooks, and sample code

### Key Question

> "How does this technology work?"

---

## Experiments

**Purpose:** Explore ideas and validate whether something is technically possible or valuable.

### Definition

Experiments are proof-of-concepts used to evaluate ideas, architectures, integrations, or technologies.

Unlike Training, experiments involve creating something new.

Typical activities include:

- Prototyping an AI agent
- Testing new Snowflake capabilities
- Evaluating architecture approaches
- Comparing frameworks
- Investigating performance characteristics

### Examples

```text
experiments/
├── mwaa-failure-agent/
├── snowflake-rag-poc/
├── mcp-airflow-server/
├── semantic-kernel-poc/
└── dbt-log-analysis-agent/
```

### Characteristics

- Exploratory
- Fast iteration
- Limited testing
- Limited documentation
- May be discarded after evaluation
- Success criteria focused on learning

### Key Question

> "Can this work?"

---

## Projects

**Purpose:** Deliver solutions intended for ongoing use.

### Definition

Projects are maintained software solutions that provide value to users, teams, or customers.

A project usually starts life as an experiment that proved useful enough to develop further.

Typical activities include:

- Building APIs
- Deploying services
- Supporting users
- Maintaining production solutions
- Operating and monitoring systems

### Examples

```text
projects/
├── platform-support-agent/
├── data-quality-assistant/
├── cost-optimisation-service/
└── analytics-self-service-platform/
```

### Characteristics

- Maintained
- Tested
- Documented
- Deployed
- Monitored
- Supported

### Key Question

> "How do we reliably operate and maintain this solution?"

---

## Templates

**Purpose:** Reusable starting points for future work.

### Examples

```text
templates/
├── python-api-template/
├── ai-agent-template/
├── snowflake-project-template/
└── dbt-project-template/
```

Templates should contain minimal boilerplate required to start a new initiative consistently.

---

## Shared

**Purpose:** Assets and utilities used across multiple training exercises, experiments, or projects.

### Examples

Currently holds `architect/` (architecture reference notes) and `docker/`
(command notes and AWS credential scripts). Other candidate groupings:

```text
shared/
├── diagrams/
├── utilities/
├── prompts/
├── datasets/
└── documentation/
```

Avoid duplicating common components across projects.

---

## Progression Model

Work typically moves through the following lifecycle:

```text
Training
    ↓
Experiment
    ↓
Project
```

### Example

```text
training/snowflake-cortex-agents/     Learn how Cortex Agents work.
    ↓
experiments/mwaa-failure-agent/       Build a proof-of-concept that investigates
                                      Airflow, dbt, and Snowflake failures.
    ↓
projects/platform-support-agent/      Create a production-ready support agent
                                      used by the Data Engineering team.
```

Not every experiment becomes a project, and that is expected.

### Promoting work

Move work between stages with `git mv` so that history follows the code:

```bash
git mv experiments/mwaa-failure-agent projects/platform-support-agent
```

Promote to `projects/` only once the work has an owner, has tests, and someone
other than the author depends on it. Promotion is also the point at which the
standard project structure below should be adopted.

### Retiring work

An experiment that has served its purpose should be **deleted**, not left to rot.
The evaluation it produced belongs in its `README.md`, and the code remains
recoverable from git history. Keep a finished experiment in place only while its
conclusions are still being acted on.

---

## Project Structure

Once work reaches the Project stage, a standard structure is recommended:

```text
project-name/
│
├── src/
├── tests/
├── docs/
├── deployment/
├── scripts/
├── README.md
└── requirements.txt
```

### Meaning

| Folder | Purpose |
|---|---|
| `src` | Application source code |
| `tests` | Unit and integration tests |
| `docs` | Technical documentation |
| `deployment` | Infrastructure and deployment artefacts |
| `scripts` | Operational and utility scripts |

The dependency manifest depends on the stack — `requirements.txt` or
`pyproject.toml` for Python, `pom.xml` for Java.

Training exercises and experiments are not expected to follow this structure, but
every directory at any stage should carry a `README.md` explaining what it is and
how to run it.

---

## Naming Guidelines

Use lowercase and separate words with hyphens.

### Experiments and projects

Name these after their **purpose**, not the technology used to build them.

Prefer:

```text
mwaa-failure-agent
platform-support-agent
snowflake-cost-analysis
customer-data-quality-monitor
```

Avoid:

```text
test1
agent-new
snowflake-demo
poc2
experiment-final-final
```

### Training

Name these after the **technology or course** being studied, since that is what
you will search for later — `apache-flink`, `snowpark`, `dbt-core-training`.

### Existing directories

Much of the current repository predates these guidelines and uses underscores
(`aes_decryption`, `dbt_intro`, `python_versions`). Existing names are being left
alone; apply the guidelines to new work.

---

## Decision Guide

When creating new work, ask these in order and stop at the first match:

1. **Is it boilerplate for starting future work?** → `templates/`
2. **Is it an asset used by more than one piece of work?** → `shared/`
3. **Will someone other than me depend on it?** → `projects/`
4. **Am I investigating whether an idea works?** → `experiments/`
5. **Is it based on a course, tutorial, or vendor documentation?** → `training/`

---

## Guiding Principle

The maturity of the work determines its location:

```text
Training   = Understanding
Experiment = Discovering
Project    = Delivering
```
