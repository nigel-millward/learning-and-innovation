#!/bin/bash
# Runs inside LocalStack once it is ready: creates the resources the pipeline expects.
set -euo pipefail

awslocal s3 mb s3://confluence-indexing-landing
awslocal sns create-topic --name confluence-indexing-alerts
