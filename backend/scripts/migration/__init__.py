"""租户业务库 schema 迁移工具

两阶段升级所有 active 租户的业务库：

  Phase 1: ensure tables —— 根据每个租户当前开通的版本对应的
            `sys_product_feature.required_tables` 自动补建缺失的业务表
            （幂等：缺什么建什么，全部用 `metadata.create_all`）。

  Phase 2: versioned migrations —— 扫描 `versions/` 下的迁移文件，
            对每个未在该租户 `biz_migration_log` 中登记的迁移按 id
            排序执行。仅用于「需要 ALTER 列 / 自定义 SQL 的不可逆变更」，
            纯建表场景无需写迁移文件。

入口：`python -m scripts.migration.runner [--dry-run] [--tenant <code>]`
"""
