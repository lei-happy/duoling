"""服务平台（生态）域共享常量

集中维护 ``sys_eco_*`` 与 ``biz_eco_post_ref`` 的业务码，避免状态值在
model / schema / service 内散落硬编码。取值与各模型的列注释、
``doc/02.需求文档/02.企业端/13.服务平台/07.数据库设计.md`` §5 状态字典保持一致。

修改此处任何取值时，必须同步更新：
  1. 对应模型的列注释
  2. 07.数据库设计.md §5
  3. 前端 frontend/client/src/config/ecosystem/enums.ts
"""


class PostType:
    """挂牌类型（``sys_eco_post.post_type``）"""

    CARGO = 1       # 货源
    CAPACITY = 2    # 运力
    SERVICE = 3     # 服务（预留，本期不做）

    ALL = (CARGO, CAPACITY)

    HALL_SLUGS = {"cargo": CARGO, "capacity": CAPACITY}


class PostStatus:
    """挂牌状态（``sys_eco_post.status``）"""

    DRAFT = 0           # 草稿
    AUDITING = 1        # 待审核
    REJECTED = 2        # 审核未通过
    LISTED = 3          # 展示中
    LOCKED = 4          # 已锁定（已选定合作方，等待确认）
    FULFILLING = 5      # 履约中
    FINISHED = 6        # 已完成
    DELISTED = 7        # 已下架
    CANCELLED = 9       # 已取消

    # 大厅可见的状态：只有展示中的挂牌对外公开
    VISIBLE_IN_HALL = (LISTED,)
    # 非终态：占用「同一源单只能有一条挂牌」的名额
    OCCUPYING = (DRAFT, AUDITING, REJECTED, LISTED, LOCKED, FULFILLING)
    # 终态：不再流转
    TERMINAL = (FINISHED, DELISTED, CANCELLED)
    # 允许发布方编辑。
    # 含「已下架」是刻意的：下架后往往正是要改内容（源单变了、被运营驳回过），
    # 不让改就只能重新发一条，历史与审核记录全断。
    # 不含「待审核」是为了避开「审核员正在看、用户同时在改」的竞态——
    # 用户想立即改可以先停止展示，改完再重新上架。
    EDITABLE = (DRAFT, REJECTED, LISTED, DELISTED)


class DelistReason:
    """下架原因（``sys_eco_post.delist_reason``）"""

    BY_OWNER = 1        # 发布方主动停止展示
    EXPIRED = 2         # 有效期到期自动下架
    FORCED = 3          # 平台强制下架（违规）
    SOURCE_INVALID = 4  # 源单已变更或取消
    DEALT = 5           # 已达成合作自动下架


class AuditStatus:
    """审核状态（``sys_eco_post.audit_status``）"""

    NOT_SUBMITTED = 0   # 未提交
    PENDING = 1         # 待审
    APPROVED = 2        # 审核通过
    REJECTED = 3        # 审核驳回
    WHITELIST_PASS = 4  # 免审直通，待抽检
    SPOT_CHECKED = 5    # 抽检通过

    # 视为「已过审」的状态
    PASSED = (APPROVED, WHITELIST_PASS, SPOT_CHECKED)


class PostAuditAction:
    """挂牌流转动作（``sys_eco_post_audit.action``）"""

    SUBMIT = 1              # 提交审核
    APPROVE = 2             # 审核通过
    REJECT = 3              # 审核驳回
    RESUBMIT = 4            # 修改后重新提交
    DELIST_BY_OWNER = 5     # 主动下架
    DELIST_EXPIRED = 6      # 到期自动下架
    DELIST_FORCED = 7       # 平台强制下架
    DELIST_SOURCE = 8       # 源单失效下架
    DELIST_DEALT = 9        # 成交自动下架
    RELIST = 10             # 重新上架
    WHITELIST_PASS = 11     # 免审直通上架
    SPOT_CHECK_PASS = 12    # 抽检通过
    SPOT_CHECK_FAIL = 13    # 抽检不通过
    EDIT = 14               # 编辑挂牌
    EXTEND = 15             # 延长展示天数


