"use strict";
const vue = require("vue");
const elementPlus = require("element-plus");
const index = require("../../icons/index");
const ComponentName = require("./component-name");
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "TypeEdit" },
  __name: "type-edit",
  props: {
    formItem: {},
    componentData: {}
  },
  emits: ["openComponentPicker"],
  setup(__props, { emit: __emit }) {
    const props = __props;
    const emit = __emit;
    const handleClick = () => {
      if (props.formItem) {
        emit("openComponentPicker", props.formItem);
      }
    };
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElButton), {
        size: "small",
        class: "ele-pro-form-builder-props-fluid-btn is-small-icon ele-pro-form-builder-type-select-btn",
        onClick: handleClick
      }, {
        default: vue.withCtx(() => [
          vue.createVNode(ComponentName, {
            itemType: __props.formItem?.type,
            componentData: __props.componentData
          }, null, 8, ["itemType", "componentData"]),
          vue.createVNode(vue.unref(elementPlus.ElIcon), null, {
            default: vue.withCtx(() => [
              vue.createVNode(vue.unref(index.ArrowDown))
            ]),
            _: 1
          })
        ]),
        _: 1
      });
    };
  }
});
module.exports = _sfc_main;
