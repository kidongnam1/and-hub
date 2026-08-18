#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

if [ -d ".git" ]; then
  echo "==> 최신 코드 받는 중 (git pull --ff-only origin main)"
  git pull --ff-only origin main
else
  echo "[경고] .git 폴더가 없어 업데이트를 건너뜁니다."
fi

exec ./start.sh