class PostRejectReason:
    """驳回 / 强制下架原因（``sys_eco_post_audit.reason_code``）

    取值即 04.运营审核与风控设计.md §2.5 的预置选项。驳回必须选一个原因，
    是因为「原因编码」才能做审核质量统计（哪类问题最多、该去优化哪条预检规则），
    自由文本统计不出来。
    """

    INCOMPLETE = 1          # 信息不完整
    UNTRUE = 2              # 信息不真实
    CONTACT_VIOLATION = 3   # 联系方式违规
    CARGO_NOT_SUPPORTED = 4  # 货物类别不支持
    PRICE_ABNORMAL = 5      # 价格异常
    DUPLICATE = 6           # 疑似重复发布
    ILLEGAL = 7             # 违法违规内容
    OTHER = 9               # 其他

    ALL = (
        INCOMPLETE, UNTRUE, CONTACT_VIOLATION, CARGO_NOT_SUPPORTED,
        PRICE_ABNORMAL, DUPLICATE, ILLEGAL, OTHER,
    )


# 驳回原因的中文名。运营后台下拉与租户端展示共用一份，避免两端各写一套对不上
REJECT_REASON_LABELS = {
    PostRejectReason.INCOMPLETE: "信息不完整",
    PostRejectReason.UNTRUE: "信息不真实",
    PostRejectReason.CONTACT_VIOLATION: "联系方式违规",
    PostRejectReason.CARGO_NOT_SUPPORTED: "货物类别不支持",
    PostRejectReason.PRICE_ABNORMAL: "价格异常",
    PostRejectReason.DUPLICATE: "疑似重复发布",
    PostRejectReason.ILLEGAL: "违法违规内容",
    PostRejectReason.OTHER: "其他",
}


class OperatorType:
    """操作人类型（``sys_eco_post_audit.operator_type``）"""

    TENANT_USER = 1     # 租户用户
    PLATFORM_OPS = 2    # 平台运营
    SYSTEM = 3          # 系统自动


class SourceType:
    """挂牌来源（``sys_eco_post.source_type`` / ``biz_eco_post_ref.source_type``）

    注意：``sys_eco_post.source_type`` 只区分粗粒度来源（系统单据 / 批量 / 手工），
    而 ``biz_eco_post_ref.source_type`` 精确到具体单据类型。两者语义不同，
    不要互相赋值。
    """

    # sys_eco_post.source_type
    SYSTEM_DOC = 1      # 系统单据（任务单 / 运力档案）
    BATCH = 2           # 批量来源
    MANUAL = 3          # 手工录入

    # biz_eco_post_ref.source_type
    REF_TASK = 1        # 任务单 biz_task
    REF_WAYBILL = 2     # 运输计划 biz_waybill（二期）
    REF_CAPACITY = 3    # 运力档案 biz_capacity
    REF_MANUAL = 4      # 手工发布（无源单）


class VisibilityLevel:
    """信息可见层级

    ``sys_eco_post.visibility_level`` 取 ANONYMOUS / CERTIFIED；
    ``sys_eco_post.contact_visibility`` 取 CERTIFIED / NEGOTIATING。
    完整字段可见性矩阵见 08.接口契约.md §2。
    """

    ANONYMOUS = 1       # L1 匿名层：已登录但未完成企业认证
    CERTIFIED = 2       # L2 认证层：已完成营业执照核验
    NEGOTIATING = 3     # L3 洽谈层：与该挂牌存在洽谈中及以后的意向
    DEALT = 4           # L4 成交层：与该挂牌存在成交单


class CooperationType:
    """合作类型（``sys_eco_post.cooperation_type``）"""

    ONCE = 1        # 单次
    LONG_TERM = 2   # 长期


class PriceType:
    """计价方式（挂牌 / 意向 / 成交共用）"""

    PACKAGE = 1       # 包车
    PER_UNIT = 2      # 按台
    PER_KM = 3        # 按公里
    NEGOTIABLE = 4    # 面议

    ALL = (PACKAGE, PER_UNIT, PER_KM, NEGOTIABLE)


class SettleType:
    """结算方式"""

    CASH = 1      # 现结
    MONTHLY = 2   # 月结
    PREPAY = 3    # 预付


