@echo off
chcp 65001 > nul
title and-hub 중복 파일/폴더 정리 도우미 (Windows)

:MENU
cls
echo ===================================================
echo     and-hub 중복 파일/폴더 정리 도우미 (Windows)
echo ===================================================
echo  [1] 다운로드 폴더 전체 미리보기 (파일+이름사본+폴더) [지우지 않음]
echo  [2] 다운로드 폴더 전체 안전 정리 (_duplicates_trash 이동)
echo  [3] 휴지통(_duplicates_trash) 파일 원위치 복구 (Restore)
echo  [4] 휴지통(_duplicates_trash) 완전 비우기
echo  [5] 종료
echo ===================================================
set /p CHOICE="메뉴 번호를 선택하세요 (1-5): "

if "%CHOICE%"=="1" goto PREVIEW
if "%CHOICE%"=="2" goto CLEAN
if "%CHOICE%"=="3" goto RESTORE
if "%CHOICE%"=="4" goto EMPTY_TRASH
if "%CHOICE%"=="5" goto END
goto MENU

:PREVIEW
echo.
echo ==> 다운로드 폴더 전체 중복 미리보기를 시작합니다...
python "%~dp0dedup_downloads.py" "%USERPROFILE%\Downloads" --by-name --recursive
python "%~dp0dedup_downloads.py" "%USERPROFILE%\Downloads" --recursive
python "%~dp0dedup_downloads.py" "%USERPROFILE%\Downloads" --folders
echo.
pause
goto MENU

:CLEAN
echo.
echo ==> 다운로드 폴더 중복 파일을 휴지통으로 정리합니다...
python "%~dp0dedup_downloads.py" "%USERPROFILE%\Downloads" --recursive --delete --trash
python "%~dp0dedup_downloads.py" "%USERPROFILE%\Downloads" --by-name --recursive --delete --trash
python "%~dp0dedup_downloads.py" "%USERPROFILE%\Downloads" --folders --delete --trash
echo.
echo 정리 완료! 파일들은 _duplicates_trash 폴더로 보관되었습니다.
echo.
pause
goto MENU

:RESTORE
echo.
echo ==> 휴지통 파일들을 원래 위치로 복구합니다...
python "%~dp0dedup_downloads.py" "%USERPROFILE%\Downloads" --restore
echo.
pause
goto MENU

:EMPTY_TRASH
echo.
if exist "%USERPROFILE%\Downloads\_duplicates_trash" (
    rmdir /s /q "%USERPROFILE%\Downloads\_duplicates_trash"
    echo [완료] _duplicates_trash 휴지통을 완전히 비웠습니다.
) else (
    echo [안내] 비울 휴지통이 없습니다: %USERPROFILE%\Downloads\_duplicates_trash
)
echo.
pause
goto MENU

:END
exit
