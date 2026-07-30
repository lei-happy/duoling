"""
批量生成证照监控 Mock 数据（写入 biz_compliance_alert，并回写源表到期日）

路径：backend/scripts/mockdata/mock_tenant_compliance_alerts.py

依赖：租户库已有自有车辆 / 驾驶员（可选社会运力）。
阈值与扫描引擎一致：horizon=60 天，critical=7 天。

用法（在 backend 目录下）:
  python scripts/mockdata/mock_tenant_compliance_alerts.py --tenant-code 1001
  python scripts/mockdata/mock_tenant_compliance_alerts.py --tenant-code 1001 --dry-run
  python scripts/mockdata/mock_tenant_compliance_alerts.py --tenant-code 1001 --vehicles 20 --drivers 15

写入 / 更新：
- biz_vehicle_ext（insurance / inspection / transport_license 到期日）
- biz_driver_license（驾驶证 / 从业资格到期日）
- biz_compliance_alert（预警物化结果，默认 open，少量 dismissed/resolved）
"""

from __future__ import annotations

import argparse
import random
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from sqlalchemy import create_engine, select  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

from app.core.config import get_settings  # noqa: E402
from app.modules.client.models.capacity.self_capacity.driver.driver import (  # noqa: E402
    Driver,
)
from app.modules.client.models.capacity.self_capacity.driver.driver_license import (  # noqa: E402
    DriverLicense,
)
from app.modules.client.models.capacity.self_capacity.vehicle import Vehicle  # noqa: E402
from app.modules.client.models.capacity.self_capacity.vehicle_ext import (  # noqa: E402
    VehicleExt,
)
from app.modules.client.models.compliance.compliance_alert import (  # noqa: E402
    BizComplianceAlert,
)

HORIZON = 60
CRITICAL = 7

# days_left 分布：过期 / 临界 / 预警
_LEVEL_DAYS = {
    "expired": (-45, -1),
    "critical": (0, CRITICAL),
    "warning": (CRITICAL + 1, HORIZON),
}


def _pick_days_left(rng: random.Random, level: str) -> int:
    lo, hi = _LEVEL_DAYS[level]
    return rng.randint(lo, hi)


def _level_of(days_left: int) -> str:
    if days_left < 0:
        return "expired"
    if days_left <= CRITICAL:
        return "critical"
    return "warning"


def _upsert_alert(
    session: Session,
    *,
    subject_type: str,
    subject_id: int,
    subject_name: str,
    subject_ref: str | None,
    doc_type: str,
    doc_no: str | None,
    expire_date: date,
    days_left: int,
    status: str,
    now: datetime,
    dry_run: bool,
) -> bool:
    level = _level_of(days_left)
    if dry_run:
        print(
            f"[dry-run] alert {subject_type}/{subject_id} {doc_type} "
            f"level={level} days={days_left} status={status}"
        )
        return True

    existing = session.execute(
        select(BizComplianceAlert).where(
            BizComplianceAlert.subject_type == subject_type,
            BizComplianceAlert.subject_id == subject_id,
            BizComplianceAlert.doc_type == doc_type,
            BizComplianceAlert.is_deleted == 0,
        )
    ).scalar_one_or_none()

    if existing is None:
        session.add(
            BizComplianceAlert(
                subject_type=subject_type,
                subject_id=subject_id,
                subject_name=subject_name,
                subject_ref=subject_ref,
                doc_type=doc_type,
                doc_no=doc_no,
                expire_date=expire_date,
                days_left=days_left,
                level=level,
                status=status,
                dismissed_user_id=1 if status == "dismissed" else None,
                dismissed_at=now if status == "dismissed" else None,
                first_alerted_at=now - timedelta(days=max(1, -min(days_left, 0))),
                last_scan_at=now,
            )
        )
    else:
        existing.subject_name = subject_name
        existing.subject_ref = subject_ref
        existing.doc_no = doc_no
        existing.expire_date = expire_date
        existing.days_left = days_left
        existing.level = level
        existing.status = status
        existing.last_scan_at = now
        if status == "dismissed":
            existing.dismissed_user_id = 1
            existing.dismissed_at = now
        else:
            existing.dismissed_user_id = None
            existing.dismissed_at = None
    return True


def _status_for(rng: random.Random) -> str:
    roll = rng.random()
    if roll < 0.78:
        return "open"
    if roll < 0.90:
        return "dismissed"
    return "resolved"


