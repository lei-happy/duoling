# 平台主库（zt_platform）数据库设计

## 概述

平台主库存储系统级数据，包括租户信息、平台用户、角色权限、产品版本、数据字典等。

**数据库命名**：
- 开发环境：`zt_platform_ci`
- 生产环境：`zt_platform`

## 表清单

| 序号 | 表名 | 说明 |
|------|------|------|
| 1 | sys_tenant | 租户/企业信息表 |
| 2 | sys_user | 平台用户表 |
| 3 | sys_role | 角色表 |
| 4 | sys_menu | 菜单表 |
| 5 | sys_role_menu | 角色菜单关联表 |
| 6 | sys_user_role | 用户角色关联表 |
| 7 | sys_product_version | 产品版本表 |
| 8 | sys_tenant_product | 租户产品版本授权表 |
| 9 | sys_dict | 数据字典表 |
| 10 | sys_dict_item | 数据字典项表 |
| 11 | sys_feedback | 意见反馈表 |
| 12 | sys_operation_log | 操作日志表 |

## 建表 SQL

完整建表 SQL 文件见：[sql/zt_platform.sql](sql/zt_platform.sql)

## 表关系说明

- `sys_user` 通过 `sys_user_role` 关联 `sys_role`（多对多）
- `sys_role` 通过 `sys_role_menu` 关联 `sys_menu`（多对多）
- `sys_tenant` 通过 `sys_tenant_product` 关联 `sys_product_version`（多对多）
- `sys_dict_item` 通过 `dict_id` 关联 `sys_dict`（一对多）
- `sys_feedback` 通过 `tenant_code` 关联 `sys_tenant`
- `sys_operation_log` 记录所有操作行为
