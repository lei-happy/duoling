#!/bin/bash
# ============================================================
# 智途(ZhiTu) 生产环境一键部署脚本
#
# 使用方法:
#   首次部署:    bash deploy.sh init
#   日常更新:    bash deploy.sh update                          # 交互式（推荐人工值守发版）
#                bash deploy.sh update --auto                   # 无人值守（CI / 定时任务）
#                bash deploy.sh update --skip-sync              # 应急：跳过平台元数据同步
#                bash deploy.sh update --skip-tenant-migration  # 应急：跳过租户业务库 schema 迁移
#   仅获SSL:     bash deploy.sh ssl
#   初始化DB:    bash deploy.sh db-init
#   同步配置:    bash deploy.sh db-sync                # 单独触发平台元数据 + 租户业务库 schema + 租户字典
#                bash deploy.sh db-sync --auto
#   仅租户迁移:  bash deploy.sh db-migrate             # 仅租户业务库 schema 迁移
#                bash deploy.sh db-migrate --dry-run
#   查看日志:    bash deploy.sh logs [service]
#   查看状态:    bash deploy.sh status
#
# 上传图片（头像、品牌图等）宿主机目录: /opt/zhitu/data/uploads
# （与 deploy/docker/docker-compose.yml 中 backend 绑定挂载一致；勿与代码仓库 backend/uploads 混淆）
#
# 平台元数据同步（菜单 / 产品版本 / 功能 / 版本-功能映射）:
#   事实源 = backend/scripts/platform_sync/snapshots/*.json（随代码 git push）
#   工具   = backend/scripts/platform_sync/        （详见其 README.md）
#   流程   = update 时先 plan（只读对比）→ 显示差异 → y/N 或 --auto 自动 apply
#   首次部署需在 prod 服务器创建 /opt/zhitu/backend/scripts/platform_sync/envs/.env.prod
#
# 租户业务库 schema 自动迁移（v2 新增）:
#   工具   = backend/scripts/migration/runner.py
#   流程   = update 时在平台元数据同步之后自动跑：
#            ① Phase 1: 按 feature.required_tables 给已开通租户补建缺失业务表
#            ② Phase 2: 按 versions/ 下迁移文件顺序执行未应用的 ALTER 等不可逆变更
#   事实源 = backend/scripts/migration/versions/*.py，执行记录写入每个租户库的 biz_migration_log
# ============================================================

set -e

# 确保 PATH 完整（sudo 可能会重置 PATH 导致找不到 git 等命令）
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

