"""能源中心 · 主数据闭环（租户库，事务回滚不落库）

覆盖供应商 / 站点 / 商品 / 车辆档案 / 风控规则。
首条用例锁住「新增供应商后立刻序列化 Out」——页面新增 500 的根因。

对应需求：doc/02.需求文档/02.企业端/15.能源中心/01.产品方案与功能设计.md
对应接口：/api/client/energy/suppliers|stations|products|vehicle-profiles|rules
对应代码：backend/app/modules/client/services/energy/supplier_service.py
覆盖用例：TC-CLI-ENERGY-001 ~ TC-CLI-ENERGY-020
"""

from __future__ import annotations

import random
import uuid
from decimal import Decimal

import pytest

from app.common.exceptions import BizException
from app.modules.client.schemas.capacity.self_capacity.vehicle import VehicleCreate

from app.modules.client.schemas.energy.supplier import (
    EnergyStationCreate,
    EnergyStationOut,
    EnergyStationProductIn,
    EnergyStationUpdate,
    EnergySupplierCreate,
    EnergySupplierOut,
    EnergySupplierUpdate,
)
from app.modules.client.services.capacity.self_capacity.vehicle_service import VehicleService
from app.modules.client.services.energy.setting_service import (
    EnergyProductService,
    EnergyRuleService,
    EnergyVehicleProfileService,
)
from app.modules.client.services.energy.supplier_service import (
    EnergyStationService,
    EnergySupplierService,
)