class CargoCategory:
    """货物类别（``sys_eco_cargo_post.cargo_category``）"""

    VEHICLE = 1   # 商品车
    GENERAL = 2   # 普货
    OTHER = 3     # 其他


# 下拉选项的中文名。大厅筛选、发布弹层、以及后续小程序端共用一份：
# 同一个枚举在两处各写一套措辞，改动时必然漏掉一处，用户就会看到
# 大厅里叫「按台」、发布时叫「每台」这种对不上的说法
COOPERATION_TYPE_LABELS = {
    CooperationType.ONCE: "单次",
    CooperationType.LONG_TERM: "长期",
}

PRICE_TYPE_LABELS = {
    PriceType.PACKAGE: "包车",
    PriceType.PER_UNIT: "按台",
    PriceType.PER_KM: "按公里",
    PriceType.NEGOTIABLE: "面议",
}

SETTLE_TYPE_LABELS = {
    SettleType.CASH: "现结",
    SettleType.MONTHLY: "月结",
    SettleType.PREPAY: "预付",
}

CARGO_CATEGORY_LABELS = {
    CargoCategory.VEHICLE: "商品车",
    CargoCategory.GENERAL: "普货",
    CargoCategory.OTHER: "其他",
}


class VehicleCondition:
    """车辆状态（``sys_eco_cargo_post.vehicle_condition``）"""

    NEW = 1        # 新车
    USED = 2       # 二手车
    TEST_DRIVE = 3  # 试驾车


class PostGranularity:
    """运力挂牌粒度（``sys_eco_capacity_post.post_granularity``）"""

    SPECIFIC = 1  # 指定车辆
    FLEET = 2     # 车队打包


class IntentStatus:
    """意向状态（``sys_eco_intent.status``）"""

    PENDING = 0     # 待响应
    TALKING = 1     # 洽谈中（联系方式已双向解锁）
    SELECTED = 2    # 已选定
    DECLINED = 3    # 已婉拒
    WITHDRAWN = 4   # 已撤回
    INVALID = 5     # 已失效

    # 占用「同一租户对同一挂牌只能有一个有效意向」的名额
    ACTIVE = (PENDING, TALKING, SELECTED)
    # 联系方式已解锁的状态
    UNLOCKED = (TALKING, SELECTED)


class IntentDeclineReason:
    """婉拒原因（``sys_eco_intent.decline_reason``）"""

    PRICE = 1       # 价格不合适
    TIME = 2        # 时间对不上
    TRUCK = 3       # 车型不匹配
    CHOSE_OTHER = 4  # 已选择其他合作方
    OTHER = 9       # 其他


class IntentInvalidReason:
    """失效原因（``sys_eco_intent.invalid_reason``）"""

    DEALT_BY_OTHER = 1  # 挂牌被他人成交
    POST_DELISTED = 2   # 挂牌已下架
    POST_EXPIRED = 3    # 挂牌已过期


class DealStatus:
    """成交状态（``sys_eco_deal.status``）"""

    PENDING_CONFIRM = 0  # 待确认
    CONFIRMED = 1        # 已成交
    FULFILLING = 2       # 履约中
    COMPLETED = 3        # 已完成
    TERMINATED = 4       # 已终止

    ACTIVE = (PENDING_CONFIRM, CONFIRMED, FULFILLING)
    TERMINAL = (COMPLETED, TERMINATED)


class CarrierSide:
    """承运角色（``sys_eco_deal.carrier_side``）

    标识成交双方中谁是承运方。运力大厅是挂牌方出车，货源大厅是意向方出车。
    """

    OWNER = 1     # 挂牌方承运（运力大厅）
    PARTNER = 2   # 合作方承运（货源大厅）


class MilestoneType:
    """履约节点（``sys_eco_deal.current_milestone`` / ``sys_eco_deal_milestone.milestone_type``）"""

    NOT_STARTED = 0     # 未开始
    TRUCK_ARRANGED = 1  # 已安排车辆
    LOADED = 2          # 已装车
    IN_TRANSIT = 3      # 运输中
    DELIVERED = 4       # 已送达
    COMPLETED = 5       # 确认完成

    # 允许携带车牌与司机信息上报的节点
    ACCEPT_CARRIER_INFO = (TRUCK_ARRANGED, LOADED)


