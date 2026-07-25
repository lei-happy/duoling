"""服务平台 · 下拉选项中文名的漂移守卫

大厅筛选与发布弹层的下拉都由后端下发（``/filters``、``/publish/options``），
措辞只在 ``constants.py`` 里定义一份。这里锁住两件事：

1. 枚举里新增了取值，却忘了配中文名——界面上会出现一个空白选项，
   或者干脆少一个选项，而两处都不会报错。
2. 两个接口下发的不是同一份——大厅里叫「按台」、发布时叫「每台」。

对应代码：backend/app/modules/console/models/ecosystem/constants.py
"""

from __future__ import annotations

from app.modules.console.models.ecosystem.constants import (
    CARGO_CATEGORY_LABELS,
    COOPERATION_TYPE_LABELS,
    PRICE_TYPE_LABELS,
    SETTLE_TYPE_LABELS,
    CargoCategory,
    CooperationType,
    PriceType,
    SettleType,
)


def values_of(enum_cls) -> set:
    """取枚举类上的取值，跳过 ALL / PASSED 这类聚合元组"""
    return {
        value
        for name, value in vars(enum_cls).items()
        if not name.startswith("_") and isinstance(value, int)
    }


class TestLabelCoverage:
    def test_price_types_all_labelled(self):
        assert values_of(PriceType) == set(PRICE_TYPE_LABELS)

    def test_settle_types_all_labelled(self):
        assert values_of(SettleType) == set(SETTLE_TYPE_LABELS)

    def test_cooperation_types_all_labelled(self):
        assert values_of(CooperationType) == set(COOPERATION_TYPE_LABELS)

    def test_cargo_categories_all_labelled(self):
        assert values_of(CargoCategory) == set(CARGO_CATEGORY_LABELS)

    def test_labels_are_non_empty(self):
        for labels in (
            PRICE_TYPE_LABELS,
            SETTLE_TYPE_LABELS,
            COOPERATION_TYPE_LABELS,
            CARGO_CATEGORY_LABELS,
        ):
            assert all(str(v).strip() for v in labels.values())


class TestBothEndpointsShareOneSource:
    """大厅与发布弹层下发的必须是同一份，否则同一个枚举会有两种说法"""

    def test_hall_and_publish_use_same_dicts(self):
        from app.modules.client.api.ecosystem import hall, publish

        assert hall._options(PRICE_TYPE_LABELS) == publish._options(PRICE_TYPE_LABELS)
        # 两个模块都不再各自维护一份措辞
        assert not hasattr(hall, "_PRICE_TYPE_LABELS")
        assert not hasattr(publish, "_PRICE_TYPE_LABELS")
