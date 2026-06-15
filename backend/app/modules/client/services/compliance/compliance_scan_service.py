"""
证照监控扫描服务

被「证照监控引擎」（独立 worker）调用，对单个租户库做一次全量扫描：
  1) 从自有驾驶员/车辆、社会运力司机/车辆等表收集即将到期 / 已过期的证照
  2) upsert 到 biz_compliance_alert（同主体同证照只保留一条 open/dismissed/resolved）
  3) 把本轮未命中的 open 预警置为 resolved（说明已续期 / 已删除）

阈值（天）：
  - horizon  : 进入预警视野的提前天数（默认 60）
  - critical : 临界阈值（默认 7）
级别：expired(<0) / critical(<=critical) / warning(<=horizon)
"""

from __future__ import annotations

import os
from datetime import date, datetime
from typing import List, Optional

from loguru import logger
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.client.models.capacity.self_capacity.driver.driver import Driver
from app.modules.client.models.capacity.self_capacity.driver.driver_license import (
    DriverLicense,
)
from app.modules.client.models.capacity.self_capacity.vehicle import Vehicle
from app.modules.client.models.capacity.self_capacity.vehicle_ext import VehicleExt
from app.modules.client.models.capacity.social_capacity.social_capacity import (
    SocialCapacity,
)
from app.modules.client.models.capacity.social_capacity.social_capacity_driver import (
    SocialCapacityDriver,
)
from app.modules.client.models.capacity.social_capacity.social_capacity_vehicle import (
    SocialCapacityVehicle,
)
from app.modules.client.models.capacity.carrier_capacity.carrier_capacity import (
    CarrierCapacity,
)
from app.modules.client.models.capacity.carrier_capacity.carrier_capacity_driver import (
    CarrierCapacityDriver,
)
from app.modules.client.models.capacity.carrier_capacity.carrier_capacity_vehicle import (
    CarrierCapacityVehicle,
)
from app.modules.client.models.compliance.compliance_alert import BizComplianceAlert


def _horizon_days() -> int:
    return int(os.getenv("COMPLIANCE_ALERT_HORIZON_DAYS", "60"))


def _critical_days() -> int:
    return int(os.getenv("COMPLIANCE_ALERT_CRITICAL_DAYS", "7"))


def _level_of(days_left: int, critical_days: int) -> str:
    if days_left < 0:
        return "expired"
    if days_left <= critical_days:
        return "critical"
    return "warning"


class _Candidate:
    __slots__ = (
        "subject_type",
        "subject_id",
        "subject_name",
        "subject_ref",
        "doc_type",
        "doc_no",
        "expire_date",
    )

    def __init__(
        self,
        subject_type: str,
        subject_id: int,
        subject_name: str,
        subject_ref: Optional[str],
        doc_type: str,
        doc_no: Optional[str],
        expire_date: date,
    ) -> None:
        self.subject_type = subject_type
        self.subject_id = subject_id
        self.subject_name = subject_name
        self.subject_ref = subject_ref
        self.doc_type = doc_type
        self.doc_no = doc_no
        self.expire_date = expire_date

    @property
    def key(self) -> tuple:
        return (self.subject_type, self.subject_id, self.doc_type)


