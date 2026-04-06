"""
汽车之家页面/数据拉取执行器。

合规说明（decide-source）：若使用网页抓取或逆向接口，须由业务方自行确认不违反
汽车之家用户协议与著作权；本代码仅提供技术能力，优先推荐官方或采购数据渠道。

抗干扰（scrape-resilience）：
- 当前首版使用 httpx 拉取参配页 HTML，无 JS 渲染；若遇反爬或需关闭广告弹窗，可后续
  接入 Playwright，并在导航前后增加：等待主选择器、点击关闭已知遮罩、拦截广告域名、
  失败重试与截图落盘（见 fetch_with_retries）。
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Optional, Tuple

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import db_manager
from app.modules.console.models.ops.autohome_sync_job import AutohomeSyncJob

logger = logging.getLogger(__name__)

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
)

# 与参配抓取一致：主站 www 车系参配对比页
CONFIG_SERIES_URL = "https://www.autohome.com.cn/config/series/{series_id}.html"


async def fetch_with_retries(
    url: str,
    *,
    max_retries: int = 3,
    base_delay_sec: float = 1.5,
    timeout_sec: float = 45.0,
) -> Tuple[int, str]:
    """
    带简单退避的 GET；用于缓解偶发网络/限流（无法处理需 JS 的弹窗，那是 Playwright 阶段）。
    """
    last_exc: Optional[Exception] = None
    async with httpx.AsyncClient(
        follow_redirects=True,
        timeout=timeout_sec,
        headers={
            "User-Agent": DEFAULT_USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9",
        },
    ) as client:
        for attempt in range(1, max_retries + 1):
            try:
                resp = await client.get(url)
                text = resp.text or ""
                return resp.status_code, text
            except Exception as e:
                last_exc = e
                logger.warning("autohome fetch attempt %s failed: %s", attempt, e)
                if attempt < max_retries:
                    await asyncio.sleep(base_delay_sec * attempt)
    raise last_exc  # type: ignore[misc]


def _append_log(current: Optional[str], line: str) -> str:
    prefix = current or ""
    return prefix + line + "\n"


async def _save_job(session: AsyncSession, job: AutohomeSyncJob) -> None:
    await session.flush()
    await session.commit()


async def run_probe_job(job_id: int) -> None:
    """异步探测：请求参配页，记录状态码与正文长度（全量同步后续扩展）。"""
    factory = db_manager._platform_session_factory
    if factory is None:
        logger.error("platform session factory not ready, job %s", job_id)
        return

    async with factory() as session:
        result = await session.execute(
            select(AutohomeSyncJob).where(AutohomeSyncJob.job_id == job_id)
        )
        job = result.scalar_one_or_none()
        if not job:
            return

        job.status = "running"
        job.progress_pct = 5
        job.log_text = _append_log(job.log_text, "[probe] 任务开始")
        await _save_job(session, job)

        series_id = 4851
        if job.payload_json:
            try:
                payload = json.loads(job.payload_json)
                if payload.get("autohomeSeriesId") is not None:
                    series_id = int(payload["autohomeSeriesId"])
            except (json.JSONDecodeError, TypeError, ValueError):
                job.log_text = _append_log(
                    job.log_text, "[probe] payload 解析失败，使用默认车系 4851"
                )

        url = CONFIG_SERIES_URL.format(series_id=series_id)
        job.log_text = _append_log(job.log_text, f"[probe] GET {url}")
        await _save_job(session, job)

        try:
            status_code, body = await fetch_with_retries(url)
            job.progress_pct = 80
            job.log_text = _append_log(
                job.log_text,
                f"[probe] HTTP {status_code}，响应长度 {len(body)} 字符",
            )
            snippet = body.strip().replace("\r", "")[:400]
            job.log_text = _append_log(job.log_text, f"[probe] 正文片段(前400字):\n{snippet}")
            if status_code == 200 and len(body) > 500:
                job.status = "success"
                job.progress_pct = 100
                job.error_message = None
            else:
                job.status = "failed"
                job.progress_pct = 100
                job.error_message = "HTTP 非 200 或正文过短，可能被拦截或需浏览器渲染"
        except Exception as e:
            logger.exception("probe job %s", job_id)
            job.status = "failed"
            job.progress_pct = 100
            job.error_message = str(e)[:2000]
            job.log_text = _append_log(job.log_text, f"[probe] 异常: {e!s}")

        await _save_job(session, job)


async def schedule_probe_job(job_id: int) -> None:
    asyncio.create_task(run_probe_job(job_id))
