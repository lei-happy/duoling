"use strict";
const vue = require("vue");
const hook = require("../utils/hook");
const index = vue.defineComponent({
  name: "EleFormItemRest",
  setup(_props, { slots }) {
    hook.useFormItemRest();
    return () => slots.default?.();
  }
});
module.exports = index;
