"use strict";
const vue = require("vue");
const elementPlus = require("element-plus");
const index = require("../../icons/index");
const common = require("../../utils/common");
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "ProFormFooter" },
  __name: "pro-form-footer",
  props: {
    /** 底栏 ElFormItem 属性 */
    footerProps: Object,
    /** 底栏 ElFormItem 插槽 */
    footerSlots: Object,
    /** 自动计算底栏栅格份数 */
    autoFooterCol: Boolean,
    /** 底栏样式 */
    footerStyle: Object,
    /** 提交按钮文本 */
    submitText: String,
    /** 重置按钮文本 */
    resetText: String,
    /** 提交按钮属性 */
    submitButtonProps: Object,
    /** 重置按钮属性 */
    resetButtonProps: Object,
    /** 是否在底栏显示表单展开收起按钮 */
    showSearchExpand: Boolean,
    /** 搜索表单展开状态 */
    searchExpand: Boolean,
    /** 展开和收起按钮属性 */
    searchExpandButtonProps: Object,
    /** 展开按钮的文字 */
    searchExpandText: String,
    /** 收起按钮的文字 */
    searchShrinkText: String
  },
  emits: {
    updateSearchExpand: (_expand) => true,
    submit: () => true,
    reset: () => true
  },
  setup(__props, { emit: __emit }) {
    const ownSlots = ["footer", "footerExtra"];
    const props = __props;
    const emit = __emit;
    const toggleSearchExpand = () => {
      emit("updateSearchExpand", !props.searchExpand);
    };
    const handleSubmit = () => {
      emit("submit");
    };
    const handleReset = () => {
      emit("reset");
    };
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElFormItem), vue.mergeProps({
        class: ["ele-pro-form-footer", { "is-search-expand": __props.autoFooterCol && __props.searchExpand }]
      }, __props.footerProps || {}, {
        labelWidth: typeof __props.footerProps?.labelWidth === "number" ? `${__props.footerProps.labelWidth}px` : __props.footerProps?.labelWidth
      }), vue.createSlots({
        default: vue.withCtx(() => [
          vue.createElementVNode("div", {
            class: "ele-pro-form-footer-body",
            style: vue.normalizeStyle(__props.footerStyle)
          }, [
            vue.renderSlot(_ctx.$slots, "footer", {
              submitForm: handleSubmit,
              resetForm: handleReset
            }, () => [
              vue.createVNode(vue.unref(elementPlus.ElButton), vue.mergeProps({ type: "primary" }, __props.submitButtonProps || {}, { onClick: handleSubmit }), {
                default: vue.withCtx(() => [
                  vue.createTextVNode(vue.toDisplayString(__props.submitText), 1)
                ]),
                _: 1
              }, 16),
              vue.createVNode(vue.unref(elementPlus.ElButton), vue.mergeProps(__props.resetButtonProps || {}, { onClick: handleReset }), {
                default: vue.withCtx(() => [
                  vue.createTextVNode(vue.toDisplayString(__props.resetText), 1)
                ]),
                _: 1
              }, 16)
            ]),
            __props.showSearchExpand ? (vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElLink), vue.mergeProps({
              key: 0,
              type: "primary",
              underline: "never",
              style: { marginLeft: "12px" }
            }, __props.searchExpandButtonProps || {}, { onClick: toggleSearchExpand }), {
              default: vue.withCtx(() => [
                __props.searchExpand ? (vue.openBlock(), vue.createElementBlock(vue.Fragment, { key: 0 }, [
                  vue.createElementVNode("span", null, vue.toDisplayString(__props.searchShrinkText), 1),
                  vue.createVNode(vue.unref(elementPlus.ElIcon), { style: { verticalAlign: "-1px" } }, {
                    default: vue.withCtx(() => [
                      vue.createVNode(vue.unref(index.ArrowUp))
                    ]),
                    _: 1
                  })
                ], 64)) : (vue.openBlock(), vue.createElementBlock(vue.Fragment, { key: 1 }, [
                  vue.createElementVNode("span", null, vue.toDisplayString(__props.searchExpandText), 1),
                  vue.createVNode(vue.unref(elementPlus.ElIcon), { style: { verticalAlign: "-2px" } }, {
                    default: vue.withCtx(() => [
                      vue.createVNode(vue.unref(index.ArrowDown))
                    ]),
                    _: 1
                  })
                ], 64))
              ]),
              _: 1
            }, 16)) : vue.createCommentVNode("", true),
            vue.renderSlot(_ctx.$slots, "footerExtra", {
              submitForm: handleSubmit,
              resetForm: handleReset
            })
          ], 4)
        ]),
        _: 2
      }, [
        vue.renderList(vue.unref(common.getSlotsMap)(
          _ctx.$slots,
          __props.footerSlots,
          ["default"],
          ownSlots
        ), (slotName, compSlotName) => {
          return {
            name: compSlotName,
            fn: vue.withCtx((slotProps) => [
              vue.renderSlot(_ctx.$slots, slotName, vue.normalizeProps(vue.guardReactiveProps(slotProps || {})))
            ])
          };
        })
      ]), 1040, ["class", "labelWidth"]);
    };
  }
});
module.exports = _sfc_main;
