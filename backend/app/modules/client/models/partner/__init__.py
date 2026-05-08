"""
合作伙伴 ORM 模型（租户库）
- 客户：托运方/收货方
- 承运商：下游运输合作伙伴 + 结算账户 + 邀请流水
"""

from app.modules.client.models.partner.customer import Customer
from app.modules.client.models.partner.carrier import Carrier
from app.modules.client.models.partner.carrier_settlement import CarrierSettlement
from app.modules.client.models.partner.carrier_invitation import CarrierInvitation

__all__ = [
    "Customer",
    "Carrier",
    "CarrierSettlement",
    "CarrierInvitation",
]
