@echo off
chcp 65001 > nul
title and-hub 중복 파일 정리기 (Web GUI)

echo ===================================================
echo     and-hub 웹 탐색기 대시보드 서버를 실행합니다...
echo     브라우저 화면이 자동으로 열립니다.
echo ===================================================
echo.
python "%~dp0web_app.py"
pause