# ---- 配置变量 ----
PROJECT_NAME="zhitu"
PROJECT_DIR="/opt/zhitu"
DEPLOY_DIR="$PROJECT_DIR/deploy/docker"
SSL_DIR="/opt/zhitu/ssl"
# 与 deploy/docker/docker-compose.yml 中 backend 卷挂载一致（XFTP 可浏览此路径）
UPLOADS_HOST_DIR="/opt/zhitu/data/uploads"
GIT_REPO="https://gitee.com/happylei/zhitu.git"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info()  { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# ============================================================
# 检查前置条件
# ============================================================
check_root() {
    if [ "$EUID" -ne 0 ]; then
        log_error "请使用 root 权限运行此脚本: sudo bash deploy.sh $1"
        exit 1
    fi
}

check_env_file() {
    if [ ! -f "$DEPLOY_DIR/.env" ]; then
        log_error "未找到环境变量文件 $DEPLOY_DIR/.env"
        log_info "请先复制并修改配置: cp $DEPLOY_DIR/.env.production $DEPLOY_DIR/.env"
        exit 1
    fi
}

# ============================================================
# 安装基础工具（git、curl 等）
# ============================================================
install_base_tools() {
    log_info "检查并安装基础工具..."
    local need_install=""

    command -v git &> /dev/null || need_install="$need_install git"
    command -v curl &> /dev/null || need_install="$need_install curl"
    command -v openssl &> /dev/null || need_install="$need_install openssl"

    if [ -n "$need_install" ]; then
        log_info "安装缺失工具:$need_install"
        yum install -y $need_install
    fi
    log_info "基础工具就绪 (git=$(git --version 2>/dev/null | awk '{print $3}'))"
}

# ============================================================
# 获取服务器公网 IP
# ============================================================
get_public_ip() {
    local ip=""
    ip=$(curl -s --connect-timeout 3 https://myip.ipip.net 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' | head -1) \
    || ip=$(curl -s --connect-timeout 3 https://ip.cn/api/index?type=0 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' | head -1) \
    || ip=$(curl -s --connect-timeout 3 ifconfig.me 2>/dev/null) \
    || ip=$(hostname -I 2>/dev/null | awk '{print $1}')
    echo "${ip:-未知}"
}

# ============================================================
# 安装 Docker
# ============================================================
install_docker() {
    if command -v docker &> /dev/null; then
        log_info "Docker 已安装: $(docker --version)"
        return
    fi

    log_info "正在安装 Docker..."
    yum install -y yum-utils
    yum-config-manager --add-repo https://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo
    yum install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    systemctl start docker
    systemctl enable docker

    # 配置 Docker 镜像加速
    mkdir -p /etc/docker
    cat > /etc/docker/daemon.json <<'DOCKER_EOF'
{
    "registry-mirrors": [
        "https://mirror.ccs.tencentyun.com",
        "https://registry.docker-cn.com"
    ],
    "log-driver": "json-file",
    "log-opts": {
        "max-size": "100m",
        "max-file": "3"
    }
}
DOCKER_EOF
    systemctl daemon-reload
    systemctl restart docker
    log_info "Docker 安装完成: $(docker --version)"
}

# ============================================================
# 配置防火墙
# ============================================================
setup_firewall() {
    log_info "配置防火墙..."
    if command -v firewall-cmd &> /dev/null; then
        firewall-cmd --permanent --add-port=80/tcp 2>/dev/null || true
        firewall-cmd --permanent --add-port=443/tcp 2>/dev/null || true
        firewall-cmd --reload 2>/dev/null || true
        log_info "防火墙已开放 80、443 端口"
    else
        log_warn "未检测到 firewalld，请手动确认端口 80、443 已开放"
    fi
}

# ============================================================
# 配置 MySQL（允许 Docker 网段访问）
# ============================================================
setup_mysql() {
    log_info "配置 MySQL 允许 Docker 网段访问..."

    # 检查 MySQL 是否运行
    if ! command -v mysql &> /dev/null; then
        log_error "未检测到 MySQL 客户端，请确认 MySQL 已安装"
        exit 1
    fi

    if ! systemctl is-active --quiet mysqld 2>/dev/null && ! systemctl is-active --quiet mysql 2>/dev/null; then
        log_warn "MySQL 服务似乎未运行，请检查服务状态"
    fi

    # 安全读取 .env 中的数据库配置（避免 source 执行特殊字符）
    DB_PASS=$(grep -E '^DB_PASSWORD=' "$DEPLOY_DIR/.env" | head -1 | cut -d'=' -f2- | tr -d '"'"'")
    DB_USR=$(grep -E '^DB_USER=' "$DEPLOY_DIR/.env" | head -1 | cut -d'=' -f2- | tr -d '"'"'")
    DB_PASS="${DB_PASS:-zhitu2026}"
    DB_USR="${DB_USR:-root}"

    log_info "请确保 MySQL 允许来自 Docker 网段 (172.17.0.0/16) 的连接"
    log_info "如果 MySQL 绑定了 127.0.0.1，需要修改 /etc/my.cnf 中的 bind-address"
    echo ""
    log_info "可以手动执行以下 SQL 授权（如使用非 root 用户）："
    echo "  GRANT ALL PRIVILEGES ON \`zt_%\`.* TO '${DB_USR}'@'172.17.%' IDENTIFIED BY '${DB_PASS}';"
    echo "  FLUSH PRIVILEGES;"
    echo ""
}

# ============================================================
# 克隆/更新代码仓库
# ============================================================
clone_repo() {
    if ! command -v git &> /dev/null; then
        if [ -d "$PROJECT_DIR/deploy" ]; then
            log_warn "git 未安装，但项目代码已存在，跳过代码更新"
            log_warn "后续请安装 git (yum install -y git) 以便使用 update 命令"
            cd "$PROJECT_DIR"
            return
        else
            log_error "git 未安装且项目代码不存在，无法继续"
            log_info "请先安装 git: yum install -y git"
            exit 1
        fi
    fi

    if [ -d "$PROJECT_DIR/.git" ]; then
        log_info "项目目录已存在，拉取最新代码..."
        cd "$PROJECT_DIR"
        git pull origin master
    else
        log_info "克隆代码仓库..."
        git clone "$GIT_REPO" "$PROJECT_DIR"
        cd "$PROJECT_DIR"
    fi
    log_info "代码已更新到最新版本"
}

# ============================================================
# 检查/生成 SSL 证书
# 所有域名使用阿里云购买的证书，缺失的生成临时自签名证书
# ============================================================
setup_ssl() {
    local SSL_DIR="/opt/zhitu/ssl"
    mkdir -p "$SSL_DIR"

    local ALL_DOMAINS="zhitu.me console.zhitu.me wuliu.zhitu.me api.zhitu.me"
    local missing=0

    for domain in $ALL_DOMAINS; do
        if [ -f "$SSL_DIR/$domain.pem" ] && [ -f "$SSL_DIR/$domain.key" ]; then
            log_info "SSL 证书已就绪: $domain"
        else
            log_warn "$domain 证书未找到，生成临时自签名证书（浏览器会提示不安全）"
            openssl req -x509 -nodes -newkey rsa:2048 -days 30 \
                -keyout "$SSL_DIR/$domain.key" \
                -out "$SSL_DIR/$domain.pem" \
                -subj "/CN=$domain" 2>/dev/null
            missing=$((missing + 1))
        fi
    done

    if [ $missing -gt 0 ]; then
        echo ""
        log_warn "有 $missing 个域名使用临时证书，请上传阿里云购买的证书到 $SSL_DIR/"
        log_info "证书文件命名规则:"
        echo "  $SSL_DIR/zhitu.me.pem         + zhitu.me.key"
        echo "  $SSL_DIR/console.zhitu.me.pem  + console.zhitu.me.key"
        echo "  $SSL_DIR/wuliu.zhitu.me.pem    + wuliu.zhitu.me.key"
        echo "  $SSL_DIR/api.zhitu.me.pem      + api.zhitu.me.key"
        echo ""
        log_info "上传后执行: docker exec zhitu-nginx nginx -s reload"
    fi
}

# ============================================================
# 宿主机上传目录（绑定到容器 /app/uploads）
# ============================================================
ensure_uploads_host_dir() {
    mkdir -p "$UPLOADS_HOST_DIR"
    chmod 755 "$UPLOADS_HOST_DIR" 2>/dev/null || true
    log_info "上传文件宿主机目录: $UPLOADS_HOST_DIR（与 compose 中 backend 挂载一致）"
}

warn_if_uploads_empty() {
    if [ ! -d "$UPLOADS_HOST_DIR" ]; then
        return
    fi
    if [ -z "$(ls -A "$UPLOADS_HOST_DIR" 2>/dev/null)" ]; then
        echo ""
        log_warn "上传目录当前为空: $UPLOADS_HOST_DIR"
        log_warn "数据库里若已有 /uploads/...（如用户头像），静态文件将 404，客户端头像会裂图。"
        log_info "处理: 从备份还原该目录，或让用户在客户端重新上传头像；品牌/车系图可重跑控制台同步任务。"
        log_info "注意: 在首次挂载宿主机卷之前，若未把旧容器内 /app/uploads 拷出，旧文件将无法恢复。"
        echo ""
    fi
}

# ============================================================
# 构建并启动服务
# ============================================================
build_and_start() {
    log_info "构建并启动 Docker 服务..."
    ensure_uploads_host_dir
    cd "$DEPLOY_DIR"

    # 启用 BuildKit 以并行构建多阶段 Dockerfile
    export DOCKER_BUILDKIT=1
    export COMPOSE_DOCKER_CLI_BUILD=1

    docker compose up -d --build

    # 等待 backend HTTP 就绪（init 场景下也用同一函数，避免 sleep 15 偶发不足）
    if ! wait_for_backend_http 180; then
        log_error "backend 启动失败，请检查日志:"
        docker compose logs --tail=80 backend
        exit 1
    fi

    # 检查服务状态（兼容 Compose V2 输出 "Up" 和 V1 输出 "running"）
    if docker compose ps | grep -qiE "(running|Up)"; then
        log_info "所有服务已启动"
        docker compose ps
        warn_if_uploads_empty
    else
        log_error "部分服务启动失败，请检查日志:"
        docker compose logs --tail=50
        exit 1
    fi
}

# ============================================================
# 重载 SSL 证书（上传新证书后调用）
# ============================================================
reload_ssl() {
    log_info "检查证书文件..."
    setup_ssl
    log_info "重载 Nginx..."
    docker exec zhitu-nginx nginx -s reload
    log_info "SSL 证书已生效"
}

# ============================================================
# 轮询等待 backend 容器 HTTP 就绪
#
# 为什么需要这个：
#   - docker compose up -d 只代表容器已 spawn，并不代表 uvicorn 已经把
#     8000 端口监听起来；冷启动加载 SQLAlchemy metadata + Pydantic schemas
#     通常要 15-30 秒
#   - 旧版 sleep 5 太短，后续 platform_sync 直接打 http://backend:8000
#     会 ConnectError([Errno 111] Connection refused) 而中止部署
#   - healthcheck start_period=15s，再加 interval/retries，靠 healthy 状态
#     轮询太慢，不如直接在 backend 容器内 curl /health 主动探活
#
# 参数:  $1 = 最长等待秒数（默认 120）
# 返回:  0=就绪；1=超时未就绪（调用方需自行决定是否中止）
# ============================================================
wait_for_backend_http() {
    local max_wait="${1:-120}"
    local elapsed=0
    local step=3
    cd "$DEPLOY_DIR"
    log_info "等待 backend HTTP 就绪 (最长 ${max_wait}s)..."
    while [ $elapsed -lt $max_wait ]; do
        # 直接在容器内 curl /health，比等 docker healthcheck 周期快很多
        # 静默全部输出，只关心 exit code
        if docker compose exec -T backend python -c \
            "import sys, httpx; sys.exit(0 if httpx.get('http://127.0.0.1:8000/health', timeout=2).status_code == 200 else 1)" \
            >/dev/null 2>&1; then
            echo ""
            log_info "backend 已就绪（耗时 ${elapsed}s）"
            return 0
        fi
        sleep $step
        elapsed=$((elapsed + step))
        printf '.'
    done
    echo ""
    log_error "backend 在 ${max_wait}s 内未通过 /health 检查"
    log_warn "请查看 backend 日志定位启动失败原因："
    log_warn "  bash deploy.sh logs backend"
    log_warn "（常见原因：DB 连接失败、ImportError、Pydantic schema 校验失败）"
    return 1
}

# ============================================================
# 平台元数据同步（菜单 / 产品功能 / 版本 / 版本-功能映射）
#
# 流程：plan（只读对比） → 视模式决定 apply：
#   - 交互式（默认）：终端 prompt y/N，仅在有差异时打扰
#   - --auto       ：无差异时安静跳过；有差异时自动 apply
#   - --skip-sync  ：完全跳过本环节（应急用，调用方设置 SKIP_PLATFORM_SYNC=1）
#
# 退出码（platform_sync sync --plan）：
#   0=无差异，10=有差异需 apply，2=配置错误（缺 .env / 缺快照），3=API 失败
#
# 凭证：容器内需要 backend/scripts/platform_sync/envs/.env.prod
# （内含 console URL + 平台超管账号；不入库，需 prod 服务器上手工预置一次）
# ============================================================
sync_platform_metadata() {
    if [ "${SKIP_PLATFORM_SYNC:-0}" = "1" ]; then
        log_warn "已设置 --skip-sync，跳过平台元数据同步（菜单/功能/版本）"
        return 0
    fi

    cd "$DEPLOY_DIR"

    # ---- 检查容器内是否有凭证文件 ----
    if ! docker compose exec -T backend test -f scripts/platform_sync/envs/.env.prod 2>/dev/null; then
        log_warn "容器内未找到 backend/scripts/platform_sync/envs/.env.prod"
        log_warn "首次部署？请按下面步骤创建该文件后再执行 db-sync："
        echo "  1) 在宿主机创建：vi $PROJECT_DIR/backend/scripts/platform_sync/envs/.env.prod"
        echo "     模板：cp $PROJECT_DIR/backend/scripts/platform_sync/envs/.env.example \\"
        echo "                $PROJECT_DIR/backend/scripts/platform_sync/envs/.env.prod"
        echo "  2) 编辑填入 console URL（容器内访问写 http://backend:8000）+ 平台超管账号"
        echo "  3) docker compose exec backend ls scripts/platform_sync/envs/  确认能看到 .env.prod"
        echo ""
        log_warn "本次 update 跳过平台元数据同步，按需手动跑 db-sync 补回。"
        return 0
    fi

    # ---- 第 1 阶段：plan（只读对比，打印差异摘要+详情） ----
    log_info "==== 平台元数据 plan：对比目标库 vs 仓库快照 ===="
    set +e
    docker compose exec backend python -m scripts.platform_sync sync --plan
    local plan_rc=$?
    set -e

    case "$plan_rc" in
        0)
            log_info "[OK] 目标库与仓库快照一致，跳过 apply"
            return 0
            ;;
        10)
            ;;  # 有差异，进入 apply 流程
        2|3|*)
            log_error "平台元数据 plan 失败 (exit=$plan_rc)，已中止部署"
            log_warn "常见原因：缺 .env.prod 凭证 / 快照不齐 / console 服务未就绪"
            log_warn "可用 db-sync 命令单独排查后再 update"
            return $plan_rc
            ;;
    esac

    # ---- 第 2 阶段：apply（人工或自动） ----
    if [ "${AUTO_MODE:-0}" = "1" ]; then
        log_warn "auto 模式：自动应用上述差异（如不希望自动应用，去掉 --auto）"
    else
        echo ""
        read -p "是否应用以上变更到生产平台库？(y/N): " confirm
        if [[ ! "$confirm" =~ ^[yY]([eE][sS])?$ ]]; then
            log_warn "已取消平台元数据同步（部署其余环节继续）"
            return 0
        fi
    fi

    log_info "==== 平台元数据 apply：写库 + 自检 ===="
    set +e
    docker compose exec backend python -m scripts.platform_sync sync --yes
    local apply_rc=$?
    set -e
    if [ "$apply_rc" -ne 0 ]; then
        log_error "平台元数据 apply 失败 (exit=$apply_rc)"
        return $apply_rc
    fi
    log_info "[OK] 平台元数据已同步"
}

