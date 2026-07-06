"""任务单域共享常量

集中维护 ``biz_task`` 相关的业务码，避免 carrier_type 等在 schema / service
内散落硬编码。值与 ``models/task/task.py`` 的列注释保持一致。
"""


class CarrierType:
    """承运类型（``task.carrier_type``）"""

    SELF = 1      # 自有车
    CARRIER = 2   # 承运商
    SOCIAL = 3    # 社会运力

    ALL = (SELF, CARRIER, SOCIAL)
