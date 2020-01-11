@echo off

set WORKSPACE=%USERPROFILE%\Desktop\watermark-me\watermark-me
set APP_NAME_SNAKE=watermark
set APP_NAME_DIST=watermark
set REPOSITORY_NAME=watermark

powershell -ExecutionPolicy Bypass .\packaging\windows\deploy.ps1 -install
rem powershell -ExecutionPolicy Bypass .\packaging\windows\deploy.ps1 -start
rem powershell -ExecutionPolicy Bypass .\packaging\windows\deploy.ps1 -tests
rem powershell -ExecutionPolicy Bypass .\packaging\windows\deploy.ps1 -check_upgrade
powershell -ExecutionPolicy Bypass .\packaging\windows\deploy.ps1 -build

pause
