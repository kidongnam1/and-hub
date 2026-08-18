import os
import subprocess

ps_script = """
$DesktopPath = [Environment]::GetFolderPath('Desktop')
$ShortcutPath = Join-Path $DesktopPath '중복파일정리 (and-hub).lnk'
$WScriptShell = New-Object -ComObject WScript.Shell
$Shortcut = $WScriptShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = 'D:\\program\\and-hub\\start_dedup.bat'
$Shortcut.WorkingDirectory = 'D:\\program\\and-hub'
$Shortcut.Save()
"""

try:
    subprocess.run(["powershell", "-NoProfile", "-Command", ps_script], check=True)
    print("Desktop shortcut created successfully!")
except Exception as e:
    print(f"Error creating shortcut: {e}")
