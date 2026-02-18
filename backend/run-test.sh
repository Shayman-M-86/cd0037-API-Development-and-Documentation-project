#!/usr/bin/env bash
set -euo pipefail

# COMPOSE="docker compose -f docker-compose.test.yml"

# cleanup() {
#   echo 
#   echo "Stopping containers..."
#   $COMPOSE down -v
# }
# trap cleanup EXIT INT TERM

# echo
# echo "-------------[ Setting up test environment ]-------------"
# echo
# echo "Starting Postgres..."
# echo

# $COMPOSE up -d trivia_db_test

# echo "Waiting for Postgres to be ready..."
# timeout_seconds=30
# start=$(date +%s)

# until $COMPOSE exec -T trivia_db_test pg_isready \
#     -U "${TEST_POSTGRES_USER:-postgres}" \
#     -d "${TEST_POSTGRES_DB:-trivia_test}" >/dev/null 2>&1
# do
#   if [ $(( $(date +%s) - start )) -ge "$timeout_seconds" ]; then
#     echo "Postgres not ready after ${timeout_seconds}s"
#     exit 1
#   fi
#   sleep 1
# done

# # If pg_isready returns too early for you, use a small loop:
# # until docker compose exec -T trivia_db_test pg_isready -U "${POSTGRES_USER:-postgres}" -d "${TEST_POSTGRES_DB:-trivia_test}" >/dev/null; do
# #   sleep 1
# # done
export TEST_DATABASE_URL="postgresql://${TEST_POSTGRES_USER:-postgres}:${TEST_POSTGRES_PASSWORD:-test_password}@localhost:5434/${TEST_POSTGRES_DB:-trivia_test}"
echo "Running tests..."
uv run pytest