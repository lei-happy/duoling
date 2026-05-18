#!/usr/bin/env bash
# ============================================================
# CI 入口：ORM ↔ snapshot drift 检查（硬阻塞）
#
# 用途：在合并前确保任何 ORM 模型变更都伴随了 versioned migration 文件 +
#       snapshot 刷新；否则线上部署就会出现 1054 Unknown column 类事故。
#
# 调用方：
#   - GitHub Actions    : .github/workflows/migration-check.yml
#   - Gitee CI / 自建 CI: 直接 `bash backend/scripts/ci/migration_check.sh`
#   - 本地手动验证      : 同上
#
# 依赖：
#   * Python 3.11+
#   * 仅安装 backend/requirements.txt 中 SQLAlchemy / pydantic-settings /
#     alembic 等少量包即可（不需要 DB 驱动；不连任何 DB）
#
# 退出码：
#   0 = 无 drift；1 = 有 drift；2 = 工具/导入异常
# ============================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$BACKEND_DIR"

if [ -f requirements.txt ]; then
  echo "[CI] 安装最小依赖（SQLAlchemy / alembic / pydantic-settings）..."
  pip install --quiet --no-cache-dir \
      'sqlalchemy>=2.0.36' \
      'alembic>=1.14.0' \
      'pydantic>=2.10.0' \
      'pydantic-settings>=2.6.0' \
      'loguru>=0.7.3'
fi

echo "[CI] 运行 drift 检查..."
python -m scripts.migration.check
rc=$?
if [ "$rc" -eq 0 ]; then
  echo "[CI][OK] ORM 与 snapshot 一致"
  exit 0
fi
echo ""
echo "[CI][FAIL] 检测到 schema drift，合并被阻塞。"
echo "请按以下步骤修复后 push："
echo "  1) cd backend"
echo "  2) python -m scripts.migration.autogen tenant   --name '<desc>'  # 改了 TenantBase 模型"
echo "     python -m scripts.migration.autogen platform --name '<desc>'  # 改了 PlatformBase 模型"
echo "  3) 人工 review 生成的迁移文件 + snapshots 改动"
echo "  4) git add 迁移文件 + snapshots/*.json"
echo "  5) 再 push"
exit "$rc"
