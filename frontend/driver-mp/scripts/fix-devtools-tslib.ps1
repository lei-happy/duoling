# 修复微信开发者工具真机调试缺 tslib（需管理员权限）
# 用法：右键「使用 PowerShell 运行」或在管理员终端执行本脚本

$ErrorActionPreference = 'Stop'

$src = Join-Path $PSScriptRoot '..\node_modules\tslib'
$src = (Resolve-Path $src).Path

$candidates = @(
  'C:\Program Files (x86)\Tencent\微信web开发者工具\code\package.nw\node_modules',
  'C:\Program Files\Tencent\微信web开发者工具\code\package.nw\node_modules'
)

$destParent = $candidates | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $destParent) {
  Write-Host '未找到微信开发者工具的 node_modules 目录，请确认已安装开发者工具。' -ForegroundColor Red
  exit 1
}

if (-not (Test-Path $src)) {
  Write-Host '项目内没有 tslib，请先在 frontend/driver-mp 执行: npm install' -ForegroundColor Red
  exit 1
}

$dest = Join-Path $destParent 'tslib'
Write-Host "源: $src"
Write-Host "目标: $dest"

if (Test-Path $dest) {
  Remove-Item $dest -Recurse -Force
}
Copy-Item -Path $src -Destination $dest -Recurse -Force

Write-Host ''
Write-Host '已修复。请完全退出微信开发者工具后重新打开，再试真机调试。' -ForegroundColor Green
Get-ChildItem $dest | Select-Object -ExpandProperty Name
