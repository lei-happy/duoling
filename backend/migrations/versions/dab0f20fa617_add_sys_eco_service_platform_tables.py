"""add sys_eco service platform tables

Revision ID: dab0f20fa617
Revises: cbd258d1e79e
Create Date: 2026-07-25 17:32:09.397288

说明：本迁移仅新增服务平台（生态）16 张平台库表 sys_eco_*。

autogen 拿 ORM 与本地开发库比对时夹带了大量历史 drift——包括会误删
open_platform 四张表的 drop_table、以及数百条无关的 alter_column / column_comment。
这些与本次需求无关且具破坏性，已全部人工剔除，只保留本次相关的建表语句。
同类处理的先例见 cbd258d1e79e_add_open_platform_tables.py。

建表使用逐表存在性守卫，重复执行安全。
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = "dab0f20fa617"
down_revision: Union[str, None] = "cbd258d1e79e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    existing = set(sa.inspect(bind).get_table_names())

    if "sys_eco_block_rule" not in existing:
        op.create_table('sys_eco_block_rule',
        sa.Column('tenant_code', sa.String(length=32), nullable=False, comment='设置方租户'),
        sa.Column('blocked_tenant_code', sa.String(length=32), nullable=False, comment='被屏蔽方租户'),
        sa.Column('blocked_tenant_name', sa.String(length=100), nullable=True, comment='被屏蔽方企业名（快照）'),
        sa.Column('remark', sa.String(length=255), nullable=True, comment='备注（仅设置方可见）'),
        sa.Column('created_by', sa.BigInteger(), nullable=True, comment='操作人 user_id'),
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False, comment='主键ID'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False, comment='更新时间'),
        sa.Column('is_deleted', sa.SmallInteger(), server_default='0', nullable=False, comment='是否删除 0-否 1-是'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tenant_code', 'blocked_tenant_code', name='uk_eco_block'),
        comment='服务平台屏蔽名单'
        )
        op.create_index('idx_eco_block_blocked', 'sys_eco_block_rule', ['blocked_tenant_code', 'tenant_code'], unique=False)

    if "sys_eco_capacity_post" not in existing:
        op.create_table('sys_eco_capacity_post',
        sa.Column('post_id', sa.BigInteger(), nullable=False, comment='挂牌ID（sys_eco_post.id）'),
        sa.Column('post_granularity', sa.SmallInteger(), server_default='1', nullable=False, comment='挂牌粒度 1-指定车辆 2-车队打包'),
        sa.Column('truck_type', sa.String(length=30), nullable=False, comment='车辆类型'),
        sa.Column('slot_count', sa.SmallInteger(), nullable=True, comment='轿运车位数'),
        sa.Column('truck_length', sa.Numeric(precision=5, scale=2), nullable=True, comment='车长（米）'),
        sa.Column('rated_load', sa.Numeric(precision=10, scale=2), nullable=True, comment='核定载重（吨）'),
        sa.Column('truck_quantity', sa.Integer(), server_default='1', nullable=False, comment='车辆数量，指定车辆时为 1'),
        sa.Column('plate_number', sa.String(length=20), nullable=True, comment='车牌号（原值，按层级脱敏后对外）'),
        sa.Column('plate_masked', sa.String(length=20), nullable=True, comment='车牌号（打码值，认证层展示）'),
        sa.Column('plate_public', sa.SmallInteger(), server_default='0', nullable=False, comment='是否完全公开车牌 0-否 1-是'),
        sa.Column('has_trailer', sa.SmallInteger(), server_default='0', nullable=False, comment='是否带挂 0-否 1-是'),
        sa.Column('trailer_plate_number', sa.String(length=20), nullable=True, comment='挂车车牌'),
        sa.Column('driver_name', sa.String(length=50), nullable=True, comment='司机姓名（原值，永不对外返回）'),
        sa.Column('driver_display', sa.String(length=30), nullable=True, comment='司机对外展示串，如「王师傅」'),
        sa.Column('driver_years', sa.SmallInteger(), nullable=True, comment='驾龄（年）'),
        sa.Column('driver_order_count', sa.Integer(), nullable=True, comment='司机历史完成单数（统计快照）'),
        sa.Column('departure_ready_at', sa.DateTime(), nullable=True, comment='可出发时间（车在途时填预计到达当前地时间）'),
        sa.Column('pickup_radius', sa.Integer(), nullable=True, comment='可接受取货半径（公里）'),
        sa.Column('good_at_categories', sa.JSON(), nullable=True, comment='擅长货物类别数组'),
        sa.Column('can_invoice', sa.SmallInteger(), server_default='0', nullable=False, comment='是否可开票 0-否 1-是'),
        sa.Column('invoice_type', sa.String(length=30), nullable=True, comment='票种'),
        sa.Column('has_insurance', sa.SmallInteger(), server_default='0', nullable=False, comment='是否有承运保险 0-否 1-是'),
        sa.Column('service_promise', sa.String(length=500), nullable=True, comment='服务承诺（需过敏感内容拦截）'),
        sa.Column('settle_require', sa.SmallInteger(), nullable=True, comment='结算要求 1-现结 2-月结可接受 3-需预付'),
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False, comment='主键ID'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False, comment='更新时间'),
        sa.Column('is_deleted', sa.SmallInteger(), server_default='0', nullable=False, comment='是否删除 0-否 1-是'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('post_id', name='uk_eco_capacity_post'),
        comment='服务平台运力挂牌扩展'
        )
        op.create_index('idx_eco_capacity_slot', 'sys_eco_capacity_post', ['truck_type', 'slot_count'], unique=False)

    if "sys_eco_cargo_post" not in existing:
        op.create_table('sys_eco_cargo_post',
        sa.Column('post_id', sa.BigInteger(), nullable=False, comment='挂牌ID（sys_eco_post.id）'),
        sa.Column('via_points', sa.JSON(), nullable=True, comment='途经点数组'),
        sa.Column('reference_mileage', sa.Numeric(precision=10, scale=1), nullable=True, comment='参考里程（公里）'),
        sa.Column('segment_count', sa.SmallInteger(), server_default='1', nullable=False, comment='分段数量'),
        sa.Column('cargo_category', sa.SmallInteger(), server_default='1', nullable=False, comment='货物类别 1-商品车 2-普货 3-其他'),
        sa.Column('cargo_items', sa.JSON(), nullable=True, comment='商品车明细 [{brand,series,quantity}]，不含 VIN'),
        sa.Column('vehicle_condition', sa.SmallInteger(), nullable=True, comment='车辆状态 1-新车 2-二手车 3-试驾车'),
        sa.Column('cargo_name', sa.String(length=100), nullable=True, comment='普货货物名称'),
        sa.Column('cargo_weight', sa.Numeric(precision=10, scale=2), nullable=True, comment='普货重量（吨）'),
        sa.Column('cargo_volume', sa.Numeric(precision=10, scale=2), nullable=True, comment='普货体积（立方）'),
        sa.Column('package_type', sa.String(length=50), nullable=True, comment='普货包装方式'),
        sa.Column('require_truck_types', sa.JSON(), nullable=True, comment='需要车型编码数组'),
        sa.Column('require_slot_min', sa.SmallInteger(), nullable=True, comment='需要轿运车位数下限'),
        sa.Column('require_slot_max', sa.SmallInteger(), nullable=True, comment='需要轿运车位数上限'),
        sa.Column('allow_split', sa.SmallInteger(), server_default='0', nullable=False, comment='是否接受分批承运 0-否 1-是'),
        sa.Column('require_insurance', sa.SmallInteger(), server_default='0', nullable=False, comment='是否需要承运方投保 0-否 1-是'),
        sa.Column('other_requirements', sa.String(length=500), nullable=True, comment='其他要求（需过敏感内容拦截）'),
        sa.Column('arrive_time', sa.DateTime(), nullable=True, comment='期望到达时间'),
        sa.Column('time_negotiable', sa.SmallInteger(), server_default='1', nullable=False, comment='时间是否可协商 0-否 1-是'),
        sa.Column('settle_type', sa.SmallInteger(), nullable=True, comment='结算方式 1-现结 2-月结 3-预付'),
        sa.Column('prepay_ratio', sa.SmallInteger(), nullable=True, comment='预付比例（%）'),
        sa.Column('freq_desc', sa.String(length=100), nullable=True, comment='预计货量频次，如「每周 3~5 车」'),
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False, comment='主键ID'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False, comment='更新时间'),
        sa.Column('is_deleted', sa.SmallInteger(), server_default='0', nullable=False, comment='是否删除 0-否 1-是'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('post_id', name='uk_eco_cargo_post'),
        comment='服务平台货源挂牌扩展'
        )

    if "sys_eco_deal" not in existing:
        op.create_table('sys_eco_deal',
        sa.Column('deal_no', sa.String(length=32), nullable=False, comment='成交编号'),
        sa.Column('post_id', sa.BigInteger(), nullable=False, comment='挂牌ID（sys_eco_post.id）'),
        sa.Column('post_type', sa.SmallInteger(), nullable=False, comment='挂牌类型（冗余）'),
        sa.Column('intent_id', sa.BigInteger(), nullable=False, comment='被选定的意向ID（sys_eco_intent.id）'),
        sa.Column('owner_tenant_code', sa.String(length=32), nullable=False, comment='挂牌方租户'),
        sa.Column('owner_tenant_name', sa.String(length=100), nullable=False, comment='挂牌方企业名（快照）'),
        sa.Column('owner_contact_name', sa.String(length=50), nullable=True, comment='挂牌方联系人'),
        sa.Column('owner_contact_phone', sa.String(length=20), nullable=True, comment='挂牌方联系电话'),
        sa.Column('partner_tenant_code', sa.String(length=32), nullable=False, comment='合作方租户'),
        sa.Column('partner_tenant_name', sa.String(length=100), nullable=False, comment='合作方企业名（快照）'),
        sa.Column('partner_contact_name', sa.String(length=50), nullable=True, comment='合作方联系人'),
        sa.Column('partner_contact_phone', sa.String(length=20), nullable=True, comment='合作方联系电话'),
        sa.Column('carrier_side', sa.SmallInteger(), nullable=False, comment='承运角色 1-挂牌方承运(运力大厅) 2-合作方承运(货源大厅)'),
        sa.Column('status', sa.SmallInteger(), server_default='0', nullable=False, comment='状态 0-待确认 1-已成交 2-履约中 3-已完成 4-已终止'),
        sa.Column('deal_quantity', sa.Integer(), nullable=True, comment='本次成交量'),
        sa.Column('quantity_unit', sa.String(length=10), server_default='台', nullable=False, comment='计量单位'),
        sa.Column('from_province', sa.String(length=50), nullable=True, comment='起点省（快照）'),
        sa.Column('from_city', sa.String(length=50), nullable=True, comment='起点市（快照）'),
        sa.Column('from_name', sa.String(length=255), nullable=True, comment='起点展示串'),
        sa.Column('to_province', sa.String(length=50), nullable=True, comment='终点省（快照）'),
        sa.Column('to_city', sa.String(length=50), nullable=True, comment='终点市（快照）'),
        sa.Column('to_name', sa.String(length=255), nullable=True, comment='终点展示串'),
        sa.Column('load_time', sa.DateTime(), nullable=True, comment='约定装车时间'),
        sa.Column('deal_price', sa.Numeric(precision=12, scale=2), nullable=True, comment='成交价'),
        sa.Column('price_type', sa.SmallInteger(), nullable=True, comment='计价方式 1-包车 2-按台 3-按公里 4-面议'),
        sa.Column('price_include_tax', sa.SmallInteger(), server_default='0', nullable=False, comment='是否含税 0-否 1-是'),
        sa.Column('settle_type', sa.SmallInteger(), nullable=True, comment='结算方式 1-现结 2-月结 3-预付'),
        sa.Column('prepay_ratio', sa.SmallInteger(), nullable=True, comment='预付比例（%）'),
        sa.Column('plate_number', sa.String(length=20), nullable=True, comment='承运车牌'),
        sa.Column('trailer_plate_number', sa.String(length=20), nullable=True, comment='承运挂车车牌'),
        sa.Column('driver_name', sa.String(length=50), nullable=True, comment='承运司机姓名（仅成交双方可见）'),
        sa.Column('driver_phone', sa.String(length=20), nullable=True, comment='承运司机电话（司机手机号进入平台库的唯一入口，仅成交双方可见）'),
        sa.Column('current_milestone', sa.SmallInteger(), server_default='0', nullable=False, comment='当前履约节点 0-未开始 1-已安排车辆 2-已装车 3-运输中 4-已送达 5-已完成'),
        sa.Column('confirm_deadline', sa.DateTime(), nullable=True, comment='承接方确认截止时间（选定 +24h）'),
        sa.Column('confirmed_at', sa.DateTime(), nullable=True, comment='确认成交时间'),
        sa.Column('started_at', sa.DateTime(), nullable=True, comment='开始履约时间'),
        sa.Column('completed_at', sa.DateTime(), nullable=True, comment='完成时间'),
        sa.Column('auto_completed', sa.SmallInteger(), server_default='0', nullable=False, comment='是否系统自动完成（送达 +7 天）0-否 1-是'),
        sa.Column('terminated_at', sa.DateTime(), nullable=True, comment='终止时间'),
        sa.Column('terminate_by', sa.String(length=32), nullable=True, comment='终止发起方租户编码'),
        sa.Column('terminate_reason', sa.String(length=255), nullable=True, comment='终止原因'),
        sa.Column('owner_evaluated', sa.SmallInteger(), server_default='0', nullable=False, comment='挂牌方是否已评价 0-否 1-是'),
        sa.Column('partner_evaluated', sa.SmallInteger(), server_default='0', nullable=False, comment='合作方是否已评价 0-否 1-是'),
        sa.Column('carrier_linked', sa.SmallInteger(), server_default='0', nullable=False, comment='是否已建立承运商关系 0-否 1-是'),
        sa.Column('carrier_link_id', sa.BigInteger(), nullable=True, comment='关联 sys_carrier_link.id'),
        sa.Column('owner_task_backfilled', sa.SmallInteger(), server_default='0', nullable=False, comment='发布方是否已把承运方回填到自己的任务单 0-否 1-是'),
        sa.Column('partner_task_id', sa.BigInteger(), nullable=True, comment='承接方任务单ID（二期运单直通预留，一期留空）'),
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False, comment='主键ID'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False, comment='更新时间'),
        sa.Column('is_deleted', sa.SmallInteger(), server_default='0', nullable=False, comment='是否删除 0-否 1-是'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('deal_no'),
        comment='服务平台成交单'
        )
        op.create_index('idx_eco_deal_deadline', 'sys_eco_deal', ['status', 'confirm_deadline'], unique=False)
        op.create_index('idx_eco_deal_owner', 'sys_eco_deal', ['owner_tenant_code', 'status', 'created_at'], unique=False)
        op.create_index('idx_eco_deal_partner', 'sys_eco_deal', ['partner_tenant_code', 'status', 'created_at'], unique=False)
        op.create_index('idx_eco_deal_post', 'sys_eco_deal', ['post_id'], unique=False)
        op.create_index('idx_eco_deal_route', 'sys_eco_deal', ['from_province', 'to_province', 'status'], unique=False)

    if "sys_eco_deal_milestone" not in existing:
        op.create_table('sys_eco_deal_milestone',
        sa.Column('deal_id', sa.BigInteger(), nullable=False, comment='成交单ID（sys_eco_deal.id）'),
        sa.Column('milestone_type', sa.SmallInteger(), nullable=False, comment='节点 1-已安排车辆 2-已装车 3-运输中 4-已送达 5-确认完成'),
        sa.Column('reporter_tenant_code', sa.String(length=32), nullable=False, comment='上报方租户'),
        sa.Column('reporter_user_id', sa.BigInteger(), nullable=True, comment='上报人 user_id'),
        sa.Column('reporter_name', sa.String(length=50), nullable=True, comment='上报人姓名'),
        sa.Column('occurred_at', sa.DateTime(), nullable=False, comment='节点发生时间'),
        sa.Column('location', sa.String(length=255), nullable=True, comment='当前位置'),
        sa.Column('eta', sa.DateTime(), nullable=True, comment='预计到达时间'),
        sa.Column('remark', sa.String(length=500), nullable=True, comment='备注'),
        sa.Column('attachments', sa.JSON(), nullable=True, comment='附件URL数组（装车照/回单）'),
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False, comment='主键ID'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False, comment='更新时间'),
        sa.Column('is_deleted', sa.SmallInteger(), server_default='0', nullable=False, comment='是否删除 0-否 1-是'),
        sa.PrimaryKeyConstraint('id'),
        comment='服务平台履约节点上报'
        )
        op.create_index('idx_eco_milestone_deal', 'sys_eco_deal_milestone', ['deal_id', 'occurred_at'], unique=False)

    if "sys_eco_evaluation" not in existing:
        op.create_table('sys_eco_evaluation',
        sa.Column('deal_id', sa.BigInteger(), nullable=False, comment='成交单ID（sys_eco_deal.id）'),
        sa.Column('post_id', sa.BigInteger(), nullable=False, comment='挂牌ID（冗余）'),
        sa.Column('from_tenant_code', sa.String(length=32), nullable=False, comment='评价方租户'),
        sa.Column('from_tenant_name', sa.String(length=100), nullable=False, comment='评价方企业名（快照）'),
        sa.Column('to_tenant_code', sa.String(length=32), nullable=False, comment='被评价方租户'),
        sa.Column('role', sa.SmallInteger(), nullable=False, comment='评价角色 1-货主评承运 2-承运评货主'),
        sa.Column('score', sa.SmallInteger(), nullable=False, comment='评分 1~5'),
        sa.Column('tags', sa.JSON(), nullable=True, comment='评价标签数组'),
        sa.Column('content', sa.String(length=500), nullable=True, comment='文字评价'),
        sa.Column('is_default', sa.SmallInteger(), server_default='0', nullable=False, comment='是否超时默认好评 0-否 1-是'),
        sa.Column('reply', sa.String(length=500), nullable=True, comment='被评方回复（仅一次）'),
        sa.Column('replied_at', sa.DateTime(), nullable=True, comment='回复时间'),
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False, comment='主键ID'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False, comment='更新时间'),
        sa.Column('is_deleted', sa.SmallInteger(), server_default='0', nullable=False, comment='是否删除 0-否 1-是'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('deal_id', 'from_tenant_code', name='uk_eco_eval'),
        comment='服务平台合作互评'
        )
        op.create_index('idx_eco_eval_to', 'sys_eco_evaluation', ['to_tenant_code', 'created_at'], unique=False)

    if "sys_eco_intent" not in existing:
        op.create_table('sys_eco_intent',
        sa.Column('intent_no', sa.String(length=32), nullable=False, comment='意向编号'),
        sa.Column('post_id', sa.BigInteger(), nullable=False, comment='挂牌ID（sys_eco_post.id）'),
        sa.Column('post_type', sa.SmallInteger(), nullable=False, comment='挂牌类型（冗余）'),
        sa.Column('owner_tenant_code', sa.String(length=32), nullable=False, comment='挂牌归属租户（冗余，避免查「我收到的」时 join 主表）'),
        sa.Column('initiator_tenant_code', sa.String(length=32), nullable=False, comment='发起方租户'),
        sa.Column('initiator_tenant_name', sa.String(length=100), nullable=False, comment='发起方企业全称（快照）'),
        sa.Column('initiator_user_id', sa.BigInteger(), nullable=True, comment='发起人 user_id'),
        sa.Column('initiator_name', sa.String(length=50), nullable=True, comment='发起人姓名'),
        sa.Column('status', sa.SmallInteger(), server_default='0', nullable=False, comment='状态 0-待响应 1-洽谈中 2-已选定 3-已婉拒 4-已撤回 5-已失效'),
        sa.Column('offer_price', sa.Numeric(precision=12, scale=2), nullable=True, comment='报价'),
        sa.Column('price_type', sa.SmallInteger(), nullable=True, comment='计价方式 1-包车 2-按台 3-按公里 4-面议'),
        sa.Column('price_include_tax', sa.SmallInteger(), server_default='0', nullable=False, comment='是否含税 0-否 1-是'),
        sa.Column('accept_quantity', sa.Integer(), nullable=True, comment='可承接量'),
        sa.Column('capability_desc', sa.String(length=255), nullable=True, comment='能力描述（货源侧=可安排车型数量；运力侧=货物描述）'),
        sa.Column('available_start', sa.DateTime(), nullable=True, comment='可配合时间起'),
        sa.Column('available_end', sa.DateTime(), nullable=True, comment='可配合时间止'),
        sa.Column('ref_post_id', sa.BigInteger(), nullable=True, comment='关联发起方自己的挂牌ID（两个大厅互引，可省一轮沟通）'),
        sa.Column('contact_name', sa.String(length=50), nullable=False, comment='发起方联系人'),
        sa.Column('contact_phone', sa.String(length=20), nullable=False, comment='发起方联系电话'),
        sa.Column('contact_unlocked', sa.SmallInteger(), server_default='0', nullable=False, comment='联系方式是否已双向解锁 0-否 1-是'),
        sa.Column('unlocked_at', sa.DateTime(), nullable=True, comment='解锁时间'),
        sa.Column('message', sa.String(length=500), nullable=True, comment='首次附言（需过敏感内容拦截）'),
        sa.Column('last_message_at', sa.DateTime(), nullable=True, comment='最后留言时间'),
        sa.Column('unread_owner', sa.Integer(), server_default='0', nullable=False, comment='挂牌方未读留言数'),
        sa.Column('unread_initiator', sa.Integer(), server_default='0', nullable=False, comment='发起方未读留言数'),
        sa.Column('responded_at', sa.DateTime(), nullable=True, comment='响应时间（用于响应速度统计）'),
        sa.Column('declined_at', sa.DateTime(), nullable=True, comment='婉拒时间'),
        sa.Column('decline_reason', sa.SmallInteger(), nullable=True, comment='婉拒原因 1-价格不合适 2-时间对不上 3-车型不匹配 4-已选其他 9-其他'),
        sa.Column('decline_remark', sa.String(length=255), nullable=True, comment='婉拒补充说明'),
        sa.Column('withdrawn_at', sa.DateTime(), nullable=True, comment='撤回时间'),
        sa.Column('invalid_reason', sa.SmallInteger(), nullable=True, comment='失效原因 1-挂牌被他人成交 2-挂牌已下架 3-挂牌已过期'),
        sa.Column('selected_at', sa.DateTime(), nullable=True, comment='被选定时间'),
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False, comment='主键ID'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False, comment='更新时间'),
        sa.Column('is_deleted', sa.SmallInteger(), server_default='0', nullable=False, comment='是否删除 0-否 1-是'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('intent_no'),
        comment='服务平台合作意向'
        )
        op.create_index('idx_eco_intent_dup', 'sys_eco_intent', ['post_id', 'initiator_tenant_code', 'status'], unique=False)
        op.create_index('idx_eco_intent_initiator', 'sys_eco_intent', ['initiator_tenant_code', 'status', 'created_at'], unique=False)
        op.create_index('idx_eco_intent_owner', 'sys_eco_intent', ['owner_tenant_code', 'status', 'created_at'], unique=False)
        op.create_index('idx_eco_intent_post', 'sys_eco_intent', ['post_id', 'status'], unique=False)

    if "sys_eco_intent_message" not in existing:
        op.create_table('sys_eco_intent_message',
        sa.Column('intent_id', sa.BigInteger(), nullable=False, comment='意向ID（sys_eco_intent.id）'),
        sa.Column('sender_tenant_code', sa.String(length=32), nullable=False, comment='发送方租户'),
        sa.Column('sender_user_id', sa.BigInteger(), nullable=True, comment='发送人 user_id'),
        sa.Column('sender_name', sa.String(length=50), nullable=True, comment='发送人姓名'),
        sa.Column('content', sa.String(length=1000), nullable=False, comment='留言内容'),
        sa.Column('attachments', sa.JSON(), nullable=True, comment='附件URL数组'),
        sa.Column('is_read', sa.SmallInteger(), server_default='0', nullable=False, comment='对方是否已读 0-否 1-是'),
        sa.Column('read_at', sa.DateTime(), nullable=True, comment='已读时间'),
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False, comment='主键ID'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False, comment='更新时间'),
        sa.Column('is_deleted', sa.SmallInteger(), server_default='0', nullable=False, comment='是否删除 0-否 1-是'),
        sa.PrimaryKeyConstraint('id'),
        comment='服务平台洽谈留言'
        )
        op.create_index('idx_eco_msg_intent', 'sys_eco_intent_message', ['intent_id', 'created_at'], unique=False)

    if "sys_eco_post" not in existing:
        op.create_table('sys_eco_post',
        sa.Column('post_no', sa.String(length=32), nullable=False, comment='挂牌编号（对外展示）'),
        sa.Column('post_type', sa.SmallInteger(), nullable=False, comment='挂牌类型 1-货源 2-运力 3-服务(预留)'),
        sa.Column('owner_tenant_code', sa.String(length=32), nullable=False, comment='归属租户编码'),
        sa.Column('owner_tenant_name', sa.String(length=100), nullable=False, comment='归属企业全称（快照）'),
        sa.Column('owner_masked_name', sa.String(length=100), nullable=False, comment='归属企业脱敏名（快照）'),
        sa.Column('publisher_user_id', sa.BigInteger(), nullable=True, comment='发布人 user_id'),
        sa.Column('publisher_name', sa.String(length=50), nullable=True, comment='发布人姓名（快照）'),
        sa.Column('title', sa.String(length=120), nullable=False, comment='标题'),
        sa.Column('status', sa.SmallInteger(), server_default='0', nullable=False, comment='状态 0-草稿 1-待审核 2-审核未通过 3-展示中 4-已锁定 5-履约中 6-已完成 7-已下架 9-已取消'),
        sa.Column('delist_reason', sa.SmallInteger(), nullable=True, comment='下架原因 1-主动 2-到期 3-平台强制 4-源单失效 5-成交自动'),
        sa.Column('delist_remark', sa.String(length=255), nullable=True, comment='下架说明'),
        sa.Column('is_top', sa.SmallInteger(), server_default='0', nullable=False, comment='是否运营置顶 0-否 1-是'),
        sa.Column('top_until', sa.DateTime(), nullable=True, comment='置顶截止时间'),
        sa.Column('source_type', sa.SmallInteger(), server_default='3', nullable=False, comment='来源 1-系统单据 2-批量来源 3-手工'),
        sa.Column('source_id', sa.BigInteger(), nullable=True, comment='源单在租户库的主键ID'),
        sa.Column('source_snapshot_at', sa.DateTime(), nullable=True, comment='源单快照时间'),
        sa.Column('source_changed', sa.SmallInteger(), server_default='0', nullable=False, comment='源单是否已变更待更新 0-否 1-是'),
        sa.Column('source_changed_at', sa.DateTime(), nullable=True, comment='源单变更标记时间'),
        sa.Column('valid_from', sa.DateTime(), nullable=False, comment='生效时间'),
        sa.Column('valid_until', sa.DateTime(), nullable=False, comment='失效时间'),
        sa.Column('from_province', sa.String(length=50), nullable=False, comment='出发地省'),
        sa.Column('from_city', sa.String(length=50), nullable=True, comment='出发地市'),
        sa.Column('from_district', sa.String(length=50), nullable=True, comment='出发地区县'),
        sa.Column('from_region_code', sa.BigInteger(), nullable=True, comment='出发地行政区划代码（sys_regions.code）'),
        sa.Column('from_name', sa.String(length=255), nullable=True, comment='出发地展示串'),
        sa.Column('to_province', sa.String(length=50), nullable=True, comment='主目的地省（任意流向时为空）'),
        sa.Column('to_city', sa.String(length=50), nullable=True, comment='主目的地市'),
        sa.Column('to_district', sa.String(length=50), nullable=True, comment='主目的地区县'),
        sa.Column('to_region_code', sa.BigInteger(), nullable=True, comment='主目的地行政区划代码（sys_regions.code）'),
        sa.Column('to_name', sa.String(length=255), nullable=True, comment='主目的地展示串'),
        sa.Column('any_direction', sa.SmallInteger(), server_default='0', nullable=False, comment='是否接受任意流向 0-否 1-是（仅运力）'),
        sa.Column('window_start', sa.DateTime(), nullable=False, comment='时间窗开始（装车起/可用起）'),
        sa.Column('window_end', sa.DateTime(), nullable=True, comment='时间窗结束（装车止/可用止），长期可用为空'),
        sa.Column('total_quantity', sa.Integer(), nullable=True, comment='数量（货源总台数/运力可载台数）'),
        sa.Column('quantity_unit', sa.String(length=10), server_default='台', nullable=False, comment='计量单位'),
        sa.Column('remaining_quantity', sa.Integer(), nullable=True, comment='剩余可承接量，分批时递减；为空表示不分批'),
        sa.Column('price_type', sa.SmallInteger(), server_default='4', nullable=False, comment='计价方式 1-包车 2-按台 3-按公里 4-面议'),
        sa.Column('price_amount', sa.Numeric(precision=12, scale=2), nullable=True, comment='价格，面议时为空'),
        sa.Column('price_include_tax', sa.SmallInteger(), server_default='0', nullable=False, comment='是否含税 0-否 1-是'),
        sa.Column('price_negotiable', sa.SmallInteger(), server_default='1', nullable=False, comment='价格是否可议 0-否 1-是'),
        sa.Column('cooperation_type', sa.SmallInteger(), server_default='1', nullable=False, comment='合作类型 1-单次 2-长期'),
        sa.Column('keep_listed_after_deal', sa.SmallInteger(), server_default='0', nullable=False, comment='成交后是否继续展示 0-否 1-是（长期运力挂牌）'),
        sa.Column('contact_name', sa.String(length=50), nullable=False, comment='联系人姓名'),
        sa.Column('contact_phone', sa.String(length=20), nullable=False, comment='联系人手机'),
        sa.Column('contact_backup', sa.String(length=100), nullable=True, comment='备用联系方式'),
        sa.Column('visibility_level', sa.SmallInteger(), server_default='2', nullable=False, comment='企业全称可见起始层级 1-匿名层 2-认证层'),
        sa.Column('contact_visibility', sa.SmallInteger(), server_default='3', nullable=False, comment='联系方式可见起始层级 2-认证层 3-洽谈层'),
        sa.Column('apply_block_rule', sa.SmallInteger(), server_default='1', nullable=False, comment='是否应用租户级屏蔽名单 0-否 1-是'),
        sa.Column('extra_block_tenants', sa.JSON(), nullable=True, comment='本条挂牌额外屏蔽的租户编码数组'),
        sa.Column('view_count', sa.Integer(), server_default='0', nullable=False, comment='详情浏览次数（冗余）'),
        sa.Column('viewer_count', sa.Integer(), server_default='0', nullable=False, comment='浏览企业数（去重冗余）'),
        sa.Column('intent_count', sa.Integer(), server_default='0', nullable=False, comment='有效意向数（冗余）'),
        sa.Column('deal_count', sa.Integer(), server_default='0', nullable=False, comment='成交数（冗余，分批时可大于1）'),
        sa.Column('last_active_at', sa.DateTime(), nullable=True, comment='最后活跃时间（用于热度排序）'),
        sa.Column('audit_status', sa.SmallInteger(), server_default='0', nullable=False, comment='审核状态 0-未提交 1-待审 2-通过 3-驳回 4-免审直通待抽检 5-抽检通过'),
        sa.Column('audit_at', sa.DateTime(), nullable=True, comment='审核时间'),
        sa.Column('audit_by', sa.BigInteger(), nullable=True, comment='审核人（平台 user_id）'),
        sa.Column('audit_reason', sa.String(length=255), nullable=True, comment='驳回原因（原样展示给租户）'),
        sa.Column('precheck_flags', sa.JSON(), nullable=True, comment='自动预检命中的可疑标记数组'),
        sa.Column('listed_at', sa.DateTime(), nullable=True, comment='首次上架时间'),
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False, comment='主键ID'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False, comment='更新时间'),
        sa.Column('is_deleted', sa.SmallInteger(), server_default='0', nullable=False, comment='是否删除 0-否 1-是'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('post_no'),
        comment='服务平台挂牌主表'
        )
        op.create_index('idx_eco_post_audit', 'sys_eco_post', ['audit_status', 'created_at'], unique=False)
        op.create_index('idx_eco_post_changed', 'sys_eco_post', ['source_changed', 'source_changed_at'], unique=False)
        op.create_index('idx_eco_post_expire', 'sys_eco_post', ['status', 'valid_until'], unique=False)
        op.create_index('idx_eco_post_hall_from', 'sys_eco_post', ['post_type', 'status', 'from_province', 'from_city', 'window_start'], unique=False)
        op.create_index('idx_eco_post_hall_new', 'sys_eco_post', ['post_type', 'status', 'listed_at'], unique=False)
        op.create_index('idx_eco_post_owner', 'sys_eco_post', ['owner_tenant_code', 'status', 'created_at'], unique=False)
        op.create_index('idx_eco_post_source', 'sys_eco_post', ['owner_tenant_code', 'source_type', 'source_id'], unique=False)

    if "sys_eco_post_audit" not in existing:
        op.create_table('sys_eco_post_audit',
        sa.Column('post_id', sa.BigInteger(), nullable=False, comment='挂牌ID（sys_eco_post.id）'),
        sa.Column('action', sa.SmallInteger(), nullable=False, comment='动作 1-提交 2-通过 3-驳回 4-重新提交 5-主动下架 6-到期下架 7-强制下架 8-源单失效下架 9-成交下架 10-重新上架 11-免审直通 12-抽检通过 13-抽检不通过 14-编辑'),
        sa.Column('from_status', sa.SmallInteger(), nullable=True, comment='变更前状态'),
        sa.Column('to_status', sa.SmallInteger(), nullable=True, comment='变更后状态'),
        sa.Column('operator_type', sa.SmallInteger(), nullable=False, comment='操作人类型 1-租户用户 2-平台运营 3-系统'),
        sa.Column('operator_id', sa.BigInteger(), nullable=True, comment='操作人ID（系统操作时为空）'),
        sa.Column('operator_name', sa.String(length=50), nullable=True, comment='操作人姓名'),
        sa.Column('operator_tenant_code', sa.String(length=32), nullable=True, comment='操作人所属租户（运营操作时为空）'),
        sa.Column('reason_code', sa.SmallInteger(), nullable=True, comment='原因编码（驳回原因/下架原因）'),
        sa.Column('reason', sa.String(length=500), nullable=True, comment='原因说明'),
        sa.Column('changed_fields', sa.JSON(), nullable=True, comment='编辑动作时记录变更字段名与新旧值'),
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False, comment='主键ID'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False, comment='更新时间'),
        sa.Column('is_deleted', sa.SmallInteger(), server_default='0', nullable=False, comment='是否删除 0-否 1-是'),
        sa.PrimaryKeyConstraint('id'),
        comment='服务平台挂牌流转审计'
        )
        op.create_index('idx_eco_post_audit_op', 'sys_eco_post_audit', ['operator_type', 'created_at'], unique=False)
        op.create_index('idx_eco_post_audit_post', 'sys_eco_post_audit', ['post_id', 'created_at'], unique=False)

    if "sys_eco_post_dest" not in existing:
        op.create_table('sys_eco_post_dest',
        sa.Column('post_id', sa.BigInteger(), nullable=False, comment='挂牌ID（sys_eco_post.id）'),
        sa.Column('post_type', sa.SmallInteger(), nullable=False, comment='挂牌类型（冗余，便于按大厅统计）'),
        sa.Column('province', sa.String(length=50), nullable=False, comment='目的地省'),
        sa.Column('city', sa.String(length=50), nullable=True, comment='目的地市，为空表示整省'),
        sa.Column('region_code', sa.BigInteger(), nullable=True, comment='行政区划代码（sys_regions.code）'),
        sa.Column('sort_order', sa.Integer(), server_default='0', nullable=False, comment='顺序，0 为主目的地'),
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False, comment='主键ID'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False, comment='更新时间'),
        sa.Column('is_deleted', sa.SmallInteger(), server_default='0', nullable=False, comment='是否删除 0-否 1-是'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('post_id', 'province', 'city', name='uk_eco_dest'),
        comment='服务平台挂牌目的地/期望流向'
        )
        op.create_index('idx_eco_dest_lookup', 'sys_eco_post_dest', ['province', 'city', 'post_id'], unique=False)

    if "sys_eco_post_view" not in existing:
        op.create_table('sys_eco_post_view',
        sa.Column('post_id', sa.BigInteger(), nullable=False, comment='挂牌ID（sys_eco_post.id）'),
        sa.Column('owner_tenant_code', sa.String(length=32), nullable=False, comment='挂牌归属租户（冗余，发布方查询用）'),
        sa.Column('viewer_tenant_code', sa.String(length=32), nullable=False, comment='查看方租户'),
        sa.Column('viewer_province', sa.String(length=50), nullable=True, comment='查看方所在省（聚合展示用，不暴露具体企业）'),
        sa.Column('viewer_city', sa.String(length=50), nullable=True, comment='查看方所在市'),
        sa.Column('view_date', sa.Date(), nullable=False, comment='统计日期'),
        sa.Column('view_count', sa.Integer(), server_default='1', nullable=False, comment='当日浏览次数'),
        sa.Column('first_viewed_at', sa.DateTime(), nullable=True, comment='首次浏览时间'),
        sa.Column('last_viewed_at', sa.DateTime(), nullable=True, comment='最后浏览时间'),
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False, comment='主键ID'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False, comment='更新时间'),
        sa.Column('is_deleted', sa.SmallInteger(), server_default='0', nullable=False, comment='是否删除 0-否 1-是'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('post_id', 'viewer_tenant_code', 'view_date', name='uk_eco_view'),
        comment='服务平台挂牌浏览统计'
        )
        op.create_index('idx_eco_view_owner', 'sys_eco_post_view', ['owner_tenant_code', 'view_date'], unique=False)
        op.create_index('idx_eco_view_post', 'sys_eco_post_view', ['post_id', 'view_date'], unique=False)

    if "sys_eco_report" not in existing:
        op.create_table('sys_eco_report',
        sa.Column('report_no', sa.String(length=32), nullable=False, comment='举报编号'),
        sa.Column('target_type', sa.SmallInteger(), nullable=False, comment='举报对象 1-挂牌 2-成交 3-企业'),
        sa.Column('post_id', sa.BigInteger(), nullable=True, comment='关联挂牌ID'),
        sa.Column('deal_id', sa.BigInteger(), nullable=True, comment='关联成交单ID'),
        sa.Column('reported_tenant_code', sa.String(length=32), nullable=False, comment='被举报方租户'),
        sa.Column('reporter_tenant_code', sa.String(length=32), nullable=False, comment='举报方租户'),
        sa.Column('reporter_user_id', sa.BigInteger(), nullable=True, comment='举报人 user_id'),
        sa.Column('reporter_name', sa.String(length=50), nullable=True, comment='举报人姓名'),
        sa.Column('report_type', sa.SmallInteger(), nullable=False, comment='类型 1-信息虚假 2-联系不上 3-恶意压价 4-骗取信息 5-爽约 6-违法违规 9-其他'),
        sa.Column('content', sa.String(length=1000), nullable=False, comment='举报说明'),
        sa.Column('attachments', sa.JSON(), nullable=True, comment='凭证附件URL数组'),
        sa.Column('status', sa.SmallInteger(), server_default='0', nullable=False, comment='状态 0-待处理 1-处理中 2-成立 3-不成立 4-证据不足'),
        sa.Column('handle_by', sa.BigInteger(), nullable=True, comment='处理人（平台 user_id）'),
        sa.Column('handle_at', sa.DateTime(), nullable=True, comment='处理时间'),
        sa.Column('handle_result', sa.String(length=500), nullable=True, comment='处理结论'),
        sa.Column('handle_action', sa.SmallInteger(), nullable=True, comment='处置动作 1-无 2-强制下架 3-警告 4-限制权限 5-关闭大厅能力'),
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False, comment='主键ID'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False, comment='更新时间'),
        sa.Column('is_deleted', sa.SmallInteger(), server_default='0', nullable=False, comment='是否删除 0-否 1-是'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('report_no'),
        comment='服务平台违规举报'
        )
        op.create_index('idx_eco_report_reported', 'sys_eco_report', ['reported_tenant_code', 'status'], unique=False)
        op.create_index('idx_eco_report_reporter', 'sys_eco_report', ['reporter_tenant_code', 'status'], unique=False)
        op.create_index('idx_eco_report_status', 'sys_eco_report', ['status', 'created_at'], unique=False)

    if "sys_eco_subscription" not in existing:
        op.create_table('sys_eco_subscription',
        sa.Column('tenant_code', sa.String(length=32), nullable=False, comment='租户编码'),
        sa.Column('user_id', sa.BigInteger(), nullable=True, comment='创建人 user_id'),
        sa.Column('name', sa.String(length=50), nullable=False, comment='订阅名称'),
        sa.Column('post_type', sa.SmallInteger(), nullable=False, comment='订阅类型 1-货源 2-运力'),
        sa.Column('from_provinces', sa.JSON(), nullable=True, comment='出发地省数组'),
        sa.Column('from_cities', sa.JSON(), nullable=True, comment='出发地市数组'),
        sa.Column('to_provinces', sa.JSON(), nullable=True, comment='目的地省数组'),
        sa.Column('to_cities', sa.JSON(), nullable=True, comment='目的地市数组'),
        sa.Column('filter_json', sa.JSON(), nullable=True, comment='其余筛选条件原样保存'),
        sa.Column('notify_channel', sa.SmallInteger(), server_default='1', nullable=False, comment='通知渠道 1-待办 2-待办+短信'),
        sa.Column('enabled', sa.SmallInteger(), server_default='1', nullable=False, comment='是否启用 0-否 1-是'),
        sa.Column('last_notified_at', sa.DateTime(), nullable=True, comment='最后通知时间'),
        sa.Column('last_matched_post_id', sa.BigInteger(), nullable=True, comment='最后命中的挂牌ID（增量扫描游标）'),
        sa.Column('matched_count', sa.Integer(), server_default='0', nullable=False, comment='累计命中数'),
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False, comment='主键ID'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False, comment='更新时间'),
        sa.Column('is_deleted', sa.SmallInteger(), server_default='0', nullable=False, comment='是否删除 0-否 1-是'),
        sa.PrimaryKeyConstraint('id'),
        comment='服务平台订阅提醒'
        )
        op.create_index('idx_eco_sub_scan', 'sys_eco_subscription', ['enabled', 'post_type'], unique=False)
        op.create_index('idx_eco_sub_tenant', 'sys_eco_subscription', ['tenant_code', 'enabled'], unique=False)

    if "sys_eco_tenant_credit" not in existing:
        op.create_table('sys_eco_tenant_credit',
        sa.Column('tenant_code', sa.String(length=32), nullable=False, comment='租户编码'),
        sa.Column('publish_count', sa.Integer(), server_default='0', nullable=False, comment='累计发布挂牌数'),
        sa.Column('listed_count', sa.Integer(), server_default='0', nullable=False, comment='累计成功上架数'),
        sa.Column('intent_sent_count', sa.Integer(), server_default='0', nullable=False, comment='累计发出意向数'),
        sa.Column('intent_received_count', sa.Integer(), server_default='0', nullable=False, comment='累计收到意向数'),
        sa.Column('intent_responded_count', sa.Integer(), server_default='0', nullable=False, comment='累计已响应意向数'),
        sa.Column('avg_respond_minutes', sa.Integer(), nullable=True, comment='平均响应时长（分钟），用于展示「通常 2 小时内回复」'),
        sa.Column('deal_count', sa.Integer(), server_default='0', nullable=False, comment='累计成交数'),
        sa.Column('deal_completed_count', sa.Integer(), server_default='0', nullable=False, comment='累计完成数'),
        sa.Column('deal_terminated_count', sa.Integer(), server_default='0', nullable=False, comment='累计终止数'),
        sa.Column('complete_rate', sa.Numeric(precision=5, scale=2), nullable=True, comment='履约完成率（%），成交数不足 5 时不对外展示'),
        sa.Column('eval_count', sa.Integer(), server_default='0', nullable=False, comment='收到评价数'),
        sa.Column('eval_score_sum', sa.Integer(), server_default='0', nullable=False, comment='评分累计和（支持原子递增）'),
        sa.Column('avg_score', sa.Numeric(precision=3, scale=2), nullable=True, comment='平均评分，评价数不足 3 时不对外展示'),
        sa.Column('top_tags', sa.JSON(), nullable=True, comment='高频好评标签（前 3 个）'),
        sa.Column('force_delist_count', sa.Integer(), server_default='0', nullable=False, comment='被强制下架次数'),
        sa.Column('report_valid_count', sa.Integer(), server_default='0', nullable=False, comment='被举报成立次数'),
        sa.Column('breach_count', sa.Integer(), server_default='0', nullable=False, comment='爽约次数'),
        sa.Column('last_breach_at', sa.DateTime(), nullable=True, comment='最近爽约时间'),
        sa.Column('audit_whitelist', sa.SmallInteger(), server_default='0', nullable=False, comment='是否免审白名单 0-否 1-是'),
        sa.Column('whitelist_at', sa.DateTime(), nullable=True, comment='进入白名单时间'),
        sa.Column('whitelist_by', sa.BigInteger(), nullable=True, comment='操作人（人工授予时）'),
        sa.Column('whitelist_source', sa.SmallInteger(), nullable=True, comment='来源 1-自动 2-人工'),
        sa.Column('publish_restricted_until', sa.DateTime(), nullable=True, comment='发布权限暂停至'),
        sa.Column('intent_restricted_until', sa.DateTime(), nullable=True, comment='意向权限暂停至'),
        sa.Column('last_calc_at', sa.DateTime(), nullable=True, comment='最后全量校准时间'),
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False, comment='主键ID'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False, comment='更新时间'),
        sa.Column('is_deleted', sa.SmallInteger(), server_default='0', nullable=False, comment='是否删除 0-否 1-是'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tenant_code', name='uk_eco_credit_tenant'),
        comment='服务平台租户信誉统计'
        )
        op.create_index('idx_eco_credit_whitelist', 'sys_eco_tenant_credit', ['audit_whitelist'], unique=False)

    if "sys_eco_tenant_profile" not in existing:
        op.create_table('sys_eco_tenant_profile',
        sa.Column('tenant_code', sa.String(length=32), nullable=False, comment='租户编码（1:1 于 sys_tenant）'),
        sa.Column('display_name', sa.String(length=100), nullable=True, comment='对外展示企业名，默认取 tenant_name'),
        sa.Column('masked_name', sa.String(length=100), nullable=True, comment='脱敏企业名（固化存储；出现在每张大厅卡片上，实时计算太贵）'),
        sa.Column('intro', sa.String(length=1000), nullable=True, comment='企业简介'),
        sa.Column('main_routes', sa.JSON(), nullable=True, comment='主营线路 [{fromProvince,fromCity,toProvince,toCity}]'),
        sa.Column('fleet_size', sa.Integer(), nullable=True, comment='车队规模（台）'),
        sa.Column('fleet_desc', sa.String(length=255), nullable=True, comment='车队描述'),
        sa.Column('good_at_categories', sa.JSON(), nullable=True, comment='擅长货物类别数组'),
        sa.Column('contact_name', sa.String(length=50), nullable=True, comment='默认联系人'),
        sa.Column('contact_phone', sa.String(length=20), nullable=True, comment='默认联系电话'),
        sa.Column('contact_wechat', sa.String(length=50), nullable=True, comment='默认微信'),
        sa.Column('license_verified', sa.SmallInteger(), server_default='0', nullable=False, comment='营业执照是否已核验 0-否 1-是（决定可见层级 L1/L2）'),
        sa.Column('license_verified_at', sa.DateTime(), nullable=True, comment='执照核验时间'),
        sa.Column('license_verified_by', sa.BigInteger(), nullable=True, comment='执照核验人（平台 user_id）'),
        sa.Column('transport_license_no', sa.String(length=100), nullable=True, comment='道路运输经营许可证号'),
        sa.Column('transport_license_file', sa.String(length=255), nullable=True, comment='许可证附件URL'),
        sa.Column('transport_license_verified', sa.SmallInteger(), server_default='0', nullable=False, comment='许可证是否已核验 0-否 1-是'),
        sa.Column('transport_license_verified_at', sa.DateTime(), nullable=True, comment='许可证核验时间'),
        sa.Column('realname_verified', sa.SmallInteger(), server_default='0', nullable=False, comment='是否实名（注册手机号已验证）0-否 1-是'),
        sa.Column('default_visibility_level', sa.SmallInteger(), server_default='2', nullable=False, comment='默认企业名可见层级'),
        sa.Column('default_contact_visibility', sa.SmallInteger(), server_default='3', nullable=False, comment='默认联系方式可见层级'),
        sa.Column('default_valid_days', sa.SmallInteger(), server_default='7', nullable=False, comment='默认展示天数'),
        sa.Column('hall_enabled', sa.SmallInteger(), server_default='1', nullable=False, comment='大厅能力是否开启 0-关闭 1-开启（运营可关停违规租户）'),
        sa.Column('disabled_reason', sa.String(length=255), nullable=True, comment='关闭原因'),
        sa.Column('disabled_until', sa.DateTime(), nullable=True, comment='关闭截止时间'),
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False, comment='主键ID'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False, comment='更新时间'),
        sa.Column('is_deleted', sa.SmallInteger(), server_default='0', nullable=False, comment='是否删除 0-否 1-是'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tenant_code', name='uk_eco_profile_tenant'),
        comment='服务平台企业名片'
        )
        op.create_index('idx_eco_profile_verified', 'sys_eco_tenant_profile', ['license_verified', 'hall_enabled'], unique=False)


def downgrade() -> None:
    bind = op.get_bind()
    existing = set(sa.inspect(bind).get_table_names())

    # 无外键约束，逆序删除即可
    if "sys_eco_tenant_profile" in existing:
        op.drop_table("sys_eco_tenant_profile")
    if "sys_eco_tenant_credit" in existing:
        op.drop_table("sys_eco_tenant_credit")
    if "sys_eco_subscription" in existing:
        op.drop_table("sys_eco_subscription")
    if "sys_eco_report" in existing:
        op.drop_table("sys_eco_report")
    if "sys_eco_post_view" in existing:
        op.drop_table("sys_eco_post_view")
    if "sys_eco_post_dest" in existing:
        op.drop_table("sys_eco_post_dest")
    if "sys_eco_post_audit" in existing:
        op.drop_table("sys_eco_post_audit")
    if "sys_eco_post" in existing:
        op.drop_table("sys_eco_post")
    if "sys_eco_intent_message" in existing:
        op.drop_table("sys_eco_intent_message")
    if "sys_eco_intent" in existing:
        op.drop_table("sys_eco_intent")
    if "sys_eco_evaluation" in existing:
        op.drop_table("sys_eco_evaluation")
    if "sys_eco_deal_milestone" in existing:
        op.drop_table("sys_eco_deal_milestone")
    if "sys_eco_deal" in existing:
        op.drop_table("sys_eco_deal")
    if "sys_eco_cargo_post" in existing:
        op.drop_table("sys_eco_cargo_post")
    if "sys_eco_capacity_post" in existing:
        op.drop_table("sys_eco_capacity_post")
    if "sys_eco_block_rule" in existing:
        op.drop_table("sys_eco_block_rule")
