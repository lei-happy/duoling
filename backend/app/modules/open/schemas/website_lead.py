"""
官网留资 Schemas
"""

import re
from typing import Dict, Optional

from pydantic import BaseModel, Field, field_validator

_CN_MOBILE = re.compile(r"^1[3-9]\d{9}$")

FLEET_SIZES = {"lt10", "10-30", "30-100", "gt100"}


class LeadSubmitRequest(BaseModel):
    """官网留资表单提交"""

    company_name: str = Field(..., min_length=2, max_length=128, description="企业名称")
    contact_person: str = Field(..., min_length=1, max_length=32, description="联系人")
    contact_phone: str = Field(..., description="联系手机号")

    fleet_size: Optional[str] = Field(None, max_length=16, description="自有板车规模")
    pain_point: Optional[str] = Field(None, max_length=255, description="最头疼的一件事")
    profile_answers: Optional[Dict[str, str]] = Field(
        None, description="自测画像题 P1-P3 作答"
    )

    stage_band: Optional[str] = Field(None, max_length=8, description="测评档位 L1-L8")
    stage_name: Optional[str] = Field(None, max_length=32, description="档位名称")
    total_score: Optional[int] = Field(None, ge=0, le=80, description="自测总分")
    dim_a: Optional[int] = Field(None, ge=0, le=20)
    dim_b: Optional[int] = Field(None, ge=0, le=20)
    dim_c: Optional[int] = Field(None, ge=0, le=20)
    dim_d: Optional[int] = Field(None, ge=0, le=20)

    source_page: Optional[str] = Field(None, max_length=64, description="提交所在页面")

    # 蜜罐：真人看不见这个字段，只有自动填表脚本会填
    website: Optional[str] = Field(None, max_length=255, description="留空即可")

    @field_validator("contact_phone")
    @classmethod
    def validate_mobile(cls, v: str) -> str:
        if not _CN_MOBILE.match((v or "").strip()):
            raise ValueError("请输入正确的手机号码")
        return v.strip()

    @field_validator("company_name", "contact_person")
    @classmethod
    def strip_text(cls, v: str) -> str:
        return (v or "").strip()

    @field_validator("fleet_size")
    @classmethod
    def validate_fleet_size(cls, v: Optional[str]) -> Optional[str]:
        if v and v not in FLEET_SIZES:
            raise ValueError("请选择车队规模")
        return v


class LeadSubmitResponse(BaseModel):
    """留资提交结果"""

    accepted: bool = True
