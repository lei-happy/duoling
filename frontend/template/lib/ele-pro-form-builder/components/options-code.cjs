"use strict";
const vue = require("vue");
const CodeEditer = require("./code-editer");
const _hoisted_1 = { class: "ele-pro-form-builder-code-edit-wrapper" };
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "OptionsCode" },
  __name: "options-code",
  props: {
    data: {},
    codePlaceholder: {},
    codePrefix: {},
    codeEditerComponent: {}
  },
  setup(__props, { expose: __expose }) {
    const props = __props;
    const codeContent = vue.ref("");
    const getResult = () => {
      const code = codeContent.value;
      if (code == null || !code) {
        return;
      }
      return `${props.codePrefix}${code}`;
    };
    vue.onMounted(() => {
      if (props.data == null || typeof props.data !== "string") {
        codeContent.value = props.codePlaceholder ?? "";
        return;
      }
      const data = props.data.trim();
      const codePrefix = props.codePrefix;
      if (data.startsWith(codePrefix)) {
        codeContent.value = data.slice(codePrefix.length);
        return;
      }
      codeContent.value = (data || props.codePlaceholder) ?? "";
    });
    __expose({
      getResult
    });
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("div", _hoisted_1, [
        (vue.openBlock(), vue.createBlock(vue.resolveDynamicComponent(__props.codeEditerComponent || CodeEditer), {
          modelValue: codeContent.value,
          "onUpdate:modelValue": _cache[0] || (_cache[0] = ($event) => codeContent.value = $event)
        }, null, 8, ["modelValue"]))
      ]);
    };
  }
});
module.exports = _sfc_main;
