@echo off

set WORKSPACE=%USERPROFILE%\Desktop\watermark-me\watermark-me
set APP_NAME_SNAKE=watermark
set APP_NAME_DIST=watermark
set REPOSITORY_NAME=watermark

rem set FREEZE_ONLY=1

powershell -ExecutionPolicy Bypass .\packaging\windows\deploy.ps1 -install
powershell -ExecutionPolicy Bypass .\packaging\windows\deploy.ps1 -start
powershell -ExecutionPolicy Bypass .\packaging\windows\deploy.ps1 -tests
powershell -ExecutionPolicy Bypass .\packaging\windows\deploy.ps1 -check_upgrade
powershell -ExecutionPolicy Bypass .\packaging\windows\deploy.ps1 -build

pause
