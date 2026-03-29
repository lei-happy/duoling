from app.modules.console.services.auth.auth_service import AuthService
from app.modules.console.services.tenant.tenant_service import TenantService
from app.modules.console.services.system.user_service import UserService
from app.modules.console.services.system.menu_service import MenuService
from app.modules.console.services.system.role_service import RoleService
from app.modules.console.services.product.product_version_service import ProductVersionService

__all__ = [
    "AuthService",
    "TenantService",
    "UserService",
    "MenuService",
    "RoleService",
    "ProductVersionService",
]
