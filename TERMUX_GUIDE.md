# Termux에서 깃허브 파일 받아 작업하기 (왕초보 가이드)

깃허브(main 또는 브랜치)에 있는 파일을 폰의 Termux로 가져와서 실행하는 방법을
단계별로 정리했습니다. 그대로 따라 하면 됩니다.

---

## 0. 준비물 (처음 한 번만)

```bash
# 1) git 설치
pkg update
pkg install git

# 2) 폰 저장소 접근 권한 허용 (팝업 뜨면 "허용")
termux-setup-storage
```

> 💡 용어
> - **clone(클론)** = 깃허브 저장소를 폰으로 **처음 통째로 내려받기**
> - **pull(풀)** = 이미 받아둔 걸 **최신으로 업데이트**
> - **branch(브랜치)** = 같은 저장소 안의 "작업 갈래". `main`이 기본이고, 따로 만든 갈래도 있음

---

## 1. 저장소 처음 받기 (clone)

### 1-A. main 브랜치를 받을 때
```bash
cd ~
git clone https://github.com/kidongnam1/and-hub.git
cd and-hub
```

### 1-B. 특정 브랜치를 받을 때
`-b` 뒤에 브랜치 이름을 적습니다.
```bash
cd ~
git clone -b claude/dedup-downloads-migration-gprgcj https://github.com/kidongnam1/and-hub.git
cd and-hub
```

> ⚠️ **비공개(private) 저장소라 Username/Password를 물어봐요.**
> - Username: 깃허브 아이디 (`kidongnam1`)
> - Password: **깃허브 비밀번호가 아니라 토큰(Personal Access Token)** 을 붙여넣어야 함
>   (토큰 만드는 법은 맨 아래 "부록" 참고)

---

## 2. 이미 받아둔 저장소를 최신으로 (pull)

폴더 안으로 들어가서 풀만 하면 됩니다.

```bash
cd ~/and-hub
git pull origin main
# 또는 브랜치 최신화
git pull origin claude/dedup-downloads-migration-gprgcj
```

---

## 3. 브랜치 갈아타기 (이미 clone 한 경우)

```bash
cd ~/and-hub

# 어떤 브랜치들이 있는지 보기
git fetch origin
git branch -a

# 원하는 브랜치로 이동
git checkout claude/dedup-downloads-migration-gprgcj

# 파일 보이는지 확인
ls
```

---

## 4. 파일 실행하기

받은 폴더 안에서 바로 실행합니다. (예: 중복 정리 스크립트)

```bash
cd ~/and-hub

# 파이썬 파일 실행
python3 dedup_downloads.py /storage/emulated/0/Download --recursive

# 셸 스크립트 실행
bash dedup.sh all-preview
```

> 💡 **경로에 띄어쓰기·한글**이 있으면 따옴표로 감싸기
> ```bash
> cd "/storage/emulated/0/SQM 4.13 입고"
> ```

---

## 5. 한 번에 하기 (최신 받기 + 실행)

`&&` 로 이으면 "앞 명령 성공하면 다음도 실행"이 됩니다.

```bash
cd ~/and-hub && git pull origin claude/dedup-downloads-migration-gprgcj && bash dedup.sh all-preview
```

자주 쓰면 **단축어(alias)** 등록:
```bash
echo 'alias ddpull="cd ~/and-hub && git pull origin claude/dedup-downloads-migration-gprgcj"' >> ~/.bashrc
source ~/.bashrc

# 이제부턴 이것만
ddpull
```

---

## 6. 매번 똑같은 흐름 (요약)

```
처음 1회:  pkg install git  →  termux-setup-storage  →  git clone
그 다음:    cd ~/and-hub  →  git pull  →  python3/bash 로 실행
```

---

## 자주 나는 문제 (트러블슈팅)

| 증상 | 원인 / 해결 |
|------|-------------|
| `No such file or directory: ...py` | main 브랜치만 받아서 파일이 그 브랜치엔 없음 → `git checkout <브랜치>` 또는 브랜치로 clone |
| `Username/Password` 계속 물어봄 | Password 칸에 **토큰** 입력 (비밀번호 아님) |
| `fatal: not a git repository` | 저장소 폴더 밖에서 실행함 → `cd ~/and-hub` 후 다시 |
| `Already up to date.` | 이미 최신이라는 뜻 (정상) |
| `Permission denied` / `/storage` 안 보임 | `termux-setup-storage` 다시 실행, 경로는 `/storage/emulated/0` 사용 |
| `gfortran/scipy` 빌드 에러 | pip로 무거운 라이브러리 빌드 실패 → `pkg install python-numpy python-scipy` 처럼 pkg로 설치 |
| 한글/공백 경로 오류 | 경로를 `"따옴표"` 로 감싸기 |

---

## 부록: 깃허브 토큰(Personal Access Token) 만들기

비공개 저장소를 받으려면 비밀번호 대신 토큰이 필요합니다.

1. 깃허브 웹 → 우측 위 프로필 → **Settings**
2. 맨 아래 **Developer settings**
3. **Personal access tokens → Tokens (classic)** → **Generate new token**
4. 권한에서 **repo** 체크 → 생성
5. 나온 토큰 문자열 복사 (한 번만 보임! 잘 저장)
6. Termux에서 Password 물을 때 이 토큰을 붙여넣기

> 💡 매번 입력하기 귀찮으면 한 번만 저장되게:
> ```bash
> git config --global credential.helper store
> ```
> (다음 로그인부터 토큰을 기억합니다. 단, 폰에 평문 저장되니 본인 폰에서만 사용)