# 租户字典种子数据（dict_code 不存在则新增，已存在则跳过；与平台元数据无关）
sync_tenant_dicts() {
    log_info "同步租户字典数据..."
    cd "$DEPLOY_DIR"
    docker compose exec backend python scripts/seed/seed_client_dicts.py
    log_info "租户字典数据已同步"
}

# ============================================================
# 租户业务库 schema 自动迁移
#
# 两阶段（细节见 backend/scripts/migration/runner.py）：
#   Phase 1: 按 sys_product_feature.required_tables 自动补表
#            （把新版本带来的新表自动建到所有已开通对应 feature 的租户）
#   Phase 2: 执行 backend/scripts/migration/versions/ 下的 versioned migration
#            （记录在租户库 biz_migration_log，幂等，仅用于 ALTER 列等场景）
#
# 完全幂等：表/列已存在、migration 已执行均自动跳过；
# 单租户失败不影响其它租户，runner 末尾返回非零退出码以告警。
#
# 必须在 sync_platform_metadata 之后执行：
#   平台先把 feature.required_tables / version_feature 写好，
#   runner 才能据此推算每个租户的目标表清单。
#
# 失败处理：
#   退出码 != 0 时本函数返回非零，但不会 set -e 中止 deploy.sh 整个流程，
#   因为单租户 schema 问题不应阻塞其它租户的服务重启；调用方仅打印告警。
# ============================================================
sync_tenant_business_schema() {
    if [ "${SKIP_TENANT_MIGRATION:-0}" = "1" ]; then
        log_warn "已设置 --skip-tenant-migration，跳过租户业务库 schema 迁移"
        return 0
    fi

    log_info "==== 租户业务库 schema 自动迁移 ===="
    cd "$DEPLOY_DIR"

    # 注入执行者标识，便于 biz_migration_log 审计
    local applied_by="deploy@$(hostname)"

    set +e
    if [ "${AUTO_MODE:-0}" = "1" ]; then
        # auto 模式：先 plan 再 apply，便于在 CI 日志里留计划
        docker compose exec -T -e MIGRATION_APPLIED_BY="$applied_by" backend \
            python -m scripts.migration.runner --dry-run
        docker compose exec -T -e MIGRATION_APPLIED_BY="$applied_by" backend \
            python -m scripts.migration.runner
        local rc=$?
    else
        # 交互式：直接 apply（runner 内部已是幂等的，且会打印计划）
        docker compose exec -T -e MIGRATION_APPLIED_BY="$applied_by" backend \
            python -m scripts.migration.runner
        local rc=$?
    fi
    set -e

    if [ "$rc" -eq 0 ]; then
        log_info "[OK] 租户业务库 schema 已对齐"
        return 0
    fi
    log_warn "租户业务库迁移返回退出码 $rc：至少一个租户失败，请翻阅上方日志"
    log_warn "（不会中止部署；建议事后用 'bash deploy.sh db-migrate' 单独排查）"
    return $rc
}

