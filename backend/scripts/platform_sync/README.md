# 平台元数据同步工具

让 dev 与 prod 两套环境的「客户端菜单 / 平台菜单 / 产品版本 / 功能清单 / 版本-功能映射」保持一致。

> **本工具不负责"新功能首次入库"**——那是开发者写一次性脚本（放在 [backend/scripts/init/](../init/) 或 [backend/scripts/fix/](../fix/)）干的事。本工具只负责把 dev 库里**已有**的菜单/feature/版本搬到 prod。

---

## 给 AI 看

直接读 [snapshots/](snapshots/) 下的 5 个 JSON 文件即可拿到当前事实源，不需要任何命令、配置或凭证。

| 文件 | 内容 |
|------|------|
| `client_menu.json` | 客户端菜单（含 `feature_code`） |
| `platform_menu.json` | Console 平台菜单 |
| `product_version.json` | 产品版本（`lite/standard/pro/...`） |
| `product_feature.json` | 功能清单（`feature_code` 列表） |
| `version_feature.json` | 版本-功能映射 `{version_code: [feature_code, ...]}` |
| `_meta.json` | 元数据（导出时间 / git_sha） |

开发新模块前先扫一眼这些文件，避免 `feature_code` / `menu_code` 重复。

---

## 给开发者看（dev 改完了想入库）

```bash
# 1. 在 dev console 配菜单 / feature / 版本
# 2. 在 backend/ 下跑一次 export
cd backend
python -m scripts.platform_sync export

# 3. git diff 看变更，确认无误后提交
git add backend/scripts/platform_sync/snapshots/
git commit -m "snapshot: <说明>"
git push
```

`export` 会自动校验：菜单引用的 `feature_code` 必须在功能清单中存在；唯一性；引用完整性。

---

## 给发版人看（prod 上想同步）

```bash
ssh user@prod-server
cd /opt/zhitu
git pull

docker compose exec backend python -m scripts.platform_sync sync
# 工具会输出变更摘要 + 详情，例如：
#   [客户端菜单] 新增 1 / 修改 2 / 删除 0
#   [产品功能]   新增 3 / 修改 0 / 删除 0
#   [版本-功能]  新增 5 / 删除 1
#   [+] 菜单 partner:invoice  发票管理
#   [+] feature partner_invoice  发票管理
#   ...
# 输入 y → 自动调用 seed 脚本写库 → 应用后再拉一次确认 0 差异
```

> **要点**：sync 会调用 `seed_client_menus.py --force-all`，意味着 prod 与 snapshots 完全对齐（包括 visible / icon / sort_order）。如果想保留 prod 的 UI 自定义，应在 dev 也照样改一遍后再发版。

---

## 配置

首次使用前需要创建本地凭证文件：

```bash
cd backend/scripts/platform_sync/envs
cp .env.example .env.dev      # 开发者机器上配
cp .env.example .env.prod     # 生产服务器上配（容器内路径相同）
# 编辑这两个文件，填入对应环境的 console URL + 平台超管账号
```

> 这些凭证文件已在 [.gitignore](.gitignore) 中排除，不会入库。CI 也可以通过环境变量（`CONSOLE_API_BASE` / `CONSOLE_ADMIN_PHONE` / `CONSOLE_ADMIN_PASSWORD`）注入，优先级高于文件。

---

## 文件结构

```
backend/scripts/platform_sync/
  README.md                # 本文档
  __main__.py              # 命令分发：export / sync
  export.py                # dev 端：拉数据 → 写快照
  sync.py                  # prod 端：对比 → 询问 → 调 seed 写库
  config.py                # 凭证加载
  http_client.py           # JWT 登录 + 重试
  validators.py            # 唯一性 / 引用完整性校验
  snapshot_io.py           # 快照 JSON 读写 + 元数据
  diff_utils.py            # 业务主键 diff
  exporters/               # 5 个数据集的导出器
  envs/.env.example        # 凭证模板（入库）
  snapshots/               # 5 份事实源 JSON + _meta.json（入库）
```

---

## 常见问题

| 现象 | 原因 / 处理 |
|------|-------------|
| `export` 报 "feature_code xxx 未定义" | 菜单挂的 feature_code 没在「产品功能清单」里。在 dev console 补完再 export |
| `sync` 提示有差异、应用后仍不一致 | 通常是有人在 prod 直接改了 console。把改动回流到 dev：在 dev 也改一遍 → export → push → 重新 sync |
| `sync` 报 "未找到 envs/.env.prod" | 在生产服务器 `backend/scripts/platform_sync/envs/` 下创建该文件，或挂载到容器内 |
| 登录失败 `[code=403] 无权登录管理后台` | 配置的账号 `user_type != 0`。必须是平台超管账号 |
| 想跳过 sync 的 y/N 确认（CI 用） | `python -m scripts.platform_sync sync --yes`，或设置 `PLATFORM_SYNC_YES=1` |

---

## 与"新模块初始化脚本"的边界

```
[开发新模块 invoice] → [手写 migrate_invoice_module.py] → [在 dev 跑一次 migrate]
                                                          ↓
                                         dev 库有了新菜单/feature/版本关联
                                                          ↓
                                  [export] → snapshots/ 文件更新 → git push
                                                          ↓
                                              [prod 上 sync] → prod 与 dev 一致
```

- **新模块初始化脚本**（如 `migrate_invoice_module.py`）：放 [backend/scripts/init/](../init/) 或 [backend/scripts/fix/](../fix/)，开发者一次性写死菜单/feature/版本，跑完即归档。
- **本工具**：只关心快照与目标库一致，不关心 dev 的数据从哪来（手敲 console 还是脚本 migrate 都可以）。

---

**维护者**：后端团队 · **首版**：2026-05-09
