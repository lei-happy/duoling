"use strict";
const vue = require("vue");
const elementPlus = require("element-plus");
const index = require("../icons/index");
const props = require("./props");
const _hoisted_1 = { key: 0 };
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "EleAlert", inheritAttrs: false },
  __name: "index",
  props: props.alertProps,
  emits: props.alertEmits,
  setup(__props, { expose: __expose, emit: __emit }) {
    const props2 = __props;
    const emit = __emit;
    const slots = vue.useSlots();
    const visible = vue.ref(true);
    const isRich = vue.computed(() => {
      return props2.description !== false && (!!props2.description || !!slots.default);
    });
    const handleClose = (e) => {
      if (!visible.value || !props2.closable) {
        return;
      }
      visible.value = false;
      emit("close", e);
    };
    const open = () => {
      if (!visible.value) {
        visible.value = true;
      }
    };
    __expose({
      handleClose,
      open
    });
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createBlock(vue.Transition, { name: _ctx.transitionName }, {
        default: vue.withCtx(() => [
          visible.value ? (vue.openBlock(), vue.createElementBlock("div", vue.mergeProps({ key: 0 }, _ctx.$attrs, {
            class: ["ele-alert", [
              { "is-success": _ctx.type === "success" },
              { "is-warning": _ctx.type === "warning" },
              { "is-error": _ctx.type === "error" },
              { "is-dark": _ctx.effect === "dark" },
              { "is-center": _ctx.center },
              { "is-rich": isRich.value }
            ]]
          }), [
            _ctx.showIcon ? (vue.openBlock(), vue.createElementBlock("div", {
              key: 0,
              class: "ele-alert-icon",
              style: vue.normalizeStyle(_ctx.iconStyle)
            }, [
              vue.renderSlot(_ctx.$slots, "icon", {}, () => [
                vue.createVNode(vue.unref(elementPlus.ElIcon), vue.normalizeProps(vue.guardReactiveProps(_ctx.iconProps || {})), {
                  default: vue.withCtx(() => [
                    _ctx.type === "success" ? (vue.openBlock(), vue.createBlock(vue.unref(index.CheckCircleFilled), { key: 0 })) : _ctx.type === "warning" ? (vue.openBlock(), vue.createBlock(vue.unref(index.ExclamationCircleFilled), { key: 1 })) : _ctx.type === "error" ? (vue.openBlock(), vue.createBlock(vue.unref(index.CloseCircleFilled), { key: 2 })) : (vue.openBlock(), vue.createBlock(vue.unref(index.InfoCircleFilled), { key: 3 }))
                  ]),
                  _: 1
                }, 16)
              ])
            ], 4)) : vue.createCommentVNode("", true),
            vue.createElementVNode("div", {
              class: "ele-alert-body",
              style: vue.normalizeStyle(_ctx.bodyStyle)
            }, [
              _ctx.title || _ctx.$slots.title ? (vue.openBlock(), vue.createElementBlock("div", {
                key: 0,
                class: "ele-alert-title",
                style: vue.normalizeStyle(_ctx.titleStyle)
              }, [
                vue.renderSlot(_ctx.$slots, "title", {}, () => [
                  vue.createTextVNode(vue.toDisplayString(_ctx.title), 1)
                ])
              ], 4)) : vue.createCommentVNode("", true),
              isRich.value ? (vue.openBlock(), vue.createElementBlock("div", {
                key: 1,
                class: "ele-alert-text",
                style: vue.normalizeStyle(_ctx.descriptionStyle)
              }, [
                vue.renderSlot(_ctx.$slots, "default", {}, () => [
                  vue.createTextVNode(vue.toDisplayString(_ctx.description === true ? "" : _ctx.description), 1)
                ])
              ], 4)) : vue.createCommentVNode("", true)
            ], 4),
            vue.renderSlot(_ctx.$slots, "action"),
            _ctx.closable ? (vue.openBlock(), vue.createElementBlock("div", {
              key: 1,
              class: "ele-alert-close",
              style: vue.normalizeStyle(_ctx.closeIconStyle),
              onClick: handleClose
            }, [
              vue.renderSlot(_ctx.$slots, "closeIcon", {}, () => [
                _ctx.closeText ? (vue.openBlock(), vue.createElementBlock("span", _hoisted_1, vue.toDisplayString(_ctx.closeText), 1)) : (vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElIcon), vue.normalizeProps(vue.mergeProps({ key: 1 }, _ctx.closeIconProps || {})), {
                  default: vue.withCtx(() => [
                    vue.createVNode(vue.unref(index.CloseOutlined))
                  ]),
                  _: 1
                }, 16))
              ])
            ], 4)) : vue.createCommentVNode("", true)
          ], 16)) : vue.createCommentVNode("", true)
        ]),
        _: 3
      }, 8, ["name"]);
    };
  }
});
module.exports = _sfc_main;