def _gen_vehicle_alerts(
    session: Session,
    limit: int,
    rng: random.Random,
    *,
    dry_run: bool,
) -> int:
    rows = session.execute(
        select(Vehicle, VehicleExt)
        .join(VehicleExt, VehicleExt.vehicle_id == Vehicle.id)
        .where(
            Vehicle.is_deleted == 0,
            VehicleExt.is_deleted == 0,
            Vehicle.status != 9,
        )
        .order_by(Vehicle.id.desc())
        .limit(limit)
    ).all()
    if not rows:
        return 0

    today = date.today()
    now = datetime.now()
    n = 0
    doc_types = ("insurance", "inspection", "transport_license")
    levels = ("expired", "critical", "warning")

    for vehicle, ext in rows:
        # 每辆车随机 1~2 类证照进入预警
        for doc_type in rng.sample(doc_types, k=rng.randint(1, 2)):
            level = rng.choice(levels)
            days_left = _pick_days_left(rng, level)
            expire = today + timedelta(days=days_left)
            doc_no = None
            if doc_type == "insurance":
                if not dry_run:
                    ext.insurance_expire = expire
            elif doc_type == "inspection":
                if not dry_run:
                    ext.inspection_expire = expire
            else:
                doc_no = ext.transport_license_no or f"TL-MOCK-{vehicle.id}"
                if not dry_run:
                    ext.transport_license_no = doc_no
                    ext.transport_license_expire = expire

            _upsert_alert(
                session,
                subject_type="vehicle",
                subject_id=vehicle.id,
                subject_name=vehicle.plate_number,
                subject_ref=vehicle.plate_number,
                doc_type=doc_type,
                doc_no=doc_no,
                expire_date=expire,
                days_left=days_left,
                status=_status_for(rng),
                now=now,
                dry_run=dry_run,
            )
            n += 1
    return n


def _gen_driver_alerts(
    session: Session,
    limit: int,
    rng: random.Random,
    *,
    dry_run: bool,
) -> int:
    rows = session.execute(
        select(Driver, DriverLicense)
        .join(DriverLicense, DriverLicense.driver_id == Driver.id)
        .where(
            Driver.is_deleted == 0,
            DriverLicense.is_deleted == 0,
            Driver.status != 2,
        )
        .order_by(Driver.id.desc())
        .limit(limit)
    ).all()
    if not rows:
        return 0

    today = date.today()
    now = datetime.now()
    n = 0
    for driver, lic in rows:
        for doc_type in rng.sample(("driver_license", "qualification"), k=rng.randint(1, 2)):
            level = rng.choice(("expired", "critical", "warning"))
            days_left = _pick_days_left(rng, level)
            expire = today + timedelta(days=days_left)
            if doc_type == "driver_license":
                doc_no = lic.license_no or f"DL-MOCK-{driver.id}"
                if not dry_run:
                    lic.license_no = doc_no
                    lic.license_expire = expire
            else:
                doc_no = getattr(lic, "qualification_no", None) or f"QG-MOCK-{driver.id}"
                if not dry_run:
                    if hasattr(lic, "qualification_no"):
                        lic.qualification_no = doc_no
                    lic.qualification_expire = expire

            _upsert_alert(
                session,
                subject_type="driver",
                subject_id=driver.id,
                subject_name=driver.name,
                subject_ref=driver.phone,
                doc_type=doc_type,
                doc_no=doc_no,
                expire_date=expire,
                days_left=days_left,
                status=_status_for(rng),
                now=now,
                dry_run=dry_run,
            )
            n += 1
    return n


def generate(
    session: Session,
    *,
    vehicles: int,
    drivers: int,
    rng: random.Random,
    dry_run: bool,
) -> dict[str, int]:
    stats = {
        "vehicle_alerts": _gen_vehicle_alerts(
            session, vehicles, rng, dry_run=dry_run
        ),
        "driver_alerts": _gen_driver_alerts(
            session, drivers, rng, dry_run=dry_run
        ),
    }
    if not dry_run:
        session.commit()
    return stats


def main() -> None:
    parser = argparse.ArgumentParser(description="向租户库批量插入证照监控 Mock 数据")
    parser.add_argument("--tenant-code", required=True, help="租户编码")
    parser.add_argument("--vehicles", type=int, default=25, help="参与的车辆数上限")
    parser.add_argument("--drivers", type=int, default=20, help="参与的驾驶员数上限")
    parser.add_argument("--seed", type=int, default=20260730, help="随机种子")
    parser.add_argument("--dry-run", action="store_true", help="只打印不写库")
    args = parser.parse_args()

    settings = get_settings()
    url = settings.tenant_db_url_sync(args.tenant_code)
    rng = random.Random(args.seed)

    engine = create_engine(url, echo=False)
    with Session(engine) as session:
        # 先探测是否有车辆/司机
        v_cnt = session.execute(
            select(Vehicle.id).where(Vehicle.is_deleted == 0).limit(1)
        ).first()
        if not v_cnt:
            raise SystemExit(
                "[ERROR] 租户库没有车辆。请先执行 mock_tenant_vehicles.py"
            )
        stats = generate(
            session,
            vehicles=args.vehicles,
            drivers=args.drivers,
            rng=rng,
            dry_run=args.dry_run,
        )

    action = "预览" if args.dry_run else "已写入"
    total = stats["vehicle_alerts"] + stats["driver_alerts"]
    print(
        f"[OK] 租户 {args.tenant_code}：{action} 证照监控 Mock 共 {total} 条\n"
        f"  车辆相关预警={stats['vehicle_alerts']}  驾驶员相关预警={stats['driver_alerts']}"
    )
    if stats["driver_alerts"] == 0:
        print(
            "  [提示] 未生成驾驶员预警（库内可能无驾驶员）。"
            "可先执行 mock_tenant_drivers.py"
        )


if __name__ == "__main__":
    main()
