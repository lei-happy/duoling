"use strict";
const vue = require("vue");
const EleProForm = require("../../ele-pro-form/index");
const buildCore = require("./build-core");
const SourceEdit = require("./source-edit");
const StyleEdit = require("./style-edit");
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "ConfigForm" },
  __name: "config-form",
  props: {
    formProps: {},
    configFormItems: {},
    configFormPresetProps: {},
    proFormComponent: {},
    jsonEditerComponent: {},
    itemTypeData: {},
    httpRequest: {}
  },
  emits: ["updateFormProp"],
  setup(__props, { emit: __emit }) {
    const props = __props;
    const emit = __emit;
    const configFormData = vue.reactive({});
    const handleUpdateFormProp = (field, value) => {
      emit("updateFormProp", field, value);
    };
    vue.watch(
      () => props.formProps,
      (formProps) => {
        const data = Object.assign(
          {},
          configFormData,
          props.configFormPresetProps || {},
          buildCore.deepCloneObject(formProps),
          { items: void 0 }
        );
        Object.assign(configFormData, data, {
          items: void 0,
          footerProps: Object.assign(
            { labelWidth: data.footerProps?.labelWidth ?? data.labelWidth },
            data.footerProps
          )
        });
      },
      {
        immediate: true,
        deep: true
      }
    );
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createBlock(vue.resolveDynamicComponent(__props.proFormComponent || EleProForm), {
        size: "small",
        labelPosition: "top",
        model: configFormData,
        items: __props.configFormItems || [],
        itemTypeData: __props.itemTypeData,
        httpRequest: __props.httpRequest,
        class: "ele-pro-form-builder-props-form",
        onUpdateValue: handleUpdateFormProp
      }, vue.createSlots({ _: 2 }, [
        !_ctx.$slots.proFormBuilderSourceEdit ? {
          name: "proFormBuilderSourceEdit",
          fn: vue.withCtx(({ item, model, updatePropValue }) => [
            vue.createVNode(SourceEdit, vue.mergeProps({ jsonEditerComponent: __props.jsonEditerComponent }, item.props || {}, {
              modelValue: model,
              "onUpdate:modelValue": (val) => updatePropValue("", val)
            }), null, 16, ["jsonEditerComponent", "modelValue", "onUpdate:modelValue"])
          ]),
          key: "0"
        } : void 0,
        !_ctx.$slots.proFormBuilderStyleEdit ? {
          name: "proFormBuilderStyleEdit",
          fn: vue.withCtx(({ item, modelValue, updateValue }) => [
            vue.createVNode(StyleEdit, vue.mergeProps(item.props || {}, {
              modelValue,
              "onUpdate:modelValue": updateValue
            }), null, 16, ["modelValue", "onUpdate:modelValue"])
          ]),
          key: "1"
        } : void 0,
        vue.renderList(Object.keys(_ctx.$slots), (name) => {
          return {
            name,
            fn: vue.withCtx((slotProps) => [
              vue.renderSlot(_ctx.$slots, name, vue.normalizeProps(vue.guardReactiveProps(slotProps || {})))
            ])
          };
        })
      ]), 1064, ["model", "items", "itemTypeData", "httpRequest"]);
    };
  }
});
module.exports = _sfc_main;
