"""
五个数据集的导出器

每个 exporter 实现 export(client) -> list/dict，输出已经是「写盘格式」，
键名是 snake_case 与数据库字段对齐（API 返回 camelCase 时会在导出器中翻译）。
"""

from .client_menu import export as export_client_menu
from .platform_menu import export as export_platform_menu
from .product_version import export as export_product_version
from .product_feature import export as export_product_feature
from .version_feature import export as export_version_feature

# 名字 → (导出函数, 输出文件名) 的注册表，pull/verify 共用
EXPORTERS = {
    "client_menu": (export_client_menu, "client_menu.json"),
    "platform_menu": (export_platform_menu, "platform_menu.json"),
    "product_version": (export_product_version, "product_version.json"),
    "product_feature": (export_product_feature, "product_feature.json"),
    "version_feature": (export_version_feature, "version_feature.json"),
}

__all__ = [
    "EXPORTERS",
    "export_client_menu",
    "export_platform_menu",
    "export_product_version",
    "export_product_feature",
    "export_version_feature",
]
