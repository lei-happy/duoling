"use strict";
const vue = require("vue");
const elementPlus = require("element-plus");
const index = require("../../icons/index");
const common = require("../../utils/common");
const EleProForm = require("../../ele-pro-form/index");
const util$1 = require("../../ele-pro-form/util");
const buildCore = require("../../ele-pro-form-builder/components/build-core");
const SourceEdit = require("../../ele-pro-form-builder/components/source-edit");
const StyleEdit = require("../../ele-pro-form-builder/components/style-edit");
const util = require("../util");
const FieldList = require("./field-list");
const _hoisted_1 = { class: "ele-crud-builder-field-header" };
const _hoisted_2 = {
  key: 0,
  class: "ele-crud-builder-field-edit-wrapper"
};
const _hoisted_3 = { class: "ele-crud-builder-field-edit-card" };
const _hoisted_4 = { class: "ele-crud-builder-field-edit-header" };
const _hoisted_5 = { class: "ele-crud-builder-field-edit-title" };
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "FieldTree" },
  __name: "field-tree",
  props: {
    /** 全部字段 */
    fields: Array,
    /** 字段编辑的表单项配置 */
    fieldEditFormItems: Array,
    /** 高级表单组件 */
    proFormComponent: [String, Object, Function],
    /** JSON 编辑器组件 */
    jsonEditerComponent: [String, Object, Function],
    /** 高级表单组件类型数据 */
    itemTypeData: Array,
    /** 远程数据源请求工具 */
    httpRequest: [Object, Function]
  },
  emits: ["deleteField", "addField", "updateField", "updateFieldChildren"],
  setup(__props, { emit: __emit }) {
    const props = __props;
    const emit = __emit;
    const collapseItemIds = vue.ref([]);
    const fieldEditData = vue.reactive({});
    const fieldEditOption = vue.reactive({});
    const handleDeleteItem = (key) => {
      emit("deleteField", key);
    };
    const handleCopyItem = (key) => {
      if (key == null) {
        return;
      }
      common.eachTree(props.fields, (item, index2, parent) => {
        if (item.key === key) {
          const newItem = buildCore.deepCloneObject(item);
          util.itemsGenerateNewKey(newItem, props.fields, true);
          emit("addField", newItem, parent?.key, index2 + 1);
          return false;
        }
      });
    };
    const handleEditItem = (item) => {
      handleOpenEdit(item);
    };
    const handleAddChildren = (parentKey) => {
      handleOpenEdit(void 0, parentKey);
    };
    const handleUpdateItemChildren = (data, parentKey) => {
      emit("updateFieldChildren", data, parentKey);
    };
    const handleToggleItemCollapse = (key) => {
      if (key == null) {
        return;
      }
      const index2 = collapseItemIds.value.indexOf(key);
      if (index2 !== -1) {
        collapseItemIds.value.splice(index2, 1);
      } else {
        collapseItemIds.value.push(key);
      }
    };
    const handleUpdateEditFieldData = (field, value) => {
      if (!field) {
        const excludeFields = ["key", "children"];
        const temp = common.omit(value, excludeFields);
        Object.assign(fieldEditData, temp);
        const valueKeys = Object.keys(temp);
        Object.keys(fieldEditData).forEach((key) => {
          if (fieldEditData && !excludeFields.includes(key) && !valueKeys.includes(key) && typeof fieldEditData[key] !== "undefined") {
            fieldEditData[key] = void 0;
          }
        });
      } else {
        util$1.setValue(fieldEditData, field, value);
      }
    };
    const resetFieldEditData = (item) => {
      Object.keys(fieldEditData).forEach((key) => {
        fieldEditData[key] = void 0;
      });
      util$1.mergeValue(
        fieldEditData,
        util$1.getFormInitValue(props.fieldEditFormItems, props.itemTypeData, true),
        item
      );
    };
    const handleOpenEdit = (item, parentKey) => {
      resetFieldEditData(item);
      if (item == null) {
        fieldEditOption.isEdit = false;
        fieldEditOption.parentKey = parentKey;
      } else {
        fieldEditOption.isEdit = true;
        fieldEditOption.parentKey = void 0;
      }
      fieldEditOption.index = void 0;
      fieldEditOption.visible = true;
    };
    const handleCancelEdit = () => {
      fieldEditOption.visible = false;
    };
    const handleSaveEdit = () => {
      handleCancelEdit();
      const field = buildCore.deepCloneObject(fieldEditData);
      if (fieldEditOption.isEdit) {
        emit("updateField", field);
      } else {
        util.itemsGenerateNewKey(field, props.fields);
        emit("addField", field, fieldEditOption.parentKey, fieldEditOption.index);
      }
    };
    vue.watch(
      () => props.fields,
      (items) => {
        for (let i = collapseItemIds.value.length - 1; i >= 0; i--) {
          if (!common.findTree(items, (item) => collapseItemIds.value[i] === item.key)) {
            collapseItemIds.value.splice(i, 1);
          }
        }
      },
      { deep: true }
    );
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock(vue.Fragment, null, [
        vue.createElementVNode("div", _hoisted_1, [
          vue.createVNode(vue.unref(elementPlus.ElButton), {
            icon: vue.unref(index.PlusOutlined),
            type: "primary",
            onClick: _cache[0] || (_cache[0] = ($event) => handleOpenEdit())
          }, {
            default: vue.withCtx(() => [..._cache[1] || (_cache[1] = [
              vue.createTextVNode(" 添加 ", -1)
            ])]),
            _: 1
          }, 8, ["icon"])
        ]),
        __props.fields && __props.fields.length ? (vue.openBlock(), vue.createBlock(FieldList, {
          key: 0,
          items: __props.fields,
          collapseItemIds: collapseItemIds.value,
          onToggleItemCollapse: handleToggleItemCollapse,
          onDeleteItem: handleDeleteItem,
          onCopyItem: handleCopyItem,
          onEditItem: handleEditItem,
          onAddChildren: handleAddChildren,
          onUpdateItemChildren: handleUpdateItemChildren
        }, null, 8, ["items", "collapseItemIds"])) : (vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElEmpty), {
          key: 1,
          imageSize: 58,
          class: "ele-crud-builder-form-empty"
        })),
        vue.createVNode(vue.Transition, { name: "anim" }, {
          default: vue.withCtx(() => [
            fieldEditOption.visible ? (vue.openBlock(), vue.createElementBlock("div", _hoisted_2, [
              vue.createElementVNode("div", _hoisted_3, [
                vue.createElementVNode("div", _hoisted_4, [
                  vue.createElementVNode("div", _hoisted_5, vue.toDisplayString(fieldEditOption.isEdit ? "修改" : "添加"), 1),
                  vue.createVNode(vue.unref(elementPlus.ElButton), {
                    text: true,
                    icon: vue.unref(index.CloseOutlined),
                    onClick: handleCancelEdit
                  }, {
                    default: vue.withCtx(() => [..._cache[2] || (_cache[2] = [
                      vue.createTextVNode(" 取消 ", -1)
                    ])]),
                    _: 1
                  }, 8, ["icon"]),
                  vue.createVNode(vue.unref(elementPlus.ElButton), {
                    icon: vue.unref(index.CheckOutlined),
                    type: "primary",
                    onClick: handleSaveEdit
                  }, {
                    default: vue.withCtx(() => [..._cache[3] || (_cache[3] = [
                      vue.createTextVNode(" 保存 ", -1)
                    ])]),
                    _: 1
                  }, 8, ["icon"])
                ]),
                (vue.openBlock(), vue.createBlock(vue.resolveDynamicComponent(__props.proFormComponent || EleProForm), {
                  itemTypeData: __props.itemTypeData,
                  httpRequest: __props.httpRequest,
                  size: "small",
                  labelPosition: "top",
                  model: fieldEditData,
                  items: __props.fieldEditFormItems,
                  class: "ele-crud-builder-field-edit-form",
                  onUpdateValue: handleUpdateEditFieldData
                }, vue.createSlots({ _: 2 }, [
                  !_ctx.$slots.crudBuilderSwitch ? {
                    name: "crudBuilderSwitch",
                    fn: vue.withCtx(({ item, modelValue, updateValue }) => [
                      vue.createVNode(vue.unref(elementPlus.ElSwitch), {
                        modelValue: (modelValue ?? item.props?.defaultValue) !== false,
                        "onUpdate:modelValue": (val) => updateValue(val ? {} : false)
                      }, null, 8, ["modelValue", "onUpdate:modelValue"])
                    ]),
                    key: "0"
                  } : void 0,
                  !_ctx.$slots.proFormBuilderSourceEdit ? {
                    name: "proFormBuilderSourceEdit",
                    fn: vue.withCtx(({ item, model, updatePropValue }) => [
                      vue.createVNode(SourceEdit, vue.mergeProps({ jsonEditerComponent: __props.jsonEditerComponent }, item.props || {}, {
                        modelValue: model,
                        "onUpdate:modelValue": (val) => updatePropValue("", val)
                      }), null, 16, ["jsonEditerComponent", "modelValue", "onUpdate:modelValue"])
                    ]),
                    key: "1"
                  } : void 0,
                  !_ctx.$slots.proFormBuilderStyleEdit ? {
                    name: "proFormBuilderStyleEdit",
                    fn: vue.withCtx(({ item, modelValue, updateValue }) => [
                      vue.createVNode(StyleEdit, vue.mergeProps(item.props || {}, {
                        modelValue,
                        "onUpdate:modelValue": updateValue
                      }), null, 16, ["modelValue", "onUpdate:modelValue"])
                    ]),
                    key: "2"
                  } : void 0,
                  vue.renderList(Object.keys(_ctx.$slots), (name) => {
                    return {
                      name,
                      fn: vue.withCtx((slotProps) => [
                        vue.renderSlot(_ctx.$slots, name, vue.normalizeProps(vue.guardReactiveProps(slotProps || {})))
                      ])
                    };
                  })
                ]), 1064, ["itemTypeData", "httpRequest", "model", "items"]))
              ])
            ])) : vue.createCommentVNode("", true)
          ]),
          _: 3
        })
      ], 64);
    };
  }
});
module.exports = _sfc_main;
