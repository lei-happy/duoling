"use strict";
const vue = require("vue");
const elementPlus = require("element-plus");
const index = require("../../icons/index");
const EleProForm = require("../../ele-pro-form/index");
const util = require("../../ele-pro-form/util");
const OptionsEdit = require("../../ele-pro-form-builder/components/options-edit");
const EventEdit = require("../../ele-pro-form-builder/components/event-edit");
const SourceEdit = require("../../ele-pro-form-builder/components/source-edit");
const StyleEdit = require("../../ele-pro-form-builder/components/style-edit");
const FormDesignModal = require("./form-design-modal");
const _hoisted_1 = {
  key: 0,
  class: "ele-crud-builder-page-config-group-list"
};
const _hoisted_2 = ["onClick"];
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "PageConfig" },
  __name: "page-config",
  props: {
    /** 配置数据 */
    config: Object,
    /** 页面设置的表单项配置 */
    pageConfigFormItems: Array,
    /** 高级表单组件 */
    proFormComponent: [String, Object, Function],
    /** 表单构建组件 */
    proFormBuilderComponent: [
      String,
      Object,
      Function
    ],
    /** 表单构建组件属性 */
    proFormBuilderProps: Object,
    /** 代码编辑器组件 */
    codeEditerComponent: [String, Object, Function],
    /** JSON 编辑器组件 */
    jsonEditerComponent: [String, Object, Function],
    /** 高级表单组件类型数据 */
    itemTypeData: Array,
    /** 远程数据源请求工具 */
    httpRequest: [Object, Function]
  },
  emits: ["updateConfigValue", "updateFormConfig"],
  setup(__props, { emit: __emit }) {
    const props = __props;
    const emit = __emit;
    const configFormData = vue.computed(() => {
      const data = {};
      util.mergeValue(
        data,
        util.getFormInitValue(props.pageConfigFormItems, props.itemTypeData, true),
        props.config
      );
      return data;
    });
    const pageConfigGroups = vue.computed(() => {
      return (props.pageConfigFormItems || []).filter((item) => !!(item.children && item.label)).map((item) => ({
        key: item.key ?? item.prop,
        label: item.label ?? item.children?.[0]?.label ?? item.prop ?? item.key
      }));
    });
    const groupActive = vue.ref(pageConfigGroups.value?.[0]?.key);
    const activePageConfigFormItems = vue.computed(() => {
      if (!props.pageConfigFormItems) {
        return [];
      }
      if (groupActive.value == null) {
        return props.pageConfigFormItems;
      }
      const items = [];
      props.pageConfigFormItems.forEach((item) => {
        if (!item.children || !item.label) {
          items.push(item);
        } else if (groupActive.value === (item.key ?? item.prop)) {
          items.push({ ...item, label: void 0 });
        }
      });
      return items;
    });
    const formDesignOption = vue.reactive({});
    const handlePageConfigGroupClick = (item) => {
      groupActive.value = item.key;
    };
    const handleUpdateConfigField = (field, value) => {
      emit("updateConfigValue", field, value);
    };
    const handleFormDesignBtnClick = (type, title) => {
      formDesignOption.type = type;
      formDesignOption.title = title;
      formDesignOption.visible = true;
    };
    const handleUpdateFormConfig = (data, type) => {
      emit("updateFormConfig", data, type);
    };
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock(vue.Fragment, null, [
        pageConfigGroups.value.length ? (vue.openBlock(), vue.createElementBlock("div", _hoisted_1, [
          (vue.openBlock(true), vue.createElementBlock(vue.Fragment, null, vue.renderList(pageConfigGroups.value, (item) => {
            return vue.openBlock(), vue.createElementBlock("div", {
              key: item.key,
              class: vue.normalizeClass(["ele-crud-builder-page-config-group-list-item", { "is-active": item.key === groupActive.value }]),
              onClick: ($event) => handlePageConfigGroupClick(item)
            }, vue.toDisplayString(item.label), 11, _hoisted_2);
          }), 128))
        ])) : vue.createCommentVNode("", true),
        (vue.openBlock(), vue.createBlock(vue.resolveDynamicComponent(__props.proFormComponent || EleProForm), {
          itemTypeData: __props.itemTypeData,
          httpRequest: __props.httpRequest,
          size: "small",
          labelPosition: "top",
          model: configFormData.value,
          items: activePageConfigFormItems.value,
          class: "ele-crud-builder-page-config-form",
          onUpdateValue: handleUpdateConfigField
        }, vue.createSlots({ _: 2 }, [
          !_ctx.$slots.crudBuilderFormDesign ? {
            name: "crudBuilderFormDesign",
            fn: vue.withCtx(({ item }) => [
              vue.createVNode(vue.unref(elementPlus.ElButton), {
                icon: vue.unref(index.FormOutlined),
                class: "ele-pro-form-builder-props-fluid-btn",
                onClick: ($event) => handleFormDesignBtnClick(item.props?.type, item.label)
              }, {
                default: vue.withCtx(() => [
                  vue.createTextVNode(vue.toDisplayString(item.label), 1)
                ]),
                _: 2
              }, 1032, ["icon", "onClick"])
            ]),
            key: "0"
          } : void 0,
          !_ctx.$slots.crudBuilderSwitch ? {
            name: "crudBuilderSwitch",
            fn: vue.withCtx(({ item, modelValue, updateValue }) => [
              vue.createVNode(vue.unref(elementPlus.ElSwitch), {
                modelValue: (modelValue ?? item.props?.defaultValue) !== false,
                "onUpdate:modelValue": (val) => updateValue(val ? {} : false)
              }, null, 8, ["modelValue", "onUpdate:modelValue"])
            ]),
            key: "1"
          } : void 0,
          !_ctx.$slots.proFormBuilderOptionsEdit ? {
            name: "proFormBuilderOptionsEdit",
            fn: vue.withCtx(({ item, modelValue, updateValue }) => [
              vue.createVNode(OptionsEdit, vue.mergeProps({ codeEditerComponent: __props.codeEditerComponent }, item.props || {}, {
                modelValue,
                "onUpdate:modelValue": updateValue
              }), null, 16, ["codeEditerComponent", "modelValue", "onUpdate:modelValue"])
            ]),
            key: "2"
          } : void 0,
          !_ctx.$slots.proFormBuilderEventEdit ? {
            name: "proFormBuilderEventEdit",
            fn: vue.withCtx(({ item, modelValue, updateValue }) => [
              vue.createVNode(EventEdit, vue.mergeProps({ codeEditerComponent: __props.codeEditerComponent }, item.props || {}, {
                modelValue,
                "onUpdate:modelValue": updateValue
              }), null, 16, ["codeEditerComponent", "modelValue", "onUpdate:modelValue"])
            ]),
            key: "3"
          } : void 0,
          !_ctx.$slots.proFormBuilderSourceEdit ? {
            name: "proFormBuilderSourceEdit",
            fn: vue.withCtx(({ item, model, updatePropValue }) => [
              vue.createVNode(SourceEdit, vue.mergeProps({ jsonEditerComponent: __props.jsonEditerComponent }, item.props || {}, {
                modelValue: model,
                "onUpdate:modelValue": (val) => updatePropValue("", val)
              }), null, 16, ["jsonEditerComponent", "modelValue", "onUpdate:modelValue"])
            ]),
            key: "4"
          } : void 0,
          !_ctx.$slots.proFormBuilderStyleEdit ? {
            name: "proFormBuilderStyleEdit",
            fn: vue.withCtx(({ item, modelValue, updateValue }) => [
              vue.createVNode(StyleEdit, vue.mergeProps(item.props || {}, {
                modelValue,
                "onUpdate:modelValue": updateValue
              }), null, 16, ["modelValue", "onUpdate:modelValue"])
            ]),
            key: "5"
          } : void 0,
          vue.renderList(Object.keys(_ctx.$slots), (name) => {
            return {
              name,
              fn: vue.withCtx((slotProps) => [
                vue.renderSlot(_ctx.$slots, name, vue.normalizeProps(vue.guardReactiveProps(slotProps || {})))
              ])
            };
          })
        ]), 1064, ["itemTypeData", "httpRequest", "model", "items"])),
        vue.createVNode(FormDesignModal, {
          modelValue: formDesignOption.visible,
          "onUpdate:modelValue": _cache[0] || (_cache[0] = ($event) => formDesignOption.visible = $event),
          title: formDesignOption.title,
          type: formDesignOption.type,
          config: __props.config,
          proFormComponent: __props.proFormComponent,
          proFormBuilderComponent: __props.proFormBuilderComponent,
          proFormBuilderProps: __props.proFormBuilderProps,
          jsonEditerComponent: __props.jsonEditerComponent,
          itemTypeData: __props.itemTypeData,
          httpRequest: __props.httpRequest,
          onUpdateFormConfig: handleUpdateFormConfig
        }, vue.createSlots({ _: 2 }, [
          vue.renderList(Object.keys(_ctx.$slots), (name) => {
            return {
              name,
              fn: vue.withCtx((slotProps) => [
                vue.renderSlot(_ctx.$slots, name, vue.normalizeProps(vue.guardReactiveProps(slotProps || {})))
              ])
            };
          })
        ]), 1032, ["modelValue", "title", "type", "config", "proFormComponent", "proFormBuilderComponent", "proFormBuilderProps", "jsonEditerComponent", "itemTypeData", "httpRequest"])
      ], 64);
    };
  }
});
module.exports = _sfc_main;
