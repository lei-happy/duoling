"""租户业务库 versioned migrations.

每个迁移文件需提供以下顶层符号：

  MIGRATION_ID   : str   形如 "20260516_001"，全局唯一、按字典序即按执行序
  MIGRATION_NAME : str   人类可读描述
  REQUIRES_TABLES: list[str]  必须存在的前置表；若租户库缺其中任一表则跳过本迁移
                               （对未启用相关 feature 的租户自动免疫）

  def upgrade(conn, tenant_code: str) -> None:
      使用 sqlalchemy.Connection 执行 DDL / DML；不要自己 commit，
      由 runner 统一在事务内执行并写 biz_migration_log。

设计原则：
  * 只增不减：发布到生产的迁移文件永远不要回退/修改 MIGRATION_ID
  * 幂等：建议 upgrade 内部用 information_schema 自检后再 ALTER，
            以便人工误重跑也能安全 no-op
  * 不删除迁移文件：哪怕功能下线，文件留下，避免新租户跳过历史步
"""
