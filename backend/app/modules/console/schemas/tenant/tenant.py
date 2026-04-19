"""
租户管理 Schemas
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


# ============================================================
# 租户 CRUD
# ============================================================

class TenantCreate(BaseModel):
    """创建租户"""
    tenantName: str = Field(description="企业名称")
    shortName: Optional[str] = Field(default=None, description="企业简称")
    contactPerson: Optional[str] = Field(default=None, description="联系人")
    contactPhone: Optional[str] = Field(default=None, description="联系电话")
    contactEmail: Optional[str] = Field(default=None, description="联系邮箱")
    province: Optional[str] = Field(default=None, description="省份")
    city: Optional[str] = Field(default=None, description="城市")
    address: Optional[str] = Field(default=None, description="详细地址")
    licenseNo: Optional[str] = Field(default=None, description="营业执照号")
    remark: Optional[str] = Field(default=None, description="备注")
    sourceChannel: Optional[str] = Field(default=None, description="来源渠道: website/console/referral")
    referrerCode: Optional[str] = Field(default=None, description="推荐人企业编码")


class TenantUpdate(BaseModel):
    """更新租户"""
    id: int = Field(description="租户ID")
    tenantName: Optional[str] = Field(default=None, description="企业名称")
    shortName: Optional[str] = Field(default=None, description="企业简称")
    contactPerson: Optional[str] = Field(default=None, description="联系人")
    contactPhone: Optional[str] = Field(default=None, description="联系电话")
    contactEmail: Optional[str] = Field(default=None, description="联系邮箱")
    province: Optional[str] = Field(default=None, description="省份")
    city: Optional[str] = Field(default=None, description="城市")
    address: Optional[str] = Field(default=None, description="详细地址")
    logo: Optional[str] = Field(default=None, description="企业Logo")
    licenseNo: Optional[str] = Field(default=None, description="营业执照号")
    remark: Optional[str] = Field(default=None, description="备注")


class TenantStatusUpdate(BaseModel):
    """租户状态更新"""
    id: int = Field(description="租户ID")
    status: int = Field(description="状态 0-停用 1-正常")


class TenantOut(BaseModel):
    """租户详情输出"""
    id: int
    tenantCode: str = Field(description="租户编码")
    tenantName: str = Field(description="企业名称")
    shortName: Optional[str] = None
    contactPerson: Optional[str] = None
    contactPhone: Optional[str] = None
    contactEmail: Optional[str] = None
    province: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    logo: Optional[str] = None
    licenseNo: Optional[str] = None
    status: int = Field(description="状态 0-停用 1-正常 2-待审核 3-已过期")
    dbName: Optional[str] = None
    dbInitialized: int = Field(description="数据库是否已初始化")
    expireTime: Optional[str] = None
    remark: Optional[str] = None
    sourceChannel: Optional[str] = None
    referrerCode: Optional[str] = None
    createTime: Optional[str] = None

    @classmethod
    def from_model(cls, t) -> "TenantOut":
        """从 ORM 模型构造"""
        return cls(
            id=t.id,
            tenantCode=t.tenant_code,
            tenantName=t.tenant_name,
            shortName=t.short_name,
            contactPerson=t.contact_person,
            contactPhone=t.contact_phone,
            contactEmail=t.contact_email,
            province=t.province,
            city=t.city,
            address=t.address,
            logo=t.logo,
            licenseNo=t.license_no,
            status=t.status,
            dbName=t.db_name,
            dbInitialized=t.db_initialized,
            expireTime=t.expire_time.strftime("%Y-%m-%d %H:%M:%S") if t.expire_time else None,
            remark=t.remark,
            sourceChannel=t.source_channel,
            referrerCode=t.referrer_code,
            createTime=t.created_at.strftime("%Y-%m-%d %H:%M:%S") if t.created_at else None,
        )


class TenantListOut(BaseModel):
    """租户列表项输出"""
    id: int
    tenantCode: str
    tenantName: str
    shortName: Optional[str] = None
    contactPerson: Optional[str] = None
    contactPhone: Optional[str] = None
    status: int
    dbInitialized: int
    expireTime: Optional[str] = None
    sourceChannel: Optional[str] = None
    referrerCode: Optional[str] = None
    inFollowPool: int = 0
    followRemark: Optional[str] = None
    createTime: Optional[str] = None
    # 当前生效授权（按 sys_tenant_product 实时计算，避免直接读 sys_tenant 反范式字段）
    currentVersionCode: Optional[str] = Field(default=None, description="当前生效版本编码（多条按到期时间最晚优先）")
    currentVersionName: Optional[str] = Field(default=None, description="当前生效版本名称")
    activeProductCount: int = Field(default=0, description="当前有效授权数量（≥2 表示存在叠加，需运营关注）")

    @classmethod
    def from_model(cls, t) -> "TenantListOut":
        """从 ORM 模型构造"""
        return cls(
            id=t.id,
            tenantCode=t.tenant_code,
            tenantName=t.tenant_name,
            shortName=t.short_name,
            contactPerson=t.contact_person,
            contactPhone=t.contact_phone,
            status=t.status,
            dbInitialized=t.db_initialized,
            expireTime=t.expire_time.strftime("%Y-%m-%d %H:%M:%S") if t.expire_time else None,
            sourceChannel=t.source_channel,
            referrerCode=t.referrer_code,
            inFollowPool=t.in_follow_pool,
            followRemark=t.follow_remark,
            createTime=t.created_at.strftime("%Y-%m-%d %H:%M:%S") if t.created_at else None,
        )


class TenantFollowPoolUpdate(BaseModel):
    """跟进池操作"""
    id: int = Field(description="租户ID")
    inFollowPool: int = Field(description="是否加入跟进池 0-移出 1-加入")
    followRemark: Optional[str] = Field(default=None, description="跟进备注")


# ============================================================
# 租户产品授权
# ============================================================

class TenantProductCreate(BaseModel):
    """为租户开通产品授权"""
    versionId: int = Field(description="产品版本ID")
    versionCode: str = Field(description="产品版本编码")
    startTime: Optional[str] = Field(default=None, description="授权开始时间 YYYY-MM-DD HH:MM:SS")
    endTime: Optional[str] = Field(default=None, description="授权到期时间 YYYY-MM-DD HH:MM:SS")
    grantType: Optional[str] = Field(default=None, description="开通类型(数据字典 grant_type)")
    grantRemark: Optional[str] = Field(default=None, description="开通备注")
    replaceActive: bool = Field(
        default=False,
        description=(
            "替换语义：true 时先取消其他生效授权再开通本次授权，"
            "且跳过时间冲突/空档期校验；false 时按叠加语义校验时间线"
        ),
    )


class TenantProductOut(BaseModel):
    """租户产品授权输出"""
    id: int
    tenantId: int
    tenantCode: str
    versionId: int
    versionCode: str
    startTime: Optional[str] = None
    endTime: Optional[str] = None
    grantType: Optional[str] = None
    grantRemark: Optional[str] = None
    status: int
    createTime: Optional[str] = None

    @classmethod
    def from_model(cls, p) -> "TenantProductOut":
        """从 ORM 模型构造"""
        return cls(
            id=p.id,
            tenantId=p.tenant_id,
            tenantCode=p.tenant_code,
            versionId=p.version_id,
            versionCode=p.version_code,
            startTime=p.start_time.strftime("%Y-%m-%d %H:%M:%S") if p.start_time else None,
            endTime=p.end_time.strftime("%Y-%m-%d %H:%M:%S") if p.end_time else None,
            grantType=p.grant_type,
            grantRemark=p.grant_remark,
            status=p.status,
            createTime=p.created_at.strftime("%Y-%m-%d %H:%M:%S") if p.created_at else None,
        )
