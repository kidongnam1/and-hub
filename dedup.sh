#!/usr/bin/env bash
# dedup.sh - 깃허브에서 스스로 최신화한 뒤 중복 정리 스크립트를 실행하는 도우미.
#
# 사용법:
#   bash dedup.sh <명령> [폴더]
#
# 명령(안 적으면 preview):
#   preview         이름 사본( (2),(3)... ) 미리보기          [안 지움]
#   clean           이름 사본 정리 → 휴지통으로 이동
#   files           내용이 같은 중복 파일 미리보기            [안 지움]
#   files-clean     내용 중복 파일 정리 → 휴지통으로 이동
#   folders         내용이 같은 중복 폴더 미리보기            [안 지움]
#   folders-clean   중복 폴더 정리 → 휴지통으로 이동
#   all-preview     세 가지(파일+이름+폴더) 모두 미리보기      [안 지움]
#   all             세 가지 모두 정리 → 휴지통으로 이동
#   restore         _duplicates_trash 항목 원래 위치로 원상복구
#   empty-trash     _duplicates_trash 휴지통 완전 비우기
#   help            이 도움말 보기
#
# 폴더(생략 시 다운로드 폴더):
#   기본값 /storage/emulated/0/Download
#   예) bash dedup.sh clean /storage/emulated/0/DCIM

set -euo pipefail

BRANCH="main"
DEFAULT_DIR="/storage/emulated/0/Download"

main() {
    local cmd="${1:-preview}"
    local target="${2:-$DEFAULT_DIR}"

    # 스크립트가 들어있는 폴더로 이동 (어디서 실행하든 동작하도록)
    local here
    here="$(cd "$(dirname "$0")" && pwd)"
    cd "$here"

    if [ "$cmd" = "help" ] || [ "$cmd" = "-h" ] || [ "$cmd" = "--help" ]; then
        sed -n '2,22p' "$0" | sed 's/^# \{0,1\}//'
        exit 0
    fi

    local py="$here/dedup_downloads.py"
    local trash="$target/_duplicates_trash"

    # 복구 명령
    if [ "$cmd" = "restore" ]; then
        echo "==> 원래 위치로 복구 실행중..."
        python3 "$py" "$target" --restore
        exit 0
    fi

    # 휴지통 비우기는 업데이트가 필요 없으니 먼저 처리
    if [ "$cmd" = "empty-trash" ]; then
        if [ -d "$trash" ]; then
            echo "[휴지통 비우기] $trash 를 완전히 삭제합니다..."
            rm -rf "$trash"
            echo "완료."
        else
            echo "비울 휴지통이 없습니다: $trash"
        fi
        exit 0
    fi

    # 1) 깃허브에서 최신 코드 받기
    echo "==> 최신 코드 받는 중 (git pull $BRANCH)"
    git pull origin "$BRANCH" || {
        echo "[경고] git pull 실패 — 현재 폴더의 버전으로 계속합니다."
    }

    # 2) 'all' 계열은 세 가지를 차례로 실행
    if [ "$cmd" = "all" ] || [ "$cmd" = "all-preview" ] || [ "$cmd" = "all-ask" ]; then
        local extra=()
        [ "$cmd" = "all" ] && extra=(--delete --trash)
        [ "$cmd" = "all-ask" ] && extra=(--delete --trash -i)
        run_step "$py" "$target" "[1/3] 내용 중복 파일" --recursive "${extra[@]}"
        run_step "$py" "$target" "[2/3] 이름 사본"       --by-name --recursive "${extra[@]}"
        run_step "$py" "$target" "[3/3] 중복 폴더"        --folders "${extra[@]}"
        echo; echo "==> 세 가지 모두 완료."
        [ "$cmd" = "all-preview" ] && echo "실제로 지우려면:  bash dedup.sh all"
        exit 0
    fi

    # 단일 명령에 맞는 옵션 정하기
    local args=()
    case "$cmd" in
        preview)        args=(--by-name --recursive) ;;
        clean)          args=(--by-name --recursive --delete --trash) ;;
        ask)            args=(--by-name --recursive --delete --trash -i) ;;
        files)          args=(--recursive) ;;
        files-clean)    args=(--recursive --delete --trash) ;;
        folders)        args=(--folders) ;;
        folders-clean)  args=(--folders --delete --trash) ;;
        *)
            echo "[오류] 모르는 명령: $cmd"
            echo "사용 가능: preview clean ask all-ask files files-clean folders folders-clean all-preview all restore empty-trash help"
            exit 1
            ;;
    esac

    # 3) 실행
    echo "==> 실행: python3 dedup_downloads.py $target ${args[*]}"
    echo
    python3 "$py" "$target" "${args[@]}"
}

# 한 단계 실행 헬퍼: 제목 출력 후 python 스크립트 호출
run_step() {
    local py="$1" target="$2" title="$3"; shift 3
    echo
    echo "================= $title ================="
    python3 "$py" "$target" "$@"
}

main "$@"
