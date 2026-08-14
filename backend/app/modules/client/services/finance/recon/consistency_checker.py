"""运输单与财务单一致性核对器

回答对账岗每天的那个问题：**财务单上写的钱，和实际拉了多少车、什么时候签收、
按什么价算，是不是一回事。**

职责边界（文档 09 §6.2）：
- 本器负责比对、置脏、差异留痕与处置、互斥校验；
- 对账行的金额字段由各侧对账 service 写（谁的表谁来写），本器只写
  ``recon_dirty`` 三列与 ``biz_recon_diff``。

客户侧与承运商侧的表结构不同（``biz_customer_recon_waybill_link`` vs
``biz_carrier_recon_task_link``），但对账行的**脏标记列名与主表冗余列名两侧同构**，
因此这里用 ``ReconBinding`` 描述差异、共用同一套实现，避免两侧各写一遍后
出现「A 路径拦住、B 路径放过」的账务事故。

绑定在各侧对账 service 首次导入时注册；未注册时置脏类方法安全空转（返回 0），
使业务侧调用点可以先于对账表落地接入。
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Any, Awaitable, Callable, Dict, List, Optional, Sequence

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.models.finance.recon_diff import ReconDiff
from app.modules.client.services.finance.base.finance_doc_event_writer import (
    FinanceDocEventWriter,
    FinanceEventType,
)
from app.modules.client.services.finance.recon.diff_constants import (
    CHECKABLE_RECON_STATUSES,
    BizDocType,
    DiffSeverity,
    DiffStatus,
    DiffType,
    ReconKind,
    diff_label,
    severity_of,
)

logger = logging.getLogger(__name__)

# 桥接表脏标记列名（两侧同构，建表时一次带上，见文档 09 §3.2）
DIRTY_FLAG_COL = "recon_dirty"
DIRTY_REASON_COL = "dirty_reason"
DIRTY_AT_COL = "dirty_at"
# 对账主表冗余计数列名（避免列表页对桥接表做 count）
DIRTY_COUNT_COL = "dirty_line_count"
DIFF_OPEN_COUNT_COL = "diff_open_count"
DIFF_FORCED_COUNT_COL = "diff_forced_count"

# 强制确认理由最小长度（文档 09 §5.3 路径三）
FORCE_CONFIRM_REASON_MIN_LEN = 10

# 单批读取的对账行数（大对账单分批，避免一次性拉全表）
_LINE_BATCH_SIZE = 200


@dataclass
class DiffCandidate:
    """一条待落库的差异（检测器产出，核对器负责去重与持久化）"""

    biz_doc_id: int
    diff_type: int
    biz_doc_no: Optional[str] = None
    link_id: Optional[int] = None
    expected_value: Optional[str] = None
    actual_value: Optional[str] = None
    diff_amount: Optional[Decimal] = None
    severity: Optional[int] = None

    def resolved_severity(self) -> int:
        return int(self.severity or severity_of(self.diff_type))


@dataclass
class ReconCheckReport:
    """一次核对的结论（前端「一致性核对」区块直接渲染）"""

    recon_id: int
    recon_kind: str
    checked_lines: int = 0
    blocking_count: int = 0
    warning_count: int = 0
    dirty_lines: int = 0
    diffs: List[DiffCandidate] = field(default_factory=list)
    checked_at: datetime = field(default_factory=datetime.now)

    @property
    def passed(self) -> bool:
        return self.blocking_count == 0 and self.warning_count == 0


# 侧特有的检测逻辑由各侧对账 service 提供：
#   (db, recon, lines) -> 差异候选列表
LineDetector = Callable[
    [AsyncSession, Any, Sequence[Any]], Awaitable[List[DiffCandidate]]
]
# 漏挂检测（依赖各侧候选池规则）：(db, filters) -> 差异候选列表
OrphanDetector = Callable[[AsyncSession, dict], Awaitable[List[DiffCandidate]]]


@dataclass(frozen=True)
class ReconBinding:
    """一侧对账的表结构绑定

    ``link_recon_fk`` / ``link_biz_fk`` 是桥接表分别指向对账主表与业务单据的列名；
    脏标记列与冗余计数列名两侧统一，不参数化。
    """

    recon_kind: str
    biz_doc_type: int
    recon_model: type
    link_model: type
    link_recon_fk: str
    link_biz_fk: str
    line_detector: Optional[LineDetector] = None
    orphan_detector: Optional[OrphanDetector] = None

    def recon_col(self):
        return getattr(self.link_model, self.link_recon_fk)

    def biz_col(self):
        return getattr(self.link_model, self.link_biz_fk)


class ConsistencyChecker:
    """运输单与财务单一致性核对器（客户侧 / 承运商侧共用）"""

    _bindings: Dict[str, ReconBinding] = {}

    # ------------------------------------------------------------------
    # 绑定注册
    # ------------------------------------------------------------------
    @classmethod
    def register_binding(cls, binding: ReconBinding) -> None:
        """注册一侧对账的表结构（各侧对账 service 模块导入时调用）。"""
        cls._bindings[binding.recon_kind] = binding

    @classmethod
    def binding_or_none(cls, recon_kind: str) -> Optional[ReconBinding]:
        return cls._bindings.get(recon_kind)

    @classmethod
    def binding_or_raise(cls, recon_kind: str) -> ReconBinding:
        b = cls._bindings.get(recon_kind)
        if b is None:
            raise BizException("该类型对账单暂不支持一致性核对，请联系管理员")
        return b

    # ------------------------------------------------------------------
    # 「已挂接」口径（候选池排除、重挂检测、编辑拦截共用一份定义）
    # ------------------------------------------------------------------
    @classmethod
    def bound_biz_ids(
        cls, recon_kind: str, *, exclude_recon_id: Optional[int] = None,
    ):
        """返回「已挂在非撤销对账单上」的业务单据 id 子查询。

        绑定未注册（对账表尚未落地）时返回 ``None``：此时不存在任何挂接关系，
        调用方按「无需排除」处理即可。

        候选池排除、重挂检测、业务侧编辑拦截三处共用本定义，避免各写一遍后
        出现「候选池里看不到、但加行时又能挂上」这类自相矛盾的行为。
        """
        binding = cls.binding_or_none(recon_kind)
        if binding is None:
            return None
        recon = binding.recon_model
        link = binding.link_model
        stmt = (
            select(binding.biz_col())
            .join(recon, recon.id == binding.recon_col())
            .where(
                link.is_deleted == 0,
                recon.is_deleted == 0,
                recon.status != 4,
            )
        )
        if exclude_recon_id is not None:
            stmt = stmt.where(binding.recon_col() != exclude_recon_id)
        return stmt

    @classmethod
    async def is_biz_doc_bound(
        cls,
        db: AsyncSession,
        recon_kind: str,
        biz_doc_id: int,
        *,
        exclude_recon_id: Optional[int] = None,
    ) -> bool:
        """该业务单据是否已挂在非撤销对账单上（业务侧编辑拦截用）。"""
        binding = cls.binding_or_none(recon_kind)
        if binding is None:
            return False
        stmt = cls.bound_biz_ids(recon_kind, exclude_recon_id=exclude_recon_id)
        r = await db.execute(
            select(func.count()).select_from(
                stmt.where(binding.biz_col() == biz_doc_id).subquery()
            )
        )
        return int(r.scalar() or 0) > 0

    # ------------------------------------------------------------------
    # 置脏（业务侧变更 → 对账行标记需重新核对）
    # ------------------------------------------------------------------
    @classmethod
    async def mark_dirty_by_waybill(
        cls, db: AsyncSession, wb_id: int, reason: str,
    ) -> int:
        """运单变更 → 置脏相关客户对账行，返回受影响行数。"""
        return await cls._mark_dirty(db, ReconKind.CUSTOMER, wb_id, reason)

    @classmethod
    async def mark_dirty_by_task(
        cls, db: AsyncSession, task_id: int, reason: str,
    ) -> int:
        """任务变更 → 置脏相关承运商对账行，返回受影响行数。"""
        return await cls._mark_dirty(db, ReconKind.CARRIER, task_id, reason)

    @classmethod
    async def _mark_dirty(
        cls, db: AsyncSession, recon_kind: str, biz_doc_id: int, reason: str,
    ) -> int:
        """只置脏、不改金额（快照不漂移原则）。

        仅作用于 ``status ∈ {0 草稿, 2 已确认}`` 的对账单：已结清或已撤销的
        钱已经动过，差异要走「解锁结清」重新走流程，不在这里悄悄改标记。

        绑定未注册（对应对账表尚未落地）时空转返回 0，让业务侧调用点可以
        先接入、后生效。
        """
        binding = cls.binding_or_none(recon_kind)
        if binding is None:
            logger.debug(
                "对账绑定未注册，跳过置脏：recon_kind=%s biz_doc_id=%s",
                recon_kind, biz_doc_id,
            )
            return 0

        recon_ids = await cls._checkable_recon_ids(db, binding, biz_doc_id)
        if not recon_ids:
            return 0

        now = datetime.now()
        link = binding.link_model
        r = await db.execute(
            update(link)
            .where(
                binding.biz_col() == biz_doc_id,
                binding.recon_col().in_(recon_ids),
                link.is_deleted == 0,
                getattr(link, DIRTY_FLAG_COL) == 0,
            )
            .values(**{
                DIRTY_FLAG_COL: 1,
                DIRTY_REASON_COL: (reason or "")[:255] or None,
                DIRTY_AT_COL: now,
            })
        )
        affected = int(r.rowcount or 0)
        if affected:
            await cls._refresh_counters(db, binding, recon_ids)
        return affected

    @classmethod
    async def _checkable_recon_ids(
        cls, db: AsyncSession, binding: ReconBinding, biz_doc_id: int,
    ) -> List[int]:
        """该业务单据挂在哪些「可核对」对账单上（状态 0 / 2）。"""
        recon = binding.recon_model
        link = binding.link_model
        r = await db.execute(
            select(binding.recon_col())
            .join(recon, recon.id == binding.recon_col())
            .where(
                binding.biz_col() == biz_doc_id,
                link.is_deleted == 0,
                recon.is_deleted == 0,
                recon.status.in_(CHECKABLE_RECON_STATUSES),
            )
            .distinct()
        )
        return [int(x) for x in r.scalars().all()]

    # ------------------------------------------------------------------
    # 核对
    # ------------------------------------------------------------------
    @classmethod
    async def check_recon(
        cls,
        db: AsyncSession,
        *,
        recon_kind: str,
        recon_id: int,
        persist: bool = True,
        operator_id: Optional[int] = None,
    ) -> ReconCheckReport:
        """核对一张对账单的全部行，返回差异报告。

        ``persist=False`` 时只返回不落库，供前端「试算」与确认前预检使用。

        执行顺序按文档 09 §二 的三个层次递进：归属（重挂）→ 数量 → 金额。
        归属层出现阻塞级问题时短路，不再算数量与金额——归属错了，后两层没有意义。
        """
        binding = cls.binding_or_raise(recon_kind)
        recon = await cls._get_recon_or_404(db, binding, recon_id)

        report = ReconCheckReport(recon_id=recon_id, recon_kind=recon_kind)
        lines = await cls._load_lines(db, binding, recon_id)
        report.checked_lines = len(lines)
        report.dirty_lines = sum(
            1 for ln in lines if int(getattr(ln, DIRTY_FLAG_COL, 0) or 0) == 1
        )

        # 层次一：归属检查（重挂在两侧同构，可通用实现）
        diffs = await cls._detect_duplicated(db, binding, recon_id, lines)

        # 层次二/三：数量与金额检查依赖各侧业务事实，交由绑定的检测器
        if not any(
            d.resolved_severity() == DiffSeverity.BLOCKING for d in diffs
        ) and binding.line_detector is not None:
            diffs.extend(await binding.line_detector(db, recon, lines))

        report.diffs = diffs
        report.blocking_count = sum(
            1 for d in diffs if d.resolved_severity() == DiffSeverity.BLOCKING
        )
        report.warning_count = len(diffs) - report.blocking_count

        if persist:
            await cls.record_diffs(
                db,
                recon_kind=recon_kind,
                recon_id=recon_id,
                candidates=diffs,
                operator_id=operator_id,
            )
            await cls._invalidate_stale(db, recon_kind, recon_id, diffs)
            await cls._refresh_counters(db, binding, [recon_id])
        return report

    @classmethod
    async def _detect_duplicated(
        cls,
        db: AsyncSession,
        binding: ReconBinding,
        recon_id: int,
        lines: Sequence[Any],
    ) -> List[DiffCandidate]:
        """重挂检测：同一业务单据出现在两张非撤销对账单中（``diff_type=2``）。

        这是账务事故里代价最高的一类——重复结算直接导致多收/多付，因此严重度
        为阻塞。检测逻辑两侧一致，故放在核对器通用层。
        """
        if not lines:
            return []
        biz_ids = [int(getattr(ln, binding.link_biz_fk)) for ln in lines]
        recon = binding.recon_model
        link = binding.link_model
        out: List[DiffCandidate] = []
        for start in range(0, len(biz_ids), _LINE_BATCH_SIZE):
            chunk = biz_ids[start:start + _LINE_BATCH_SIZE]
            r = await db.execute(
                select(binding.biz_col(), binding.recon_col())
                .join(recon, recon.id == binding.recon_col())
                .where(
                    binding.biz_col().in_(chunk),
                    binding.recon_col() != recon_id,
                    link.is_deleted == 0,
                    recon.is_deleted == 0,
                    recon.status != 4,
                )
            )
            for biz_id, other_recon_id in r.all():
                out.append(DiffCandidate(
                    biz_doc_id=int(biz_id),
                    diff_type=DiffType.DUPLICATED,
                    expected_value=f"仅本单 #{recon_id}",
                    actual_value=f"另挂对账单 #{int(other_recon_id)}",
                ))
        return out

    @classmethod
    async def detect_orphans(
        cls, db: AsyncSession, *, recon_kind: str, **filters,
    ) -> List[DiffCandidate]:
        """漏挂检测（``diff_type=1``）：周期内已完成但未挂任何对账单的业务单据。

        依赖各侧候选池规则，故由绑定提供实现；未提供时返回空列表。
        """
        binding = cls.binding_or_raise(recon_kind)
        if binding.orphan_detector is None:
            return []
        return await binding.orphan_detector(db, dict(filters))

    # ------------------------------------------------------------------
    # 差异留痕
    # ------------------------------------------------------------------
    @classmethod
    async def record_diffs(
        cls,
        db: AsyncSession,
        *,
        recon_kind: str,
        recon_id: Optional[int],
        candidates: Sequence[DiffCandidate],
        operator_id: Optional[int] = None,
    ) -> List[ReconDiff]:
        """把差异候选写入 ``biz_recon_diff``，已存在的待处置同类差异只更新现值。

        幂等由 ``dedup_key`` 保证：同一 (对账单, 业务单, 差异类型) 在待处置期间
        只有一条记录，反复核对不会刷出一堆重复待办。
        """
        if not candidates:
            return []
        binding = cls.binding_or_none(recon_kind)
        biz_doc_type = (
            binding.biz_doc_type if binding
            else BizDocType.WAYBILL
        )
        now = datetime.now()
        rows: List[ReconDiff] = []
        raised = 0

        # 已存在的待处置差异（含人工登记）参与去重：同一 dedup_key 只更新现值，
        # 否则会撞 uk_rdiff_dedup 唯一索引
        existing = await cls._load_open_diffs(db, recon_kind, recon_id)
        for c in candidates:
            key = ReconDiff.build_dedup_key(
                recon_kind, recon_id, c.biz_doc_id, c.diff_type,
            )
            row = existing.get(key)
            if row is not None:
                row.actual_value = c.actual_value
                row.expected_value = c.expected_value
                row.diff_amount = c.diff_amount
                row.severity = c.resolved_severity()
                row.link_id = c.link_id if c.link_id is not None else row.link_id
                row.detected_at = now
                row.detected_by = operator_id
                rows.append(row)
                continue
            row = ReconDiff(
                recon_kind=recon_kind,
                recon_id=recon_id,
                link_id=c.link_id,
                biz_doc_type=biz_doc_type,
                biz_doc_id=c.biz_doc_id,
                biz_doc_no=c.biz_doc_no,
                diff_type=c.diff_type,
                severity=c.resolved_severity(),
                expected_value=c.expected_value,
                actual_value=c.actual_value,
                diff_amount=c.diff_amount,
                detected_at=now,
                detected_by=operator_id,
                status=DiffStatus.OPEN,
                is_manual=0,
                dedup_key=key,
            )
            db.add(row)
            existing[key] = row
            rows.append(row)
            raised += 1
        await db.flush()

        if raised and recon_id:
            await FinanceDocEventWriter.write(
                db,
                doc_kind=recon_kind,
                doc_id=recon_id,
                event_type=FinanceEventType.DIFF_RAISED,
                operator_id=operator_id,
                reason=f"核对检出 {raised} 项新差异",
                payload_snapshot={
                    "newDiffCount": raised,
                    "diffTypes": sorted({
                        int(c.diff_type) for c in candidates
                    }),
                },
            )
        return rows

    @classmethod
    async def list_diffs(
        cls,
        db: AsyncSession,
        *,
        recon_kind: str,
        recon_id: Optional[int] = None,
        status: Optional[int] = None,
        severity: Optional[int] = None,
        only_open: bool = False,
        limit: int = 200,
    ) -> List[ReconDiff]:
        """差异列表（详情页「一致性核对」区块与对账工作台待办用）。

        默认按「未处置在前、检出时间倒序」排，对账岗打开就是待办清单。
        """
        stmt = select(ReconDiff).where(
            ReconDiff.recon_kind == recon_kind,
            ReconDiff.is_deleted == 0,
        )
        if recon_id is not None:
            stmt = stmt.where(ReconDiff.recon_id == recon_id)
        if only_open:
            stmt = stmt.where(ReconDiff.status == DiffStatus.OPEN)
        elif status is not None:
            stmt = stmt.where(ReconDiff.status == status)
        if severity is not None:
            stmt = stmt.where(ReconDiff.severity == severity)
        r = await db.execute(
            stmt.order_by(
                ReconDiff.status.asc(),
                ReconDiff.severity.desc(),
                ReconDiff.id.desc(),
            ).limit(max(1, int(limit)))
        )
        return list(r.scalars().all())

    @classmethod
    async def _load_open_diffs(
        cls, db: AsyncSession, recon_kind: str, recon_id: Optional[int],
    ) -> Dict[str, ReconDiff]:
        r = await db.execute(
            select(ReconDiff).where(
                ReconDiff.recon_kind == recon_kind,
                ReconDiff.recon_id == recon_id,
                ReconDiff.status == DiffStatus.OPEN,
                ReconDiff.is_deleted == 0,
            )
        )
        return {
            row.dedup_key: row
            for row in r.scalars().all()
            if row.dedup_key
        }

    @classmethod
    async def _invalidate_stale(
        cls,
        db: AsyncSession,
        recon_kind: str,
        recon_id: int,
        candidates: Sequence[DiffCandidate],
    ) -> int:
        """本轮未再检出的待处置差异自动置失效（业务侧已改回一致）。

        人工登记的差异（``is_manual=1``）不在自动失效范围内：那是对账岗主动记下的
        待办，核对器没检出不代表它已经解决。
        """
        alive = {
            ReconDiff.build_dedup_key(
                recon_kind, recon_id, c.biz_doc_id, c.diff_type,
            )
            for c in candidates
        }
        existing = await cls._load_open_diffs(db, recon_kind, recon_id)
        stale = [
            row for key, row in existing.items()
            if key not in alive and int(row.is_manual or 0) == 0
        ]
        for row in stale:
            cls._close(
                row, DiffStatus.INVALID, resolution="业务数据已与对账行一致",
            )
        if stale:
            await db.flush()
        return len(stale)

    @staticmethod
    def _close(
        row: ReconDiff,
        status: int,
        *,
        resolution: Optional[str] = None,
        operator_id: Optional[int] = None,
    ) -> None:
        """关闭一条差异：置终态、写处置信息、释放 ``dedup_key`` 占用。"""
        row.status = status
        row.resolution = (resolution or "")[:255] or None
        row.resolved_by = operator_id
        row.resolved_at = datetime.now()
        row.dedup_key = None

    # ------------------------------------------------------------------
    # 处置
    # ------------------------------------------------------------------
    @classmethod
    async def raise_manual_diff(
        cls,
        db: AsyncSession,
        *,
        recon_kind: str,
        recon_id: int,
        candidate: DiffCandidate,
        operator_id: Optional[int] = None,
    ) -> ReconDiff:
        """对账岗手工登记一条差异（对账工作台「登记差异」）。

        与核对器检出的差异同表同流程，只是 ``is_manual=1``，不会被下一轮核对
        自动置失效。
        """
        rows = await cls.record_diffs(
            db,
            recon_kind=recon_kind,
            recon_id=recon_id,
            candidates=[candidate],
            operator_id=operator_id,
        )
        row = rows[0]
        row.is_manual = 1
        await db.flush()
        binding = cls.binding_or_none(recon_kind)
        if binding is not None:
            await cls._refresh_counters(db, binding, [recon_id])
        return row

    @classmethod
    async def resolve_diff(
        cls,
        db: AsyncSession,
        diff_id: int,
        *,
        status: int,
        resolution: str,
        operator_id: Optional[int] = None,
    ) -> ReconDiff:
        """处置单条差异（协商确认 / 回灌消解）。"""
        if status not in DiffStatus.CLOSED:
            raise BizException("差异处置结果不合法，请重新选择处置方式")
        if not (resolution or "").strip():
            raise BizException("请填写差异处置说明，便于事后追溯")

        r = await db.execute(
            select(ReconDiff).where(
                ReconDiff.id == diff_id, ReconDiff.is_deleted == 0,
            )
        )
        row = r.scalar_one_or_none()
        if row is None:
            raise BizException("差异记录不存在或已被处理")
        if int(row.status) != DiffStatus.OPEN:
            raise BizException(
                f"该差异已是「{DiffStatus.LABELS.get(int(row.status), '已处置')}」，"
                "无需重复处置"
            )

        cls._close(
            row, status, resolution=resolution.strip(), operator_id=operator_id,
        )
        await db.flush()

        if row.recon_id:
            await FinanceDocEventWriter.write(
                db,
                doc_kind=row.recon_kind,
                doc_id=int(row.recon_id),
                event_type=FinanceEventType.DIFF_CLOSED,
                operator_id=operator_id,
                reason=f"{diff_label(row.diff_type)}差异已处置：{resolution.strip()}",
                payload_snapshot={
                    "diffId": int(row.id),
                    "diffType": int(row.diff_type),
                    "status": int(status),
                },
            )
            binding = cls.binding_or_none(row.recon_kind)
            if binding is not None:
                await cls._refresh_counters(db, binding, [int(row.recon_id)])
        return row

    @classmethod
    async def assert_confirmable(
        cls, db: AsyncSession, *, recon_kind: str, recon_id: int,
    ) -> None:
        """对账单 0→2 确认前置校验：存在阻塞级未处置差异则拒绝。

        直接查差异表计数，不重跑全量比对——确认动作不应因核对而变慢。
        """
        r = await db.execute(
            select(func.count(ReconDiff.id)).where(
                ReconDiff.recon_kind == recon_kind,
                ReconDiff.recon_id == recon_id,
                ReconDiff.status == DiffStatus.OPEN,
                ReconDiff.severity == DiffSeverity.BLOCKING,
                ReconDiff.is_deleted == 0,
            )
        )
        blocking = int(r.scalar() or 0)
        if blocking:
            raise BizException(
                f"还有 {blocking} 项差异需要处理才能确认对账单；"
                "请到对账工作台逐项处理，或申请带差异强制确认"
            )

    @classmethod
    async def force_confirm(
        cls,
        db: AsyncSession,
        *,
        recon_kind: str,
        recon_id: int,
        reason: str,
        operator_id: Optional[int] = None,
    ) -> int:
        """强制确认：放行阻塞级待处置差异并留痕，返回被放行条数。

        与「协商确认」的关键区别是**不清除差异痕迹**：协商确认表示账已对平，
        强制确认表示账没对平但先走流程，后者必须在报表里可筛出来——痕迹靠
        ``status=3 已强制放行`` 与主表 ``diff_forced_count`` 冗余保留，不靠让
        ``diff_open_count`` 停留在旧值。

        提示级差异不放行：它们本来就不阻塞确认，留着继续提醒。
        """
        text = (reason or "").strip()
        if len(text) < FORCE_CONFIRM_REASON_MIN_LEN:
            raise BizException(
                f"强制确认必须说明原因，且不少于 {FORCE_CONFIRM_REASON_MIN_LEN} 个字"
            )

        r = await db.execute(
            select(ReconDiff).where(
                ReconDiff.recon_kind == recon_kind,
                ReconDiff.recon_id == recon_id,
                ReconDiff.status == DiffStatus.OPEN,
                ReconDiff.severity == DiffSeverity.BLOCKING,
                ReconDiff.is_deleted == 0,
            )
        )
        rows = list(r.scalars().all())
        if not rows:
            raise BizException("当前没有阻塞确认的差异，直接确认即可，无需强制确认")

        snapshot = [
            {
                "diffId": int(row.id),
                "diffType": int(row.diff_type),
                "bizDocNo": row.biz_doc_no,
                "diffAmount": (
                    float(row.diff_amount) if row.diff_amount is not None else None
                ),
            }
            for row in rows
        ]
        for row in rows:
            cls._close(
                row, DiffStatus.FORCED,
                resolution=f"强制确认放行：{text}",
                operator_id=operator_id,
            )
        await db.flush()

        await FinanceDocEventWriter.write(
            db,
            doc_kind=recon_kind,
            doc_id=recon_id,
            event_type=FinanceEventType.FORCE_CONFIRM,
            operator_id=operator_id,
            reason=text,
            payload_snapshot={"forcedCount": len(rows), "diffs": snapshot},
        )
        binding = cls.binding_or_none(recon_kind)
        if binding is not None:
            await cls._refresh_counters(db, binding, [recon_id])
        return len(rows)

    @classmethod
    async def invalidate_by_recon(
        cls,
        db: AsyncSession,
        *,
        recon_kind: str,
        recon_id: int,
        reason: str = "对账单已撤销",
    ) -> int:
        """对账单撤销时，名下待处置差异全部失效。"""
        r = await db.execute(
            select(ReconDiff).where(
                ReconDiff.recon_kind == recon_kind,
                ReconDiff.recon_id == recon_id,
                ReconDiff.status == DiffStatus.OPEN,
                ReconDiff.is_deleted == 0,
            )
        )
        rows = list(r.scalars().all())
        for row in rows:
            cls._close(row, DiffStatus.INVALID, resolution=reason)
        if rows:
            await db.flush()
        return len(rows)

    # ------------------------------------------------------------------
    # 互斥校验（统一收口，见文档 09 §4.3）
    # ------------------------------------------------------------------
    @staticmethod
    async def assert_task_settle_exclusive(
        db: AsyncSession, task_id: int, *, intent: str,
    ) -> None:
        """任务级最终结算单 与 承运商对账 二选一。

        - ``intent='carrier_recon'``：要把任务挂入承运商对账单，若已有已支付的
          最终结算单则拒绝；
        - ``intent='final_settle'``：要为任务创建最终结算单，若任务已挂对账则拒绝。

        候选池过滤、对账单加行、费用单创建三个入口共用本方法。此前三处各写一遍，
        任何一处漏改就会出现「A 路径拦住、B 路径放过」的重复结算事故。
        """
        from app.modules.client.models.task.task import Task
        from app.modules.client.models.task.task_finance_doc import TaskFinanceDoc
        from app.modules.client.services.finance.base.constants import DocType
        from app.modules.client.services.finance.base.finance_state_machine import (
            FIN_PAID,
        )

        if intent not in ("carrier_recon", "final_settle"):
            raise BizException("互斥校验意图不合法，请联系管理员")

        if intent == "carrier_recon":
            r = await db.execute(
                select(func.count(TaskFinanceDoc.id)).where(
                    TaskFinanceDoc.task_id == task_id,
                    TaskFinanceDoc.is_deleted == 0,
                    TaskFinanceDoc.doc_type == DocType.SETTLE,
                    TaskFinanceDoc.is_final == 1,
                    TaskFinanceDoc.status == FIN_PAID,
                )
            )
            if int(r.scalar() or 0) > 0:
                raise BizException(
                    "该任务已按任务级最终结算单付过款，不能再纳入承运商对账，"
                    "以免重复结算"
                )
            return

        r = await db.execute(
            select(Task.is_recon_bound).where(
                Task.id == task_id, Task.is_deleted == 0,
            )
        )
        bound = r.scalar_one_or_none()
        if bound is None:
            raise BizException("任务单不存在")
        if int(bound or 0) == 1:
            raise BizException(
                "该任务已纳入承运商对账，不能再开最终结算单，以免重复结算"
            )

    # ------------------------------------------------------------------
    # 内部工具
    # ------------------------------------------------------------------
    @staticmethod
    async def _get_recon_or_404(
        db: AsyncSession, binding: ReconBinding, recon_id: int,
    ) -> Any:
        recon = binding.recon_model
        r = await db.execute(
            select(recon).where(recon.id == recon_id, recon.is_deleted == 0)
        )
        row = r.scalar_one_or_none()
        if row is None:
            raise BizException("对账单不存在")
        return row

    @staticmethod
    async def _load_lines(
        db: AsyncSession, binding: ReconBinding, recon_id: int,
    ) -> List[Any]:
        link = binding.link_model
        r = await db.execute(
            select(link)
            .where(binding.recon_col() == recon_id, link.is_deleted == 0)
            .order_by(link.id.asc())
        )
        return list(r.scalars().all())

    @classmethod
    async def _refresh_counters(
        cls, db: AsyncSession, binding: ReconBinding, recon_ids: Sequence[int],
    ) -> None:
        """刷新对账主表的脏行数与差异数冗余（三个计数列）。"""
        if not recon_ids:
            return
        recon = binding.recon_model
        link = binding.link_model
        for rid in set(int(x) for x in recon_ids):
            r = await db.execute(
                select(func.count(link.id)).where(
                    binding.recon_col() == rid,
                    link.is_deleted == 0,
                    getattr(link, DIRTY_FLAG_COL) == 1,
                )
            )
            dirty = int(r.scalar() or 0)
            r = await db.execute(
                select(ReconDiff.status, func.count(ReconDiff.id))
                .where(
                    ReconDiff.recon_kind == binding.recon_kind,
                    ReconDiff.recon_id == rid,
                    ReconDiff.status.in_(
                        (DiffStatus.OPEN, DiffStatus.FORCED)
                    ),
                    ReconDiff.is_deleted == 0,
                )
                .group_by(ReconDiff.status)
            )
            by_status = {int(s): int(c) for s, c in r.all()}
            await db.execute(
                update(recon)
                .where(recon.id == rid)
                .values(**{
                    DIRTY_COUNT_COL: dirty,
                    DIFF_OPEN_COUNT_COL: by_status.get(DiffStatus.OPEN, 0),
                    DIFF_FORCED_COUNT_COL: by_status.get(DiffStatus.FORCED, 0),
                })
            )
        await db.flush()
