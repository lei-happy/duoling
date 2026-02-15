"use strict";
const vue = require("vue");
const _hoisted_1 = {
  class: "ele-icon-border-color-base",
  style: {
    borderTopStyle: "solid",
    borderTopWidth: "1px",
    borderLeftStyle: "solid",
    borderLeftWidth: "1px"
  }
};
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  __name: "cover-table",
  setup(__props) {
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("div", _hoisted_1, [
        (vue.openBlock(), vue.createElementBlock(vue.Fragment, null, vue.renderList(4, (i) => {
          return vue.createElementVNode("div", {
            key: i,
            style: { display: "flex" }
          }, [
            (vue.openBlock(), vue.createElementBlock(vue.Fragment, null, vue.renderList(4, (j) => {
              return vue.createElementVNode("div", {
                key: `${i}-${j}`,
                class: "ele-icon-border-color-base",
                style: {
                  flex: 1,
                  height: "12px",
                  borderRightStyle: "solid",
                  borderRightWidth: "1px",
                  borderBottomStyle: "solid",
                  borderBottomWidth: "1px"
                }
              });
            }), 64))
          ]);
        }), 64))
      ]);
    };
  }
});
module.exports = _sfc_main;
