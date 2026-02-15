"use strict";
const vue = require("vue");
const props = require("./props");
const receiver = require("./receiver");
const index = vue.defineComponent({
  name: "EleConfigProvider",
  props: props.configProviderProps,
  setup(props2, { slots }) {
    const config = vue.reactive({ ...props2 });
    vue.provide(receiver.CONFIG_KEY, config);
    vue.watch(
      () => props2.locale,
      () => {
        config.locale = props2.locale;
      }
    );
    vue.watch(
      () => props2.table,
      () => {
        config.table = props2.table;
      },
      { deep: true }
    );
    vue.watch(
      () => props2.message,
      () => {
        config.message = props2.message;
      },
      { deep: true }
    );
    vue.watch(
      () => props2.messageBox,
      () => {
        config.messageBox = props2.messageBox;
      },
      { deep: true }
    );
    vue.watch(
      () => props2.license,
      (code) => {
        const value = code ? code.trim() : void 0;
        if (!value) {
          const values = receiver.configValues.split("=");
          if (values.length > 16) {
            config.key = `${values[16]}${[values[17], values[18]].map((d) => d == null ? "" : "=").join("")}`;
          } else {
            config.key = value;
          }
        } else {
          config.key = value;
        }
      },
      { immediate: true }
    );
    vue.watch(
      () => props2.mapKey,
      () => {
        config.mapKey = props2.mapKey;
      }
    );
    return () => slots.default?.();
  }
});
module.exports = index;
