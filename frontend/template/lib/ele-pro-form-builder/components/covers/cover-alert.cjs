"use strict";
const vue = require("vue");
const index = require("../icons/index");
const _hoisted_1 = { style: { maxWidth: "92%", margin: "0 auto" } };
const _hoisted_2 = {
  class: "ele-icon-border-color-base",
  style: {
    display: "flex",
    alignItems: "center",
    borderStyle: "solid",
    borderWidth: "1px",
    borderRadius: "4px",
    padding: "4px 6px"
  }
};
const _hoisted_3 = {
  class: "ele-icon-border-color-base",
  style: {
    display: "flex",
    alignItems: "center",
    borderStyle: "solid",
    borderWidth: "1px",
    borderRadius: "4px",
    padding: "4px 6px",
    marginTop: "8px"
  }
};
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  __name: "cover-alert",
  setup(__props) {
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("div", _hoisted_1, [
        vue.createElementVNode("div", _hoisted_2, [
          vue.createVNode(vue.unref(index.SvgIcon), {
            name: "ExclamationCircleFilled",
            size: "sm"
          }),
          vue.createVNode(vue.unref(index.IconSkeleton), {
            size: "sm",
            style: { flex: 1, margin: "0 2px 0 4px" }
          }),
          vue.createVNode(vue.unref(index.SvgIcon), {
            name: "CloseOutlined",
            size: "sm",
            color: "placeholder",
            style: { transform: "scale(0.8)" }
          })
        ]),
        vue.createElementVNode("div", _hoisted_3, [
          vue.createVNode(vue.unref(index.SvgIcon), {
            name: "CheckCircleFilled",
            size: "sm",
            color: "success"
          }),
          vue.createVNode(vue.unref(index.IconSkeleton), {
            size: "sm",
            style: { flex: 1, margin: "0 2px 0 4px" }
          }),
          vue.createVNode(vue.unref(index.SvgIcon), {
            name: "CloseOutlined",
            size: "sm",
            color: "placeholder",
            style: { transform: "scale(0.8)" }
          })
        ])
      ]);
    };
  }
});
module.exports = _sfc_main;