class ComplianceScanService:
    """证照监控扫描（单租户）"""

    @staticmethod
    async def scan_tenant(db: AsyncSession) -> dict:
        """对当前租户库执行一次全量扫描并落库，返回统计信息。"""
        today = date.today()
        horizon = _horizon_days()
        critical = _critical_days()
        cutoff = today.fromordinal(today.toordinal() + horizon)
        run_ts = datetime.now()

        candidates: List[_Candidate] = []
        candidates += await ComplianceScanService._scan_self_drivers(db, cutoff)
        candidates += await ComplianceScanService._scan_self_vehicles(db, cutoff)
        candidates += await ComplianceScanService._scan_social_drivers(db, cutoff)
        candidates += await ComplianceScanService._scan_social_vehicles(db, cutoff)
        candidates += await ComplianceScanService._scan_carrier_drivers(db, cutoff)
        candidates += await ComplianceScanService._scan_carrier_vehicles(db, cutoff)

        inserted = updated = reopened = 0
        for cand in candidates:
            days_left = (cand.expire_date - today).days
            level = _level_of(days_left, critical)

            existing = (
                await db.execute(
                    select(BizComplianceAlert).where(
                        BizComplianceAlert.subject_type == cand.subject_type,
                        BizComplianceAlert.subject_id == cand.subject_id,
                        BizComplianceAlert.doc_type == cand.doc_type,
                        BizComplianceAlert.is_deleted == 0,
                    )
                )
            ).scalar_one_or_none()

            if existing is None:
                db.add(
                    BizComplianceAlert(
                        subject_type=cand.subject_type,
                        subject_id=cand.subject_id,
                        subject_name=cand.subject_name,
                        subject_ref=cand.subject_ref,
                        doc_type=cand.doc_type,
                        doc_no=cand.doc_no,
                        expire_date=cand.expire_date,
                        days_left=days_left,
                        level=level,
                        status="open",
                        first_alerted_at=run_ts,
                        last_scan_at=run_ts,
                    )
                )
                inserted += 1
            else:
                existing.subject_name = cand.subject_name
                existing.subject_ref = cand.subject_ref
                existing.doc_no = cand.doc_no
                existing.expire_date = cand.expire_date
                existing.days_left = days_left
                existing.level = level
                existing.last_scan_at = run_ts
                # resolved 的预警再次进入视野（极少见，但语义上应重新打开）；
                # dismissed 保持人工忽略状态，不被扫描覆盖。
                if existing.status == "resolved":
                    existing.status = "open"
                    reopened += 1
                updated += 1

        await db.flush()

        # 本轮未命中的 open 预警 → 已续期 / 已删除 → 置为 resolved
        resolved_res = await db.execute(
            update(BizComplianceAlert)
            .where(
                BizComplianceAlert.is_deleted == 0,
                BizComplianceAlert.status == "open",
                BizComplianceAlert.last_scan_at < run_ts,
            )
            .values(status="resolved", last_scan_at=run_ts)
        )
        await db.commit()

        resolved = resolved_res.rowcount if resolved_res.rowcount is not None else -1
        stats = {
            "candidates": len(candidates),
            "inserted": inserted,
            "updated": updated,
            "reopened": reopened,
            "resolved": resolved,
        }
        return stats

    # ---------- 各来源扫描 ----------

    @staticmethod
    async def _scan_self_drivers(db: AsyncSession, cutoff: date) -> List[_Candidate]:
        rows = (
            await db.execute(
                select(Driver, DriverLicense)
                .join(DriverLicense, DriverLicense.driver_id == Driver.id)
                .where(
                    Driver.is_deleted == 0,
                    DriverLicense.is_deleted == 0,
                    Driver.status != 2,  # 排除离职
                )
            )
        ).all()

        out: List[_Candidate] = []
        for driver, lic in rows:
            if lic.license_expire and lic.license_expire <= cutoff:
                out.append(
                    _Candidate(
                        "driver", driver.id, driver.name, driver.phone,
                        "driver_license", lic.license_no, lic.license_expire,
                    )
                )
            if lic.qualification_expire and lic.qualification_expire <= cutoff:
                out.append(
                    _Candidate(
                        "driver", driver.id, driver.name, driver.phone,
                        "qualification", lic.qualification_no, lic.qualification_expire,
                    )
                )
        return out

    @staticmethod
    async def _scan_self_vehicles(db: AsyncSession, cutoff: date) -> List[_Candidate]:
        rows = (
            await db.execute(
                select(Vehicle, VehicleExt)
                .join(VehicleExt, VehicleExt.vehicle_id == Vehicle.id)
                .where(
                    Vehicle.is_deleted == 0,
                    VehicleExt.is_deleted == 0,
                    Vehicle.status != 9,  # 排除已报废
                )
            )
        ).all()

        out: List[_Candidate] = []
        for vehicle, ext in rows:
            plate = vehicle.plate_number
            if ext.insurance_expire and ext.insurance_expire <= cutoff:
                out.append(
                    _Candidate(
                        "vehicle", vehicle.id, plate, plate,
                        "insurance", None, ext.insurance_expire,
                    )
                )
            if ext.inspection_expire and ext.inspection_expire <= cutoff:
                out.append(
                    _Candidate(
                        "vehicle", vehicle.id, plate, plate,
                        "inspection", None, ext.inspection_expire,
                    )
                )
            if (
                ext.transport_license_expire
                and ext.transport_license_expire <= cutoff
            ):
                out.append(
                    _Candidate(
                        "vehicle", vehicle.id, plate, plate,
                        "transport_license", ext.transport_license_no,
                        ext.transport_license_expire,
                    )
                )
        return out

    @staticmethod
    async def _scan_social_drivers(db: AsyncSession, cutoff: date) -> List[_Candidate]:
        rows = (
            await db.execute(
                select(SocialCapacity, SocialCapacityDriver)
                .join(
                    SocialCapacityDriver,
                    SocialCapacityDriver.social_capacity_id == SocialCapacity.id,
                )
                .where(
                    SocialCapacity.is_deleted == 0,
                    SocialCapacityDriver.is_deleted == 0,
                    SocialCapacity.status != 3,  # 排除黑名单
                )
            )
        ).all()

        out: List[_Candidate] = []
        for sc, d in rows:
            name = sc.driver_name or d.name
            phone = sc.driver_phone or d.phone
            if d.license_expire and d.license_expire <= cutoff:
                out.append(
                    _Candidate(
                        "social_driver", sc.id, name, phone,
                        "driver_license", d.license_no, d.license_expire,
                    )
                )
            if d.qualification_expire and d.qualification_expire <= cutoff:
                out.append(
                    _Candidate(
                        "social_driver", sc.id, name, phone,
                        "qualification", d.qualification_no, d.qualification_expire,
                    )
                )
        return out

    @staticmethod
    async def _scan_social_vehicles(db: AsyncSession, cutoff: date) -> List[_Candidate]:
        rows = (
            await db.execute(
                select(SocialCapacity, SocialCapacityVehicle)
                .join(
                    SocialCapacityVehicle,
                    SocialCapacityVehicle.social_capacity_id == SocialCapacity.id,
                )
                .where(
                    SocialCapacity.is_deleted == 0,
                    SocialCapacityVehicle.is_deleted == 0,
                    SocialCapacity.status != 3,  # 排除黑名单
                )
            )
        ).all()

        out: List[_Candidate] = []
        for sc, v in rows:
            plate = sc.plate_number or v.plate_number
            if v.inspection_expire and v.inspection_expire <= cutoff:
                out.append(
                    _Candidate(
                        "social_vehicle", sc.id, plate, plate,
                        "inspection", None, v.inspection_expire,
                    )
                )
            if v.insurance_expire and v.insurance_expire <= cutoff:
                out.append(
                    _Candidate(
                        "social_vehicle", sc.id, plate, plate,
                        "insurance", None, v.insurance_expire,
                    )
                )
            if v.transport_license_expire and v.transport_license_expire <= cutoff:
                out.append(
                    _Candidate(
                        "social_vehicle", sc.id, plate, plate,
                        "transport_license", v.transport_license_no,
                        v.transport_license_expire,
                    )
                )
        return out

    @staticmethod
    async def _scan_carrier_drivers(db: AsyncSession, cutoff: date) -> List[_Candidate]:
        rows = (
            await db.execute(
                select(CarrierCapacity, CarrierCapacityDriver)
                .join(
                    CarrierCapacityDriver,
                    CarrierCapacityDriver.carrier_capacity_id == CarrierCapacity.id,
                )
                .where(
                    CarrierCapacity.is_deleted == 0,
                    CarrierCapacityDriver.is_deleted == 0,
                    CarrierCapacity.status != 3,  # 排除黑名单
                )
            )
        ).all()

        out: List[_Candidate] = []
        for cc, d in rows:
            name = cc.driver_name or d.name
            phone = cc.driver_phone or d.phone
            if d.license_expire and d.license_expire <= cutoff:
                out.append(
                    _Candidate(
                        "carrier_driver", cc.id, name, phone,
                        "driver_license", d.license_no, d.license_expire,
                    )
                )
            if d.qualification_expire and d.qualification_expire <= cutoff:
                out.append(
                    _Candidate(
                        "carrier_driver", cc.id, name, phone,
                        "qualification", d.qualification_no, d.qualification_expire,
                    )
                )
        return out

    @staticmethod
    async def _scan_carrier_vehicles(db: AsyncSession, cutoff: date) -> List[_Candidate]:
        rows = (
            await db.execute(
                select(CarrierCapacity, CarrierCapacityVehicle)
                .join(
                    CarrierCapacityVehicle,
                    CarrierCapacityVehicle.carrier_capacity_id == CarrierCapacity.id,
                )
                .where(
                    CarrierCapacity.is_deleted == 0,
                    CarrierCapacityVehicle.is_deleted == 0,
                    CarrierCapacity.status != 3,  # 排除黑名单
                )
            )
        ).all()

        out: List[_Candidate] = []
        for cc, v in rows:
            plate = cc.plate_number or v.plate_number
            if v.inspection_expire and v.inspection_expire <= cutoff:
                out.append(
                    _Candidate(
                        "carrier_vehicle", cc.id, plate, plate,
                        "inspection", None, v.inspection_expire,
                    )
                )
            if v.insurance_expire and v.insurance_expire <= cutoff:
                out.append(
                    _Candidate(
                        "carrier_vehicle", cc.id, plate, plate,
                        "insurance", None, v.insurance_expire,
                    )
                )
            if v.transport_license_expire and v.transport_license_expire <= cutoff:
                out.append(
                    _Candidate(
                        "carrier_vehicle", cc.id, plate, plate,
                        "transport_license", v.transport_license_no,
                        v.transport_license_expire,
                    )
                )
        return out
