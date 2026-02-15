"use strict";
const vue = require("vue");
const elementPlus = require("element-plus");
const buildCore = require("./build-core");
const buildUtil = require("./build-util");
const _hoisted_1 = { class: "ele-pro-form-builder-template-wrapper" };
const _hoisted_2 = ["onClick"];
const _hoisted_3 = { class: "ele-pro-form-builder-template-item-label" };
const _hoisted_4 = { class: "ele-pro-form-builder-template-item-body" };
const _hoisted_5 = { class: "ele-pro-form-builder-template-item-cover" };
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "TemplateList" },
  __name: "template-list",
  props: {
    templateData: {}
  },
  emits: ["importData"],
  setup(__props, { emit: __emit }) {
    const emit = __emit;
    const handleImportTemplate = (item) => {
      const result = buildCore.deepCloneObject(item.config);
      buildUtil.itemsGenerateNewKey(result.items, [], false);
      emit("importData", result);
    };
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("div", _hoisted_1, [
        !__props.templateData || !__props.templateData.length ? (vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElEmpty), {
          key: 0,
          imageSize: 58,
          class: "ele-pro-form-builder-form-empty"
        })) : (vue.openBlock(true), vue.createElementBlock(vue.Fragment, { key: 1 }, vue.renderList(__props.templateData, (item) => {
          return vue.openBlock(), vue.createElementBlock("div", {
            key: item.name,
            class: "ele-pro-form-builder-template-item",
            onClick: ($event) => handleImportTemplate(item)
          }, [
            vue.createElementVNode("div", _hoisted_3, vue.toDisplayString(item.name), 1),
            vue.createElementVNode("div", _hoisted_4, [
              vue.createElementVNode("div", _hoisted_5, [
                item.cover ? (vue.openBlock(), vue.createBlock(vue.resolveDynamicComponent(item.cover), { key: 0 })) : vue.createCommentVNode("", true)
              ])
            ])
          ], 8, _hoisted_2);
        }), 128))
      ]);
    };
  }
});
module.exports = _sfc_main;
