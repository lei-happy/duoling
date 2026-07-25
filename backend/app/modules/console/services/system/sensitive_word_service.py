"""敏感词库 Service

职责有两块：
1. **运营维护**：增删改查、启停、批量导入。
2. **运行时加载**：给发布预检提供规则，带进程内 TTL 缓存。

缓存沿用 ``app.core.permissions._feature_cache`` 的做法（进程内 + TTL +
显式失效），不引入 Redis：词库是「读极多、写极少、量很小」的数据，
几百个词常驻内存不到几十 KB，跨进程最终一致由 TTL 兜住即可。
运营改词后本进程立即失效，其他进程最多滞后一个 TTL。
"""

from __future__ import annotations

import os
import time
from datetime import datetime
from typing import Dict, List, Optional, Sequence, Tuple

from sqlalchemy import func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.console.models.system.sensitive_word import (
    SensitiveWord,
    SensitiveWordAction,
    SensitiveWordCategory,
    SensitiveWordRule,
    SensitiveWordScope,
)

# scope -> (过期时间戳, 规则元组)
_word_cache: Dict[str, Tuple[float, Tuple[SensitiveWordRule, ...]]] = {}

BATCH_IMPORT_LIMIT = 500


def _cache_ttl() -> int:
    return int(os.getenv("SENSITIVE_WORD_CACHE_TTL", "300"))


def invalidate_sensitive_word_cache(scope: Optional[str] = None) -> None:
    """词库变更后调用，使指定 scope（或全部）的缓存失效"""
    if scope is None:
        _word_cache.clear()
    else:
        _word_cache.pop(scope, None)
        # scope=all 的词会被所有范围引用，改动它必须清空全部
        if scope == SensitiveWordScope.ALL:
            _word_cache.clear()


