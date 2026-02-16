#!/bin/bash
# ============================================================
# 智途(ZhiTu) 生产环境一键部署脚本
#
# 使用方法:
#   首次部署:  bash deploy.sh init
#   日常更新:  bash deploy.sh update
#   仅获SSL:   bash deploy.sh ssl
#   初始化DB:  bash deploy.sh db-init
#   查看日志:  bash deploy.sh logs [service]
#   查看状态:  bash deploy.sh status
# ============================================================

set -e

# ---- 配置变量 ----
PROJECT_NAME="zhitu"
PROJECT_DIR="/opt/zhitu"
DEPLOY_DIR="$PROJECT_DIR/deploy/docker"
CERTBOT_DIR="/opt/zhitu/certbot"
GIT_REPO="https://gitee.com/happylei/zhitu.git"  # 请修改为实际仓库地址
DOMAINS="zhitu.me www.zhitu.me console.zhitu.me wuliu.zhitu.me api.zhitu.me"

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

    # 从 .env 读取数据库密码
    source "$DEPLOY_DIR/.env"
    DB_PASS="${DB_PASSWORD:-zhitu2026}"
    DB_USR="${DB_USER:-root}"

    log_info "请确保 MySQL 允许来自 Docker 网段 (172.17.0.0/16) 的连接"
    log_info "如果 MySQL 绑定了 127.0.0.1，需要修改 /etc/my.cnf 中的 bind-address"
    echo ""
    log_info "可以手动执行以下 SQL 授权（如使用非 root 用户）："
    echo "  GRANT ALL PRIVILEGES ON \`zt_%\`.* TO '${DB_USR}'@'172.17.%' IDENTIFIED BY '${DB_PASS}';"
    echo "  FLUSH PRIVILEGES;"
    echo ""
}

