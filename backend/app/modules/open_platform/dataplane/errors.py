"""数据面错误：对外用稳定错误码 + 友好文案，不泄露内部细节。"""


class OpenApiError(Exception):
    def __init__(self, http_status: int, error_code: str, message: str):
        self.http_status = http_status
        self.error_code = error_code
        self.message = message
        super().__init__(message)


# 常见错误（error_code 对外稳定，message 面向集成方）
def unauthorized(msg: str = "凭证无效或已过期，请检查密钥配置") -> OpenApiError:
    return OpenApiError(401, "UNAUTHORIZED", msg)


def forbidden_scope(cap: str) -> OpenApiError:
    return OpenApiError(403, "SCOPE_DENIED", f"当前凭证未被授权使用能力「{cap}」")


def forbidden_ip() -> OpenApiError:
    return OpenApiError(403, "IP_NOT_ALLOWED", "来源 IP 不在白名单内")


def replay() -> OpenApiError:
    return OpenApiError(401, "REPLAY_DETECTED", "请求已过期或重复，请重新签名后重试")


def rate_limited() -> OpenApiError:
    return OpenApiError(429, "RATE_LIMITED", "调用过于频繁，请稍后重试")


def not_found_cap() -> OpenApiError:
    return OpenApiError(404, "CAPABILITY_NOT_FOUND", "能力不存在或已下线")


def bad_request(msg: str) -> OpenApiError:
    return OpenApiError(400, "BAD_REQUEST", msg)
