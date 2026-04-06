"""官网自助注册策略 API 模型"""

from pydantic import BaseModel, ConfigDict, Field


class OpenRegisterPolicyOut(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    version_code: str = Field(alias="versionCode")
    trial_days: int = Field(alias="trialDays")


class OpenRegisterPolicyUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    version_code: str = Field(alias="versionCode")
    trial_days: int = Field(ge=0, le=3650, alias="trialDays")