class SensitiveWordService:
    """敏感词库"""

    # ------------------------------------------------------------------
    # 运行时加载
    # ------------------------------------------------------------------

    @staticmethod
    async def get_rules(
        db: AsyncSession, scope: str = SensitiveWordScope.ECOSYSTEM
    ) -> List[SensitiveWordRule]:
        """取指定范围生效的规则（含 scope=all 的通用词）

        词库为空时返回空列表，预检的敏感词规则自然关闭——不该因为没配词
        就拦下任何东西，也不该反过来放行本该拦的其他规则。
        """
        now = time.time()
        cached = _word_cache.get(scope)
        if cached and cached[0] > now:
            return list(cached[1])

        scopes = {SensitiveWordScope.ALL, scope}
        rows = (
            await db.execute(
                select(
                    SensitiveWord.word,
                    SensitiveWord.category,
                    SensitiveWord.action,
                ).where(
                    SensitiveWord.status == 1,
                    SensitiveWord.scope.in_(list(scopes)),
                    SensitiveWord.is_deleted == 0,
                )
            )
        ).all()

        rules = tuple(
            SensitiveWordRule(word=r.word, category=r.category, action=r.action)
            for r in rows
        )
        _word_cache[scope] = (now + _cache_ttl(), rules)
        return list(rules)

    @staticmethod
    async def bump_hit_count(db: AsyncSession, words: Sequence[str]) -> None:
        """回写命中次数

        统计用于让运营看出哪些词是「死词」、哪些词在频繁误伤，否则词库
        只会越加越长、没人敢删。统计失败不能影响主流程，由调用方吞掉异常。
        """
        if not words:
            return
        await db.execute(
            update(SensitiveWord)
            .where(SensitiveWord.word.in_(list(set(words))), SensitiveWord.is_deleted == 0)
            .values(hit_count=SensitiveWord.hit_count + 1, last_hit_at=datetime.now())
        )

    # ------------------------------------------------------------------
    # 运营维护
    # ------------------------------------------------------------------

    @staticmethod
    async def page_words(
        db: AsyncSession,
        page: int = 1,
        limit: int = 20,
        keyword: Optional[str] = None,
        category: Optional[int] = None,
        action: Optional[int] = None,
        scope: Optional[str] = None,
        status: Optional[int] = None,
    ) -> dict:
        stmt = select(SensitiveWord).where(SensitiveWord.is_deleted == 0)
        if keyword:
            stmt = stmt.where(
                or_(
                    SensitiveWord.word.like(f"%{keyword.strip()}%"),
                    SensitiveWord.remark.like(f"%{keyword.strip()}%"),
                )
            )
        if category is not None:
            stmt = stmt.where(SensitiveWord.category == category)
        if action is not None:
            stmt = stmt.where(SensitiveWord.action == action)
        if scope:
            stmt = stmt.where(SensitiveWord.scope == scope)
        if status is not None:
            stmt = stmt.where(SensitiveWord.status == status)

        total = int(
            (await db.execute(select(func.count()).select_from(stmt.subquery()))).scalar()
            or 0
        )
        page = max(1, int(page or 1))
        limit = min(200, max(1, int(limit or 20)))
        rows = (
            await db.execute(
                stmt.order_by(SensitiveWord.updated_at.desc(), SensitiveWord.id.desc())
                .offset((page - 1) * limit)
                .limit(limit)
            )
        ).scalars().all()

        return {
            "list": [SensitiveWordService._to_dict(r) for r in rows],
            "count": total,
        }

    @staticmethod
    async def create_word(
        db: AsyncSession,
        word: str,
        category: int = SensitiveWordCategory.OTHER,
        action: int = SensitiveWordAction.BLOCK,
        scope: str = SensitiveWordScope.ALL,
        remark: Optional[str] = None,
    ) -> int:
        """新增敏感词

        命中已软删的同词同范围记录时**复活**而非报错：本表是软删除，
        「删掉某词 → 过一阵又想加回来」是高频运营动作，报「已存在」会让人困惑。
        """
        word = SensitiveWordService._clean_word(word)
        SensitiveWordService._validate(category, action, scope)

        existing = (
            await db.execute(
                select(SensitiveWord).where(
                    SensitiveWord.word == word, SensitiveWord.scope == scope
                )
            )
        ).scalars().first()

        if existing and existing.is_deleted == 0:
            raise BizException(f"「{word}」已经在词库里了，不用重复添加")

        if existing:
            existing.is_deleted = 0
            existing.category = category
            existing.action = action
            existing.status = 1
            existing.remark = remark
            await db.flush()
            invalidate_sensitive_word_cache(scope)
            return existing.id

        row = SensitiveWord(
            word=word, category=category, action=action, scope=scope,
            status=1, remark=remark,
        )
        db.add(row)
        await db.flush()
        invalidate_sensitive_word_cache(scope)
        return row.id

    @staticmethod
    async def update_word(
        db: AsyncSession,
        word_id: int,
        word: Optional[str] = None,
        category: Optional[int] = None,
        action: Optional[int] = None,
        scope: Optional[str] = None,
        status: Optional[int] = None,
        remark: Optional[str] = None,
    ) -> None:
        row = await SensitiveWordService._get_or_raise(db, word_id)
        old_scope = row.scope

        if word is not None:
            row.word = SensitiveWordService._clean_word(word)
        if category is not None:
            SensitiveWordService._validate(category=category)
            row.category = category
        if action is not None:
            SensitiveWordService._validate(action=action)
            row.action = action
        if scope is not None:
            SensitiveWordService._validate(scope=scope)
            row.scope = scope
        if status is not None:
            row.status = 1 if int(status) == 1 else 0
        if remark is not None:
            row.remark = remark

        await db.flush()
        invalidate_sensitive_word_cache(old_scope)
        invalidate_sensitive_word_cache(row.scope)

    @staticmethod
    async def delete_words(db: AsyncSession, word_ids: Sequence[int]) -> int:
        if not word_ids:
            raise BizException("请选择要删除的敏感词")
        result = await db.execute(
            update(SensitiveWord)
            .where(SensitiveWord.id.in_(list(word_ids)), SensitiveWord.is_deleted == 0)
            .values(is_deleted=1)
        )
        invalidate_sensitive_word_cache()
        return int(result.rowcount or 0)

    @staticmethod
    async def set_status(
        db: AsyncSession, word_ids: Sequence[int], status: int
    ) -> int:
        """批量启停

        停用比删除更常用：某个词误伤时先停掉观察，确认无用再删。
        """
        if not word_ids:
            raise BizException("请选择要操作的敏感词")
        result = await db.execute(
            update(SensitiveWord)
            .where(SensitiveWord.id.in_(list(word_ids)), SensitiveWord.is_deleted == 0)
            .values(status=1 if int(status) == 1 else 0)
        )
        invalidate_sensitive_word_cache()
        return int(result.rowcount or 0)

    @staticmethod
    async def batch_import(
        db: AsyncSession,
        words: Sequence[str],
        category: int = SensitiveWordCategory.OTHER,
        action: int = SensitiveWordAction.BLOCK,
        scope: str = SensitiveWordScope.ALL,
    ) -> dict:
        """批量导入

        已存在的词跳过而不报错——批量导入的常见用法是「补一份新词表」，
        其中必然与现有词库有重叠，因重叠而整批失败毫无意义。
        """
        SensitiveWordService._validate(category, action, scope)

        cleaned: List[str] = []
        for w in words:
            try:
                c = SensitiveWordService._clean_word(w)
            except BizException:
                continue
            if c not in cleaned:
                cleaned.append(c)

        if not cleaned:
            raise BizException("没有可导入的敏感词，请检查一下内容")
        if len(cleaned) > BATCH_IMPORT_LIMIT:
            raise BizException(
                f"一次最多导入 {BATCH_IMPORT_LIMIT} 个词，请拆分后分批导入"
            )

        existing_rows = (
            await db.execute(
                select(SensitiveWord).where(
                    SensitiveWord.word.in_(cleaned), SensitiveWord.scope == scope
                )
            )
        ).scalars().all()
        existing_map = {r.word: r for r in existing_rows}

        added = revived = skipped = 0
        for w in cleaned:
            row = existing_map.get(w)
            if row is None:
                db.add(
                    SensitiveWord(
                        word=w, category=category, action=action, scope=scope, status=1
                    )
                )
                added += 1
            elif row.is_deleted == 1:
                row.is_deleted = 0
                row.status = 1
                row.category = category
                row.action = action
                revived += 1
            else:
                skipped += 1

        await db.flush()
        invalidate_sensitive_word_cache(scope)
        return {"added": added, "revived": revived, "skipped": skipped}

    @staticmethod
    async def test_text(
        db: AsyncSession, text: str, scope: str = SensitiveWordScope.ECOSYSTEM
    ) -> dict:
        """试测：给运营一个「这段话会不会被拦」的自查入口

        没有这个功能，运营加完词只能靠猜，或者拿真实发布去试——
        而真实发布被误拦时用户已经受影响了。
        """
        from app.modules.client.services.ecosystem.content_guard import (
            find_contact_info,
            find_sensitive_words,
        )

        if not (text or "").strip():
            raise BizException("请输入要试测的内容")

        rules = await SensitiveWordService.get_rules(db, scope)
        word_hits = find_sensitive_words(text, rules)
        contact_hits = find_contact_info(text)

        blocked = bool(contact_hits) or any(
            h.action == SensitiveWordAction.BLOCK for h in word_hits
        )
        return {
            "blocked": blocked,
            "contactHits": contact_hits,
            "wordHits": [
                {"word": h.word, "category": h.category, "action": h.action}
                for h in word_hits
            ],
        }

    # ------------------------------------------------------------------
    # 内部
    # ------------------------------------------------------------------

    @staticmethod
    async def _get_or_raise(db: AsyncSession, word_id: int) -> SensitiveWord:
        row = (
            await db.execute(
                select(SensitiveWord).where(
                    SensitiveWord.id == word_id, SensitiveWord.is_deleted == 0
                )
            )
        ).scalars().first()
        if not row:
            raise BizException("这个敏感词不存在或已被删除，请刷新后重试")
        return row

    @staticmethod
    def _clean_word(word: str) -> str:
        w = (word or "").strip()
        if not w:
            raise BizException("敏感词不能为空")
        if len(w) > 64:
            raise BizException("敏感词太长了，请控制在 64 个字以内")
        # 单字词会大面积误伤（如「枪」会拦掉「枪支模型玩具运输」之外的正常词），
        # 运营很容易手滑录入，这里直接挡住。
        if len(w) < 2:
            raise BizException("敏感词至少要 2 个字，单字容易误伤正常内容")
        return w

    @staticmethod
    def _validate(
        category: Optional[int] = None,
        action: Optional[int] = None,
        scope: Optional[str] = None,
    ) -> None:
        if category is not None and category not in SensitiveWordCategory.ALL:
            raise BizException("请选择正确的敏感词分类")
        if action is not None and action not in SensitiveWordAction.ALL:
            raise BizException("请选择正确的命中处置方式")
        if scope is not None and scope not in SensitiveWordScope.VALUES:
            raise BizException("请选择正确的适用范围")

    @staticmethod
    def _to_dict(row: SensitiveWord) -> dict:
        return {
            "id": row.id,
            "word": row.word,
            "category": row.category,
            "action": row.action,
            "scope": row.scope,
            "status": row.status,
            "hitCount": row.hit_count,
            "lastHitAt": row.last_hit_at.strftime("%Y-%m-%d %H:%M:%S")
            if row.last_hit_at
            else None,
            "remark": row.remark,
            "createdAt": row.created_at.strftime("%Y-%m-%d %H:%M:%S")
            if row.created_at
            else None,
            "updatedAt": row.updated_at.strftime("%Y-%m-%d %H:%M:%S")
            if row.updated_at
            else None,
        }
