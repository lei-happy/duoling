"""
产品功能清单管理服务
"""

from typing import Optional, List

from sqlalchemy import select, func, update, or_
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.common.exceptions import BizException
from app.modules.console.models.product.product_feature import ProductFeature, VersionFeature
from app.modules.console.models.product.product_version import ProductVersion
from app.modules.console.models.system.menu import Menu
from app.modules.console.models.tenant.tenant import Tenant
from app.modules.console.models.tenant.tenant_product import TenantProduct
from app.modules.console.schemas.product.product_feature import (
    ProductFeatureCreate, ProductFeatureUpdate,
)


class ProductFeatureService:

    # ---- 功能清单 CRUD ----

    @staticmethod
    async def list_features(
        db: AsyncSession,
        module: Optional[str] = None,
        status: Optional[int] = None,
        keyword: Optional[str] = None,
    ) -> list:
        """全量返回 feature 列表（兼容旧调用方，例如版本-功能配置弹窗）"""
        query = select(ProductFeature).where(ProductFeature.is_deleted == 0)
        if module:
            query = query.where(ProductFeature.module == module)
        if status is not None:
            query = query.where(ProductFeature.status == status)
        if keyword:
            kw = f"%{keyword}%"
            query = query.where(
                or_(
                    ProductFeature.feature_code.like(kw),
                    ProductFeature.feature_name.like(kw),
                )
            )
        query = query.order_by(ProductFeature.sort_order, ProductFeature.id)
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def page_features(
        db: AsyncSession,
        page: int = 1,
        page_size: int = 20,
        module: Optional[str] = None,
        status: Optional[int] = None,
        keyword: Optional[str] = None,
    ) -> dict:
        """分页查询功能清单，并附带每个功能已关联的版本列表"""
        base = select(ProductFeature).where(ProductFeature.is_deleted == 0)
        if module:
            base = base.where(ProductFeature.module == module)
        if status is not None:
            base = base.where(ProductFeature.status == status)
        if keyword:
            kw = f"%{keyword}%"
            base = base.where(
                or_(
                    ProductFeature.feature_code.like(kw),
                    ProductFeature.feature_name.like(kw),
                )
            )

        count_q = select(func.count()).select_from(base.subquery())
        total = (await db.execute(count_q)).scalar() or 0

        rows_q = (
            base.order_by(ProductFeature.sort_order, ProductFeature.id)
            .offset(max(page - 1, 0) * page_size)
            .limit(page_size)
        )
        items = list((await db.execute(rows_q)).scalars().all())
        feature_ids = [f.id for f in items]

        # 一次性查询本页所有功能的版本关联，避免 N+1
        assigned_map: dict[int, list[dict]] = {fid: [] for fid in feature_ids}
        if feature_ids:
            rel_q = (
                select(
                    VersionFeature.feature_id,
                    ProductVersion.id,
                    ProductVersion.version_code,
                    ProductVersion.version_name,
                    ProductVersion.sort_order,
                )
                .join(ProductVersion, ProductVersion.id == VersionFeature.version_id)
                .where(
                    VersionFeature.feature_id.in_(feature_ids),
                    VersionFeature.is_deleted == 0,
                    VersionFeature.status == 1,
                    ProductVersion.is_deleted == 0,
                )
                .order_by(ProductVersion.sort_order, ProductVersion.id)
            )
            for fid, vid, vcode, vname, _vsort in (await db.execute(rel_q)).all():
                assigned_map.setdefault(fid, []).append(
                    {"id": vid, "code": vcode, "name": vname}
                )

        return {
            "list": items,
            "total": total,
            "page": page,
            "pageSize": page_size,
            "assignedVersionsMap": assigned_map,
        }

    @staticmethod
    async def create_feature(db: AsyncSession, data: ProductFeatureCreate) -> ProductFeature:
        existing = await db.execute(
            select(ProductFeature).where(
                ProductFeature.feature_code == data.feature_code,
                ProductFeature.is_deleted == 0,
            )
        )
        if existing.scalar_one_or_none():
            raise BizException(f"功能编码 {data.feature_code} 已存在")

        feature = ProductFeature(
            feature_code=data.feature_code,
            feature_name=data.feature_name,
            module=data.module,
            description=data.description,
            required_tables=data.required_tables,
            sort_order=data.sort_order,
        )
        db.add(feature)
        await db.flush()
        return feature

    @staticmethod
    async def update_feature(
        db: AsyncSession, feature_id: int, data: ProductFeatureUpdate
    ) -> ProductFeature:
        result = await db.execute(
            select(ProductFeature).where(
                ProductFeature.id == feature_id,
                ProductFeature.is_deleted == 0,
            )
        )
        feature = result.scalar_one_or_none()
        if not feature:
            raise BizException("功能项不存在")

        for field in ("feature_name", "module", "description", "required_tables", "sort_order", "status"):
            val = getattr(data, field, None)
            if val is not None:
                setattr(feature, field, val)

        await db.flush()
        return feature

    @staticmethod
    async def delete_feature(db: AsyncSession, feature_id: int) -> None:
        result = await db.execute(
            select(ProductFeature).where(
                ProductFeature.id == feature_id,
                ProductFeature.is_deleted == 0,
            )
        )
        feature = result.scalar_one_or_none()
        if not feature:
            raise BizException("功能项不存在")
        feature.is_deleted = 1
        await db.flush()

    # ---- 版本-功能关联 ----

    @staticmethod
    async def get_version_features(db: AsyncSession, version_id: int) -> list:
        """获取版本的功能清单"""
        result = await db.execute(
            select(VersionFeature, ProductFeature)
            .join(ProductFeature, VersionFeature.feature_id == ProductFeature.id)
            .where(
                VersionFeature.version_id == version_id,
                VersionFeature.is_deleted == 0,
                VersionFeature.status == 1,
                ProductFeature.is_deleted == 0,
            )
            .order_by(ProductFeature.sort_order)
        )
        rows = result.all()
        return [
            {
                "id": vf.id,
                "versionId": vf.version_id,
                "featureId": vf.feature_id,
                "status": vf.status,
                "featureCode": pf.feature_code,
                "featureName": pf.feature_name,
                "module": pf.module,
                "requiredTables": pf.required_tables,
            }
            for vf, pf in rows
        ]

    @staticmethod
    async def assign_features(
        db: AsyncSession, version_id: int, feature_ids: List[int]
    ) -> None:
        """
        批量设置版本的功能清单（全量替换）。

        变更说明（修复"勾选 AI 助手等远期菜单后客户端依然不显示"问题）：
        1. 关联功能的 client 菜单自动 visible=1，运营勾选即视为"该菜单允许展示"，
           覆盖菜单 seed 时打的"远期预留 visible=0"标记；
        2. 取消关联且不再被任何版本引用的 feature 对应 client 菜单回到 visible=0，
           保持"无任何版本许可时该菜单依旧隐藏"的语义一致；
        3. 自动递增所有持有该版本（且授权未删除）的租户 menu_version，触发其客户端
           侧重新拉取菜单，避免运营改完功能清单后老租户菜单不刷新的问题。
        """
        # 取出旧关联，便于做"差集"判断
        old_result = await db.execute(
            select(VersionFeature).where(
                VersionFeature.version_id == version_id,
                VersionFeature.is_deleted == 0,
            )
        )
        old_vfs = list(old_result.scalars().all())
        old_feature_ids = {vf.feature_id for vf in old_vfs}
        new_feature_ids = set(feature_ids)

        added = new_feature_ids - old_feature_ids
        removed = old_feature_ids - new_feature_ids

        for vf in old_vfs:
            vf.is_deleted = 1

        for fid in feature_ids:
            db.add(VersionFeature(
                version_id=version_id,
                feature_id=fid,
                status=1,
            ))

        await db.flush()
        logger.info(
            f"版本 {version_id} 已更新功能清单：保留 {len(new_feature_ids & old_feature_ids)}，"
            f"新增 {len(added)}，移除 {len(removed)}"
        )

        # ---- 同步联动菜单 visible ----
        try:
            await ProductFeatureService._sync_menu_visibility(
                db, added_feature_ids=added, removed_feature_ids=removed
            )
        except Exception as e:
            logger.warning(
                f"版本 {version_id} 功能联动菜单 visible 失败（不影响功能关联保存）：{e!r}"
            )

        # ---- 触发持有该版本的租户 menu_version 递增 ----
        try:
            bumped = await ProductFeatureService._bump_tenants_menu_version(
                db, version_id
            )
            if bumped:
                logger.info(
                    f"版本 {version_id} 功能清单变更：已递增 {bumped} 个租户的 menu_version"
                )
        except Exception as e:
            logger.warning(
                f"版本 {version_id} 触发租户 menu_version 递增失败（不影响功能关联保存）：{e!r}"
            )

    @staticmethod
    async def _sync_menu_visibility(
        db: AsyncSession,
        added_feature_ids: set,
        removed_feature_ids: set,
    ) -> None:
        """
        根据本次 added/removed 的 feature_id，调整对应 client 菜单的 visible。
        - added：直接将 feature_code 对应的 client 菜单 visible 置 1
        - removed：仅当该 feature_code 已不被任何启用的版本引用时，才把 visible 置 0
        platform 端菜单不受此联动影响。
        """
        affected_ids = added_feature_ids | removed_feature_ids
        if not affected_ids:
            return

        feat_rows = await db.execute(
            select(ProductFeature.id, ProductFeature.feature_code).where(
                ProductFeature.id.in_(affected_ids),
                ProductFeature.is_deleted == 0,
            )
        )
        id_to_code = {row.id: row.feature_code for row in feat_rows.all()}

        added_codes = {id_to_code[fid] for fid in added_feature_ids if fid in id_to_code}
        removed_codes = {id_to_code[fid] for fid in removed_feature_ids if fid in id_to_code}

        if added_codes:
            # 1) 自身（叶子/中间）菜单 visible 置 1
            await db.execute(
                update(Menu)
                .where(
                    Menu.feature_code.in_(added_codes),
                    Menu.app_type == "client",
                    Menu.is_deleted == 0,
                    Menu.visible == 0,
                )
                .values(visible=1)
            )
            logger.info(f"已将 client 菜单 visible 置 1，feature_code={added_codes}")

            # 2) 沿 parent_id 链路上溯，把祖先目录菜单（feature_code IS NULL/空）也放开
            #    避免「子菜单被勾选放开但父目录仍 visible=0，整棵子树孤儿化」
            await ProductFeatureService._open_ancestor_directories(db, added_codes)

        if removed_codes:
            still_used = await db.execute(
                select(ProductFeature.feature_code)
                .join(VersionFeature, VersionFeature.feature_id == ProductFeature.id)
                .where(
                    ProductFeature.feature_code.in_(removed_codes),
                    VersionFeature.is_deleted == 0,
                    VersionFeature.status == 1,
                )
                .distinct()
            )
            still_used_codes = {r for r in still_used.scalars().all()}
            truly_removed = removed_codes - still_used_codes
            if truly_removed:
                await db.execute(
                    update(Menu)
                    .where(
                        Menu.feature_code.in_(truly_removed),
                        Menu.app_type == "client",
                        Menu.is_deleted == 0,
                        Menu.visible == 1,
                    )
                    .values(visible=0)
                )
                logger.info(
                    f"已将 client 菜单 visible 置 0（feature 已无任何版本引用）"
                    f"feature_code={truly_removed}"
                )

    @staticmethod
    async def _open_ancestor_directories(
        db: AsyncSession, added_codes: set
    ) -> None:
        """
        把本次放开的 feature_code 所属菜单的所有祖先「目录菜单」visible 置 1。

        目录菜单的特征是：feature_code 为 NULL 或空字符串（如 /resource、/finance），
        它们不参与 feature 过滤，但若 visible=0 也会在前端侧边栏隐藏，从而带飞整个
        子树。这里只放开 visible=0 的祖先，不会改动用户主动设置 visible=1 的菜单。
        """
        if not added_codes:
            return

        # 找出本次受影响菜单的 parent_id 链路
        rows = await db.execute(
            select(Menu.id, Menu.parent_id).where(
                Menu.feature_code.in_(added_codes),
                Menu.app_type == "client",
                Menu.is_deleted == 0,
            )
        )
        parent_ids: set[int] = {pid for _id, pid in rows.all() if pid and pid > 0}
        ancestor_ids: set[int] = set()
        # 防御性地限制循环深度，菜单树通常不会超过 8 层
        for _ in range(8):
            if not parent_ids:
                break
            ancestor_ids.update(parent_ids)
            up = await db.execute(
                select(Menu.parent_id).where(
                    Menu.id.in_(parent_ids),
                    Menu.app_type == "client",
                    Menu.is_deleted == 0,
                )
            )
            parent_ids = {pid for pid in up.scalars().all() if pid and pid > 0}

        if not ancestor_ids:
            return

        from sqlalchemy import or_

        result = await db.execute(
            update(Menu)
            .where(
                Menu.id.in_(ancestor_ids),
                Menu.app_type == "client",
                Menu.is_deleted == 0,
                Menu.visible == 0,
                or_(Menu.feature_code.is_(None), Menu.feature_code == ""),
            )
            .values(visible=1)
        )
        affected = result.rowcount or 0
        if affected:
            logger.info(
                f"已上溯放开 {affected} 个祖先目录菜单 visible=1，"
                f"避免子菜单孤儿化（ancestor_ids={ancestor_ids}）"
            )

    @staticmethod
    async def _bump_tenants_menu_version(
        db: AsyncSession, version_id: int
    ) -> int:
        """
        把所有持有该 version_id 且未软删除的授权对应的租户 menu_version +1。
        返回受影响的租户数。
        """
        from datetime import datetime
        from sqlalchemy import or_

        now = datetime.now()
        tenant_rows = await db.execute(
            select(TenantProduct.tenant_id)
            .where(
                TenantProduct.version_id == version_id,
                TenantProduct.is_deleted == 0,
                TenantProduct.status == 1,
                or_(TenantProduct.end_time.is_(None), TenantProduct.end_time > now),
            )
            .distinct()
        )
        tenant_ids = [r for r in tenant_rows.scalars().all() if r is not None]
        if not tenant_ids:
            return 0
        await db.execute(
            update(Tenant)
            .where(Tenant.id.in_(tenant_ids))
            .values(menu_version=Tenant.menu_version + 1)
        )
        return len(tenant_ids)

    @staticmethod
    async def get_feature_codes_by_version_ids(
        db: AsyncSession, version_ids: List[int]
    ) -> List[str]:
        """根据版本ID列表获取所有 feature_code"""
        if not version_ids:
            return []
        result = await db.execute(
            select(ProductFeature.feature_code)
            .join(VersionFeature, VersionFeature.feature_id == ProductFeature.id)
            .where(
                VersionFeature.version_id.in_(version_ids),
                VersionFeature.is_deleted == 0,
                VersionFeature.status == 1,
                ProductFeature.is_deleted == 0,
                ProductFeature.status == 1,
            )
        )
        return list(set(result.scalars().all()))

    @staticmethod
    async def health_check(db: AsyncSession) -> dict:
        """
        全链路一致性体检：

        - orphanFeatureCodes：sys_menu 中引用了但 sys_product_feature 未定义/已软删的 feature_code
                              （这些菜单永远过不了客户端的 feature_code 过滤）
        - unboundFeatureCodes：sys_product_feature 中存在但任何启用版本都未勾选的 feature_code
                              （表示功能没有任何版本能看到）
        """
        menu_codes_q = await db.execute(
            select(Menu.feature_code).where(
                Menu.app_type == "client",
                Menu.is_deleted == 0,
                Menu.feature_code.is_not(None),
                Menu.feature_code != "",
            )
        )
        menu_codes = {c for c in menu_codes_q.scalars().all() if c}

        feature_codes_q = await db.execute(
            select(ProductFeature.feature_code).where(
                ProductFeature.is_deleted == 0,
            )
        )
        feature_codes = set(feature_codes_q.scalars().all())

        orphan = sorted(menu_codes - feature_codes)

        bound_q = await db.execute(
            select(ProductFeature.feature_code)
            .join(VersionFeature, VersionFeature.feature_id == ProductFeature.id)
            .where(
                ProductFeature.is_deleted == 0,
                VersionFeature.is_deleted == 0,
                VersionFeature.status == 1,
            )
            .distinct()
        )
        bound_codes = set(bound_q.scalars().all())
        unbound = sorted(feature_codes - bound_codes)

        return {
            "orphanFeatureCodes": orphan,
            "unboundFeatureCodes": unbound,
        }

    @staticmethod
    async def get_required_tables_by_version_id(
        db: AsyncSession, version_id: int
    ) -> List[str]:
        """根据版本ID获取所有需要的租户库表名"""
        result = await db.execute(
            select(ProductFeature.required_tables)
            .join(VersionFeature, VersionFeature.feature_id == ProductFeature.id)
            .where(
                VersionFeature.version_id == version_id,
                VersionFeature.is_deleted == 0,
                VersionFeature.status == 1,
                ProductFeature.is_deleted == 0,
                ProductFeature.status == 1,
            )
        )
        tables = set()
        for row in result.scalars().all():
            if row and isinstance(row, list):
                tables.update(row)
        return list(tables)
