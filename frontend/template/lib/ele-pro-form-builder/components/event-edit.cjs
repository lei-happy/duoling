"use strict";
const vue = require("vue");
const elementPlus = require("element-plus");
const index = require("../../icons/index");
const renderCore = require("../../ele-pro-form/components/render-core");
const EleModal = require("../../ele-modal/index");
const CodeEditer = require("./code-editer");
const _hoisted_1 = { class: "ele-pro-form-builder-code-edit-header" };
const _hoisted_2 = { class: "ele-pro-form-builder-code-edit-tip" };
const _hoisted_3 = { class: "ele-pro-form-builder-code-edit-wrapper" };
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "EventEdit" },
  __name: "event-edit",
  props: {
    modelValue: {},
    title: {},
    codeTips: {},
    codePlaceholder: {},
    codePrefix: {},
    codeEditerComponent: {}
  },
  emits: ["update:modelValue"],
  setup(__props, { emit: __emit }) {
    const props = __props;
    const emit = __emit;
    const visible = vue.ref(false);
    const codeContent = vue.ref("");
    const getCodePrefix = () => {
      return props.codePrefix ?? renderCore.codeStringPrefix;
    };
    const getResult = () => {
      const code = codeContent.value;
      if (code == null || !code) {
        return;
      }
      return `${getCodePrefix()}${code}`;
    };
    const openModal = () => {
      const codePrefix = getCodePrefix();
      if (props.modelValue == null || typeof props.modelValue !== "string") {
        codeContent.value = props.codePlaceholder ?? "";
      } else if (props.modelValue.trim().startsWith(codePrefix)) {
        codeContent.value = props.modelValue.trim().slice(codePrefix.length);
      } else {
        codeContent.value = (props.modelValue || props.codePlaceholder) ?? "";
      }
      visible.value = true;
    };
    const handleCancel = () => {
      visible.value = false;
      codeContent.value = "";
    };
    const handleSave = () => {
      const result = getResult();
      handleCancel();
      emit("update:modelValue", result);
    };
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock(vue.Fragment, null, [
        vue.createVNode(vue.unref(elementPlus.ElButton), {
          size: "small",
          class: "ele-pro-form-builder-props-fluid-btn",
          onClick: openModal
        }, {
          default: vue.withCtx(() => [
            vue.createTextVNode(vue.toDisplayString(__props.title), 1)
          ]),
          _: 1
        }),
        vue.createVNode(EleModal, {
          width: 800,
          maxable: true,
          position: "center",
          modelValue: visible.value,
          "onUpdate:modelValue": _cache[3] || (_cache[3] = ($event) => visible.value = $event),
          closeOnClickModal: false,
          destroyOnClose: true,
          bodyStyle: {
            height: "520px",
            minHeight: "100%",
            maxHeight: "100%",
            padding: "8px 16px"
          }
        }, {
          header: vue.withCtx(() => [
            vue.createElementVNode("div", _hoisted_1, [
              vue.createElementVNode("div", null, vue.toDisplayString(__props.title), 1),
              __props.codeTips ? (vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElIcon), {
                key: 0,
                class: "ele-pro-form-builder-code-edit-icon",
                onMousedown: _cache[0] || (_cache[0] = vue.withModifiers(() => {
                }, ["stop"])),
                onTouchstartPassive: _cache[1] || (_cache[1] = vue.withModifiers(() => {
                }, ["stop"]))
              }, {
                default: vue.withCtx(() => [
                  vue.createVNode(vue.unref(index.QuestionCircleOutlined)),
                  vue.createElementVNode("div", _hoisted_2, vue.toDisplayString(__props.codeTips), 1)
                ]),
                _: 1
              })) : vue.createCommentVNode("", true)
            ])
          ]),
          footer: vue.withCtx(() => [
            vue.createVNode(vue.unref(elementPlus.ElButton), {
              size: "default",
              onClick: handleCancel
            }, {
              default: vue.withCtx(() => [..._cache[4] || (_cache[4] = [
                vue.createTextVNode("取消", -1)
              ])]),
              _: 1
            }),
            vue.createVNode(vue.unref(elementPlus.ElButton), {
              type: "primary",
              size: "default",
              onClick: handleSave
            }, {
              default: vue.withCtx(() => [..._cache[5] || (_cache[5] = [
                vue.createTextVNode(" 保存 ", -1)
              ])]),
              _: 1
            })
          ]),
          default: vue.withCtx(() => [
            vue.createElementVNode("div", _hoisted_3, [
              (vue.openBlock(), vue.createBlock(vue.resolveDynamicComponent(__props.codeEditerComponent || CodeEditer), {
                modelValue: codeContent.value,
                "onUpdate:modelValue": _cache[2] || (_cache[2] = ($event) => codeContent.value = $event)
              }, null, 8, ["modelValue"]))
            ])
          ]),
          _: 1
        }, 8, ["modelValue"])
      ], 64);
    };
  }
});
module.exports = _sfc_main;
