"""模型注册集中点

所有 ORM 类必须通过 `import_all_models()` 触发一次性导入，
否则 PlatformBase / TenantBase 的 metadata 是不完整的（snapshot / autogen 会漏表）。

这是单点入口：以后如果新增模块，只需在对应 modules/__init__.py 里 export，
此处 `import app.modules.xxx.models` 会一并加载。
"""

from __future__ import annotations


def import_all_models() -> None:
    # 平台库
    import app.modules.console.models  # noqa: F401
    # 租户库
    import app.modules.client.models  # noqa: F401
    # AI（同时含 platform/* 与 tenant/*）
    try:
        import app.modules.ai.models.platform  # noqa: F401
        import app.modules.ai.models.tenant  # noqa: F401
    except Exception:
        pass
    # 开放接口
    try:
        import app.modules.open.models  # noqa: F401
    except Exception:
        pass
    # 开放平台（含 platform/* 与 tenant/*）
    try:
        import app.modules.open_platform.models  # noqa: F401
    except Exception:
        pass
