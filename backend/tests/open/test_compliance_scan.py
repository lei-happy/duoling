"""运力宝 - 证照监控扫描分级逻辑测试（纯逻辑）

对应需求：doc/02.需求文档/06.运力宝/02.证照监控引擎技术设计.md
         doc/06.测试用例体系/04.开放接口与LITE与运力宝/05.运力宝证照监控与承运商建档.md
对应后端：backend/app/modules/client/services/compliance/compliance_scan_service.py
覆盖用例：TC-OPN-COMPLIANCE-001 ~ TC-OPN-COMPLIANCE-006

说明：``scan_tenant`` 内部会 ``db.commit()``（破坏外层事务回滚隔离），不适合纳入
"不落库"的集成用例，此处仅覆盖分级规则与阈值读取等纯逻辑（零 DB）。
数据库级 upsert / resolved 自愈行为标记为「仅手工 / 待补」。
"""

import importlib

import pytest

from app.modules.client.services.compliance import compliance_scan_service as css


class TestLevelClassification:
    """TC-OPN-COMPLIANCE-001：days_left 分级规则 expired/critical/warning"""

    def test_expired(self):
        assert css._level_of(-1, 7) == "expired"
        assert css._level_of(-100, 7) == "expired"

    def test_critical_boundary(self):
        # 0 <= days_left <= critical → critical
        assert css._level_of(0, 7) == "critical"
        assert css._level_of(7, 7) == "critical"

    def test_warning_above_critical(self):
        # critical < days_left <= horizon → warning
        assert css._level_of(8, 7) == "warning"
        assert css._level_of(60, 7) == "warning"

    def test_custom_critical_threshold(self):
        assert css._level_of(3, 3) == "critical"
        assert css._level_of(4, 3) == "warning"


class TestThresholdEnv:
    """TC-OPN-COMPLIANCE-002：阈值环境变量读取（默认 horizon=60 / critical=7）"""

    def test_defaults(self, monkeypatch):
        monkeypatch.delenv("COMPLIANCE_ALERT_HORIZON_DAYS", raising=False)
        monkeypatch.delenv("COMPLIANCE_ALERT_CRITICAL_DAYS", raising=False)
        importlib.reload(css)
        assert css._horizon_days() == 60
        assert css._critical_days() == 7

    def test_override(self, monkeypatch):
        monkeypatch.setenv("COMPLIANCE_ALERT_HORIZON_DAYS", "90")
        monkeypatch.setenv("COMPLIANCE_ALERT_CRITICAL_DAYS", "15")
        assert css._horizon_days() == 90
        assert css._critical_days() == 15


class TestCandidateKey:
    """TC-OPN-COMPLIANCE-003：_Candidate.key 唯一性以 (subject_type, subject_id, doc_type) 为准"""

    def test_key_tuple(self):
        from datetime import date

        c = css._Candidate(
            "carrier_driver", 10, "王师傅", "13800000000",
            "driver_license", "JZ123", date(2026, 8, 1),
        )
        assert c.key == ("carrier_driver", 10, "driver_license")
