"""审批中心 - 常量枚举

集中维护实例 / 节点 / 任务 / 动作 / 审批人类型 / 签署方式 等枚举，
避免散落在各处的魔法数字。
"""

# ---- 实例状态 ----
INSTANCE_RUNNING = 0   # 审批中
INSTANCE_APPROVED = 1  # 已通过
INSTANCE_REJECTED = 2  # 已拒绝
INSTANCE_WITHDRAWN = 3  # 已撤回

INSTANCE_FINAL_STATES = {INSTANCE_APPROVED, INSTANCE_REJECTED, INSTANCE_WITHDRAWN}

# ---- 实例节点状态 ----
NODE_NOT_STARTED = 0
NODE_RUNNING = 1
NODE_PASSED = 2
NODE_REJECTED = 3
NODE_SKIPPED = 4

# ---- 任务状态 ----
TASK_PENDING = 0
TASK_AGREED = 1
TASK_REJECTED = 2
TASK_TRANSFERRED = 3  # 已转审失效
TASK_SKIPPED = 4

# ---- 节点类型 ----
NODE_TYPE_APPROVAL = 1
NODE_TYPE_CC = 2

# ---- 审批人类型 ----
APPROVER_USER = 1        # 指定成员
APPROVER_ROLE = 2        # 指定角色
APPROVER_DEPT = 3        # 指定部门（成员）
APPROVER_DEPT_LEADER = 4  # 部门负责人
APPROVER_SUPERVISOR = 5   # 逐级上级主管
APPROVER_INITIATOR_PICK = 6  # 发起人自选
APPROVER_INITIATOR = 7    # 发起人本人

# ---- 签署方式 ----
SIGN_ANY = 1          # 或签
SIGN_ALL = 2          # 会签
SIGN_SEQUENTIAL = 3   # 依次会签

# ---- 空审批人策略 ----
EMPTY_AUTO_PASS = 1   # 自动通过
EMPTY_TO_ADMIN = 2    # 转交管理员（暂等价 auto_pass，记录提示）
EMPTY_RAISE = 3       # 报错阻断

# ---- 动作类型（审批记录 action） ----
ACTION_SUBMIT = 1
ACTION_AGREE = 2
ACTION_REJECT = 3
ACTION_WITHDRAW = 4
ACTION_TRANSFER = 5
ACTION_ADDSIGN_BEFORE = 6
ACTION_ADDSIGN_AFTER = 7
ACTION_CC = 8
ACTION_AUTO_PASS = 9
ACTION_SKIP = 10

# ---- 任务来源 ----
SOURCE_NORMAL = 1
SOURCE_TRANSFER = 2
SOURCE_ADDSIGN_BEFORE = 3
SOURCE_ADDSIGN_AFTER = 4

INSTANCE_STATUS_LABELS = {
    INSTANCE_RUNNING: "审批中",
    INSTANCE_APPROVED: "已通过",
    INSTANCE_REJECTED: "已拒绝",
    INSTANCE_WITHDRAWN: "已撤回",
}
