"use strict";
const vue = require("vue");
const ElePopconfirm = require("../ele-popconfirm/index");
const util = require("./util");
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "ElePopconfirmProvider" },
  __name: "index",
  setup(__props, { expose: __expose }) {
    const {
      popconfirmRef,
      popconfirmVirtualRef,
      popconfirmProps,
      openPopconfirm
    } = util.usePopconfirmProvider();
    __expose({
      openPopconfirm
    });
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock(vue.Fragment, null, [
        vue.renderSlot(_ctx.$slots, "default"),
        vue.createVNode(ElePopconfirm, vue.mergeProps({
          width: 200,
          triggerKeys: [],
          persistent: false,
          placement: "top-end"
        }, vue.unref(popconfirmProps), {
          ref_key: "popconfirmRef",
          ref: popconfirmRef,
          virtualTriggering: true,
          virtualRef: vue.unref(popconfirmVirtualRef)
        }), null, 16, ["virtualRef"])
      ], 64);
    };
  }
});
module.exports = _sfc_main;
