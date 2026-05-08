-- =====================================================================
-- 承运商管理模块 · 单租户库 SQL（zt_biz_{tenant_code}）
--
-- 执行对象：每一个已开通 basic 及以上版本的"存量"租户业务库
--   - 例如：zt_biz_1001、zt_biz_1002...（按 sys_tenant.db_name 列出）
-- 执行频率：每个租户库执行一次
-- 关联文档：项目文档/02.需求文档/02.企业端/05.合作伙伴模块/02.承运商管理.md 第 4.2-4.4 节
--
-- 内容概览：
--   1. biz_carrier              承运商主体档案（含互联状态预留 + 考核评分预留）
--   2. biz_carrier_settlement   承运商结算账户（一对多）
--   3. biz_carrier_invitation   承运商邀请流水（含 C1/C2/C3 字段全量预留）
--
-- 注意：
--   * 新建租户库由 SQLAlchemy 模型自动建表，无需手工执行本 SQL
--   * 所有"互联状态字段（linked_tenant_code/invite_status/invite_path/forwarder_*/
--     a_review_*/pending_a_review/target_match）" 在本期 Phase B 中部分使用，
--     但全部字段必须建好以避免后续路径 C1/C2/C3 上线时再改表
-- =====================================================================

SET NAMES utf8mb4;

