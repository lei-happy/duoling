"use strict";
const vue = require("vue");
const index = require("./index");
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  __name: "icon-radio-button",
  props: {
    size: {},
    checked: { type: Boolean },
    type: {}
  },
  setup(__props) {
    const props = __props;
    const buttonStyle = vue.computed(() => {
      const style = { flex: 1 };
      if (props.type !== 1) {
        style.borderLeftWidth = 0;
      }
      if (props.type === 1 || props.type === 2) {
        style.borderTopRightRadius = 0;
        style.borderBottomRightRadius = 0;
      }
      if (props.type === 3 || props.type === 2) {
        style.borderTopLeftRadius = 0;
        style.borderBottomLeftRadius = 0;
      }
      return style;
    });
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createBlock(vue.unref(index.IconButton), {
        size: __props.size,
        type: __props.checked ? "primary" : "bordered",
        style: vue.normalizeStyle(buttonStyle.value)
      }, null, 8, ["size", "type", "style"]);
    };
  }
});
module.exports = _sfc_main;
