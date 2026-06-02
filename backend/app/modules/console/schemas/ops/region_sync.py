"""
运营后台：行政区域高德同步任务 API 模型
"""

from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class RegionSyncTriggerBody(BaseModel):
    model_config = ConfigDict(extra="ignore")

    maxConcurrent: Optional[int] = Field(
        default=None,
        ge=1,
        le=10,
        description="并发请求数，不传则使用服务端默认配置",
    )
    requestDelayMs: Optional[int] = Field(
        default=None,
        ge=0,
        le=5000,
        description="请求间隔毫秒，不传则使用服务端默认配置",
    )


class RegionSyncJobOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    jobId: int
    status: str
    progressPct: int
    payloadJson: Optional[str] = None
    logText: Optional[str] = None
    errorMessage: Optional[str] = None
    totalCount: Optional[int] = None
    createTime: Optional[str] = None
    lastUpdateTime: Optional[str] = None

    @classmethod
    def from_row(cls, row: Any) -> "RegionSyncJobOut":
        return cls(
            jobId=row.job_id,
            status=row.status,
            progressPct=row.progress_pct,
            payloadJson=row.payload_json,
            logText=row.log_text,
            errorMessage=row.error_message,
            totalCount=row.total_count,
            createTime=row.create_time.isoformat(sep=" ", timespec="seconds")
            if row.create_time
            else None,
            lastUpdateTime=row.last_update_time.isoformat(sep=" ", timespec="seconds")
            if row.last_update_time
            else None,
        )
