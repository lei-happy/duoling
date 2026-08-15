"""能源中心元数据"""

from fastapi import APIRouter, Depends

from app.common.response import success
from app.core.dependencies import get_current_user
from app.modules.client.services.energy.constants import (
    ACCOUNT_TYPES,
    CARD_STATUSES,
    ENERGY_TYPES,
    SOURCE_CHANNELS,
    SUPPLIER_TYPES,
    TXN_TYPES,
)
from app.modules.client.services.energy.connectors import list_connectors

router = APIRouter()


@router.get("/meta")
async def meta(_=Depends(get_current_user)):
    return success(data={
        "energyTypes": ENERGY_TYPES,
        "supplierTypes": SUPPLIER_TYPES,
        "accountTypes": ACCOUNT_TYPES,
        "cardStatuses": CARD_STATUSES,
        "txnTypes": TXN_TYPES,
        "sourceChannels": SOURCE_CHANNELS,
        "connectors": [
            {"code": s.code, "name": s.name, "syncModes": s.sync_modes}
            for s in list_connectors()
        ],
    })
