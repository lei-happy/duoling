"""初始化敏感词库（sys_sensitive_word，upsert 模式）

WORD_DEFS 是**初始词库**的来源，不是唯一真实来源：词库上线后由运营在
后台自行增删（运营平台 → 内容风控 → 敏感词库）。因此本脚本只做「缺则补」：

- 词不存在 → 新增
- 词已存在（含已停用/已软删）→ **跳过**，绝不覆盖

跳过而非覆盖是刻意的：运营可能已经把某个词停用了（因为它在误伤），
每次部署又把它改回启用，会让运营的调整反复失效、且无从察觉。

用法：
    python scripts/seed/seed_sensitive_words.py
    python scripts/seed/seed_sensitive_words.py --dry-run
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.modules.console.models.system.sensitive_word import (
    SensitiveWordAction,
    SensitiveWordCategory,
    SensitiveWordScope,
)

BLOCK = SensitiveWordAction.BLOCK
REVIEW = SensitiveWordAction.REVIEW

CONTRABAND = SensitiveWordCategory.CONTRABAND
DIVERSION = SensitiveWordCategory.DIVERSION
FRAUD = SensitiveWordCategory.FRAUD
OTHER = SensitiveWordCategory.OTHER

ALL_SCOPE = SensitiveWordScope.ALL
ECO_SCOPE = SensitiveWordScope.ECOSYSTEM

# ============================================================
# 初始词库
# 格式: (word, category, action, scope, remark)
#
# 只收录与物流业务强相关、且判断明确的词。政治 / 色情类通用词库属于运营
# 资产，不放在代码仓库里——由运营通过后台「批量导入」维护。
# ============================================================
WORD_DEFS = [
    # --- 违禁品：命中后给「这类货物需要专门资质」的专门文案 ---
    ("危化品", CONTRABAND, BLOCK, ECO_SCOPE, "危险化学品运输需专门资质"),
    ("危险化学品", CONTRABAND, BLOCK, ECO_SCOPE, None),
    ("易燃易爆", CONTRABAND, BLOCK, ECO_SCOPE, None),
    ("爆炸物", CONTRABAND, BLOCK, ECO_SCOPE, None),
    ("放射性", CONTRABAND, BLOCK, ECO_SCOPE, None),
    ("剧毒", CONTRABAND, BLOCK, ECO_SCOPE, None),
    ("活体", CONTRABAND, BLOCK, ECO_SCOPE, "活体运输不在大厅支持范围"),
    ("活禽", CONTRABAND, BLOCK, ECO_SCOPE, None),
    ("活畜", CONTRABAND, BLOCK, ECO_SCOPE, None),
    ("枪支", CONTRABAND, BLOCK, ALL_SCOPE, None),
    ("弹药", CONTRABAND, BLOCK, ALL_SCOPE, None),
    ("管制刀具", CONTRABAND, BLOCK, ALL_SCOPE, None),
    ("毒品", CONTRABAND, BLOCK, ALL_SCOPE, None),
    ("冰毒", CONTRABAND, BLOCK, ALL_SCOPE, None),
    ("海洛因", CONTRABAND, BLOCK, ALL_SCOPE, None),
    ("走私", CONTRABAND, BLOCK, ALL_SCOPE, None),
    ("象牙", CONTRABAND, BLOCK, ALL_SCOPE, None),
    # --- 违法违规经营 ---
    ("代开发票", FRAUD, BLOCK, ALL_SCOPE, None),
    ("发票代开", FRAUD, BLOCK, ALL_SCOPE, None),
    ("虚开发票", FRAUD, BLOCK, ALL_SCOPE, None),
    ("洗钱", FRAUD, BLOCK, ALL_SCOPE, None),
    ("假证", FRAUD, BLOCK, ALL_SCOPE, None),
    ("套牌", FRAUD, BLOCK, ALL_SCOPE, "套牌车运输属违法"),
    ("赌博", OTHER, BLOCK, ALL_SCOPE, None),
    ("博彩", OTHER, BLOCK, ALL_SCOPE, None),
    # --- 竞品导流：引导用户离开平台私下成交 ---
    ("加微信", DIVERSION, BLOCK, ECO_SCOPE, "引导私下联系"),
    ("私聊", DIVERSION, REVIEW, ECO_SCOPE, "可能是正常表述，先转人工"),
    ("站外", DIVERSION, REVIEW, ECO_SCOPE, None),
    ("线下交易", DIVERSION, REVIEW, ECO_SCOPE, None),
    # --- 需人工确认：不阻断，标红进审核队列 ---
    ("押金", FRAUD, REVIEW, ECO_SCOPE, "预收押金是常见骗局特征，人工确认"),
    ("先打款", FRAUD, REVIEW, ECO_SCOPE, None),
    ("保证金", FRAUD, REVIEW, ECO_SCOPE, "正常业务也会用，仅标红"),
]


def seed(dry_run: bool = False) -> dict:
    settings = get_settings()
    engine = create_engine(settings.platform_db_url_sync)
    added = skipped = 0

    try:
        with Session(engine) as session:
            for word, category, action, scope, remark in WORD_DEFS:
                existing = session.execute(
                    text(
                        "SELECT id FROM sys_sensitive_word "
                        "WHERE word = :w AND scope = :s LIMIT 1"
                    ),
                    {"w": word, "s": scope},
                ).scalar_one_or_none()

                if existing is not None:
                    skipped += 1
                    continue

                if not dry_run:
                    session.execute(
                        text(
                            "INSERT INTO sys_sensitive_word "
                            "(word, category, action, scope, status, hit_count, "
                            " remark, is_deleted) "
                            "VALUES (:w, :c, :a, :s, 1, 0, :r, 0)"
                        ),
                        {
                            "w": word, "c": category, "a": action,
                            "s": scope, "r": remark,
                        },
                    )
                added += 1

            if dry_run:
                session.rollback()
            else:
                session.commit()
    finally:
        engine.dispose()

    return {"added": added, "skipped": skipped}


def main():
    dry_run = "--dry-run" in sys.argv
    if dry_run:
        print("[INFO] dry-run 模式，不会写库")

    result = seed(dry_run=dry_run)
    print(
        f"[OK] 敏感词库同步完成：新增 {result['added']} 个，"
        f"已存在跳过 {result['skipped']} 个"
    )
    print("[TIP] 政治 / 色情等通用词库请由运营在后台「批量导入」维护")


if __name__ == "__main__":
    main()
