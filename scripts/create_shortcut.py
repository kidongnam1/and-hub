import os
import subprocess

ps_script = """
$DesktopPath = [Environment]::GetFolderPath('Desktop')

# 1. 콘솔 런처 바로가기
$SC1 = (New-Object -ComObject WScript.Shell).CreateShortcut((Join-Path $DesktopPath '중복파일정리 (and-hub).lnk'))
$SC1.TargetPath = 'D:\\program\\and-hub\\start_dedup.bat'
$SC1.WorkingDirectory = 'D:\\program\\and-hub'
$SC1.Description = 'and-hub 중복 파일 정리 도우미 (콘솔 런처)'
$SC1.Save()

# 2. 웹앱 대시보드 바로가기
$SC2 = (New-Object -ComObject WScript.Shell).CreateShortcut((Join-Path $DesktopPath '중복정리_웹앱 (and-hub).lnk'))
$SC2.TargetPath = 'D:\\program\\and-hub\\start_web_app.bat'
$SC2.WorkingDirectory = 'D:\\program\\and-hub'
$SC2.Description = 'and-hub 중복 파일 정리기 (웹 탐색기 UI)'
$SC2.Save()
"""

try:
    subprocess.run(["powershell", "-NoProfile", "-Command", ps_script], check=True)
    print("Desktop shortcuts created successfully!")
except Exception as e:
    print(f"Error creating shortcut: {e}")
