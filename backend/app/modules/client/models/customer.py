"""
客户管理表（租户库）- 已迁移到 partner/customer.py

本文件保留仅做兼容，所有引用请改为：
    from app.modules.client.models.partner.customer import Customer
"""

# 直接复用 partner 下的模型，避免同一张表注册两个 ORM 类
from app.modules.client.models.partner.customer import Customer  # noqa: F401
