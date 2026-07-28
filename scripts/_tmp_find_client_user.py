# -*- coding: utf-8 -*-
import asyncio
from sqlalchemy import text
from app.core.database import db_manager


async def main():
    await db_manager.init_platform_db()
    async with db_manager.get_platform_session() as s:
        rows = (
            await s.execute(
                text(
                    "SELECT id, phone, username, status FROM sys_user "
                    "WHERE phone LIKE '139%' OR phone LIKE '138%' LIMIT 30"
                )
            )
        ).fetchall()
        print("users:")
        for r in rows:
            print(r)
        tenants = (
            await s.execute(
                text("SELECT tenant_code, name, status FROM sys_tenant LIMIT 15")
            )
        ).fetchall()
        print("tenants:")
        for t in tenants:
            print(t)


if __name__ == "__main__":
    asyncio.run(main())