# 老接口保留，封装为顺序调用（向后兼容旧调用点）
# 顺序：平台元数据 → 租户业务库 schema → 租户字典
#   1) 平台先把 feature / version_feature / required_tables 写好
#   2) 租户库再据此补表 + 跑 versioned migration
#   3) 字典最后灌（依赖 biz_dict 表已存在，core 表本来就有，所以顺序其实无强约束）
sync_platform_data() {
    sync_platform_metadata
    sync_tenant_business_schema
    sync_tenant_dicts
}

# ============================================================
# 初始化数据库
# ============================================================
init_database() {
    log_info "初始化平台数据库..."
    cd "$DEPLOY_DIR"

    # 在 backend 容器中执行初始化脚本
    docker compose exec backend python scripts/init/init_platform_db.py
    log_info "平台数据库表结构已创建"

    echo ""
    log_warn "即将写入种子数据（超级管理员、菜单、字典等），已有数据不会重复插入"
    read -p "是否继续？(y/N): " confirm
    if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
        log_info "跳过种子数据写入"
        return
    fi

    docker compose exec backend python scripts/seed/seed_data.py
    log_info "种子数据已写入（管理员: 13800000000 / admin123）"

    # 同步菜单和产品功能模块
    sync_platform_data

    echo ""
    log_warn "首次登录后请立即修改默认密码！"
}

