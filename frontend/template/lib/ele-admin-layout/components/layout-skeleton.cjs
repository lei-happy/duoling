"use strict";
const vue = require("vue");
const ReceiverView = require("../../ele-config-provider/components/receiver-view");
const _hoisted_1 = { class: "ele-admin-body" };
const _hoisted_2 = { class: "ele-admin-wrapper" };
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "LayoutSkeleton" },
  __name: "layout-skeleton",
  props: {
    /** logo是否位于顶栏 */
    isHeaderLogo: Boolean
  },
  setup(__props) {
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("div", {
        class: vue.normalizeClass(["ele-admin-layout", { "is-row-direction": !__props.isHeaderLogo }])
      }, [
        __props.isHeaderLogo ? vue.renderSlot(_ctx.$slots, "head", { key: 0 }) : vue.renderSlot(_ctx.$slots, "side", { key: 1 }),
        vue.createVNode(vue.unref(ReceiverView), {
          class: vue.normalizeClass(["ele-admin-main", { "is-row-direction": __props.isHeaderLogo }])
        }, {
          default: vue.withCtx((slotProps) => [
            __props.isHeaderLogo ? vue.renderSlot(_ctx.$slots, "side", {
              key: 0,
              param: slotProps
            }) : vue.renderSlot(_ctx.$slots, "head", {
              key: 1,
              param: slotProps
            }),
            vue.createElementVNode("div", _hoisted_1, [
              vue.renderSlot(_ctx.$slots, "tabs", { param: slotProps }),
              vue.createElementVNode("div", _hoisted_2, [
                vue.renderSlot(_ctx.$slots, "body", { param: slotProps })
              ])
            ])
          ]),
          _: 3
        }, 8, ["class"]),
        vue.renderSlot(_ctx.$slots, "default")
      ], 2);
    };
  }
});
module.exports = _sfc_main;
