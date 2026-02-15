"use strict";
const vue = require("vue");
const elementPlus = require("element-plus");
const EleModal = require("../../ele-modal/index");
const util$1 = require("../../ele-pro-form/util");
const EleProForm = require("../../ele-pro-form/index");
const util = require("../util");
const buildCore = require("./build-core");
const _hoisted_1 = { class: "ele-pro-form-builder-screen-radio" };
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "PreviewModal" },
  __name: "preview-modal",
  props: {
    modelValue: { type: Boolean },
    formProps: {},
    proFormComponent: {},
    itemTypeData: {},
    httpRequest: {}
  },
  emits: ["update:modelValue", "previewFormSubmit"],
  setup(__props, { emit: __emit }) {
    const props = __props;
    const emit = __emit;
    const previewFormRef = vue.ref(null);
    const previewFormProps = vue.ref({ items: [] });
    const formData = vue.reactive({});
    const previewScreen = vue.ref("pc");
    const handleUpdateModelValue = (visible) => {
      emit("update:modelValue", visible);
    };
    const setPreviewFormDataFieldValue = (field, value) => {
      util$1.setValue(formData, field, value);
    };
    const handlePreviewFormSubmit = () => {
      emit("previewFormSubmit", formData);
    };
    const handlePreviewFormReset = () => {
      Object.keys(formData).forEach((k) => {
        formData[k] = void 0;
      });
      util$1.mergeValue(
        formData,
        util$1.getFormInitValue(previewFormProps.value?.items, props.itemTypeData, true)
      );
    };
    const handleUpdatePreviewScreen = (size) => {
      previewScreen.value = size;
    };
    vue.watch(
      () => props.modelValue,
      (visible) => {
        if (visible) {
          previewFormProps.value = buildCore.deepCloneObject(
            props.formProps || { items: [] }
          );
          handlePreviewFormReset();
          vue.nextTick(() => {
            previewFormRef.value?.clearValidate?.();
            vue.nextTick(() => {
              previewFormRef.value?.clearValidate?.();
            });
          });
        }
      }
    );
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createBlock(EleModal, {
        width: 980,
        maxable: true,
        draggable: false,
        position: "center",
        closeOnClickModal: false,
        destroyOnClose: true,
        modalBodyClass: [
          "ele-pro-form-builder-preview",
          previewScreen.value === "pad" ? "is-pad" : previewScreen.value === "phone" ? "is-phone" : "is-pc"
        ].join(" "),
        modelValue: __props.modelValue,
        "onUpdate:modelValue": handleUpdateModelValue
      }, {
        header: vue.withCtx(() => [
          vue.createElementVNode("div", _hoisted_1, [
            (vue.openBlock(true), vue.createElementBlock(vue.Fragment, null, vue.renderList(vue.unref(util.screenItems), (item) => {
              return vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElIcon), {
                key: item.value,
                class: vue.normalizeClass(["ele-pro-form-builder-header-tool ele-pro-form-builder-screen-icon", { "is-active": item.value === previewScreen.value }]),
                onClick: ($event) => handleUpdatePreviewScreen(item.value)
              }, {
                default: vue.withCtx(() => [
                  (vue.openBlock(), vue.createBlock(vue.resolveDynamicComponent(item.icon), {
                    style: vue.normalizeStyle(item.iconStyle)
                  }, null, 8, ["style"]))
                ]),
                _: 2
              }, 1032, ["class", "onClick"]);
            }), 128))
          ])
        ]),
        default: vue.withCtx(() => [
          (vue.openBlock(), vue.createBlock(vue.resolveDynamicComponent(__props.proFormComponent || EleProForm), vue.mergeProps({ validateOnRuleChange: false }, previewFormProps.value, {
            ref_key: "previewFormRef",
            ref: previewFormRef,
            model: formData,
            editable: false,
            screenSize: previewScreen.value,
            itemTypeData: __props.itemTypeData,
            httpRequest: __props.httpRequest,
            class: "ele-pro-form-builder-preview-form",
            onUpdateValue: setPreviewFormDataFieldValue,
            onSubmit: handlePreviewFormSubmit,
            onReset: handlePreviewFormReset
          }), vue.createSlots({ _: 2 }, [
            vue.renderList(Object.keys(_ctx.$slots), (name) => {
              return {
                name,
                fn: vue.withCtx((slotProps) => [
                  vue.renderSlot(_ctx.$slots, name, vue.normalizeProps(vue.guardReactiveProps(slotProps || {})))
                ])
              };
            })
          ]), 1040, ["model", "screenSize", "itemTypeData", "httpRequest"]))
        ]),
        _: 3
      }, 8, ["modalBodyClass", "modelValue"]);
    };
  }
});
module.exports = _sfc_main;
