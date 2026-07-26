@echo off
chcp 65001 >nul
echo 将以管理员权限向微信开发者工具安装缺失的 tslib...
echo.
powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process powershell -Verb RunAs -ArgumentList '-NoProfile -ExecutionPolicy Bypass -File \"%~dp0fix-devtools-tslib.ps1\"' -Wait"
echo.
echo 若 UAC 弹窗已同意且未报错，请完全退出并重启微信开发者工具后再真机调试。
pause
