# 智途(ZhiTu) 开发规范

## 1. 后端开发规范

### 1.1 代码风格

- 遵循 PEP 8 规范
- 使用 Type Hints 进行类型标注
- 所有模块、类、函数必须有 docstring
- 缩进使用 4 个空格

### 1.2 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 文件名 | 下划线命名 | `user_service.py` |
| 类名 | 大驼峰 | `UserService` |
| 函数/变量 | 下划线命名 | `get_user_list` |
| 常量 | 全大写下划线 | `MAX_PAGE_SIZE` |
| API 路径 | 短横线命名 | `/product-version` |

### 1.3 模块开发流程

新增业务功能时，按以下顺序开发：

1. **models/** - 定义数据模型（SQLAlchemy ORM）
2. **schemas/** - 定义请求/响应数据结构（Pydantic）
3. **services/** - 实现业务逻辑
4. **api/** - 编写 API 路由接口
5. 在模块的 `api/__init__.py` 中注册路由

### 1.4 数据库规范

- 表名前缀：平台库 `sys_` / `res_`，租户库 `biz_`
- 主键使用 BigInteger 自增
- 所有表包含 `created_at`、`updated_at`、`is_deleted` 字段
- 软删除：通过 `is_deleted` 字段标记，不做物理删除
- 字段必须有 comment 注释

### 1.5 API 响应格式

统一使用以下 JSON 格式：

```json
{
  "code": 0,
  "message": "success",
  "data": {}
}
```

- `code = 0` 表示成功，其他值表示失败
- 分页数据通过 `data.list` / `data.total` / `data.page` / `data.page_size` 返回

## 2. 前端开发规范

### 2.1 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 组件文件 | 大驼峰 | `UserList.vue` |
| 目录名 | 短横线 | `user-management` |
| 变量/函数 | 小驼峰 | `getUserInfo` |
| 常量 | 全大写下划线 | `API_BASE_URL` |
| CSS 类名 | 短横线 | `user-card` |

### 2.2 目录规范

- `views/` 中的每个页面使用 `index.vue` 作为入口
- `api/` 中按模块组织接口文件
- 公共组件放在 `components/` 目录
- 工具函数放在 `utils/` 目录

### 2.3 API 调用规范

- 所有 API 调用统一放在 `src/api/` 目录
- 使用 TypeScript Interface 定义请求和响应类型
- 使用 `@/utils/request` 统一的 axios 实例

## 3. Git 规范

### 3.1 分支规范

| 分支 | 说明 |
|------|------|
| main | 主分支，稳定版本 |
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