# ============================================================
# 命令: init（首次完整部署）
# ============================================================
cmd_init() {
    check_root "init"

    echo "============================================================"
    echo "  智途(ZhiTu) 生产环境首次部署"
    echo "============================================================"
    echo ""

    # Step 1: 安装基础工具（git、curl 等）
    install_base_tools

    log_info "服务器 IP: $(get_public_ip)"
    echo ""

    # Step 2: 安装 Docker
    install_docker

    # Step 3: 配置防火墙
    setup_firewall

    # Step 4: 克隆/更新代码
    clone_repo

    # Step 5: 检查环境变量配置
    if [ ! -f "$DEPLOY_DIR/.env" ]; then
        log_info "创建环境变量配置文件..."
        cp "$DEPLOY_DIR/.env.production" "$DEPLOY_DIR/.env"
        log_warn "请编辑 $DEPLOY_DIR/.env 修改数据库密码和密钥"
        log_warn "修改完成后重新运行: bash deploy.sh init"
        echo ""
        log_info "需要修改的关键配置:"
        echo "  DB_PASSWORD     - MySQL 数据库密码"
        echo "  APP_SECRET_KEY  - 应用密钥（随机字符串）"
        echo "  JWT_SECRET_KEY  - JWT 密钥（随机字符串）"
        echo "  CERTBOT_EMAIL   - SSL 证书通知邮箱"
        echo ""
        log_info "生成随机密钥: python3 -c \"import secrets; print(secrets.token_urlsafe(32))\""
        exit 0
    fi
    check_env_file

    # Step 6: 配置 MySQL
    setup_mysql

    # Step 7: 检查/生成 SSL 证书
    setup_ssl

    # Step 8: 构建并启动
    build_and_start

    # Step 9: 初始化数据库
    init_database

    echo ""
    echo "============================================================"
    log_info "部署完成！"
    echo "============================================================"
    echo ""
    echo "  官网:     http://www.zhitu.me"
    echo "  管理后台: http://console.zhitu.me"
    echo "  客户端:   http://wuliu.zhitu.me"
    echo "  API:      http://api.zhitu.me/docs"
    echo ""
    echo "  管理员账号: 13800000000"
    echo "  管理员密码: admin123（请尽快修改！）"
    echo ""
    echo "  查看日志: bash deploy.sh logs"
    echo "  查看状态: bash deploy.sh status"
    echo "============================================================"
}

