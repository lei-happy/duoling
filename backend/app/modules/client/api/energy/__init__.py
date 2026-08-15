from app.modules.client.api.energy.account import router as account_router
from app.modules.client.api.energy.analysis import router as analysis_router
from app.modules.client.api.energy.card import router as card_router
from app.modules.client.api.energy.connector import router as connector_router
from app.modules.client.api.energy.consumption import router as consumption_router
from app.modules.client.api.energy.exception import router as exception_router
from app.modules.client.api.energy.meta import router as meta_router
from app.modules.client.api.energy.recharge import router as recharge_router
from app.modules.client.api.energy.recon import router as recon_router
from app.modules.client.api.energy.setting import (
    product_router,
    profile_router,
    rule_router,
)
from app.modules.client.api.energy.supplier import (
    station_router,
    supplier_router,
)

__all__ = [
    "account_router",
    "analysis_router",
    "card_router",
    "connector_router",
    "consumption_router",
    "exception_router",
    "meta_router",
    "product_router",
    "profile_router",
    "recharge_router",
    "recon_router",
    "rule_router",
    "station_router",
    "supplier_router",
]
