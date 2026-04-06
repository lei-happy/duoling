"""官网自助注册策略相关配置键与默认值"""

KEY_OPEN_REGISTER_DEFAULT_VERSION_CODE = "open_register_default_version_code"
KEY_OPEN_REGISTER_TRIAL_DAYS = "open_register_trial_days"

DEFAULT_VERSION_CODE = "basic"
DEFAULT_TRIAL_DAYS = 0

# 自助注册自动开通的授权类型（与数据字典 grant_type 对齐时可扩展）
GRANT_TYPE_SELF_REGISTER_TRIAL = "trial"
