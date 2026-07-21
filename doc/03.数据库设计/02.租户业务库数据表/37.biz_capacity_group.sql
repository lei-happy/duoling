-- =============================================================
-- 运力分组（biz_capacity_group） + 分组成员（biz_capacity_group_member）
-- 表层级：business（开通产品版本时按 feature.required_tables 自动创建）
-- 关系：运力(司机) ↔ 分组 多对多；成员以司机为锚点，运力为操作入口
-- =============================================================

CREATE TABLE biz_capacity_group (
    id            BIGINT       NOT NULL AUTO_INCREMENT,
    enterprise_id BIGINT       DEFAULT NULL COMMENT '所属经营主体ID（空=企业级公共分组）',
    group_name    VARCHAR(50)  NOT NULL COMMENT '分组名称（同企业未删除内唯一）',
    group_code    VARCHAR(50)  DEFAULT NULL COMMENT '分组编码（唯一，留空自动生成）',
    color         VARCHAR(16)  DEFAULT NULL COMMENT '标签颜色（如 #409EFF）',
    sort_order    INT          NOT NULL DEFAULT 0 COMMENT '排序号，越小越靠前',
    status        SMALLINT     NOT NULL DEFAULT 1 COMMENT '状态 0-停用 1-启用',
    remark        VARCHAR(255) DEFAULT NULL COMMENT '备注',
    created_by    BIGINT       DEFAULT NULL COMMENT '创建人',
    updated_by    BIGINT       DEFAULT NULL COMMENT '更新人',
    created_at    DATETIME     DEFAULT CURRENT_TIMESTAMP,
    updated_at    DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_deleted    SMALLINT     NOT NULL DEFAULT 0,
    PRIMARY KEY (id),
    UNIQUE KEY uk_group_code (group_code),
    KEY idx_group_enterprise (enterprise_id),
    KEY idx_group_status (status, is_deleted)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='运力分组表';

CREATE TABLE biz_capacity_group_member (
    id           BIGINT       NOT NULL AUTO_INCREMENT,
    group_id     BIGINT       NOT NULL COMMENT '关联分组ID',
    driver_id    BIGINT       NOT NULL COMMENT '成员锚点：司机ID',
    driver_name  VARCHAR(50)  NOT NULL COMMENT '司机姓名（冗余）',
    capacity_id  BIGINT       DEFAULT NULL COMMENT '加入时运力ID（展示快照，不参与命中）',
    plate_number VARCHAR(20)  DEFAULT NULL COMMENT '加入时车牌（冗余快照）',
    created_by   BIGINT       DEFAULT NULL COMMENT '添加人',
    created_at   DATETIME     DEFAULT CURRENT_TIMESTAMP,
    updated_at   DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_deleted   SMALLINT     NOT NULL DEFAULT 0,
    PRIMARY KEY (id),
    UNIQUE KEY uk_group_driver (group_id, driver_id, is_deleted),
    KEY idx_member_group (group_id),
    KEY idx_member_driver (driver_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='运力分组成员关联表';
