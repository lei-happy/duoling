# 平台主库（zt_platform）数据库设计

## 概述

平台主库存储系统级数据，包括租户信息、平台用户、角色权限、产品版本、数据字典等。

**数据库命名**：
- 开发环境：`zt_platform_ci`
- 生产环境：`zt_platform`

## 表清单

| 序号 | 表名 | 说明 | ORM 模型 |
|------|------|------|----------|
| 1 | sys_tenant | 租户/企业信息表 | `Tenant` |
| 2 | sys_user | 平台用户表 | `User` |
| 3 | sys_user_tenant | 用户企业关联表 | `UserTenant` |
| 4 | sys_role | 角色表 | `Role` |
| 5 | sys_menu | 菜单表 | `Menu` |
| 6 | sys_role_menu | 角色菜单关联表 | `RoleMenu` |
| 7 | sys_user_role | 用户角色关联表 | `UserRole` |
| 8 | sys_product_version | 产品版本表 | `ProductVersion` |
| 9 | sys_tenant_product | 租户产品版本授权表 | `TenantProduct` |
| 10 | sys_dict | 数据字典表 | `Dict` |
| 11 | sys_dict_item | 数据字典项表 | `DictItem` |
| 12 | sys_changelog | 产品更新日志表 | `Changelog` |
| 13 | sys_feedback | 意见反馈表 | `Feedback` |
| 14 | sys_operation_log | 操作日志表 | `OperationLog` |

共 **14** 张表，全部有对应的 SQLAlchemy ORM 模型（定义于 `backend/app/modules/console/models/`）。

## 建表 SQL

完整建表 SQL 文件见：[sql/zt_platform.sql](sql/zt_platform.sql)

## 表关系说明

- `sys_user` 通过 `sys_user_role` 关联 `sys_role`（多对多）
- `sys_user` 通过 `sys_user_tenant` 关联 `sys_tenant`（多对多，同一用户可属于多个企业）
- `sys_role` 通过 `sys_role_menu` 关联 `sys_menu`（多对多）
- `sys_tenant` 通过 `sys_tenant_product` 关联 `sys_product_version`（多对多）
- `sys_dict_item` 通过 `dict_id` 关联 `sys_dict`（一对多）
- `sys_feedback` 通过 `tenant_code` 关联 `sys_tenant`
- `sys_operation_log` 记录所有操作行为

## 关键表字段说明

### sys_user_tenant（用户企业关联表）

支撑"一个用户属于多个企业"的核心关联表。用户登录 Client 端时，若手机号关联多个企业，系统返回企业选择列表供用户切换。

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT | 主键 |
| user_id | BIGINT | 用户 ID |
| tenant_code | VARCHAR(32) | 企业编码 |
| user_type | SMALLINT | 角色类型：1-租户管理员 2-租户用户 3-驾驶员 |
| status | SMALLINT | 状态：0-停用 1-正常 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |
| is_deleted | SMALLINT | 软删除标记 |

唯一约束：`(user_id, tenant_code)`
