#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_DIR"

cat <<'EOF'
==> and-hub 원터치 준비 시작
이 스크립트는 업데이트, 권한 설정, 점검, 위젯 등록만 합니다.
중복 파일 삭제/정리는 자동 실행하지 않습니다.

EOF

if [ -d ".git" ]; then
  echo "==> 최신 코드 받는 중 (git pull --ff-only origin main)"
  if ! git pull --ff-only origin main; then
    cat <<'EOF'

[업데이트 실패]
인터넷 연결, GitHub 접근, 또는 폰에서 직접 수정한 파일 충돌을 확인하세요.
데이터 보호를 위해 자동 정리나 강제 초기화는 하지 않습니다.

확인 명령:
  cd ~/and-hub
  git status

EOF
    exit 1
  fi
else
  echo "[주의] .git 폴더가 없어 업데이트를 건너뜁니다."
fi

echo "==> 실행 권한 설정"
chmod +x start.sh update_and_start.sh dedup.sh scripts/*.sh

echo "==> 실행 전 점검"
./scripts/phone_smoke_check.sh

echo "==> Termux:Widget 단축 실행 등록"
bash ./scripts/setup_termux_widget.sh

cat <<'EOF'

[완료] and-hub 폰 준비 완료
서버 실행:
  cd ~/and-hub
  ./update_and_start.sh

브라우저:
  http://localhost:8088

홈 화면 위젯:
  중복정리_모바일앱

EOF
