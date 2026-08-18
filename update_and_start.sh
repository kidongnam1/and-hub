#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

if [ -d ".git" ]; then
  echo "==> 최신 코드 받는 중 (git pull --ff-only origin main)"
  if ! git pull --ff-only origin main; then
    cat <<'EOF'

[업데이트 실패]
원인 후보:
1. 인터넷 연결이 끊겼습니다.
2. 폰 안의 파일을 직접 수정해서 Git 충돌이 생겼습니다.
3. GitHub 로그인/권한 문제가 있습니다.

먼저 확인:
  cd ~/and-hub
  git status

데이터를 지우는 명령은 자동으로 실행하지 않습니다.
현재 폴더의 기존 버전으로 서버를 계속 시작합니다.

EOF
  fi
else
  echo "[경고] .git 폴더가 없어 업데이트를 건너뜁니다."
fi

exec ./start.sh
