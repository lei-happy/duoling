"use strict";
const vue = require("vue");
const elementPlus = require("element-plus");
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "CodeEditer" },
  __name: "code-editer",
  props: {
    modelValue: {}
  },
  emits: ["update:modelValue"],
  setup(__props, { emit: __emit }) {
    const emit = __emit;
    const updateModelValue = (value) => {
      emit("update:modelValue", value);
    };
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElInput), {
        size: "default",
        type: "textarea",
        modelValue: __props.modelValue,
        "onUpdate:modelValue": updateModelValue,
        class: "ele-pro-form-builder-code-editer"
      }, null, 8, ["modelValue"]);
    };
  }
});
module.exports = _sfc_main;