class EvaluationRole:
    """评价角色（``sys_eco_evaluation.role``）"""

    CARGO_TO_CARRIER = 1  # 货主评承运方
    CARRIER_TO_CARGO = 2  # 承运方评货主


class ReportTargetType:
    """举报对象类型（``sys_eco_report.target_type``）"""

    POST = 1     # 挂牌
    DEAL = 2     # 成交
    TENANT = 3   # 企业


class ReportType:
    """举报类型（``sys_eco_report.report_type``）"""

    FAKE_INFO = 1       # 信息虚假
    UNREACHABLE = 2     # 联系不上
    MALICIOUS_PRICE = 3  # 恶意压价
    PHISHING = 4        # 骗取信息
    BREACH = 5          # 爽约
    ILLEGAL = 6         # 违法违规
    OTHER = 9           # 其他


class ReportStatus:
    """举报处理状态（``sys_eco_report.status``）"""

    PENDING = 0         # 待处理
    HANDLING = 1        # 处理中
    VALID = 2           # 成立
    INVALID = 3         # 不成立
    NO_EVIDENCE = 4     # 证据不足


class ReportAction:
    """举报处置动作（``sys_eco_report.handle_action``）"""

    NONE = 1            # 无
    FORCE_DELIST = 2    # 强制下架
    WARN = 3            # 警告
    RESTRICT = 4        # 限制权限
    DISABLE_HALL = 5    # 关闭大厅能力


class NotifyChannel:
    """订阅通知渠道（``sys_eco_subscription.notify_channel``）"""

    TODO = 1        # 站内待办
    TODO_SMS = 2    # 待办 + 短信


class WhitelistSource:
    """免审白名单来源（``sys_eco_tenant_credit.whitelist_source``）"""

    AUTO = 1    # 系统自动授予
    MANUAL = 2  # 运营人工授予


class PostNoPrefix:
    """业务编号前缀（生成规则见 07.数据库设计.md §3.6）"""

    CARGO_POST = "HY"
    CAPACITY_POST = "YL"
    INTENT = "YX"
    DEAL = "CJ"
    REPORT = "JB"


# 信誉数据对外展示的最小样本量：样本不足时前端不展示完成率与评分，
# 改显示「新加入」标签。理由见 04.运营审核与风控设计.md §4.2 ——
# 样本不足的百分比比没有数字更有害。
MIN_SAMPLES_FOR_COMPLETE_RATE = 5
MIN_SAMPLES_FOR_AVG_SCORE = 3

# 承接方确认成交的时限（小时），超时成交自动作废、挂牌回到展示中
DEAL_CONFIRM_HOURS = 24

# 挂牌展示天数（见 02.货源大厅设计.md §8 规则 2）。
# 上限是为了逼出「过期即复核」：线路与时间越久越不可能还准确，
# 允许无限期挂着等于默认放行陈旧信息。
DEFAULT_VALID_DAYS = 7
VALID_DAYS_OPTIONS = (1, 3, 7, 15, 30)
MAX_VALID_DAYS = 30
MAX_VALID_DAYS_LONG_TERM = 90

# 源单变更后未同步的容忍时长（小时），超时自动下架
SOURCE_CHANGED_TOLERANCE_HOURS = 48

# ===== 审核（04.运营审核与风控设计.md §2）=====

# 免审直通挂牌的抽检时限（小时）。免审是「先发后审」，抽检就是那个「后审」，
# 没有时限的抽检等于没有审核
SPOT_CHECK_HOURS = 24

# 单次批量通过的上限。不设上限时一次点几千条，任一条报错整批都难定位，
# 而且长事务会把待审队列锁住
MAX_BATCH_APPROVE = 50

# 免审白名单自动准入门槛（§2.2）
WHITELIST_MIN_PUBLISH = 5       # 累计发布数
WHITELIST_MIN_DEAL = 1          # 累计完成成交数
WHITELIST_CLEAN_DAYS = 90       # 无违规、无驳回的回溯窗口（天）
WHITELIST_RECOVER_DAYS = 30     # 被移出后重新累积的干净天数
