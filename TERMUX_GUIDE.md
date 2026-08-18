# Termux에서 깃허브 파일 받아 작업하기 (가이드)

깃허브(main 브랜치)에 있는 파일을 폰의 Termux로 가져와서 실행하는 방법 및 중복 정리 사용법을 단계별로 정리했습니다.

---

## 0. 준비물 (처음 한 번만)

```bash
# 1) git 및 python 설치
pkg update
pkg install git python

# 2) 폰 저장소 접근 권한 허용 (팝업 뜨면 "허용")
termux-setup-storage
```

> 💡 용어
> - **clone(클론)** = 깃허브 저장소를 폰으로 **처음 통째로 내려받기**
> - **pull(풀)** = 이미 받아둔 걸 **최신으로 업데이트**

---

## 1. 저장소 처음 받기 (clone)

```bash
cd ~
git clone https://github.com/kidongnam1/and-hub.git
cd and-hub
```

---

## 2. 이미 받아둔 저장소를 최신으로 (pull)

폴더 안으로 들어가서 풀만 하면 됩니다.

```bash
cd ~/and-hub
git pull origin main
```

---

## 3. 파일 및 원클릭 자동 실행하기

```bash
cd ~/and-hub

# 1) 깃허브 최신 받기 + 미리보기
bash dedup.sh all-preview

# 2) 깃허브 최신 받기 + 세 가지 전체 중복 자동 정리 (휴지통 이동)
bash dedup.sh all

# 3) 실수로 정리한 항목 원래 자리에 복구하기
bash dedup.sh restore

# 4) 휴지통 비우기
bash dedup.sh empty-trash
```

---

## 4. 원스톱 단축어(alias) 등록

매번 길게 치지 않고 단어 하나로 최신 코드를 받고 정리하도록 설정합니다.

```bash
# 1) 대화형 확인 정리 (물어보고 삭제 - 가장 추천!)
echo 'alias ddask="cd ~/and-hub && git pull origin main && bash dedup.sh all-ask"' >> ~/.bashrc

# 2) 일괄 자동 정리 (물어보지 않고 삭제)
echo 'alias ddclean="cd ~/and-hub && git pull origin main && bash dedup.sh all"' >> ~/.bashrc

# 3) 원상복구
echo 'alias ddrestore="cd ~/and-hub && bash dedup.sh restore"' >> ~/.bashrc

source ~/.bashrc

# 이제부턴 폰에서 이것만 입력하면 끝!
ddask
```

---

## 5. 스마트폰 홈 화면 원터치 아이콘 (Termux:Widget)

스마트폰 바탕화면에 앱 아이콘처럼 위젯을 올려 터치 한 번으로 정리하려면:

```bash
bash scripts/setup_termux_widget.sh
```
실행 후 스마트폰 홈 화면에서 **[위젯 추가] $\rightarrow$ [Termux:Widget]**을 선택하여 배치하면 터치 1초 만에 실행됩니다.

---

## 6. Kivy Android APK 앱 빌드 안내 (`mobile_app/`)

- `mobile_app/main.py`: 스마트폰 터치 화면 전용 Kivy GUI 앱
- `mobile_app/buildozer.spec`: 안드로이드 .apk 패키징 설정 파일
- Buildozer 실행 환경(Linux/WSL)에서 `buildozer android debug` 실행 시 `andhubdedup-1.0.0.apk` 설치 파일이 생성됩니다.

---

## 자주 나는 문제 (트러블슈팅)

| 증상 | 원인 / 해결 |
|------|-------------|
| `Permission denied` / `/storage` 안 보임 | `termux-setup-storage` 다시 실행 후 허용 |
| `Already up to date.` | 이미 최신 코드라는 뜻 (정상) |
| 한글/공백 경로 오류 | 경로를 `"따옴표"` 로 감싸기 |
| 복구하고 싶을 때 | `bash dedup.sh restore` (또는 `ddrestore`) 실행 시 `_duplicates_trash/undo_log.json` 기록 기반 100% 원위치 복원 |

