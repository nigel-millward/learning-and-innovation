# dagster_university

This is a [Dagster](https://dagster.io/) project made to accompany Dagster University coursework.
https://github.com/dagster-io/project-dagster-university

## Getting started

First, install your Dagster code location as a Python package by running the command below in your terminal. By using the --editable (`-e`) flag, pip will install your Python package in ["editable mode"](https://pip.pypa.io/en/latest/topics/local-project-installs/#editable-installs) so that as you develop, local code changes will automatically apply.

```bash
pip install -e ".[dev]"
```

Duplicate the `.env.example` file and rename it to `.env`.

Then, start the Dagster UI web server:

```bash
dagster dev
```

Open http://localhost:3000 with your browser to see the project.

## Development

### Adding new Python dependencies

You can specify new Python dependencies in `setup.py`.

## Deploy on Dagster Cloud

The easiest way to deploy your Dagster project is to use Dagster Cloud.

Check out the [Dagster Cloud Documentation](https://docs.dagster.cloud) to learn more.

## Asset based approach
Before we move on, let’s recap the benefits of an asset-centric approach to building workflows:
* Context and visibility. Everyone in your organization can understand the data lineage and how data assets relate to each other
* Productivity. By building a DAG that globally understands what data exists and why, asset-centric workflows allow for reusing assets without changing an existing sequence of tasks
* Observability. It’s easy to tell exactly why assets are out-of-date, whether it might be late upstream data or errors in code
* Troubleshooting. Every run and computation is tied to the goal of producing data, so debugging tools like logs are specific to the assets being produced


## Software define asset
To create an asset, you write code that describes an asset that you want to exist, along with any other assets that the asset is derived from, and a function that computes the contents of the asset.

Specifically, an asset includes:
* An @asset decorator. This tells Dagster that the function produces an asset.
* An asset key that uniquely identifies the asset in Dagster. By default, this is the function name. However, asset keys can have prefixes, much like how files are in folders or database tables are in schemas.
* A set of upstream asset dependencies, referenced using their asset keys. We’ll talk about this more in the next lesson, which focuses on asset dependencies.
* A Python function that defines how the asset is computed.


@asset
def cookie_dough(dry_ingredients, wet_ingredients):
    return dry_ingredients + wet_ingredients


## Code Locations

A code location is a collection of Dagster definitions, such as assets. In Dagster, a code location is made up of two components:
* A Python module that contains a Definitions object
* A Python environment that can load the module above

How are code locations helpful?
Code locations exist to solve issues that come as Dagster deployments scale. When your organization grows to multiple teams orchestrating their data, things can become complicated with a single deployment.
Traditionally, this created problems such as:
* One team deploying their changes creates downtime for another team
* Two machine learning models use two different versions of the same Python package
* Being stuck using an old version of an orchestrator because your newer code uses the same dependency as your orchestrator
* Multiple teams contributing thousands of assets, making the UI difficult to search and navigate

. With code locations, users isolate their codebases without requiring multiple deployments.



Run dagster running from mulitiple code locations from modules:
dagster dev -m code_example -m dagster_university