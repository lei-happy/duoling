"use strict";
const vue = require("vue");
const elementPlus = require("element-plus");
const index = require("../../icons/index");
const _hoisted_1 = { class: "ele-message-icon" };
const _hoisted_2 = ["innerHTML"];
const _hoisted_3 = {
  key: 1,
  class: "ele-message-content"
};
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "MessageBody" },
  __name: "message-body",
  props: {
    /** 内容 */
    message: String,
    /** 类型 */
    type: String,
    /** 图标 */
    icon: [String, Object, Function],
    /** 是否显示关闭按钮 */
    showClose: Boolean,
    /** 内容是否是富文本 */
    dangerouslyUseHTMLString: Boolean,
    /** 是否是加载框 */
    loading: Boolean,
    /** 标识id */
    messageId: String
  },
  emits: {
    close: () => true,
    messageDestroy: (_messageId) => true
  },
  setup(__props, { emit: __emit }) {
    const props = __props;
    const emit = __emit;
    vue.onBeforeUnmount(() => {
      emit("messageDestroy", props.messageId);
    });
    const handleClose = () => {
      emit("close");
    };
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock(vue.Fragment, null, [
        vue.createElementVNode("div", _hoisted_1, [
          vue.createVNode(vue.unref(elementPlus.ElIcon), {
            class: vue.normalizeClass({ "is-loading": __props.loading })
          }, {
            default: vue.withCtx(() => [
              __props.icon ? (vue.openBlock(), vue.createBlock(vue.resolveDynamicComponent(__props.icon), { key: 0 })) : __props.loading ? (vue.openBlock(), vue.createBlock(vue.unref(index.LoadingOutlined), { key: 1 })) : __props.type === "success" ? (vue.openBlock(), vue.createBlock(vue.unref(index.CheckCircleFilled), { key: 2 })) : __props.type === "warning" ? (vue.openBlock(), vue.createBlock(vue.unref(index.ExclamationCircleFilled), { key: 3 })) : __props.type === "error" ? (vue.openBlock(), vue.createBlock(vue.unref(index.CloseCircleFilled), { key: 4 })) : (vue.openBlock(), vue.createBlock(vue.unref(index.InfoCircleFilled), { key: 5 }))
            ]),
            _: 1
          }, 8, ["class"])
        ]),
        vue.renderSlot(_ctx.$slots, "default", {}, () => [
          __props.dangerouslyUseHTMLString ? (vue.openBlock(), vue.createElementBlock("div", {
            key: 0,
            innerHTML: __props.message,
            class: "ele-message-content"
          }, null, 8, _hoisted_2)) : (vue.openBlock(), vue.createElementBlock("div", _hoisted_3, vue.toDisplayString(__props.message), 1))
        ]),
        __props.showClose ? (vue.openBlock(), vue.createElementBlock("div", {
          key: 0,
          class: "ele-message-close",
          onClick: handleClose
        }, [
          vue.createVNode(vue.unref(elementPlus.ElIcon), null, {
            default: vue.withCtx(() => [
              vue.createVNode(vue.unref(index.CloseOutlined))
            ]),
            _: 1
          })
        ])) : vue.createCommentVNode("", true)
      ], 64);
    };
  }
});
module.exports = _sfc_main;
