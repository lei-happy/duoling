# 智途 - 驾驶员 H5 端

面向驾驶员（user_type=3）的轻量级移动 H5 应用。技术栈：Vue 3.5 + TypeScript + Vant 4 + Vite 7 + Pinia 3。

## 端口与代理

- 开发端口：`5176`（避开 console=5173 / client=5174 / website=5175）
- API 基路径：`/api/driver`
- 后端代理：`VITE_API_PROXY_URL=http://localhost:8000`（dev 环境）

## 核心特性

- **多租户切换**：同一手机号关联多个企业，登录时选择企业、登录后可随时切换
- **强制 `user_type=3` 校验**：仅 sys_user_tenant 中标记为驾驶员的关联企业可见
- **数据隔离**：JWT 必带 `tenant_code`，后端 TenantMiddleware 自动切到对应租户业务库
- **状态驱动业务**：装车、出发、到达通过 task.status 推进；item 级签收通过聚合驱动 task 4→5
- **接口通用**：所有 `/api/driver/*` 接口可被未来的 APP / 小程序直接复用

## 目录结构

```
src/
├── main.ts                 # 入口
├── App.vue                 # 根组件
├── api/                    # 接口封装（request / auth / task / finance / profile）
├── router/                 # 路由 + 守卫
├── store/                  # Pinia（user / tenant / task）
├── views/                  # 页面（login / home / task / finance / profile）
├── components/             # 通用组件
├── composables/            # 组合式逻辑
├── utils/                  # 工具
└── styles/                 # 全局样式与 Vant 主题
```

## 启动

两种方式任选其一（推荐方式 A）：

### 方式 A：从 monorepo 根目录（与 console / client / website 统一管理）

```bash
# 在 frontend/ 目录
pnpm install            # 一次性安装所有子包依赖
pnpm dev:driver         # 启动开发服务器（端口 5176）
pnpm build:driver       # 生产构建
```

### 方式 B：从当前子项目目录

```bash
# 在 frontend/driver-h5/ 目录
pnpm install            # 仅安装本子包（pnpm 仍会复用 workspace 共享依赖）
pnpm dev                # 启动开发服务器（端口 5176）
pnpm build              # 生产构建
```

> 因为 `frontend/` 是 pnpm workspace，**不要混用 `npm install`**（容易生成多份 lockfile）。
> 访问地址：http://localhost:5176


## 与后端的契合点

| 路径 | 说明 |
|------|------|
| `POST /api/driver/auth/login` | 手机号+密码（强制 user_type=3） |
| `POST /api/driver/auth/sms-login` | 验证码登录（强制 user_type=3） |
| `POST /api/driver/auth/switch-tenant` | 切换企业，重新签发 JWT |
| `GET /api/driver/task/my` | 我的任务列表 |
| `POST /api/driver/task/{id}/confirm-load` | 确认装车 |
| `POST /api/driver/task/{id}/depart` | 确认出发 |
| `POST /api/driver/task/{id}/confirm-arrive` | 确认到达 |
| `POST /api/driver/task/items/{itemId}/sign` | item 级签收（聚合驱动 task 4→5） |
| `GET /api/driver/finance/my` | 我的费用单 |

详见 [项目文档/01.架构设计/驾驶员H5架构设计.md](../../项目文档/01.架构设计/驾驶员H5架构设计.md)。
