"""
阿里云短信认证客户端（DYPNS 号码认证服务）
封装 SendSmsVerifyCode 接口，提供验证码短信发送能力
"""

import json
from typing import Optional

from alibabacloud_dypnsapi20170525.client import Client
from alibabacloud_dypnsapi20170525 import models as dypns_models
from alibabacloud_tea_openapi import models as open_api_models
from loguru import logger

from app.core.config import get_settings

TEMPLATE_MAP = {
    1: "100001",  # 登录/注册
    2: "100003",  # 重置密码
    3: "100004",  # 变更手机号（预留）
    4: "100001",  # 企业注册（与登录共用模板，可按需改为独立模板号）
}

PURPOSE_LABELS = {
    1: "登录",
    2: "重置密码",
    3: "变更手机号",
    4: "企业注册",
}


class AliyunSmsClient:
    """阿里云 DYPNS 短信验证码客户端（单例）"""

    _client: Optional[Client] = None

    @classmethod
    def _get_client(cls) -> Client:
        if cls._client is None:
            settings = get_settings()
            config = open_api_models.Config(
                access_key_id=settings.ALIYUN_ACCESS_KEY_ID,
                access_key_secret=settings.ALIYUN_ACCESS_KEY_SECRET,
            )
            config.endpoint = "dypnsapi.aliyuncs.com"
            cls._client = Client(config)
        return cls._client

    @classmethod
    def send_verify_code(cls, phone: str, code: str, purpose: int) -> None:
        """
        发送短信验证码。

        Args:
            phone: 目标手机号
            code: 验证码（由业务层生成）
            purpose: 用途（1-登录 2-重置密码 3-变更手机号 4-企业注册）

        Raises:
            ValueError: purpose 无对应模板
            RuntimeError: 阿里云接口调用失败
        """
        settings = get_settings()

        if not settings.ALIYUN_SMS_ENABLED:
            logger.info(f"短信发送已关闭(SMS_ENABLED=false)，跳过发送 | phone={phone}")
            return

        template_code = TEMPLATE_MAP.get(purpose)
        if not template_code:
            raise ValueError(f"未知的验证码用途: {purpose}")

        purpose_label = PURPOSE_LABELS.get(purpose, str(purpose))
        template_param = json.dumps({"code": code, "min": "5"})

        request = dypns_models.SendSmsVerifyCodeRequest(
            phone_number=phone,
            sign_name=settings.ALIYUN_SMS_SIGN_NAME,
            template_code=template_code,
            template_param=template_param,
            code_length=6,
            valid_time=300,
            interval=60,
        )

        try:
            client = cls._get_client()
            response = client.send_sms_verify_code(request)
            body = response.body

            if body.code != "OK":
                logger.error(
                    f"短信发送失败 | phone={phone} purpose={purpose_label} "
                    f"code={body.code} message={body.message}"
                )
                raise RuntimeError(f"短信发送失败: {body.message}")

            biz_id = body.model.biz_id if body.model else None
            logger.info(
                f"短信发送成功 | phone={phone} purpose={purpose_label} "
                f"biz_id={biz_id}"
            )

        except RuntimeError:
            raise
        except Exception as e:
            logger.error(f"短信发送异常 | phone={phone} purpose={purpose_label} error={e}")
            raise RuntimeError(f"短信服务调用异常: {e}") from e
