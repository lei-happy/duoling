"""business_entity: 经营主体主表 + 各业务表 enterprise_id 归属列

引入「经营主体」（法人/独立核算单元）概念：
  * 新建 core 表 biz_business_entity，并 seed 一条默认主体；
  * 给 biz_driver / biz_vehicle / biz_capacity / biz_task /
    biz_task_finance_doc 增加可空 enterprise_id + 索引；
  * 将存量数据的 enterprise_id 回填到默认主体，保证分主体对账口径一致
    （账户服务对 NULL 也会兜底归一到默认主体，回填只是让库内数据更干净）。

幂等：表 / 列 / 索引均先 information_schema 探测再执行；REQUIRES_TABLES 留空，
biz_business_entity 属 core 表需对所有租户执行，业务表列则逐表判断存在性。
"""

from sqlalchemy import text

MIGRATION_ID = "20260706_002"
MIGRATION_NAME = "business_entity + enterprise_id ownership columns"
REQUIRES_TABLES = []


_TABLE_EXISTS_SQL = text(
    """
    SELECT 1 FROM information_schema.tables
    WHERE table_schema = DATABASE() AND table_name = :tn
    LIMIT 1
    """
)
_COL_EXISTS_SQL = text(
    """
    SELECT 1 FROM information_schema.columns
    WHERE table_schema = DATABASE() AND table_name = :tn AND column_name = :cn
    LIMIT 1
    """
)
_INDEX_EXISTS_SQL = text(
    """
    SELECT 1 FROM information_schema.statistics
    WHERE table_schema = DATABASE() AND table_name = :tn AND index_name = :ix
    LIMIT 1
    """
)

_CREATE_ENTITY_SQL = text(
    """
    CREATE TABLE IF NOT EXISTS biz_business_entity (
        id BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
        entity_code VARCHAR(50) NOT NULL COMMENT '主体编码（业务唯一标识）',
        entity_name VARCHAR(100) NOT NULL COMMENT '主体名称（法人全称）',
        short_name VARCHAR(50) DEFAULT NULL COMMENT '简称（列表/选择器展示）',
        unified_credit_code VARCHAR(30) DEFAULT NULL COMMENT '统一社会信用代码',
        legal_person VARCHAR(50) DEFAULT NULL COMMENT '法定代表人',
        registered_address VARCHAR(255) DEFAULT NULL COMMENT '注册地址',
        contact_person VARCHAR(50) DEFAULT NULL COMMENT '联系人',
        contact_phone VARCHAR(20) DEFAULT NULL COMMENT '联系电话',
        bank_name VARCHAR(100) DEFAULT NULL COMMENT '对公开户行',
        bank_account VARCHAR(50) DEFAULT NULL COMMENT '对公账号',
        invoice_title VARCHAR(100) DEFAULT NULL COMMENT '开票抬头',
        invoice_tax_no VARCHAR(30) DEFAULT NULL COMMENT '开票税号',
        is_default SMALLINT NOT NULL DEFAULT 0 COMMENT '是否默认主体 1-是 0-否',
        status SMALLINT NOT NULL DEFAULT 1 COMMENT '状态 1-正常 0-停用',
        sort_order SMALLINT NOT NULL DEFAULT 0 COMMENT '排序号',
        remark TEXT DEFAULT NULL COMMENT '备注',
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
        updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
        is_deleted SMALLINT NOT NULL DEFAULT 0 COMMENT '是否删除 0-否 1-是',
        PRIMARY KEY (id),
        UNIQUE KEY uk_entity_code (entity_code)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
      COMMENT='经营主体表（法人/独立核算单元）'
    """
)

# 归属列所在业务表（表可能因版本未开通而不存在，逐表判断）
_OWNER_TABLES = [
    "biz_driver",
    "biz_vehicle",
    "biz_capacity",
    "biz_task",
    "biz_task_finance_doc",
]


def _table_exists(conn, tn: str) -> bool:
    return conn.execute(_TABLE_EXISTS_SQL, {"tn": tn}).fetchone() is not None


def _col_exists(conn, tn: str, cn: str) -> bool:
    return conn.execute(_COL_EXISTS_SQL, {"tn": tn, "cn": cn}).fetchone() is not None


def _index_exists(conn, tn: str, ix: str) -> bool:
    return conn.execute(_INDEX_EXISTS_SQL, {"tn": tn, "ix": ix}).fetchone() is not None


def upgrade(conn, tenant_code: str) -> None:
    # 1) 建主表
    conn.execute(_CREATE_ENTITY_SQL)

    # 2) seed 默认主体（表空时插入一条 is_default=1）
    has_any = conn.execute(
        text("SELECT 1 FROM biz_business_entity WHERE is_deleted = 0 LIMIT 1")
    ).fetchone()
    if has_any is None:
        conn.execute(
            text(
                "INSERT INTO biz_business_entity "
                "(entity_code, entity_name, invoice_title, is_default, status, sort_order, is_deleted) "
                "VALUES ('ENT0001', '默认经营主体', '默认经营主体', 1, 1, 0, 0)"
            )
        )
    default_id = conn.execute(
        text(
            "SELECT id FROM biz_business_entity "
            "WHERE is_deleted = 0 AND is_default = 1 "
            "ORDER BY id LIMIT 1"
        )
    ).scalar()

    # 3) 各业务表加 enterprise_id + 索引 + 回填默认主体
    for tn in _OWNER_TABLES:
        if not _table_exists(conn, tn):
            continue
        if not _col_exists(conn, tn, "enterprise_id"):
            conn.execute(
                text(
                    f"ALTER TABLE `{tn}` ADD COLUMN `enterprise_id` BIGINT NULL "
                    f"COMMENT '所属经营主体ID（biz_business_entity.id）'"
                )
            )
        ix = f"ix_{tn}_enterprise_id"
        if not _index_exists(conn, tn, ix):
            conn.execute(
                text(f"CREATE INDEX `{ix}` ON `{tn}` (`enterprise_id`)")
            )
        if default_id is not None:
            conn.execute(
                text(
                    f"UPDATE `{tn}` SET enterprise_id = :eid "
                    f"WHERE enterprise_id IS NULL"
                ),
                {"eid": int(default_id)},
            )
