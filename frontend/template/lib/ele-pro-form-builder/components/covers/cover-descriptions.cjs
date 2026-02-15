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
  __name: "cover-descriptions",
  setup(__props) {
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("div", _hoisted_1, [
        (vue.openBlock(), vue.createElementBlock(vue.Fragment, null, vue.renderList(3, (i) => {
          return vue.createElementVNode("div", {
            key: i,
            style: { display: "flex" }
          }, [
            (vue.openBlock(), vue.createElementBlock(vue.Fragment, null, vue.renderList(4, (j) => {
              return vue.createElementVNode("div", {
                key: `${i}-${j}`,
                class: vue.normalizeClass(["ele-icon-border-color-base", {
                  "ele-icon-bg-fill": ["1-1", "1-3", "2-1", "2-3", "3-1"].includes(
                    `${i}-${j}`
                  )
                }]),
                style: vue.normalizeStyle({
                  flex: 1,
                  height: "12px",
                  borderRightStyle: ["3-2", "3-3"].includes(`${i}-${j}`) ? void 0 : "solid",
                  borderRightWidth: ["3-2", "3-3"].includes(`${i}-${j}`) ? void 0 : "1px",
                  borderBottomStyle: "solid",
                  borderBottomWidth: "1px"
                })
              }, null, 6);
            }), 64))
          ]);
        }), 64))
      ]);
    };
  }
});
module.exports = _sfc_main;
