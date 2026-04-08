"""
运营后台：经销商同步任务 API 模型
"""

from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class DealerSyncTriggerBody(BaseModel):
    model_config = ConfigDict(extra="ignore")

    maxCities: Optional[int] = Field(
        default=None,
        description="最多处理城市数，不传或 0 表示全部",
    )
    delayMs: int = Field(
        default=400,
        ge=80,
        le=8000,
        description="请求间隔毫秒，降低对汽车之家压力",
    )


class DealerSyncJobOut(BaseModel):
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
    def from_row(cls, row: Any) -> "DealerSyncJobOut":
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
