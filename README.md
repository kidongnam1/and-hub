# and-hub
안드로이드와 깃허브 연결 & 중복 파일/폴더 자동 정리 도구

## dedup_downloads.py
내용이 같은 중복 **파일** 또는 **폴더**를 찾아 정리하는 초고속 멀티스레드 스크립트입니다.  
(크기 1차 분류 → 10MB 이상 64KB 부분 해시 → SHA-256 전체 해시 비교 후 안전 정리 및 원클릭 복구를 지원합니다.)

### Termux에서 사용하기
```bash
# 최초 1회: 저장소 접근 권한
termux-setup-storage

# 깃허브에서 파일 받기 (최초)
git clone https://github.com/kidongnam1/and-hub.git
cd and-hub
# 이미 받았다면 최신화
git pull origin main

# 파일 하나만 받고 싶을 때 (clone 대신)
curl -O https://raw.githubusercontent.com/kidongnam1/and-hub/main/dedup_downloads.py
```

### 가장 쉬운 방법: dedup.sh (자동 업데이트 + 실행)
`dedup.sh`는 깃허브에서 최신 코드를 스스로 받은 뒤(`git pull`) 청소를 실행합니다.
```bash
cd ~/and-hub

bash dedup.sh preview        # 이름 사본( (2),(3)… ) 미리보기  [안 지움]
bash dedup.sh clean          # 이름 사본 정리 → 휴지통으로 이동
bash dedup.sh files          # 내용 중복 파일 미리보기
bash dedup.sh files-clean    # 내용 중복 파일 정리 → 휴지통
bash dedup.sh folders        # 중복 폴더 미리보기
bash dedup.sh folders-clean  # 중복 폴더 정리 → 휴지통
bash dedup.sh all-preview    # 세 가지(파일+이름+폴더) 모두 미리보기
bash dedup.sh all            # 세 가지 모두 일괄 정리 → 휴지통 (일괄 추천)
bash dedup.sh all-ask        # 세 가지 모두 대화형 정리 (그룹별로 물어보고 이동)
bash dedup.sh restore        # 휴지통(_duplicates_trash) 항목 원래 위치로 원상복구
bash dedup.sh empty-trash    # 휴지통(_duplicates_trash) 비우기
bash dedup.sh help           # 도움말

# 다른 폴더를 청소하려면 뒤에 경로를 붙이면 됩니다
bash dedup.sh clean /storage/emulated/0/DCIM
```

### Windows PC 사용 방법: start_dedup.bat & 주간 자동 스케줄러
- **원클릭 메뉴**: Windows 사용자는 `start_dedup.bat` 파일만 더블클릭하면 파란 창에서 1번(미리보기), 2번(안전 정리), 3번(원위치 복구)을 메뉴로 실행할 수 있습니다.
- **주간 자동 청소 등록**: `powershell -ExecutionPolicy Bypass -File scripts/schedule_auto_clean.ps1` 실행 시 매주 일요일 오전 09:00시마다 다운로드 폴더 중복 파일이 자동으로 `_duplicates_trash`로 정돈됩니다.

### (직접 실행) 파이썬 실행 예시
```bash
# ① 중복 파일 미리보기 (하위 폴더 포함, 아무것도 안 지움)
python3 dedup_downloads.py /storage/emulated/0/Download --recursive

# ② 안전 정리 — 휴지통(_duplicates_trash)으로 이동
python3 dedup_downloads.py /storage/emulated/0/Download --recursive --delete --trash

# ③ 원위치 복구 (휴지통에 있던 파일들을 원래 자리로 복원)
python3 dedup_downloads.py /storage/emulated/0/Download --restore

# ④ 중복 폴더 정리 — 휴지통으로 이동
python3 dedup_downloads.py /storage/emulated/0/Download --folders --delete --trash

# ⑤ 이름 사본 정리 — 휴지통으로 이동
python3 dedup_downloads.py /storage/emulated/0/Download --by-name --recursive --delete --trash
```

### 옵션
| 옵션 | 설명 |
|------|------|
| (없음) | **미리보기만** — 무엇이 지워질지와 확보 가능 용량만 출력 |
| `--delete` | 실제 삭제 실행 |
| `--trash` | 삭제 대신 `_duplicates_trash` 폴더로 이동 (가장 안전, 복구 가능) |
| `--restore` | `_duplicates_trash` 내 항목들을 `undo_log.json` 기록 기반 원래 위치로 원상복구 |
| `--recursive` | 하위 폴더까지 검사 (파일 모드 전용) |
| `--folders` | 파일 대신 내용이 같은 중복 **폴더**를 탐지 (항상 재귀) |
| `--by-name` | 이름 끝 ` (숫자)` 사본을 중복으로 처리 (**내용은 비교 안 함**) |
| `--workers` | 멀티스레드 병렬 처리 스레드 수 지정 (기본: 자동) |

권장 순서: 먼저 옵션 없이 미리보기 → 결과 확인 → `--delete --trash`로 정리.  
실수나 문제 발생 시 `--restore`로 100% 원래 자리로 복원 가능합니다.
