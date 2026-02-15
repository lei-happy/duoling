"use strict";
const vue = require("vue");
const elementPlus = require("element-plus");
const index = require("../../icons/index");
const EleModal = require("../../ele-modal/index");
const EleProFormBuilder = require("../../ele-pro-form-builder/index");
const util$1 = require("../../ele-pro-form-builder/util");
const util = require("../../ele-crud/util");
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "FormDesignModal" },
  __name: "form-design-modal",
  props: {
    /** 弹窗是否打开 */
    modelValue: Boolean,
    /** 弹窗标题 */
    title: String,
    /** 类型 */
    type: String,
    /** 配置数据 */
    config: Object,
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
    /** JSON 编辑器组件 */
    jsonEditerComponent: [String, Object, Function],
    /** 高级表单组件类型数据 */
    itemTypeData: Array,
    /** 远程数据源请求工具 */
    httpRequest: [Object, Function]
  },
  emits: ["update:modelValue", "updateFormConfig"],
  setup(__props, { emit: __emit }) {
    const ownSlots = ["default", "headerTools"];
    const props = __props;
    const emit = __emit;
    const formConfig = vue.ref();
    const handleUpdateModelValue = (visible) => {
      emit("update:modelValue", visible);
    };
    const handleSave = () => {
      handleCloseModal();
      emit("updateFormConfig", formConfig.value, props.type);
    };
    const handleCloseModal = () => {
      handleUpdateModelValue(false);
    };
    const handleUpdateFormConfig = (config) => {
      formConfig.value = config;
    };
    vue.watch(
      () => props.modelValue,
      (visible) => {
        if (!visible) {
          return;
        }
        const config = props.config || {};
        const fields = config.fields;
        if (props.type === "search") {
          const searchConfig = config.searchConfig;
          const formProps = (searchConfig === false || searchConfig === true ? void 0 : searchConfig)?.formProps || {};
          const items = formProps.items?.length ? formProps.items : util.getFieldsSearchFormItems(fields);
          formConfig.value = {
            ...util.getDefaultSearchFormProps() || {},
            ...formProps,
            items
          };
          return;
        }
        if (props.type === "add") {
          const addConfig = config.addConfig;
          const formProps = (addConfig === false || addConfig === true ? void 0 : addConfig)?.formProps || {};
          const items = formProps.items?.length ? formProps.items : util.getFieldsAddFormItems(fields);
          formConfig.value = { ...formProps, items };
          return;
        }
        if (props.type === "edit") {
          const editConfig = config.editConfig;
          const formProps = (editConfig === false || editConfig === true ? void 0 : editConfig)?.formProps || {};
          const items = formProps.items?.length ? formProps.items : util.getFieldsEditFormItems(fields);
          formConfig.value = { ...formProps, items };
        }
      }
    );
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createBlock(EleModal, {
        width: 1260,
        maxable: true,
        position: "center",
        title: __props.title,
        modelValue: __props.modelValue,
        closeOnClickModal: false,
        destroyOnClose: true,
        class: "ele-crud-builder-form-design-modal",
        "onUpdate:modelValue": handleUpdateModelValue
      }, {
        default: vue.withCtx(() => [
          (vue.openBlock(), vue.createBlock(vue.resolveDynamicComponent(__props.proFormBuilderComponent || EleProFormBuilder), vue.mergeProps({
            proFormComponent: __props.proFormComponent,
            itemTypeData: __props.itemTypeData,
            httpRequest: __props.httpRequest,
            headerTools: vue.unref(util$1.defaultHeaderRightTools)
          }, __props.proFormBuilderProps || {}, {
            modelValue: formConfig.value,
            "onUpdate:modelValue": handleUpdateFormConfig
          }), vue.createSlots({
            headerTools: vue.withCtx(() => [
              vue.createVNode(vue.unref(elementPlus.ElButton), {
                type: "primary",
                icon: vue.unref(index.CheckOutlined),
                onClick: handleSave
              }, {
                default: vue.withCtx(() => [..._cache[0] || (_cache[0] = [
                  vue.createTextVNode(" 保存 ", -1)
                ])]),
                _: 1
              }, 8, ["icon"])
            ]),
            _: 2
          }, [
            vue.renderList(Object.keys(_ctx.$slots).filter((k) => !ownSlots.includes(k)), (name) => {
              return {
                name,
                fn: vue.withCtx((slotProps) => [
                  vue.renderSlot(_ctx.$slots, name, vue.normalizeProps(vue.guardReactiveProps(slotProps || {})))
                ])
              };
            })
          ]), 1040, ["proFormComponent", "itemTypeData", "httpRequest", "headerTools", "modelValue"]))
        ]),
        _: 3
      }, 8, ["title", "modelValue"]);
    };
  }
});
module.exports = _sfc_main;
