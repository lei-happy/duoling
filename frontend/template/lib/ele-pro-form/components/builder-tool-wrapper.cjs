"use strict";
const vue = require("vue");
const elementPlus = require("element-plus");
const index = require("../../icons/index");
const _hoisted_1 = { class: "ele-pro-form-builder-item-tool-wrapper" };
const _hoisted_2 = { class: "ele-pro-form-builder-item-handle-content" };
const _hoisted_3 = { class: "ele-pro-form-builder-item-tools" };
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "BuilderToolWrapper" },
  __name: "builder-tool-wrapper",
  props: {
    item: {},
    activeItemKey: {},
    handle: { type: Boolean }
  },
  setup(__props) {
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("div", _hoisted_1, [
        vue.createElementVNode("div", {
          class: vue.normalizeClass(["ele-pro-form-builder-item-handle", { "is-disabled": !__props.handle }])
        }, [
          __props.handle ? (vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElIcon), {
            key: 0,
            class: "ele-pro-form-builder-item-handle-icon"
          }, {
            default: vue.withCtx(() => [
              vue.createVNode(vue.unref(index.DragOutlined))
            ]),
            _: 1
          })) : vue.createCommentVNode("", true),
          vue.renderSlot(_ctx.$slots, "builderItemHandleContent", {
            item: __props.item,
            activeItemKey: __props.activeItemKey
          }, () => [
            vue.createElementVNode("div", _hoisted_2, vue.toDisplayString(__props.item.type), 1)
          ])
        ], 2),
        vue.createElementVNode("div", _hoisted_3, [
          vue.renderSlot(_ctx.$slots, "builderItemTools", {
            item: __props.item,
            activeItemKey: __props.activeItemKey
          })
        ])
      ]);
    };
  }
});
module.exports = _sfc_main;
