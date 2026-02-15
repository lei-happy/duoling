"use strict";
const vue = require("vue");
const index = require("../icons/index");
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  __name: "cover-date",
  setup(__props) {
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("div", null, [
        vue.createVNode(vue.unref(index.IconInput), { size: "sm" }, {
          default: vue.withCtx(() => [
            vue.createVNode(vue.unref(index.IconSkeleton), {
              size: "sm",
              style: { width: "50%" }
            }),
            vue.createVNode(vue.unref(index.SvgIcon), {
              name: "CalendarOutlined",
              size: "sm",
              style: { margin: "0 0 0 auto" }
            })
          ]),
          _: 1
        }),
        vue.createVNode(vue.unref(index.IconPanel), { style: { padding: "1px 0" } }, {
          default: vue.withCtx(() => [
            vue.createVNode(vue.unref(index.IconCalendar), { size: "sm" })
          ]),
          _: 1
        })
      ]);
    };
  }
});
module.exports = _sfc_main;
