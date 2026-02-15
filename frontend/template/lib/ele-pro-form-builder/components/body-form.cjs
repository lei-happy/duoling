"use strict";
const vue = require("vue");
const elementPlus = require("element-plus");
const common = require("../../utils/common");
const util = require("../../ele-pro-form/util");
const EleProForm = require("../../ele-pro-form/index");
const buildUtil = require("./build-util");
const ComponentName = require("./component-name");
const BuilderTools = require("./builder-tools");
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "BodyForm" },
  __name: "body-form",
  props: {
    formProps: {},
    currentFormItemId: {},
    currentScreen: {},
    componentData: {},
    proFormComponent: {},
    itemTypeData: {},
    httpRequest: {}
  },
  emits: ["update:currentFormItemId", "updateItems", "openTableTool", "updateFormItems"],
  setup(__props, { emit: __emit }) {
    const ownSlots = ["builderItemHandleContent", "builderItemTools"];
    const props = __props;
    const emit = __emit;
    const proFormRef = vue.ref(null);
    const formData = vue.reactive({});
    const cachebuilderFormData = vue.reactive({});
    const handleUpdateItems = (result) => {
      emit("updateItems", result);
    };
    const handleUpdateCurrentFormItemId = (formItemId) => {
      emit("update:currentFormItemId", formItemId);
    };
    const handleDeleteItem = (item) => {
      if (item.key != null) {
        handleUpdateItems({
          deleteItemIds: [item.key],
          addItems: [],
          updateItems: []
        });
      }
    };
    const handleAddChildrenItem = (formItem, action) => {
      if (formItem.key != null) {
        common.eachTree(props.formProps?.items, (item, cIndex, parent) => {
          if (item.key === formItem.key) {
            const result = buildUtil.generateAddChildData(
              item,
              parent,
              cIndex,
              action,
              props.formProps?.items,
              void 0,
              props.componentData
            );
            handleUpdateItems(result);
            return false;
          }
        });
      }
    };
    const handleCopyItem = (item) => {
      if (item.key != null) {
        handleUpdateItems(
          buildUtil.generateCopyItemData(item.key, props.formProps?.items)
        );
      }
    };
    const handleOpenTableTool = (item, e) => {
      if (item.key != null) {
        emit("openTableTool", item.key, e.currentTarget);
      }
    };
    const setBuilderFormDataFieldValue = (field, value) => {
      util.setValue(formData, field, value);
      util.setValue(cachebuilderFormData, field, value);
    };
    const handleUpdateFormItems = (items) => {
      emit("updateFormItems", items);
    };
    vue.watch(
      () => props.currentFormItemId,
      (currentFormItemId) => {
        common.eachTree(props.formProps?.items, (item, _cIndex, parent) => {
          if (item.key === currentFormItemId) {
            if (item.type && ["tabPane", "collapseItem"].includes(item.type) && parent && parent.prop) {
              setBuilderFormDataFieldValue(parent.prop, item.prop);
            }
            return false;
          }
        });
      }
    );
    vue.watch(
      () => props.formProps,
      () => {
        Object.keys(formData).forEach((k) => {
          formData[k] = void 0;
        });
        util.mergeValue(
          formData,
          util.getFormInitValue(props.formProps?.items, props.itemTypeData, true),
          cachebuilderFormData
        );
      },
      {
        deep: true,
        immediate: true
      }
    );
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("div", {
        class: vue.normalizeClass(["ele-pro-form-builder-body", [
          { "is-pc": __props.currentScreen === "pc" },
          { "is-pad": __props.currentScreen === "pad" },
          { "is-phone": __props.currentScreen === "phone" }
        ]])
      }, [
        (vue.openBlock(), vue.createBlock(vue.resolveDynamicComponent(__props.proFormComponent || EleProForm), vue.mergeProps(__props.formProps || {}, {
          ref_key: "proFormRef",
          ref: proFormRef,
          model: formData,
          activeItemKey: __props.currentFormItemId,
          editable: true,
          screenSize: __props.currentScreen,
          footer: false,
          validateOnRuleChange: false,
          scrollToError: false,
          showMessage: false,
          itemTypeData: __props.itemTypeData,
          httpRequest: __props.httpRequest,
          class: "ele-pro-form-builder-body-form",
          onUpdateValue: setBuilderFormDataFieldValue,
          "onUpdate:items": handleUpdateFormItems,
          "onUpdate:activeItemKey": handleUpdateCurrentFormItemId
        }), vue.createSlots({
          builderItemHandleContent: vue.withCtx(({ item }) => [
            vue.createVNode(ComponentName, {
              itemType: item.type,
              componentData: __props.componentData
            }, null, 8, ["itemType", "componentData"])
          ]),
          builderItemTools: vue.withCtx(({ item }) => [
            vue.createVNode(BuilderTools, {
              itemType: item.type,
              onDelete: ($event) => handleDeleteItem(item),
              onCopy: ($event) => handleCopyItem(item),
              onAdd: ($event) => handleAddChildrenItem(item),
              onAddTableRow: ($event) => handleAddChildrenItem(item, "addTableRow"),
              onAddTableCol: ($event) => handleAddChildrenItem(item, "addTableCol"),
              onOpenTableTool: (e) => handleOpenTableTool(item, e)
            }, null, 8, ["itemType", "onDelete", "onCopy", "onAdd", "onAddTableRow", "onAddTableCol", "onOpenTableTool"])
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
        ]), 1040, ["model", "activeItemKey", "screenSize", "itemTypeData", "httpRequest"])),
        !__props.formProps || !__props.formProps.items || !__props.formProps.items.length ? (vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElEmpty), {
          key: 0,
          imageSize: 80,
          description: "拖拽左侧组件到此",
          class: "ele-pro-form-builder-form-empty"
        })) : vue.createCommentVNode("", true)
      ], 2);
    };
  }
});
module.exports = _sfc_main;
