"""
platform_sync — 平台元数据快照同步工具

通过 Console REST API 将开发环境平台库（zt_platform）中的菜单 / 产品版本 /
功能清单 / 版本-功能映射拉取到仓库内的 JSON 快照（snapshots/），作为生产
部署的唯一事实源；并在部署后用 verify 命令校验目标环境是否与仓库快照一致。

子命令：
    python -m scripts.platform_sync.pull   --env dev
    python -m scripts.platform_sync.verify --env prod

详见同目录下的 README.md。
"""
