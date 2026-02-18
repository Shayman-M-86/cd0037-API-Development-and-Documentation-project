#!/usr/bin/env bash
# this script is for quick running of tests. Requires Docker for Test Database.
set -euo pipefail

export TEST_DATABASE_URL="postgresql://${TEST_POSTGRES_USER:-postgres}:${TEST_POSTGRES_PASSWORD:-test_password}@localhost:5434/${TEST_POSTGRES_DB:-trivia_test}"
echo "Running tests..."
uv run pytest