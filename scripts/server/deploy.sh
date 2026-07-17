#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR=${PROJECT_DIR:-/opt/hermes-invest}

echo "[1/4] create runtime directories"
mkdir -p "$PROJECT_DIR/data"

cd "$PROJECT_DIR"

echo "[2/4] build image"
docker compose build --pull

echo "[3/4] start container"
docker compose up -d

echo "[4/4] show status"
docker compose ps
