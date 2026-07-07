"""资源管理 · 车牌号校验（纯逻辑，零 DB）测试

覆盖自有运力车辆/挂车号牌规范化与格式校验：
  - ``normalize_plate_input``：去空白/分隔符
  - ``validate_plate_category_value``：车牌类型枚举
  - ``validate_plate_for_category``：蓝/黄(7 位) 与 新能源(8 位)
  - ``validate_trailer_plate_for_category``：黄牌挂车「省+字母+4数字+挂」

对应需求：项目文档/02.需求文档/02.企业端/04.运力资源模块/**
对应代码：backend/app/modules/client/constants/plate_category.py
覆盖用例：TC-CLI-VEHICLE-050 ~ TC-CLI-VEHICLE-065
"""

from __future__ import annotations

import pytest

from app.common.exceptions import BizException
from app.modules.client.constants.plate_category import (
    PLATE_CATEGORY_BLUE,
    PLATE_CATEGORY_NEW_ENERGY,
    PLATE_CATEGORY_YELLOW,
    normalize_plate_input,
    validate_plate_category_value,
    validate_plate_for_category,
    validate_trailer_plate_for_category,
)


class TestNormalize:
    @pytest.mark.parametrize("raw,expected", [
        (" 沪A 12345 ", "沪A12345"),
        ("沪A·12345", "沪A12345"),
        ("沪A-12345", "沪A12345"),
        ("", ""),
    ])
    def test_normalize(self, raw, expected):
        assert normalize_plate_input(raw) == expected


class TestCategoryValue:
    @pytest.mark.parametrize("cat", [
        PLATE_CATEGORY_BLUE, PLATE_CATEGORY_YELLOW, PLATE_CATEGORY_NEW_ENERGY,
    ])
    def test_valid(self, cat):
        validate_plate_category_value(cat)  # 不抛异常

    @pytest.mark.parametrize("cat", [None, "", "GREEN", "blue"])
    def test_invalid(self, cat):
        with pytest.raises(BizException):
            validate_plate_category_value(cat)


class TestPlateForCategory:
    def test_blue_7_digits_ok(self):
        validate_plate_for_category(PLATE_CATEGORY_BLUE, "沪A12345")

    def test_yellow_7_digits_ok(self):
        validate_plate_for_category(PLATE_CATEGORY_YELLOW, "京B12345")

    def test_new_energy_8_digits_ok(self):
        validate_plate_for_category(PLATE_CATEGORY_NEW_ENERGY, "沪AD12345")

    def test_blue_wrong_length(self):
        with pytest.raises(BizException):
            validate_plate_for_category(PLATE_CATEGORY_BLUE, "沪A1234")

    def test_new_energy_wrong_length(self):
        with pytest.raises(BizException):
            validate_plate_for_category(PLATE_CATEGORY_NEW_ENERGY, "沪A12345")

    def test_must_start_with_chinese(self):
        with pytest.raises(BizException):
            validate_plate_for_category(PLATE_CATEGORY_BLUE, "AA12345")

    def test_empty_plate(self):
        with pytest.raises(BizException):
            validate_plate_for_category(PLATE_CATEGORY_BLUE, "")

    def test_letter_i_o_rejected(self):
        # 车牌字母不允许 I / O（正则 [A-HJ-NP-Z]）
        with pytest.raises(BizException):
            validate_plate_for_category(PLATE_CATEGORY_BLUE, "沪I12345")


class TestTrailerPlate:
    def test_yellow_trailer_ok(self):
        validate_trailer_plate_for_category(PLATE_CATEGORY_YELLOW, "京A1234挂")

    def test_trailer_without_gua_suffix(self):
        with pytest.raises(BizException):
            validate_trailer_plate_for_category(PLATE_CATEGORY_YELLOW, "京A12345")

    def test_trailer_new_energy_uses_car_rule(self):
        validate_trailer_plate_for_category(PLATE_CATEGORY_NEW_ENERGY, "沪AD12345")