# ============================================================
# 命令: update（日常更新）
#
# 用法:
#   bash deploy.sh update              # 默认：交互式（仅在 metadata 有差异时 prompt）
#   bash deploy.sh update --auto       # 无人值守：metadata 有差异自动 apply
#   bash deploy.sh update --skip-sync  # 应急：完全不动平台 metadata
# ============================================================
cmd_update() {
    check_root "update"

    # 解析 flags（$1=update 已被 case 消费，从 $2 开始）
    AUTO_MODE=0
    SKIP_PLATFORM_SYNC=0
    SKIP_TENANT_MIGRATION=0
    shift  # 跳过子命令本身
    while [ $# -gt 0 ]; do
        case "$1" in
            --auto)                    AUTO_MODE=1 ;;
            --skip-sync)               SKIP_PLATFORM_SYNC=1 ;;
            --skip-tenant-migration)   SKIP_TENANT_MIGRATION=1 ;;
            *)
                log_warn "未知参数: $1（已忽略）"
                ;;
        esac
        shift
    done
    export AUTO_MODE SKIP_PLATFORM_SYNC SKIP_TENANT_MIGRATION

    log_info "开始更新部署...  (auto=$AUTO_MODE, skip-sync=$SKIP_PLATFORM_SYNC, skip-tenant-migration=$SKIP_TENANT_MIGRATION)"
    cd "$PROJECT_DIR"

    # 拉取最新代码
    if command -v git &> /dev/null; then
        git pull origin master
    else
        log_error "未找到 git，请先安装: yum install -y git"
        exit 1
    fi
    log_info "代码已更新"

    # 重新构建并启动
    cd "$DEPLOY_DIR"
    check_env_file

    ensure_uploads_host_dir

    export DOCKER_BUILDKIT=1
    export COMPOSE_DOCKER_CLI_BUILD=1

    # 清理 BuildKit 构建缓存（docker image prune 不会清这层）。
    # 避免 nginx 多阶段构建复用旧层导致线上前端仍是旧页面。
    # 若仍不生效，可临时执行: docker compose build --no-cache && docker compose up -d
    log_info "清理 Docker 构建缓存..."
    docker builder prune -f 2>/dev/null || log_warn "builder prune 跳过（可能为旧版 Docker 或未启用 BuildKit）"

    docker compose up -d --build
    log_info "服务已重启"

    # 等待 backend HTTP 就绪后再做平台元数据/租户迁移
    # （旧版 sleep 5 太短，新构建容器加载需 15-30s，导致 sync 因端口未开而失败）
    if ! wait_for_backend_http 180; then
        log_error "backend 未就绪，跳过后续 sync_platform_data 步骤"
        log_warn "排查完成后请单独执行: bash deploy.sh db-sync"
        docker compose ps
        return 1
    fi

    sync_platform_data

    # 清理旧镜像
    docker image prune -f
    log_info "旧镜像已清理"

    docker compose ps
    warn_if_uploads_empty
}

