# 客户生命周期管理

## 一、生命周期阶段定义

客户在平台经历以下阶段：

```
注册 ──自动开通basic──> 免费体验 ──开通pro/enterprise──> 付费客户
                         │                                │
                         │停用                            │到期未续费
                         ▼                                ▼
                       流失客户 <───────────────────── 流失客户
                         │                                │
                         │重新激活(恢复basic)              │开通付费版本
                         ▼                                ▼
                       免费体验                          付费客户
```

### 1.1 新注册客户

- 筛选条件：`status=1` 且 `created_at >= NOW() - 30天`
- 说明：最近 30 天内注册的客户，是一个**时间窗口视图**，可与"免费体验"或"付费客户"重叠
- 运营用途：快速关注新增客户，进行首轮触达

### 1.2 免费体验客户

- 筛选条件：`status=1` 且仅有 `basic` 版本的**有效**授权
- 有效授权判定：`is_deleted=0 AND status=1 AND (end_time IS NULL OR end_time > NOW())`
- 流入方式：注册时自动开通 basic 版本
- 运营用途：引导转化为付费客户

### 1.3 付费客户

- 筛选条件：`status=1` 且拥有非 `basic` 的**有效**授权
- 子分类：
  - 专业版：有效授权中包含 `version_code='pro'`
  - 旗舰版：有效授权中包含 `version_code='enterprise'`
  - 到期预警：`expire_time` 距今 <= 30 天
- 流入方式：运营后台为客户开通 pro/enterprise 版本
- 运营用途：续费管理、增值服务

### 1.4 流失客户

- 筛选条件：`status IN (0, 3)`（停用或已过期）
- 流入方式：
  - 手动停用（status=0）
  - 所有有效授权到期（status=3）
  - 过期检查任务自动标记
- 运营用途：客户召回

### 1.5 跟进池

- 筛选条件：`in_follow_pool=1`
- 说明：运营人员手动标记，跨阶段的客户关注列表

### 1.6 全量客户

- 筛选条件：无额外过滤
- 说明：所有客户的完整视图

## 二、流转规则

### 2.1 注册 → 免费体验

- 触发：调用 `POST /tenant` 创建客户
- 自动行为：
  1. 创建 `sys_tenant` 记录，`status=1`
  2. 查询 `sys_product_version` 获取 `basic` 版本
  3. 自动创建 `sys_tenant_product` 记录（basic 版本，无到期时间）
  4. 创建管理员账号和用户-企业关联

### 2.2 免费体验 → 付费客户

- 触发：运营后台为客户开通 pro/enterprise 版本（`POST /tenant/{id}/products`）
- 自动行为：
  1. 创建 `sys_tenant_product` 记录（付费版本，含到期时间）
  2. 更新 `sys_tenant.expire_time` 为所有授权中最晚的到期时间
  3. 如客户 `status=3`（已过期），自动恢复为 `status=1`
- basic 授权保留不删除，作为兜底版本

### 2.3 付费客户 → 续费

- 触发：修改现有授权的到期时间，或重新开通同版本授权
- 自动行为：更新 `sys_tenant.expire_time`

### 2.4 付费客户 → 流失客户

- 触发条件：所有付费版本授权到期
- 检测方式：
  1. 用户登录时检查（`auth_service.py`）
  2. `POST /tenant/check-expirations` 手动触发过期检查
  3. 后续可接入定时任务（每日执行）
- 自动行为：`sys_tenant.status` 设为 `3`（已过期）

### 2.5 流失客户 → 重新激活

- 触发：运营后台点击"重新激活"或开通新版本
- 重新激活（status 恢复为 1）：
  - 自动检查是否有 basic 授权，没有则自动补齐
- 开通付费版本：
  - 直接开通，`status` 自动恢复为 `1`

### 2.6 取消授权 → 状态回退

- 取消付费版本后若仍有 basic 有效授权 → 回到"免费体验"
- 取消所有有效授权（含 basic）→ `status=3`，进入"流失客户"

## 三、数据模型

### 3.1 核心表关系

```
sys_tenant (客户)
  ├── status: 0-停用 / 1-正常 / 3-已过期
  ├── expire_time: 最晚授权到期时间
  └── 1:N ── sys_tenant_product (授权)
                ├── version_code: basic / pro / enterprise
                ├── start_time: 授权开始时间
                ├── end_time: 授权到期时间 (NULL=永不过期)
                └── N:1 ── sys_product_version (版本定义)
                              ├── version_code
                              ├── version_name
                              └── price
```

### 3.2 授权有效性判定

授权记录被视为"有效"需同时满足：

1. `is_deleted = 0`
2. `status = 1`
3. `end_time IS NULL OR end_time > NOW()`

## 四、API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /tenant | 注册客户（自动开通 basic） |
| GET | /tenant/page | 分页查询（支持 lifecycle 筛选） |
| GET | /tenant/stats | 各阶段客户数量统计 |
| PUT | /tenant/status | 启用/停用（重新激活时自动补 basic） |
| POST | /tenant/{id}/products | 开通产品版本（过期客户自动恢复） |
| DELETE | /tenant/{id}/products/{pid} | 取消授权（自动回退状态） |
| PUT | /tenant/follow-pool | 标记/移出跟进池 |
| POST | /tenant/check-expirations | 手动触发过期检查 |

## 五、过期检查

### 5.1 检查逻辑

1. 查找 `status=1` 且 `expire_time IS NOT NULL` 且 `expire_time < NOW()` 的客户
2. 逐一检查是否还有其他有效授权（end_time 未过期或无到期时间）
3. 无有效付费授权但仍有 basic → 保持 `status=1`（回到免费体验）
4. 无任何有效授权 → `status=3`（已过期，进入流失）

### 5.2 触发方式

- 手动：`POST /tenant/check-expirations`
- 登录时：`auth_service` 中检查当前企业
- 定时任务：后续可接入 APScheduler 或 cron，建议每日 02:00 执行
