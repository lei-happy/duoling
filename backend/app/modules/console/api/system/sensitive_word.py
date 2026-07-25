"""运营后台：敏感词库

词库供服务平台挂牌发布预检使用（04.运营审核与风控设计.md §2.3）。
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.response import success
from app.core.dependencies import get_current_user, get_platform_db
from app.core.security import TokenData
from app.modules.console.models.system.sensitive_word import (
    SensitiveWordAction,
    SensitiveWordCategory,
    SensitiveWordScope,
)
from app.modules.console.schemas.system.sensitive_word import (
    SensitiveWordBatchImport,
    SensitiveWordCreate,
    SensitiveWordIds,
    SensitiveWordStatusUpdate,
    SensitiveWordTest,
    SensitiveWordUpdate,
)
from app.modules.console.services.system.sensitive_word_service import (
    SensitiveWordService,
)

router = APIRouter()


@router.get("/options")
async def get_options(_: TokenData = Depends(get_current_user)):
    """分类 / 处置 / 范围的可选项

    由后端下发而非前端硬编码，避免两边取值漂移。
    """
    return success(
        data={
            "categories": [
                {"value": SensitiveWordCategory.POLITICS, "label": "政治"},
                {"value": SensitiveWordCategory.PORN, "label": "色情低俗"},
                {"value": SensitiveWordCategory.CONTRABAND, "label": "违禁品"},
                {"value": SensitiveWordCategory.DIVERSION, "label": "竞品导流"},
                {"value": SensitiveWordCategory.FRAUD, "label": "诈骗"},
                {"value": SensitiveWordCategory.OTHER, "label": "其他"},
            ],
            "actions": [
                {
                    "value": SensitiveWordAction.BLOCK,
                    "label": "禁止发布",
                    "desc": "命中后用户当场无法提交",
                },
                {
                    "value": SensitiveWordAction.REVIEW,
                    "label": "转人工审核",
                    "desc": "不阻止提交，标红进审核队列",
                },
            ],
            "scopes": [
                {"value": SensitiveWordScope.ALL, "label": "全平台"},
                {"value": SensitiveWordScope.ECOSYSTEM, "label": "货源/运力大厅"},
            ],
        }
    )


@router.get("/page")
async def page_words(
    page: int = Query(1),
    limit: int = Query(20),
    keyword: Optional[str] = Query(None),
    category: Optional[int] = Query(None),
    action: Optional[int] = Query(None),
    scope: Optional[str] = Query(None),
    status: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """分页查询敏感词"""
    result = await SensitiveWordService.page_words(
        db, page, limit, keyword, category, action, scope, status
    )
    return success(data=result)


@router.post("")
async def add_word(
    data: SensitiveWordCreate,
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """新增敏感词"""
    await SensitiveWordService.create_word(
        db, data.word, data.category, data.action, data.scope, data.remark
    )
    return success(message=f"已添加「{data.word.strip()}」")


@router.put("")
async def update_word(
    data: SensitiveWordUpdate,
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """修改敏感词"""
    await SensitiveWordService.update_word(
        db, data.id, data.word, data.category, data.action,
        data.scope, data.status, data.remark,
    )
    return success(message="已保存修改")


@router.put("/status")
async def set_status(
    data: SensitiveWordStatusUpdate,
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """批量启用 / 停用

    停用比删除更常用：某个词误伤时先停掉观察，确认无用再删。
    """
    count = await SensitiveWordService.set_status(db, data.ids, data.status)
    action_text = "启用" if int(data.status) == 1 else "停用"
    return success(message=f"已{action_text} {count} 个敏感词")


@router.post("/batch-import")
async def batch_import(
    data: SensitiveWordBatchImport,
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """批量导入"""
    result = await SensitiveWordService.batch_import(
        db, data.words, data.category, data.action, data.scope
    )
    parts = [f"新增 {result['added']} 个"]
    if result["revived"]:
        parts.append(f"恢复 {result['revived']} 个")
    if result["skipped"]:
        parts.append(f"已存在 {result['skipped']} 个未重复添加")
    return success(data=result, message="导入完成：" + "，".join(parts))


@router.post("/test")
async def test_text(
    data: SensitiveWordTest,
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """试测一段文字会不会被拦下

    没有这个入口，运营改完词库只能靠猜，或者拿真实发布去试——
    而真实发布被误拦时用户已经受影响了。
    """
    result = await SensitiveWordService.test_text(db, data.text, data.scope)
    return success(
        data=result,
        message="这段内容会被拦下" if result["blocked"] else "这段内容可以正常发布",
    )


@router.post("/delete")
async def delete_words(
    data: SensitiveWordIds,
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """批量删除"""
    count = await SensitiveWordService.delete_words(db, data.ids)
    return success(message=f"已删除 {count} 个敏感词")