# ============================================================
# 命令: ssl
# ============================================================
cmd_ssl() {
    check_root "ssl"
    reload_ssl
}

# ============================================================
# 命令: db-init
# ============================================================
cmd_db_init() {
    check_root "db-init"
    init_database
}

# ============================================================
# 命令: db-sync（同步菜单和产品功能模块）
#
# 用法:
#   bash deploy.sh db-sync             # 交互式
#   bash deploy.sh db-sync --auto      # 无人值守
#   bash deploy.sh db-sync --skip-sync # 仅跑租户字典 seed，不动 metadata
# ============================================================
cmd_db_sync() {
    check_root "db-sync"
    check_env_file

    AUTO_MODE=0
    SKIP_PLATFORM_SYNC=0
    SKIP_TENANT_MIGRATION=0
    shift
    while [ $# -gt 0 ]; do
        case "$1" in
            --auto)                    AUTO_MODE=1 ;;
            --skip-sync)               SKIP_PLATFORM_SYNC=1 ;;
            --skip-tenant-migration)   SKIP_TENANT_MIGRATION=1 ;;
            *)                         log_warn "未知参数: $1（已忽略）" ;;
        esac
        shift
    done
    export AUTO_MODE SKIP_PLATFORM_SYNC SKIP_TENANT_MIGRATION

    # 单独触发 db-sync 时也确保 backend HTTP 就绪（用户可能刚重启完）
    if ! wait_for_backend_http 180; then
        log_error "backend 未就绪，db-sync 中止"
        return 1
    fi

    sync_platform_data
    log_info "平台配置数据同步完成"
}

# ============================================================
# 命令: db-migrate（单独触发租户业务库 schema 迁移）
#
# 用法:
#   bash deploy.sh db-migrate                  # 全租户 apply
#   bash deploy.sh db-migrate --dry-run        # 只打印计划，不写库
#   bash deploy.sh db-migrate --tenant 1001    # 只处理指定租户
# ============================================================
cmd_db_migrate() {
    check_root "db-migrate"
    check_env_file
    cd "$DEPLOY_DIR"

    shift
    # 直接把后续参数透传给 runner
    local applied_by="manual@$(hostname)"
    docker compose exec -T -e MIGRATION_APPLIED_BY="$applied_by" backend \
        python -m scripts.migration.runner "$@"
}

# ============================================================
# 命令: logs
# ============================================================
cmd_logs() {
    cd "$DEPLOY_DIR"
    if [ -n "$2" ]; then
        docker compose logs -f --tail=100 "$2"
    else
        docker compose logs -f --tail=100
    fi
}

