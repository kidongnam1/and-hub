# and-hub
안드로이드와 깃허브 연결

## dedup_downloads.py
내용이 같은 중복 **파일** 또는 **폴더**를 찾아 정리하는 스크립트입니다.
(크기로 1차 묶고 SHA-256 해시로 내용을 비교합니다.)

### Termux에서 사용하기
```bash
# 최초 1회: 저장소 접근 권한
termux-setup-storage

# 깃허브에서 파일 받기 (최초)
git clone https://github.com/kidongnam1/and-hub.git
cd and-hub
# 이미 받았다면 최신화
git pull

# 파일 하나만 받고 싶을 때 (clone 대신)
curl -O https://raw.githubusercontent.com/kidongnam1/and-hub/main/dedup_downloads.py
```

### 실행 예시
```bash
# ① 중복 파일 미리보기 (하위 폴더 포함, 아무것도 안 지움)
python3 dedup_downloads.py /storage/emulated/0/Download --recursive

# ② 안전 정리 — 휴지통(_duplicates_trash)으로 이동
python3 dedup_downloads.py /storage/emulated/0/Download --recursive --delete --trash

# ③ 중복 폴더 미리보기 (내용·구조가 완전히 같은 폴더)
python3 dedup_downloads.py /storage/emulated/0/Download --folders

# ④ 중복 폴더 정리 — 휴지통으로 이동
python3 dedup_downloads.py /storage/emulated/0/Download --folders --delete --trash

# ⑤ 이름 사본 미리보기 — "사진 (2).png" 처럼 끝에 (숫자)가 붙은 파일
python3 dedup_downloads.py /storage/emulated/0/Download --by-name --recursive

# ⑥ 이름 사본 정리 — 휴지통으로 이동
python3 dedup_downloads.py /storage/emulated/0/Download --by-name --recursive --delete --trash
```

### 옵션
| 옵션 | 설명 |
|------|------|
| (없음) | **미리보기만** — 무엇이 지워질지와 확보 가능 용량만 출력 |
| `--delete` | 실제 삭제 실행 |
| `--trash` | 삭제 대신 `_duplicates_trash` 폴더로 이동 (가장 안전, 복구 가능) |
| `--recursive` | 하위 폴더까지 검사 (파일 모드 전용) |
| `--folders` | 파일 대신 내용이 같은 중복 **폴더**를 탐지 (항상 재귀) |
| `--by-name` | 이름 끝 ` (숫자)` 사본을 중복으로 처리 (**내용은 비교 안 함**) |

권장 순서: 먼저 옵션 없이 미리보기 → 결과 확인 → `--delete --trash`로 정리.
각 그룹에서 가장 얕고 짧은 경로의 파일/폴더를 남기고 나머지를 정리합니다.
