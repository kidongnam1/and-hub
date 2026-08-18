#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

echo "==> and-hub 모바일 웹앱 서버 시작 준비"
python3 web_app.py
