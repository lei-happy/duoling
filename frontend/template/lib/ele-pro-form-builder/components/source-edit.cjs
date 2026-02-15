"use strict";
const vue = require("vue");
const elementPlus = require("element-plus");
const index = require("../../icons/index");
const common = require("../../utils/common");
const EleModal = require("../../ele-modal/index");
const CodeEditer = require("./code-editer");
const _hoisted_1 = { class: "ele-pro-form-builder-code-edit-wrapper" };
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "SourceEdit" },
  __name: "source-edit",
  props: {
    modelValue: {},
    title: {},
    excludeFields: {},
    jsonEditerComponent: {}
  },
  emits: ["update:modelValue"],
  setup(__props, { emit: __emit }) {
    const props = __props;
    const emit = __emit;
    const visible = vue.ref(false);
    const jsonContent = vue.ref("");
    const openModal = () => {
      jsonContent.value = JSON.stringify(
        common.omit(props.modelValue || {}, props.excludeFields || ["key", "children"]),
        void 0,
        2
      );
      visible.value = true;
    };
    const handleCancel = () => {
      visible.value = false;
      jsonContent.value = "";
    };
    const handleSave = () => {
      if (jsonContent.value) {
        let result;
        try {
          result = JSON.parse(jsonContent.value);
        } catch (e) {
          console.error(e);
        }
        if (result) {
          handleCancel();
          emit("update:modelValue", result);
        }
      }
    };
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock(vue.Fragment, null, [
        vue.createVNode(vue.unref(elementPlus.ElButton), {
          size: "small",
          icon: vue.unref(index.CodeOutlined),
          class: "ele-pro-form-builder-props-fluid-btn",
          onClick: openModal
        }, {
          default: vue.withCtx(() => [
            vue.createTextVNode(vue.toDisplayString(__props.title), 1)
          ]),
          _: 1
        }, 8, ["icon"]),
        vue.createVNode(EleModal, {
          width: 800,
          maxable: true,
          position: "center",
          title: __props.title,
          modelValue: visible.value,
          "onUpdate:modelValue": _cache[1] || (_cache[1] = ($event) => visible.value = $event),
          closeOnClickModal: false,
          destroyOnClose: true,
          bodyStyle: {
            height: "520px",
            minHeight: "100%",
            maxHeight: "100%",
            padding: "8px 16px"
          }
        }, {
          footer: vue.withCtx(() => [
            vue.createVNode(vue.unref(elementPlus.ElButton), {
              size: "default",
              onClick: handleCancel
            }, {
              default: vue.withCtx(() => [..._cache[2] || (_cache[2] = [
                vue.createTextVNode("取消", -1)
              ])]),
              _: 1
            }),
            vue.createVNode(vue.unref(elementPlus.ElButton), {
              type: "primary",
              size: "default",
              onClick: handleSave
            }, {
              default: vue.withCtx(() => [..._cache[3] || (_cache[3] = [
                vue.createTextVNode(" 保存 ", -1)
              ])]),
              _: 1
            })
          ]),
          default: vue.withCtx(() => [
            vue.createElementVNode("div", _hoisted_1, [
              (vue.openBlock(), vue.createBlock(vue.resolveDynamicComponent(__props.jsonEditerComponent || CodeEditer), {
                modelValue: jsonContent.value,
                "onUpdate:modelValue": _cache[0] || (_cache[0] = ($event) => jsonContent.value = $event)
              }, null, 8, ["modelValue"]))
            ])
          ]),
          _: 1
        }, 8, ["title", "modelValue"])
      ], 64);
    };
  }
});
module.exports = _sfc_main;
