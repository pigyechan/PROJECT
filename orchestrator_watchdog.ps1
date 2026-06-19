$proc = Get-WmiObject Win32_Process | Where-Object {
    $_.CommandLine -match "orchestrator\.py" -and
    $_.CommandLine -notmatch "WindowsPowerShell"
}

if (-not $proc) {
    Start-ScheduledTask -TaskName "BlogPipelineOrchestrator"
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Add-Content -Path "C:\PROJECT\orchestrator.log" -Value "`n[watchdog] $timestamp - restarted" -Encoding UTF8
}
