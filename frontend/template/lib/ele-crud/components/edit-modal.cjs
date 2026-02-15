"use strict";
const vue = require("vue");
const common = require("../../utils/common");
const EleModal = require("../../ele-modal/index");
const EleProForm = require("../../ele-pro-form/index");
const util = require("../../ele-pro-form/util");
const EleButtons = require("../../ele-buttons/index");
const util$1 = require("../util");
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "EditModal" },
  __name: "edit-modal",
  props: {
    /** 弹窗是否打开 */
    modelValue: Boolean,
    /** 编辑弹窗数据 */
    data: Object,
    /** 弹窗标题 */
    title: String,
    /** 编辑配置 */
    editConfig: Object,
    /** 字段数据 */
    fields: Array,
    /** 获取字段数据对应的表单项的方法 */
    getFieldsEditFormItems: Function,
    /** 获取字段数据对应的表单项的方法 */
    getAndCacheCode: {
      type: Function,
      required: true
    },
    /** 高级表单组件 */
    proFormComponent: [String, Object, Function],
    /** 修改数据接口 */
    editApi: [Function, String],
    /** 高级表单组件类型数据 */
    itemTypeData: Array,
    /** 远程数据源请求工具 */
    httpRequest: [Object, Function],
    /** 屏幕尺寸 */
    screenSize: String
  },
  emits: {
    /** 更新弹窗打开状态事件 */
    "update:modelValue": (_visible) => true,
    /** 编辑保存失败事件 */
    editError: (_e) => true,
    /** 编辑保存成功事件 */
    editDone: (_msg) => true
  },
  setup(__props, { emit: __emit }) {
    const props = __props;
    const emit = __emit;
    const loading = vue.ref(false);
    const editFormRef = vue.ref(null);
    const editForm = vue.reactive({});
    const editFormProps = vue.computed(() => {
      const formProps = props.editConfig?.formProps || {};
      return {
        ...formProps,
        items: formProps.items?.length ? formProps.items : props.getFieldsEditFormItems?.(props.fields)
      };
    });
    const handleUpdateVisible = (visible) => {
      emit("update:modelValue", visible);
    };
    const handleSave = () => {
      editFormRef.value?.validate?.((valid) => {
        if (valid) {
          handleSubmitEditForm(editForm);
        }
      });
    };
    const handleCancel = () => {
      handleUpdateVisible(false);
      loading.value = false;
    };
    const handleUpdateEditForm = (field, value) => {
      util.setValue(editForm, field, value);
    };
    const handleResetEditForm = (item) => {
      Object.keys(editForm).forEach((key) => {
        editForm[key] = void 0;
      });
      util.mergeValue(
        editForm,
        util.getFormInitValue(
          editFormProps.value.items,
          editFormProps.value.itemTypeData || props.itemTypeData,
          true
        ),
        item
      );
    };
    const handleSubmitEditForm = (form) => {
      if (!props.editApi) {
        return;
      }
      const editApiFunc = typeof props.editApi === "function" ? props.editApi : props.editApi.startsWith(util$1.codeStringPrefix) ? props.getAndCacheCode(props.editApi) : void 0;
      if (!editApiFunc) {
        return;
      }
      loading.value = true;
      editApiFunc(form).then((msg) => {
        handleCancel();
        emit("editDone", msg);
      }).catch((e) => {
        loading.value = false;
        emit("editError", e);
      });
    };
    const btnItems = vue.computed(() => {
      const items = [];
      if (props.editConfig?.cancelBtnProps !== false) {
        items.push({
          preset: "cancel",
          props: props.editConfig?.cancelBtnProps === true ? void 0 : props.editConfig?.cancelBtnProps,
          onClick: handleCancel
        });
      }
      if (props.editConfig?.saveBtnProps !== false) {
        items.push({
          preset: "save",
          props: {
            loading: loading.value,
            ...(props.editConfig?.saveBtnProps === true ? void 0 : props.editConfig?.saveBtnProps) || {}
          },
          onClick: handleSave
        });
      }
      return items;
    });
    vue.watch(
      () => props.modelValue,
      (visible) => {
        if (visible) {
          handleResetEditForm(props.data);
        }
      }
    );
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createBlock(EleModal, vue.mergeProps({
        width: 460,
        form: true,
        title: __props.title,
        destroyOnClose: true,
        loading: loading.value
      }, __props.editConfig?.modalProps || {}, {
        modelValue: __props.modelValue,
        "onUpdate:modelValue": handleUpdateVisible
      }), vue.createSlots({
        default: vue.withCtx(() => [
          (vue.openBlock(), vue.createBlock(vue.resolveDynamicComponent(__props.proFormComponent || EleProForm), vue.mergeProps({
            itemTypeData: __props.itemTypeData,
            httpRequest: __props.httpRequest,
            screenSize: __props.screenSize
          }, editFormProps.value, {
            ref_key: "editFormRef",
            ref: editFormRef,
            model: editForm,
            onUpdateValue: handleUpdateEditForm,
            onSubmit: handleSubmitEditForm,
            onReset: _cache[0] || (_cache[0] = ($event) => handleResetEditForm())
          }), vue.createSlots({ _: 2 }, [
            vue.renderList(vue.unref(common.getSlotsMap)(
              _ctx.$slots,
              __props.editConfig?.formSlots,
              [],
              [],
              true
            ), (slotName, compSlotName) => {
              return {
                name: compSlotName,
                fn: vue.withCtx((slotProps) => [
                  vue.renderSlot(_ctx.$slots, slotName, vue.normalizeProps(vue.guardReactiveProps(slotProps || {})))
                ])
              };
            })
          ]), 1040, ["itemTypeData", "httpRequest", "screenSize", "model"]))
        ]),
        _: 2
      }, [
        btnItems.value.length ? {
          name: "footer",
          fn: vue.withCtx(() => [
            vue.createVNode(EleButtons, { items: btnItems.value }, null, 8, ["items"])
          ]),
          key: "0"
        } : void 0,
        vue.renderList(vue.unref(common.getSlotsMap)(
          _ctx.$slots,
          __props.editConfig?.modalSlots,
          ["default", "footer"]
        ), (slotName, compSlotName) => {
          return {
            name: compSlotName,
            fn: vue.withCtx((slotProps) => [
              vue.renderSlot(_ctx.$slots, slotName, vue.normalizeProps(vue.guardReactiveProps(slotProps || {})))
            ])
          };
        })
      ]), 1040, ["title", "loading", "modelValue"]);
    };
  }
});
module.exports = _sfc_main;