def _name(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def _code(prefix: str) -> str:
    return f"{prefix}{uuid.uuid4().hex[:8].upper()}"


def _plate() -> str:
    prov = random.choice("京沪粤浙苏鲁")
    letter = random.choice("ABCDEFGHJKLMNPQRSTUVWXYZ")
    tail = "".join(random.choice("0123456789") for _ in range(5))
    return f"{prov}{letter}{tail}"


class TestSupplierCreateSerialize:
    """复现：flush 后 created_at 未 refresh，from_model 触发异步懒加载炸 500。"""

    async def test_create_then_serialize_out(self, tenant_session):
        obj = await EnergySupplierService.create(
            tenant_session,
            EnergySupplierCreate(supplierName=_name("测试供应商")),
        )
        assert obj.id is not None
        assert obj.supplier_code.startswith("ES")
        out = EnergySupplierOut.from_model(obj).model_dump()
        assert out["id"] == obj.id
        assert out["supplierName"]
        assert out["createdAt"] is not None
        assert out["status"] == 1


class TestSupplierCrud:
    async def test_custom_code_and_page(self, tenant_session):
        name = _name("中石化")
        code = _code("SP")
        obj = await EnergySupplierService.create(
            tenant_session,
            EnergySupplierCreate(
                supplierName=name, supplierCode=code, supplierType=1,
            ),
        )
        assert obj.supplier_code == code
        page = await EnergySupplierService.page(tenant_session, keyword=name)
        assert page["count"] >= 1
        assert any(x["supplierName"] == name for x in page["list"])

    async def test_empty_name_rejected(self, tenant_session):
        with pytest.raises(BizException, match="供应商名称"):
            await EnergySupplierService.create(
                tenant_session, EnergySupplierCreate(supplierName="  "),
            )

    async def test_duplicate_code_rejected(self, tenant_session):
        code = _code("SP")
        await EnergySupplierService.create(
            tenant_session,
            EnergySupplierCreate(supplierName=_name("供应商"), supplierCode=code),
        )
        with pytest.raises(BizException, match="编码已存在"):
            await EnergySupplierService.create(
                tenant_session,
                EnergySupplierCreate(supplierName=_name("供应商"), supplierCode=code),
            )

    async def test_soft_deleted_code_rejected(self, tenant_session):
        code = _code("SP")
        obj = await EnergySupplierService.create(
            tenant_session,
            EnergySupplierCreate(supplierName=_name("供应商"), supplierCode=code),
        )
        await EnergySupplierService.delete(tenant_session, obj.id)
        with pytest.raises(BizException, match="编码已存在"):
            await EnergySupplierService.create(
                tenant_session,
                EnergySupplierCreate(supplierName=_name("供应商"), supplierCode=code),
            )

    async def test_update_and_delete(self, tenant_session):
        obj = await EnergySupplierService.create(
            tenant_session, EnergySupplierCreate(supplierName=_name("供应商")),
        )
        updated = await EnergySupplierService.update(
            tenant_session, obj.id, EnergySupplierUpdate(contactName="张三", status=0),
        )
        assert updated.contact_name == "张三"
        assert updated.status == 0
        await EnergySupplierService.delete(tenant_session, obj.id)
        with pytest.raises(BizException, match="不存在"):
            await EnergySupplierService.get(tenant_session, obj.id)


class TestStationCrud:
    async def _supplier(self, db):
        return await EnergySupplierService.create(
            db, EnergySupplierCreate(supplierName=_name("站点供应商")),
        )

    async def test_create_then_serialize(self, tenant_session):
        sup = await self._supplier(tenant_session)
        st = await EnergyStationService.create(
            tenant_session,
            EnergyStationCreate(
                supplierId=sup.id, stationCode=_code("ST"), stationName="东站",
            ),
        )
        out = EnergyStationOut.from_model(st).model_dump()
        assert out["supplierId"] == sup.id
        assert out["stationName"] == "东站"
        assert out["status"] == 1

    async def test_missing_supplier_rejected(self, tenant_session):
        with pytest.raises(BizException, match="供应商不存在"):
            await EnergyStationService.create(
                tenant_session,
                EnergyStationCreate(
                    supplierId=987_654_321, stationCode="ST1", stationName="东站",
                ),
            )

    async def test_duplicate_code_rejected(self, tenant_session):
        sup = await self._supplier(tenant_session)
        code = _code("ST")
        await EnergyStationService.create(
            tenant_session,
            EnergyStationCreate(supplierId=sup.id, stationCode=code, stationName="东站"),
        )
        with pytest.raises(BizException, match="站点编码已存在"):
            await EnergyStationService.create(
                tenant_session,
                EnergyStationCreate(supplierId=sup.id, stationCode=code, stationName="西站"),
            )

    async def test_empty_fields_rejected(self, tenant_session):
        sup = await self._supplier(tenant_session)
        with pytest.raises(BizException, match="站点编码"):
            await EnergyStationService.create(
                tenant_session,
                EnergyStationCreate(supplierId=sup.id, stationCode="  ", stationName="东站"),
            )
        with pytest.raises(BizException, match="站点名称"):
            await EnergyStationService.create(
                tenant_session,
                EnergyStationCreate(supplierId=sup.id, stationCode=_code("ST"), stationName="  "),
            )

    async def test_create_with_location_and_prices(self, tenant_session):
        sup = await self._supplier(tenant_session)
        st = await EnergyStationService.create(
            tenant_session,
            EnergyStationCreate(
                supplierId=sup.id,
                stationCode=_code("ST"),
                stationName="沪太路站",
                address="沪太路 100 号",
                longitude=Decimal("121.473700"),
                latitude=Decimal("31.230400"),
                products=[
                    EnergyStationProductIn(
                        energyType="OIL", settlementPrice=Decimal("7.20"), unit="L",
                    ),
                    EnergyStationProductIn(
                        energyType="GAS", settlementPrice=Decimal("4.50"), unit="kg",
                    ),
                ],
            ),
        )
        detail = await EnergyStationService.detail(tenant_session, st.id)
        assert detail["address"] == "沪太路 100 号"
        assert Decimal(str(detail["longitude"])) == Decimal("121.473700")
        assert len(detail["products"]) == 2
        oil = next(p for p in detail["products"] if p["energyType"] == "OIL")
        assert Decimal(str(oil["settlementPrice"])) == Decimal("7.20")

        await EnergyStationService.update(
            tenant_session,
            st.id,
            EnergyStationUpdate(products=[
                EnergyStationProductIn(
                    energyType="ELECTRIC", settlementPrice=Decimal("1.20"), unit="kWh",
                ),
            ]),
        )
        again = await EnergyStationService.detail(tenant_session, st.id)
        assert len(again["products"]) == 1
        assert again["products"][0]["energyType"] == "ELECTRIC"

        page = await EnergyStationService.page(
            tenant_session, supplier_id=sup.id, energy_type="ELECTRIC",
        )
        assert page["count"] >= 1
        assert page["list"][0]["supplierName"]

    async def test_invalid_price_and_lng_rejected(self, tenant_session):
        sup = await self._supplier(tenant_session)
        with pytest.raises(BizException, match="结算价"):
            await EnergyStationService.create(
                tenant_session,
                EnergyStationCreate(
                    supplierId=sup.id, stationCode=_code("ST"), stationName="东站",
                    products=[EnergyStationProductIn(energyType="OIL", settlementPrice=0)],
                ),
            )
        with pytest.raises(BizException, match="经度"):
            await EnergyStationService.create(
                tenant_session,
                EnergyStationCreate(
                    supplierId=sup.id, stationCode=_code("ST"), stationName="东站",
                    longitude=Decimal("200"),
                ),
            )

    async def test_update_page_delete(self, tenant_session):
        sup = await self._supplier(tenant_session)
        st = await EnergyStationService.create(
            tenant_session,
            EnergyStationCreate(
                supplierId=sup.id, stationCode=_code("ST"), stationName="东站",
            ),
        )
        updated = await EnergyStationService.update(
            tenant_session, st.id, EnergyStationUpdate(address="某路 1 号"),
        )
        assert updated.address == "某路 1 号"
        page = await EnergyStationService.page(tenant_session, supplier_id=sup.id)
        assert page["count"] >= 1
        await EnergyStationService.delete(tenant_session, st.id)
        with pytest.raises(BizException, match="不存在"):
            await EnergyStationService.get(tenant_session, st.id)


class TestProductAndProfile:
    async def test_product_create_and_list(self, tenant_session):
        code = _code("P")
        obj = await EnergyProductService.create(tenant_session, {
            "productCode": code,
            "productName": "0#柴油",
            "energyType": "OIL",
        })
        assert obj.id is not None
        assert obj.standard_unit == "L"
        rows = await EnergyProductService.list_all(tenant_session)
        assert any(x["productCode"] == code for x in rows)

    async def test_product_empty_code_rejected(self, tenant_session):
        with pytest.raises(BizException, match="商品编码"):
            await EnergyProductService.create(tenant_session, {
                "productCode": "  ", "productName": "柴油",
            })

    async def test_product_duplicate_code_rejected(self, tenant_session):
        code = _code("P")
        await EnergyProductService.create(tenant_session, {
            "productCode": code, "productName": "柴油",
        })
        with pytest.raises(BizException, match="编码已存在"):
            await EnergyProductService.create(tenant_session, {
                "productCode": code, "productName": "另一柴油",
            })

    async def test_profile_upsert(self, tenant_session):
        vehicle = await VehicleService.create_vehicle(
            tenant_session,
            VehicleCreate(plateNumber=_plate(), plateCategory="BLUE"),
        )
        obj = await EnergyVehicleProfileService.upsert(tenant_session, {
            "vehicleId": vehicle.id,
            "energyType": "OIL",
            "tankCapacity": 600,
        })
        assert obj.vehicle_id == vehicle.id
        assert float(obj.tank_capacity) == 600
        again = await EnergyVehicleProfileService.upsert(tenant_session, {
            "vehicleId": vehicle.id,
            "energyType": "OIL",
            "tankCapacity": 650,
        })
        assert again.id == obj.id
        assert float(again.tank_capacity) == 650

    async def test_profile_missing_vehicle_rejected(self, tenant_session):
        with pytest.raises(BizException, match="车辆不存在"):
            await EnergyVehicleProfileService.upsert(tenant_session, {
                "vehicleId": 987_654_321, "energyType": "OIL",
            })


class TestRules:
    async def test_list_seeds_defaults(self, tenant_session):
        rows = await EnergyRuleService.list_all(tenant_session)
        codes = {x["ruleCode"] for x in rows}
        assert "OVER_TANK" in codes
        assert "REPEAT_FILL" in codes
        assert "ABNORMAL_PRICE" in codes
        again = await EnergyRuleService.list_all(tenant_session)
        assert {x["ruleCode"] for x in again} == codes
