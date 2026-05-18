## 智途 backend 开发者命令封装
##
## 在 backend/ 目录下执行 `make help` 查看全部命令；项目同时支持 Linux/macOS
## 与 Windows（Git Bash 或 wsl 下运行）。Windows PowerShell 直接执行
## `make` 需要先装 https://chocolatey.org/packages/make 或使用 Git Bash。

PYTHON ?= python

.PHONY: help dev-setup migrate-check migrate-new-tenant migrate-new-platform \
        migrate-apply-local migrate-snapshot migrate-runner-drift \
        platform-status platform-stamp platform-upgrade

help: ## 列出所有命令
	@echo "智途 backend 数据库迁移规范 — 常用命令"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-26s\033[0m %s\n", $$1, $$2}'

dev-setup: ## 安装本地 git pre-commit hook（软提示，不阻塞 commit）
	@if [ -d "../.git" ]; then \
		cp tools/pre-commit ../.git/hooks/pre-commit && \
		chmod +x ../.git/hooks/pre-commit && \
		echo "[OK] pre-commit hook 已安装到 .git/hooks/pre-commit"; \
	else \
		echo "[ERROR] 未找到 ../.git；请在仓库根目录的 backend/ 子目录下执行"; \
		exit 1; \
	fi

migrate-check: ## 静态检查 ORM ↔ snapshot 对齐（CI 也跑这个）
	$(PYTHON) -m scripts.migration.check

migrate-new-tenant: ## 生成租户库迁移文件（runner 风格）+ 刷新 tenant_schema.json；用法 make migrate-new-tenant name="add waybill region"
	@if [ -z "$(name)" ]; then echo "用法: make migrate-new-tenant name=\"<desc>\""; exit 2; fi
	$(PYTHON) -m scripts.migration.autogen tenant --name "$(name)"

migrate-new-platform: ## 生成平台库迁移文件（alembic）+ 刷新 platform_schema.json；用法 make migrate-new-platform name="add ai prompt template"
	@if [ -z "$(name)" ]; then echo "用法: make migrate-new-platform name=\"<desc>\""; exit 2; fi
	$(PYTHON) -m scripts.migration.autogen platform --name "$(name)"

migrate-snapshot: ## 强制刷新 snapshots/*.json（在批量重构 / 误删 snapshot 后用）
	$(PYTHON) -m scripts.migration.dump_snapshots

migrate-apply-local: ## 本地一键应用：平台库 alembic + 全部租户库 runner
	$(PYTHON) -m scripts.migration.platform_migrate
	$(PYTHON) -m scripts.migration.runner

migrate-runner-drift: ## 连真实租户库对比 ORM 列差异（仅报警，不写库）
	$(PYTHON) -m scripts.migration.runner --check-drift

platform-status: ## 查看平台库 alembic current
	$(PYTHON) -m scripts.migration.platform_migrate --status

platform-stamp: ## 把当前平台库标记为 alembic head（老库纳管）
	$(PYTHON) -m scripts.migration.platform_migrate --stamp

platform-upgrade: ## 平台库 alembic upgrade head
	$(PYTHON) -m scripts.migration.platform_migrate --upgrade