# ============================================================
# 克隆代码仓库
# ============================================================
clone_repo() {
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
# 生成自签名临时证书（首次启动用，certbot 后会替换）
# ============================================================
create_dummy_cert() {
    if [ -f "$CERTBOT_DIR/conf/live/zhitu.me/fullchain.pem" ]; then
        log_info "SSL 证书已存在，跳过临时证书生成"
        return
    fi

    log_info "生成临时自签名证书..."
    mkdir -p "$CERTBOT_DIR/conf/live/zhitu.me"
    mkdir -p "$CERTBOT_DIR/www"

    openssl req -x509 -nodes -newkey rsa:2048 -days 1 \
        -keyout "$CERTBOT_DIR/conf/live/zhitu.me/privkey.pem" \
        -out "$CERTBOT_DIR/conf/live/zhitu.me/fullchain.pem" \
        -subj "/CN=zhitu.me" 2>/dev/null

    log_info "临时证书已生成（仅用于首次启动 Nginx）"
}

# ============================================================
# 构建并启动服务
# ============================================================
build_and_start() {
    log_info "构建并启动 Docker 服务..."
    cd "$DEPLOY_DIR"

    # 启用 BuildKit 以并行构建多阶段 Dockerfile
    export DOCKER_BUILDKIT=1
    export COMPOSE_DOCKER_CLI_BUILD=1

    docker compose up -d --build

    log_info "等待服务启动..."
    sleep 10

    # 检查服务状态
    if docker compose ps | grep -q "running"; then
        log_info "所有服务已启动"
        docker compose ps
    else
        log_error "部分服务启动失败，请检查日志:"
        docker compose logs --tail=50
        exit 1
    fi
}

# ============================================================
# 申请 SSL 证书（Let's Encrypt）
# ============================================================
request_ssl() {
    log_info "申请 Let's Encrypt SSL 证书..."

    source "$DEPLOY_DIR/.env"
    EMAIL="${CERTBOT_EMAIL:-admin@zhitu.me}"

    # 构建 certbot 域名参数
    DOMAIN_ARGS=""
    for domain in $DOMAINS; do
        DOMAIN_ARGS="$DOMAIN_ARGS -d $domain"
    done

    # 删除临时证书
    rm -rf "$CERTBOT_DIR/conf/live/zhitu.me"
    rm -rf "$CERTBOT_DIR/conf/archive/zhitu.me"
    rm -rf "$CERTBOT_DIR/conf/renewal/zhitu.me.conf"

    # 使用 webroot 模式申请证书
    docker run --rm \
        -v "$CERTBOT_DIR/www:/var/www/certbot" \
        -v "$CERTBOT_DIR/conf:/etc/letsencrypt" \
        certbot/certbot certonly \
        --webroot -w /var/www/certbot \
        $DOMAIN_ARGS \
        --email "$EMAIL" \
        --agree-tos \
        --no-eff-email \
        --force-renewal

    if [ $? -eq 0 ]; then
        log_info "SSL 证书申请成功！"
        # 重载 Nginx 使新证书生效
        docker exec zhitu-nginx nginx -s reload
        log_info "Nginx 已重载，SSL 证书已生效"
    else
        log_error "SSL 证书申请失败，请检查域名 DNS 解析是否正确"
        log_info "确保以下域名都已解析到本服务器:"
        for domain in $DOMAINS; do
            echo "  $domain -> $(curl -s ifconfig.me)"
        done
        exit 1
    fi
}

# ============================================================
# 设置 SSL 证书自动续期
# ============================================================
setup_ssl_renewal() {
    log_info "配置 SSL 证书自动续期..."

    # 创建续期脚本
    cat > /opt/zhitu/renew-cert.sh <<'RENEW_EOF'
#!/bin/bash
docker run --rm \
    -v /opt/zhitu/certbot/www:/var/www/certbot \
    -v /opt/zhitu/certbot/conf:/etc/letsencrypt \
    certbot/certbot renew --quiet
docker exec zhitu-nginx nginx -s reload 2>/dev/null || true
RENEW_EOF
    chmod +x /opt/zhitu/renew-cert.sh

    # 添加 crontab（每天凌晨 3 点检查续期）
    (crontab -l 2>/dev/null | grep -v "renew-cert"; echo "0 3 * * * /opt/zhitu/renew-cert.sh >> /opt/zhitu/certbot/renewal.log 2>&1") | crontab -
    log_info "已添加 crontab 定时任务，每天 03:00 自动检查证书续期"
}

# ============================================================
# 初始化数据库
# ============================================================
init_database() {
    log_info "初始化平台数据库..."
    cd "$DEPLOY_DIR"

    # 在 backend 容器中执行初始化脚本
    docker compose exec backend python scripts/init_platform_db.py
    log_info "平台数据库表结构已创建"

    # 写入种子数据
    docker compose exec backend python scripts/seed_data.py
    log_info "种子数据已写入（超级管理员: admin / admin123）"

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
    log_info "服务器 IP: $(curl -s --connect-timeout 5 ifconfig.me 2>/dev/null || echo '获取失败')"
    echo ""

    # Step 1: 安装 Docker
    install_docker

    # Step 2: 配置防火墙
    setup_firewall

    # Step 3: 克隆代码
    clone_repo

    # Step 4: 检查环境变量配置
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

    # Step 5: 配置 MySQL
    setup_mysql

    # Step 6: 生成临时证书
    create_dummy_cert

    # Step 7: 构建并启动
    build_and_start

    # Step 8: 初始化数据库
    init_database

    # Step 9: 申请 SSL 证书
    echo ""
    log_info "是否现在申请 SSL 证书？(需要域名已解析到本服务器)"
    read -p "输入 y 继续，n 跳过 [y/n]: " ssl_choice
    if [ "$ssl_choice" = "y" ] || [ "$ssl_choice" = "Y" ]; then
        request_ssl
        setup_ssl_renewal
    else
        log_warn "跳过 SSL 证书申请，之后可运行: bash deploy.sh ssl"
    fi

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
    echo "  管理员账号: admin"
    echo "  管理员密码: admin123（请尽快修改！）"
    echo ""
    echo "  查看日志: bash deploy.sh logs"
    echo "  查看状态: bash deploy.sh status"
    echo "============================================================"
}

# ============================================================
# 命令: update（日常更新）
# ============================================================
cmd_update() {
    check_root "update"

    log_info "开始更新部署..."
    cd "$PROJECT_DIR"

    # 拉取最新代码
    git pull origin master
    log_info "代码已更新"

    # 重新构建并启动
    cd "$DEPLOY_DIR"
    check_env_file

    export DOCKER_BUILDKIT=1
    export COMPOSE_DOCKER_CLI_BUILD=1

    docker compose up -d --build
    log_info "服务已重启"

    # 清理旧镜像
    docker image prune -f
    log_info "旧镜像已清理"

    docker compose ps
}

# ============================================================
# 命令: ssl
# ============================================================
cmd_ssl() {
    check_root "ssl"
    check_env_file
    request_ssl
    setup_ssl_renewal
}

# ============================================================
# 命令: db-init
# ============================================================
cmd_db_init() {
    check_root "db-init"
    init_database
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
        cmd_init
        ;;
    update)
        cmd_update
        ;;
    ssl)
        cmd_ssl
        ;;
    db-init)
        cmd_db_init
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
        echo "用法: bash deploy.sh <命令>"
        echo ""
        echo "命令:"
        echo "  init      首次完整部署（安装 Docker、配置、构建、启动）"
        echo "  update    日常更新（拉取代码、重新构建、重启服务）"
        echo "  ssl       申请/续期 SSL 证书"
        echo "  db-init   初始化数据库（创建表结构和种子数据）"
        echo "  logs      查看日志（可指定服务: logs backend / logs nginx）"
        echo "  status    查看服务状态"
        echo "  restart   重启所有服务"
        echo "  stop      停止所有服务"
        echo ""
        ;;
esac
