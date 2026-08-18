#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_DIR"

echo "==> and-hub 폰 실행 전 점검"

need_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "[실패] '$1' 명령이 없습니다. Termux에서 설치하세요: pkg install $2"
    exit 1
  fi
}

need_cmd git git
need_cmd python3 python

if [ ! -d "$HOME/and-hub" ]; then
  echo "[주의] 표준 경로가 아닙니다: $HOME/and-hub"
  echo "현재 경로: $PROJECT_DIR"
fi

if [ -d ".git" ]; then
  echo "==> Git 상태"
  git status --short --branch
else
  echo "[주의] .git 폴더가 없습니다. zip/curl 복사본이면 자동 업데이트는 건너뜁니다."
fi

echo "==> Python 문법 검사"
python3 -m py_compile web_app.py dedup_downloads.py

echo "==> Bash 문법 검사"
bash -n dedup.sh
bash -n start.sh
bash -n update_and_start.sh
bash -n scripts/setup_termux_widget.sh

echo "==> 저장소 접근 확인"
if [ -d ".git" ]; then
  git ls-remote --heads origin main >/dev/null
fi

cat <<'EOF'

[통과] 기본 점검 완료
실행:
  cd ~/and-hub
  ./update_and_start.sh

브라우저:
  http://localhost:8088

EOF
