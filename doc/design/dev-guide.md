# 智途(ZhiTu) 开发规范

> **最后更新**：2026-02-15

## 1. 后端开发规范

### 1.1 代码风格

- 遵循 PEP 8 规范
- 使用 Type Hints 进行类型标注
- 所有模块、类、函数必须有 docstring
- 缩进使用 4 个空格
- 全面使用 async/await 异步编程

### 1.2 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 文件名 | 下划线命名 | `user_service.py` |
| 类名 | 大驼峰 | `UserService` |
| 函数/变量 | 下划线命名 | `get_user_list` |
| 常量 | 全大写下划线 | `MAX_PAGE_SIZE` |
| API 路径 | 短横线命名 | `/product-version` |
| 数据库表名 | 下划线命名 + 前缀 | `sys_user`、`biz_vehicle` |

### 1.3 模块开发流程

新增业务功能时，按以下顺序开发：

1. **models/** - 定义数据模型（SQLAlchemy ORM），继承 `PlatformModelBase` 或 `TenantModelBase`
2. **schemas/** - 定义请求/响应数据结构（Pydantic V2 BaseModel）
3. **services/** - 实现业务逻辑（静态方法类，接收 `AsyncSession` 参数）
4. **api/** - 编写 API 路由接口（使用 `Depends` 注入 db session 和 current_user）
5. 在模块的 `api/__init__.py` 中注册路由
6. 在 `models/__init__.py` 中注册导出模型

### 1.4 数据库规范

- 表名前缀：平台库 `sys_`，租户库 `biz_`
- 主键使用 BigInteger 自增
- 所有表包含 `created_at`、`updated_at`、`is_deleted` 字段（通过基类统一定义）
- 软删除：通过 `is_deleted` 字段标记，不做物理删除
- 字段必须有 `comment` 注释
- 使用 `mapped_column` 定义字段（SQLAlchemy 2.0 声明式风格）

### 1.5 API 响应格式

统一使用以下 JSON 格式（由 `app.common.response` 模块提供）：

**普通响应**：

```json
{
  "code": 0,
  "message": "success",
  "data": {}
}
```

**分页响应**：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "list": [],
    "total": 100,
    "page": 1,
    "page_size": 20
  }
}
```

**错误响应**：

```json
{
  "code": -1,
  "message": "错误信息描述"
}
```

- `code = 0` 表示成功，其他值表示失败
- 使用 `success(data=...)` 和 `fail(message=...)` 快捷函数
- 分页参数通过 `PageParams` 依赖注入（`page` 默认 1，`page_size` 默认 20，最大 200）

### 1.6 Service 层规范

- Service 类使用静态方法（`@staticmethod`），不持有状态
- 数据库 Session 作为第一个参数传入
- 业务异常通过自定义异常类抛出，由全局异常处理器捕获
- Console 和 Client 共有的功能（如用户/角色管理），Service 各自实现但保持接口一致

### 1.7 依赖注入

| 依赖 | 函数 | 说明 |
|------|------|------|
| 平台库 Session | `get_platform_db` | 操作 zt_platform 库 |
| 租户库 Session | `get_tenant_db` | 操作 zt_biz_{code} 库，需要 tenant_code |
| 当前用户 | `get_current_user` | 解析 JWT Token，返回 `TokenData` |

## 2. 前端开发规范

### 2.1 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 组件文件 | 页面入口用 `index.vue`，子组件大驼峰 | `index.vue`、`UserEdit.vue` |
| 目录名 | 短横线 | `operation-record` |
| 变量/函数 | 小驼峰 | `getUserInfo` |
| 常量 | 全大写下划线 | `API_BASE_URL` |
| CSS 类名 | 短横线 | `user-card` |
| TypeScript Interface | 大驼峰 | `UserInfo` |
| Pinia Store | `use` 前缀 + `Store` 后缀 | `useUserStore` |

### 2.2 目录规范

- `views/` 中的每个页面使用 `index.vue` 作为入口，子组件放在同级 `components/` 目录
- `api/` 中按模块组织接口文件，每个模块一个目录
- 公共组件放在 `components/` 目录
- 工具函数放在 `utils/` 目录
- Pinia Store 放在 `store/modules/` 目录

### 2.3 API 调用规范

- 所有 API 调用统一放在 `src/api/` 目录
- 使用 TypeScript Interface 定义请求和响应类型
- 使用 `@/utils/request` 统一的 axios 实例
- API 响应类型使用 `ApiResult<T>` 和 `PageResult<T>` 泛型

```typescript
// API 响应基础类型
interface ApiResult<T> {
  code: number;
  message?: string;
  data?: T;
}

// 分页数据类型
interface PageResult<T> {
  list: T[];
  total: number;
  page: number;
  page_size: number;
}
```

### 2.4 组件开发规范

- 统一使用 Composition API + `<script setup lang="ts">`
- 组件 Props 使用 `defineProps<T>()` 类型声明
- 组件事件使用 `defineEmits<T>()` 类型声明
- 组件样式使用 `<style scoped lang="scss">`

### 2.5 权限指令使用

```vue
<!-- 要求拥有指定角色 -->
<el-button v-role="'admin'">管理员操作</el-button>

<!-- 要求拥有任一角色 -->
<el-button v-any-role="['admin', 'operator']">操作按钮</el-button>

<!-- 要求拥有指定权限标识 -->
<el-button v-permission="'sys:user:add'">新增用户</el-button>

<!-- 要求拥有任一权限 -->
<el-button v-any-permission="['sys:user:add', 'sys:user:edit']">编辑</el-button>
```

编程式权限检查：

```typescript
import { usePermission } from '@/utils/use-permission';

const { hasPermission, hasRole } = usePermission();

if (hasPermission('sys:user:add')) {
  // 有权限
}
```

### 2.6 状态管理规范

- 使用 Pinia 管理全局状态，按功能拆分 Store 模块
- Store 文件放在 `store/modules/` 下
- 需要持久化的状态使用 localStorage
- 主题配置支持服务端同步（通过 API 保存/恢复）

## 3. Git 规范

### 3.1 分支规范

| 分支 | 说明 |
|------|------|
| master | 主分支，稳定版本 |
| develop | 开发分支 |
| feature/* | 功能分支 |
| bugfix/* | Bug修复分支 |
| release/* | 发布分支 |

### 3.2 提交信息规范

```
<type>(<scope>): <subject>

feat(tenant): 新增租户管理功能
fix(auth): 修复登录Token过期问题
docs(readme): 更新部署文档
refactor(database): 重构数据库连接池管理
```

类型：feat / fix / docs / refactor / test / chore / style

### 3.3 提交范围（scope）

| scope | 说明 |
|-------|------|
| auth | 认证相关 |
| tenant | 租户管理 |
| user | 用户管理 |
| role | 角色管理 |
| menu | 菜单管理 |
| dict | 数据字典 |
| vehicle | 车辆管理 |
| driver | 驾驶员管理 |
| order | 运单管理 |
| website | 产品官网 |
| console | 管理后台 |
| client | 客户端 |
| deploy | 部署配置 |
| database | 数据库 |

## 4. 部署规范

### 4.1 环境区分

| 环境 | DB_SUFFIX | 数据库示例 | 说明 |
|------|-----------|-----------|------|
| 本地开发 | `_ci` | `zt_platform_ci` | 开发人员本地调试 |
| 生产环境 | （空） | `zt_platform` | Docker Compose 部署 |

### 4.2 Docker 部署

- 后端镜像：`deploy/docker/Dockerfile.backend`
- 前端镜像：`deploy/docker/Dockerfile.frontend`
- 编排文件：`deploy/docker/docker-compose.yml`

### 4.3 Nginx 配置

每个前端项目有独立的 Nginx 配置：

| 配置文件 | 说明 |
|----------|------|
| `deploy/nginx/console.conf` | Console 管理后台 |
| `deploy/nginx/client.conf` | Client 客户端 |
| `deploy/nginx/website.conf` | Website 产品官网 |

Nginx 同时负责 API 反向代理（`/api/*` → FastAPI 后端）。
