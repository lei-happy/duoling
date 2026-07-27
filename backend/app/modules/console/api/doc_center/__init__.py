from fastapi import APIRouter

from app.modules.console.api.doc_center.doc_center import router as docs_router
from app.modules.console.api.doc_center.design_module import (
    router as design_module_router,
)
from app.modules.console.api.doc_center.prototype import (
    router as prototype_router,
)

router = APIRouter()
router.include_router(docs_router)
router.include_router(
    design_module_router,
    prefix="/design-modules",
    tags=["管理后台-设计对接"],
)
router.include_router(
    prototype_router,
    prefix="/prototypes",
    tags=["管理后台-产品原型"],
)

__all__ = ["router"]
