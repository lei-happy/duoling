"""服务平台（生态）租户库模型

跨租户的撮合数据全部在平台库 ``sys_eco_*``（见
app/modules/console/models/ecosystem/），租户库只保留一张关联表。
"""

from app.modules.client.models.ecosystem.post_ref import BizEcoPostRef

__all__ = ["BizEcoPostRef"]
