from app.modules.console.schemas.auth.auth import LoginRequest, LoginResponse
from app.modules.console.schemas.tenant.tenant import (
    TenantCreate, TenantUpdate, TenantOut, TenantListOut,
)
from app.modules.console.schemas.system.user import (
    UserCreate, UserUpdate, UserOut,
)
from app.modules.console.schemas.system.menu import (
    MenuCreate, MenuUpdate, MenuOut,
)
from app.modules.console.schemas.system.role import (
    RoleCreate, RoleUpdate, RoleOut, RoleMenuUpdate,
)
from app.modules.console.schemas.product.product_version import (
    ProductVersionCreate, ProductVersionUpdate, ProductVersionOut,
)
from app.modules.console.schemas.changelog.changelog import (
    ChangelogCreate, ChangelogUpdate, ChangelogOut,
)

__all__ = [
    "LoginRequest", "LoginResponse",
    "TenantCreate", "TenantUpdate", "TenantOut", "TenantListOut",
    "UserCreate", "UserUpdate", "UserOut",
    "MenuCreate", "MenuUpdate", "MenuOut",
    "RoleCreate", "RoleUpdate", "RoleOut", "RoleMenuUpdate",
    "ProductVersionCreate", "ProductVersionUpdate", "ProductVersionOut",
    "ChangelogCreate", "ChangelogUpdate", "ChangelogOut",
]