# ============================================================
# 命令: status
# ============================================================
cmd_status() {
    cd "$DEPLOY_DIR"
    echo ""
    echo "---- 服务状态 ----"
    docker compose ps
    echo ""
    echo "---- 上传目录（宿主机，对应容器 /app/uploads） ----"
    if [ -d "$UPLOADS_HOST_DIR" ]; then
        uf=$(find "$UPLOADS_HOST_DIR" -type f 2>/dev/null | wc -l)
        echo "  路径: $UPLOADS_HOST_DIR"
        echo "  文件数: ${uf// /}"
    else
        echo "  目录不存在（将随 deploy 创建）: $UPLOADS_HOST_DIR"
    fi
    echo ""
    echo "---- 磁盘使用 ----"
    docker system df
    echo ""
    echo "---- 证书状态 ----"
    if [ -f "$CERTBOT_DIR/conf/live/zhitu.me/fullchain.pem" ]; then
        expiry=$(openssl x509 -enddate -noout -in "$CERTBOT_DIR/conf/live/zhitu.me/fullchain.pem" 2>/dev/null | cut -d= -f2)
        issuer=$(openssl x509 -issuer -noout -in "$CERTBOT_DIR/conf/live/zhitu.me/fullchain.pem" 2>/dev/null)
        echo "  证书到期: $expiry"
        echo "  签发机构: $issuer"
    else
        echo "  未找到 SSL 证书"
    fi
}

# ============================================================
# 命令: restart
# ============================================================
cmd_restart() {
    check_root "restart"
    cd "$DEPLOY_DIR"
    docker compose restart
    docker compose ps
}

# ============================================================
# 命令: stop
# ============================================================
cmd_stop() {
    check_root "stop"
    cd "$DEPLOY_DIR"
    docker compose down
    log_info "所有服务已停止"
}

# ============================================================
# 主入口
# ============================================================
case "${1:-}" in
    init)
        cmd_init "$@"
        ;;
    update)
        cmd_update "$@"
        ;;
    ssl)
        cmd_ssl
        ;;
    db-init)
        cmd_db_init
        ;;
    db-sync)
        cmd_db_sync "$@"
        ;;
    db-migrate)
        cmd_db_migrate "$@"
        ;;
    logs)
        cmd_logs "$@"
        ;;
    status)
        cmd_status
        ;;
    restart)
        cmd_restart
        ;;
    stop)
        cmd_stop
        ;;
    *)
        echo "智途(ZhiTu) 部署管理脚本"
        echo ""
        echo "用法: bash deploy.sh <命令> [选项]"
        echo ""
        echo "命令:"
        echo "  init                       首次完整部署（安装 Docker、配置、构建、启动）"
        echo "  update [--auto|--skip-sync|--skip-tenant-migration]"
        echo "                             日常更新；--auto 跳过 sync 的人工确认；"
        echo "                             --skip-sync 跳过平台元数据同步（应急）；"
        echo "                             --skip-tenant-migration 跳过租户业务库 schema 自动迁移（应急）"
        echo "  ssl                        检查并重载 SSL 证书（上传新证书后执行）"
        echo "  db-init                    初始化数据库（创建表结构和种子数据）"
        echo "  db-sync [--auto|--skip-sync|--skip-tenant-migration]"
        echo "                             单独触发: 平台元数据 + 租户业务库 schema + 租户字典"
        echo "  db-migrate [--dry-run|--tenant <code>]"
        echo "                             单独触发: 仅租户业务库 schema 迁移（runner）"
        echo "  logs [service]             查看日志（如 logs backend / logs nginx）"
        echo "  status                     查看服务状态"
        echo "  restart                    重启所有服务"
        echo "  stop                       停止所有服务"
        echo ""
        echo "平台元数据同步说明（菜单/产品功能/版本）:"
        echo "  事实源: backend/scripts/platform_sync/snapshots/*.json（随代码 git push）"
        echo "  首次部署需创建凭证文件:"
        echo "    /opt/zhitu/backend/scripts/platform_sync/envs/.env.prod"
        echo "  详见 backend/scripts/platform_sync/README.md"
        echo ""
        echo "租户业务库 schema 迁移说明:"
        echo "  自动两阶段：按 feature.required_tables 补表 + 执行 versioned migrations"
        echo "  迁移文件: backend/scripts/migration/versions/*.py"
        echo "  执行记录: 每个租户库的 biz_migration_log 表（幂等，可重复运行）"
        echo "  详见 backend/scripts/migration/__init__.py"
        echo ""
        ;;
esac