-- ---------------------------------------------------------------------
-- 1. biz_carrier 承运商主体档案
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS biz_carrier (
  id                     BIGINT       NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  carrier_code           VARCHAR(50)  NULL     COMMENT '承运商编码（租户内唯一）',
  carrier_name           VARCHAR(100) NOT NULL COMMENT '承运商全称',
  short_name             VARCHAR(50)  NULL     COMMENT '简称',
  carrier_type           SMALLINT     NOT NULL DEFAULT 0
                                      COMMENT '承运商类型 0-公司车队 1-个体司机/小车队 2-其他',
  credit_code            VARCHAR(50)  NULL     COMMENT '统一社会信用代码（公司必填，个体可空）',
  id_card_no             VARCHAR(20)  NULL     COMMENT '身份证号（个体场景）',
  legal_person           VARCHAR(50)  NULL     COMMENT '法人代表/负责人',
  contact_person         VARCHAR(50)  NULL     COMMENT '主要联系人',
  contact_phone          VARCHAR(20)  NOT NULL COMMENT '联系电话（互联激活关键字段）',
  contact_email          VARCHAR(100) NULL     COMMENT '联系邮箱',
  province               VARCHAR(50)  NULL     COMMENT '省',
  city                   VARCHAR(50)  NULL     COMMENT '市',
  district               VARCHAR(50)  NULL     COMMENT '区/县',
  address                VARCHAR(255) NULL     COMMENT '详细地址',
  cooperation_start_date DATE         NULL     COMMENT '合作起始日',
  status                 SMALLINT     NOT NULL DEFAULT 1
                                      COMMENT '状态 0-停用 1-正常 2-黑名单',
  -- ===== 互联字段 =====
  linked_tenant_code     VARCHAR(32)  NULL     COMMENT '互联：B 在本系统的 tenant_code，NULL 表示纯档案',
  invite_status          SMALLINT     NOT NULL DEFAULT 0
                                      COMMENT '0-未邀请 1-邀请中 2-已激活 3-邀请失败 4-A 端预审待确认 5-A 已撤回 6-B 已拒绝 7-代转交中 8-A 端预审拒绝 9-B 端解绑',
  invite_user_id         BIGINT       NULL     COMMENT '触发邀请的操作员 user_id',
  invited_at             DATETIME     NULL     COMMENT '最近邀请时间',
  activated_at           DATETIME     NULL     COMMENT 'B 首次登录或确认接受时间',
  -- ===== 考核评价（远期预留）=====
  rating_score           DECIMAL(3,1) NULL     COMMENT '考核综合评分 0.0~5.0',
  rating_level           SMALLINT     NULL     COMMENT '考核等级 1-A 2-B 3-C 4-D',
  last_evaluated_at      DATETIME     NULL     COMMENT '最近一次考核时间',
  capacity_summary       JSON         NULL     COMMENT '运力概要快照（车数/车型分布等）',
  remark                 TEXT         NULL     COMMENT '备注',
  created_at             DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at             DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  is_deleted             SMALLINT     NOT NULL DEFAULT 0 COMMENT '软删除标记',
  PRIMARY KEY (id),
  UNIQUE KEY uk_carrier_code (carrier_code),
  KEY idx_carrier_name (carrier_name),
  KEY idx_contact_phone (contact_phone),
  KEY idx_linked_tenant_code (linked_tenant_code),
  KEY idx_status_invite (status, invite_status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='承运商档案表';

-- ---------------------------------------------------------------------
-- 2. biz_carrier_settlement 承运商结算账户（一对多）
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS biz_carrier_settlement (
  id                  BIGINT       NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  carrier_id          BIGINT       NOT NULL COMMENT '关联 biz_carrier.id',
  account_label       VARCHAR(50)  NOT NULL COMMENT '账户标签（如对公主账户/私户-司机张三/运输专用账户）',
  account_type        SMALLINT     NOT NULL DEFAULT 0
                                   COMMENT '账户类型 0-对公 1-对私 2-其他',
  settlement_type     SMALLINT     NOT NULL COMMENT '结算方式 0-月结 1-票结 2-预付 3-趟结',
  settlement_period   SMALLINT     NULL     COMMENT '月结/趟结周期天数（票结/预付场景为空）',
  settlement_day      SMALLINT     NULL     COMMENT '月结结账日（每月几号 1-28，预留）',
  bank_name           VARCHAR(100) NULL     COMMENT '开户行',
  bank_branch         VARCHAR(100) NULL     COMMENT '开户支行',
  bank_account        VARCHAR(50)  NULL     COMMENT '银行账号',
  bank_account_name   VARCHAR(100) NULL     COMMENT '户名',
  swift_code          VARCHAR(20)  NULL     COMMENT '联行号（可选）',
  tax_rate            DECIMAL(5,2) NULL     COMMENT '税率 %（远期，结合发票）',
  applicable_scope    VARCHAR(255) NULL     COMMENT '适用范围（业务线/路线/车型，文本备注）',
  is_default          SMALLINT     NOT NULL DEFAULT 0
                                   COMMENT '是否默认账户 1-是 0-否（同 carrier_id 内最多 1 条 is_default=1）',
  status              SMALLINT     NOT NULL DEFAULT 1 COMMENT '状态 0-停用 1-正常',
  sort_order          INT          NOT NULL DEFAULT 0 COMMENT '排序',
  remark              TEXT         NULL     COMMENT '备注',
  created_at          DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at          DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  is_deleted          SMALLINT     NOT NULL DEFAULT 0,
  PRIMARY KEY (id),
  KEY idx_carrier_id (carrier_id),
  KEY idx_carrier_default (carrier_id, is_default, status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='承运商结算账户表';

-- ---------------------------------------------------------------------
-- 3. biz_carrier_invitation 承运商邀请流水（含 C1/C2/C3 字段全量预留）
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS biz_carrier_invitation (
  id                     BIGINT       NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  carrier_id             BIGINT       NOT NULL COMMENT '关联 biz_carrier.id',
  invite_code            VARCHAR(32)  NOT NULL COMMENT '邀请码（用于短链 URL，全局唯一）',
  invite_phone           VARCHAR(20)  NOT NULL COMMENT '被邀请人手机号',
  expected_carrier_name  VARCHAR(100) NOT NULL COMMENT 'A 录入承运商档案时的名称快照',
  invite_channel         VARCHAR(20)  NOT NULL DEFAULT 'sms' COMMENT 'sms / wechat / link',
  sms_content            TEXT         NULL     COMMENT '短信内容快照（便于审计与追责）',
  invite_token           VARCHAR(64)  NOT NULL COMMENT '一次性激活 token（hash 后存储）',
  expires_at             DATETIME     NOT NULL COMMENT '失效时间，default now()+7d',
  invite_path            VARCHAR(8)   NOT NULL COMMENT '路径分支：B / C1 / C2 / C3',
  status                 SMALLINT     NOT NULL DEFAULT 0
                                      COMMENT '0-待发送 1-已发送 2-已点击 3-已激活 4-已过期 5-A 已撤回 6-B 已拒绝 7-代转交中 8-A 端预审拒绝',
  -- ===== 被邀请人识别（路径 C 用，本期 B 路径激活后回填） =====
  invitee_user_id        BIGINT       NULL     COMMENT '被邀请人 sys_user.id',
  invitee_role_in_tenant SMALLINT     NULL     COMMENT '被邀请人角色 1-管理员 2-员工 3-驾驶员（C2 触发）',
  -- ===== C2 转交字段（本期不写入，但表结构预留） =====
  forwarder_user_id      BIGINT       NULL     COMMENT '代转交者 user_id',
  forwarder_tenant_code  VARCHAR(32)  NULL     COMMENT 'C2 场景被邀请人选择转交所在的租户 tenant_code',
  -- ===== 接受方信息（本期 B 路径激活后回填） =====
  accepted_tenant_code   VARCHAR(32)  NULL     COMMENT '最终建立互联时的租户编码',
  accepted_user_id       BIGINT       NULL     COMMENT '最终接受邀请的 user_id',
  accepted_role          SMALLINT     NULL     COMMENT '最终接受方在所选租户中的角色 1-管理员 2-员工',
  -- ===== C3 A 端预审字段（本期不读写，但表结构预留） =====
  target_match           SMALLINT     NULL     COMMENT '0-完全匹配 1-相近 2-不匹配（C3 触发）',
  pending_a_review       SMALLINT     NOT NULL DEFAULT 0 COMMENT 'A 端预审待确认 1-是 0-否',
  a_review_decision      SMALLINT     NULL     COMMENT 'A 端预审决策：0-未决策 1-同意 2-拒绝',
  a_review_user_id       BIGINT       NULL     COMMENT '进行预审的 A 端操作员 user_id',
  -- ===== 通用 =====
  revoked_reason         VARCHAR(255) NULL     COMMENT '撤回/拒绝/解绑的原因',
  created_at             DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at             DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  is_deleted             SMALLINT     NOT NULL DEFAULT 0,
  PRIMARY KEY (id),
  UNIQUE KEY uk_invite_code (invite_code),
  KEY idx_carrier_id (carrier_id),
  KEY idx_invite_phone (invite_phone),
  KEY idx_status_expires (status, expires_at),
  KEY idx_pending_a_review (pending_a_review, status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='承运商邀请流水表';
