"use strict";
const vue = require("vue");
const buildCore = require("./build-core");
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "ComponentName" },
  __name: "component-name",
  props: {
    itemType: {},
    componentData: {}
  },
  setup(__props) {
    const props = __props;
    const typeName = vue.computed(() => {
      const type = props.itemType;
      return buildCore.getComponentItemByType(type, props.componentData)?.name ?? type;
    });
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("span", null, vue.toDisplayString(typeName.value), 1);
    };
  }
});
module.exports = _sfc_main;
