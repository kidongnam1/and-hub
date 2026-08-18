$TaskName = "and-hub Auto Clean"
$PythonPath = (Get-Command python.exe -ErrorAction SilentlyContinue).Source
if (-not $PythonPath) { $PythonPath = "python.exe" }
$DownloadsPath = Join-Path $env:USERPROFILE "Downloads"
$ScriptPath = "D:\program\and-hub\dedup_downloads.py"
$ArgString = "`"$ScriptPath`" `"$DownloadsPath`" --recursive --delete --trash"

$Action = New-ScheduledTaskAction -Execute $PythonPath -Argument $ArgString -WorkingDirectory "D:\program\and-hub"
$Trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At 9am
Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Description "and-hub 주간 다운로드 폴더 자동 중복 정리" -Force
Write-Host "Successfully registered Windows Task Scheduler task: $TaskName"
