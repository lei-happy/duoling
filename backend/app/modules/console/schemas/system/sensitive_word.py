"""敏感词库 Schemas（camelCase，对齐前端）"""

from typing import List, Optional

from pydantic import BaseModel, Field

from app.modules.console.models.system.sensitive_word import (
    SensitiveWordAction,
    SensitiveWordCategory,
    SensitiveWordScope,
)


class SensitiveWordCreate(BaseModel):
    """新增敏感词"""

    word: str
    category: int = SensitiveWordCategory.OTHER
    action: int = SensitiveWordAction.BLOCK
    scope: str = SensitiveWordScope.ALL
    remark: Optional[str] = None


class SensitiveWordUpdate(BaseModel):
    """修改敏感词"""

    id: int
    word: Optional[str] = None
    category: Optional[int] = None
    action: Optional[int] = None
    scope: Optional[str] = None
    status: Optional[int] = None
    remark: Optional[str] = None


class SensitiveWordIds(BaseModel):
    """批量操作入参"""

    ids: List[int] = Field(default_factory=list)


class SensitiveWordStatusUpdate(SensitiveWordIds):
    """批量启停"""

    status: int


class SensitiveWordBatchImport(BaseModel):
    """批量导入

    ``words`` 支持换行 / 逗号分隔的文本由前端拆好后传数组，后端只做清洗与去重。
    """

    words: List[str] = Field(default_factory=list)
    category: int = SensitiveWordCategory.OTHER
    action: int = SensitiveWordAction.BLOCK
    scope: str = SensitiveWordScope.ALL


class SensitiveWordTest(BaseModel):
    """试测文本"""

    text: str
    scope: str = SensitiveWordScope.ECOSYSTEM
