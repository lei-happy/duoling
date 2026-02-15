"use strict";
const vue = require("vue");
const elementPlus = require("element-plus");
const EleTooltip = require("../../ele-tooltip/index");
const index = require("../../icons/index");
const _hoisted_1 = { class: "ele-table-filter-footer" };
const _hoisted_2 = {
  key: 1,
  class: "ele-table-filter-list"
};
const _hoisted_3 = ["onClick"];
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "CellFilter" },
  __name: "cell-filter",
  props: {
    /** 选中项 */
    filtered: Array,
    /** 是否多选 */
    filterMultiple: Boolean,
    /** 数据项 */
    filters: Array,
    /** 弹出框定位 */
    filterPlacement: {
      type: String,
      default: "bottom-start"
    }
  },
  emits: {
    /** 选中改变事件 */
    change: (_filtered) => true
  },
  setup(__props, { expose: __expose, emit: __emit }) {
    const props = __props;
    const emit = __emit;
    const { t } = elementPlus.useLocale();
    const popperRef = vue.ref(null);
    const checkedValue = vue.ref([]);
    const clearFilterText = vue.computed(() => {
      return t("el.table.clearFilter");
    });
    const filteredValue = vue.computed(() => {
      if (!props.filtered || !props.filtered.length) {
        return;
      }
      return props.filtered[0];
    });
    const confirmText = vue.computed(() => {
      return t("el.table.confirmFilter");
    });
    const resetText = vue.computed(() => {
      return t("el.table.resetFilter");
    });
    const hidePopper = () => {
      popperRef.value && popperRef.value.hide();
    };
    const handleBeforeEnter = () => {
      checkedValue.value = props.filtered ?? [];
    };
    const handleItemClick = (value) => {
      handleFilterChange(value == null ? [] : [value]);
      hidePopper();
    };
    const handleFilterChange = (filtered) => {
      emit("change", filtered);
    };
    const handleConfirm = () => {
      handleFilterChange(checkedValue.value);
      hidePopper();
    };
    const handleReset = () => {
      checkedValue.value = [];
      handleFilterChange([]);
      hidePopper();
    };
    __expose({
      popperRef
    });
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("div", {
        class: "ele-table-filter",
        onClick: _cache[2] || (_cache[2] = vue.withModifiers(() => {
        }, ["stop"]))
      }, [
        vue.createVNode(EleTooltip, {
          ref_key: "popperRef",
          ref: popperRef,
          trigger: "click",
          showArrow: false,
          placement: __props.filterPlacement,
          popperClass: "ele-table-filter-popper",
          gpuAcceleration: true,
          effect: "light",
          isPopover: true,
          popperOptions: {
            strategy: "fixed",
            modifiers: [{ name: "offset", options: { offset: [0, 4] } }]
          },
          onBeforeShow: handleBeforeEnter
        }, {
          body: vue.withCtx(() => [
            __props.filterMultiple ? (vue.openBlock(), vue.createElementBlock(vue.Fragment, { key: 0 }, [
              vue.createVNode(vue.unref(elementPlus.ElScrollbar), { class: "ele-table-filter-body" }, {
                default: vue.withCtx(() => [
                  vue.createVNode(vue.unref(elementPlus.ElCheckboxGroup), {
                    modelValue: checkedValue.value,
                    "onUpdate:modelValue": _cache[0] || (_cache[0] = ($event) => checkedValue.value = $event)
                  }, {
                    default: vue.withCtx(() => [
                      (vue.openBlock(true), vue.createElementBlock(vue.Fragment, null, vue.renderList(__props.filters, (item) => {
                        return vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElCheckbox), {
                          key: item.value,
                          value: item.value,
                          label: item.text
                        }, null, 8, ["value", "label"]);
                      }), 128))
                    ]),
                    _: 1
                  }, 8, ["modelValue"])
                ]),
                _: 1
              }),
              vue.createElementVNode("div", _hoisted_1, [
                vue.createVNode(vue.unref(elementPlus.ElButton), {
                  size: "small",
                  text: true,
                  onClick: handleReset
                }, {
                  default: vue.withCtx(() => [
                    vue.createTextVNode(vue.toDisplayString(resetText.value), 1)
                  ]),
                  _: 1
                }),
                vue.createVNode(vue.unref(elementPlus.ElButton), {
                  size: "small",
                  type: "primary",
                  disabled: !checkedValue.value.length,
                  onClick: handleConfirm
                }, {
                  default: vue.withCtx(() => [
                    vue.createTextVNode(vue.toDisplayString(confirmText.value), 1)
                  ]),
                  _: 1
                }, 8, ["disabled"])
              ])
            ], 64)) : (vue.openBlock(), vue.createElementBlock("div", _hoisted_2, [
              vue.createElementVNode("div", {
                class: vue.normalizeClass(["ele-table-filter-item", { "is-active": filteredValue.value == null }]),
                onClick: _cache[1] || (_cache[1] = ($event) => handleItemClick())
              }, vue.toDisplayString(clearFilterText.value), 3),
              (vue.openBlock(true), vue.createElementBlock(vue.Fragment, null, vue.renderList(__props.filters, (d) => {
                return vue.openBlock(), vue.createElementBlock("div", {
                  key: d.value,
                  class: vue.normalizeClass(["ele-table-filter-item", { "is-active": filteredValue.value === d.value }]),
                  onClick: ($event) => handleItemClick(d.value)
                }, vue.toDisplayString(d.text), 11, _hoisted_3);
              }), 128))
            ]))
          ]),
          default: vue.withCtx(() => [
            vue.createVNode(vue.unref(elementPlus.ElIcon), null, {
              default: vue.withCtx(() => [
                vue.createVNode(vue.unref(index.FilterFilled))
              ]),
              _: 1
            })
          ]),
          _: 1
        }, 8, ["placement"])
      ]);
    };
  }
});
module.exports = _sfc_main;
