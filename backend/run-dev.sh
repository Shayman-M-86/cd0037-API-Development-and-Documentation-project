#!/usr/bin/env bash
set -euo pipefail

cleanup() {
  echo ""
  echo "Stopping containers..."
  docker compose down
}
trap cleanup EXIT INT TERM

echo
echo "-------------[ Setting up development environment ]-------------"
echo
echo "Starting Postgres..."
echo

docker compose up -d trivia_db

echo "Waiting for Postgres to be ready..."
timeout_seconds=30
start=$(date +%s)

until docker compose exec -T trivia_db pg_isready \
    -U "${POSTGRES_USER:-postgres}" \
    -d "${POSTGRES_DB:-trivia}" >/dev/null 2>&1
do
  if [ $(( $(date +%s) - start )) -ge "$timeout_seconds" ]; then
    echo "Postgres not ready after ${timeout_seconds}s"
    exit 1
  fi
  sleep 1
done

# If pg_isready returns too early for you, use a small loop:
# until docker compose exec -T trivia_db pg_isready -U "${POSTGRES_USER:-postgres}" -d "${POSTGRES_DB:-trivia}" >/dev/null; do
#   sleep 1
# done

echo "Running Flask..."
export FLASK_APP=flaskr
export FLASK_ENV=development
uv run flask run --debug --host 0.0.0.0 --port 5000