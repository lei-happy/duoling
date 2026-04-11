"""
客户管理 Schemas - 已迁移到 partner/customer.py

本文件保留仅做兼容，所有引用请改为：
    from app.modules.client.schemas.partner.customer import ...
"""

from app.modules.client.schemas.partner.customer import (  # noqa: F401
    CustomerCreate,
    CustomerUpdate,
    CustomerOut,
)
