from typing import Optional

from fastapi import APIRouter, Depends, File, Query, UploadFile
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.common.operation_log import operation_log
from app.common.response import success
from app.core.dependencies import get_current_user, get_tenant_db
from app.modules.client.services.energy.connector_service import EnergyConnectorService
from app.modules.client.services.energy.connectors.excel import ExcelConnector

router = APIRouter()


class ConnectorCreate(BaseModel):
    connectorCode: str = "excel"
    connectorName: str
    supplierId: int
    accountId: Optional[int] = None
    authConfig: Optional[dict] = None
    fieldMapping: Optional[dict] = None
    syncMode: str = "manual"
    cron: Optional[str] = None
    remark: Optional[str] = None


class ConnectorUpdate(BaseModel):
    connectorName: Optional[str] = None
    accountId: Optional[int] = None
    authConfig: Optional[dict] = None
    fieldMapping: Optional[dict] = None
    syncMode: Optional[str] = None
    cron: Optional[str] = None
    status: Optional[int] = None
    remark: Optional[str] = None


@router.get("/catalog")
async def catalog(_=Depends(get_current_user)):
    return success(data=EnergyConnectorService.catalog())


@router.get("")
async def page_connectors(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, alias="limit", ge=1, le=100),
    supplierId: Optional[int] = None,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    return success(data=await EnergyConnectorService.page(db, page, page_size, supplierId))


@router.post("")
@operation_log(module="能源接入", action="新增", description="新增数据接入配置")
async def create_connector(
    data: ConnectorCreate,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    obj = await EnergyConnectorService.create(db, data.model_dump())
    return success(data={"id": obj.id})


@router.put("/{cid}")
@operation_log(module="能源接入", action="编辑", description="编辑数据接入配置")
async def update_connector(
    cid: int,
    data: ConnectorUpdate,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    await EnergyConnectorService.update(db, cid, data.model_dump(exclude_unset=True))
    return success()


@router.delete("/{cid}")
@operation_log(module="能源接入", action="删除", description="删除数据接入配置")
async def delete_connector(
    cid: int,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    await EnergyConnectorService.delete(db, cid)
    return success()


@router.post("/{cid}/import")
@operation_log(module="能源接入", action="导入", description="导入能源账单")
async def import_excel(
    cid: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    name = (file.filename or "").lower()
    if not name.endswith((".xlsx", ".xls")):
        raise BizException("请上传 Excel 文件")
    content = await file.read()
    rows = ExcelConnector.parse_workbook(content)
    if not rows:
        raise BizException("文件里没有读到有效账单行，请核对模板表头")
    result = await EnergyConnectorService.run_import(db, cid, rows)
    return success(
        data=result,
        message=f"已导入 {result['imported']} 笔，重复 {result['duplicated']} 笔，失败 {result['failed']} 笔",
    )


@router.post("/{cid}/pull")
@operation_log(module="能源接入", action="同步", description="拉取供应商账单")
async def pull_connector(
    cid: int,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    result = await EnergyConnectorService.pull(db, cid)
    return success(data=result)
