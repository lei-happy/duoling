"""
运营后台：汽车之家同步任务 API 模型
"""

from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class AutohomeSyncTriggerBody(BaseModel):
    model_config = ConfigDict(extra="ignore")

    jobType: str = Field(default="probe", description="probe | full")
    autohomeSeriesId: Optional[int] = Field(
        default=4851, description="探测任务使用的汽车之家车系ID"
    )
    maxBrands: Optional[int] = Field(
        default=None,
        description="全量时最多处理品牌数，不传表示全部（默认可售 state=1）",
    )
    delayMs: int = Field(
        default=400,
        ge=80,
        le=8000,
        description="全量时请求间隔毫秒，降低对汽车之家压力",
    )
    includeInactiveBrands: bool = Field(
        default=False,
        description="全量时是否包含未在售品牌（state!=1）",
    )
    fetchSpecs: bool = Field(
        default=True,
        description="全量时是否拉取参配页并写入能源类型、尺寸、轴距、整备质量等（每车系额外请求）",
    )


class AutohomeSyncJobOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    jobId: int
    jobType: str
    status: str
    progressPct: int
    payloadJson: Optional[str] = None
    logText: Optional[str] = None
    errorMessage: Optional[str] = None
    createTime: Optional[str] = None
    lastUpdateTime: Optional[str] = None

    @classmethod
    def from_row(cls, row: Any) -> "AutohomeSyncJobOut":
        return cls(
            jobId=row.job_id,
            jobType=row.job_type,
            status=row.status,
            progressPct=row.progress_pct,
            payloadJson=row.payload_json,
            logText=row.log_text,
            errorMessage=row.error_message,
            createTime=row.create_time.isoformat(sep=" ", timespec="seconds")
            if row.create_time
            else None,
            lastUpdateTime=row.last_update_time.isoformat(sep=" ", timespec="seconds")
            if row.last_update_time
            else None,
        )
