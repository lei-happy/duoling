"""
平台元数据同步工具 — 命令入口

使用方式：
    python -m scripts.platform_sync export   # 在 dev 跑：拉取 dev 平台库 → 写仓库快照
    python -m scripts.platform_sync sync     # 在 prod 跑：把仓库快照应用到 prod 平台库

详见同目录 README.md。
"""

from __future__ import annotations

import sys


HELP_TEXT = """\
平台元数据同步工具

子命令：
  export   把 dev console 平台库的菜单/版本/功能/版本-功能映射拉取到仓库快照
           （在开发者本机或 dev 跳板机执行）

  sync     把仓库快照应用到目标环境（默认 prod）的平台库
           （在生产服务器的 backend 容器内执行）

示例：
  python -m scripts.platform_sync export
  python -m scripts.platform_sync sync
  python -m scripts.platform_sync sync --yes        # CI/无人值守

详见 backend/scripts/platform_sync/README.md
"""


def main() -> int:
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help", "help"):
        print(HELP_TEXT)
        return 0

    cmd = sys.argv[1]
    # 把子命令名从 argv 中剥掉，让子模块的 argparse 看到的是干净的参数
    sys.argv = [sys.argv[0]] + sys.argv[2:]

    if cmd == "export":
        from scripts.platform_sync.export import main as export_main
        return export_main()
    if cmd == "sync":
        from scripts.platform_sync.sync import main as sync_main
        return sync_main()

    print(f"[ERROR] 未知子命令: {cmd}\n", file=sys.stderr)
    print(HELP_TEXT, file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
