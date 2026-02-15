"use strict";
const vue = require("vue");
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "CardItem" },
  __name: "card-item",
  props: {
    /** 数据 */
    item: Object,
    /** 是否选中 */
    checked: Boolean,
    /** 是否禁用 */
    disabled: Boolean,
    /** 是否显示边框 */
    bordered: Boolean,
    /** 是否需要选中箭头 */
    arrow: Boolean,
    /** 选中箭头样式 */
    arrowStyle: Object
  },
  setup(__props) {
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("div", {
        class: vue.normalizeClass(["ele-check-card", [
          { "is-bordered": __props.bordered },
          { "is-checked": __props.checked },
          { "is-disabled": __props.disabled }
        ]])
      }, [
        vue.renderSlot(_ctx.$slots, "default", {
          item: __props.item,
          checked: __props.checked,
          disabled: __props.disabled
        }),
        __props.arrow ? (vue.openBlock(), vue.createElementBlock("div", {
          key: 0,
          class: "ele-check-card-arrow",
          style: vue.normalizeStyle(__props.arrowStyle)
        }, null, 4)) : vue.createCommentVNode("", true)
      ], 2);
    };
  }
});
module.exports = _sfc_main;
