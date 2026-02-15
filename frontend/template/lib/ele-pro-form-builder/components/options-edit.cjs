"use strict";
const vue = require("vue");
const elementPlus = require("element-plus");
const index = require("../../icons/index");
const renderCore = require("../../ele-pro-form/components/render-core");
const EleModal = require("../../ele-modal/index");
const EleTabBar = require("../../ele-tab-bar/index");
const OptionsTable = require("./options-table");
const OptionsCode = require("./options-code");
const _hoisted_1 = { class: "ele-pro-form-builder-code-edit-tip" };
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "OptionsEdit" },
  __name: "options-edit",
  props: {
    modelValue: {},
    title: {},
    isTreeData: { type: [Boolean, Object] },
    columns: {},
    codeOptions: { type: Boolean },
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
    const optionsType = vue.ref("optionsTable");
    const editerRef = vue.ref(null);
    const codePrefixStr = vue.computed(() => {
      return props.codePrefix ?? renderCore.codeStringPrefix;
    });
    const openModal = () => {
      if (props.modelValue != null && typeof props.modelValue === "string" && props.modelValue.startsWith(codePrefixStr.value)) {
        optionsType.value = "optionsCode";
      } else {
        optionsType.value = "optionsTable";
      }
      visible.value = true;
    };
    const handleCancel = () => {
      visible.value = false;
    };
    const handleSave = () => {
      const result = editerRef.value?.getResult?.();
      emit("update:modelValue", result ?? []);
      visible.value = false;
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
          width: 960,
          maxable: true,
          position: "center",
          title: __props.title,
          modelValue: visible.value,
          "onUpdate:modelValue": _cache[1] || (_cache[1] = ($event) => visible.value = $event),
          closeOnClickModal: false,
          destroyOnClose: true,
          bodyStyle: {
            height: "568px",
            minHeight: "100%",
            maxHeight: "100%",
            padding: "0 16px 8px 16px",
            display: "flex",
            flexDirection: "column"
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
            __props.codeOptions ? (vue.openBlock(), vue.createBlock(EleTabBar, {
              key: 0,
              modelValue: optionsType.value,
              "onUpdate:modelValue": _cache[0] || (_cache[0] = ($event) => optionsType.value = $event),
              items: [
                { value: "optionsTable", label: "静态数据" },
                { value: "optionsCode", label: "远程数据" }
              ],
              type: "plain",
              class: "ele-pro-form-builder-options-tabs"
            }, {
              label: vue.withCtx(({ label, item }) => [
                vue.createElementVNode("span", null, vue.toDisplayString(label), 1),
                optionsType.value === "optionsCode" && item.value === "optionsCode" && __props.codeTips ? (vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElIcon), {
                  key: 0,
                  class: "ele-pro-form-builder-code-edit-icon"
                }, {
                  default: vue.withCtx(() => [
                    vue.createVNode(vue.unref(index.QuestionCircleOutlined)),
                    vue.createElementVNode("div", _hoisted_1, vue.toDisplayString(__props.codeTips), 1)
                  ]),
                  _: 1
                })) : vue.createCommentVNode("", true)
              ]),
              _: 1
            }, 8, ["modelValue"])) : vue.createCommentVNode("", true),
            !__props.codeOptions || optionsType.value === "optionsTable" ? (vue.openBlock(), vue.createBlock(OptionsTable, {
              key: 1,
              ref_key: "editerRef",
              ref: editerRef,
              data: __props.modelValue,
              isTreeData: __props.isTreeData,
              columns: __props.columns
            }, null, 8, ["data", "isTreeData", "columns"])) : __props.codeOptions ? (vue.openBlock(), vue.createBlock(OptionsCode, {
              key: 2,
              ref_key: "editerRef",
              ref: editerRef,
              data: __props.modelValue,
              codePlaceholder: __props.codePlaceholder,
              codePrefix: codePrefixStr.value,
              codeEditerComponent: __props.codeEditerComponent
            }, null, 8, ["data", "codePlaceholder", "codePrefix", "codeEditerComponent"])) : vue.createCommentVNode("", true)
          ]),
          _: 1
        }, 8, ["title", "modelValue"])
      ], 64);
    };
  }
});
module.exports = _sfc_main;
