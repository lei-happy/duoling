"use strict";
Object.defineProperty(exports, Symbol.toStringTag, { value: "Module" });
const vue = require("vue");
const lodashEs = require("lodash-es");
const VueDraggable = require("vuedraggable");
const elementPlus = require("element-plus");
const receiver = require("../../ele-config-provider/receiver");
const common = require("../../utils/common");
const props = require("../props");
const BuilderWrapper = require("./builder-wrapper");
const BuilderToolWrapper = require("./builder-tool-wrapper");
const DraggableRow = require("./draggable-row");
const itemTypeData = require("./item-type-data");
const renderCore = require("./render-core");
function _isSlot(s) {
  return typeof s === "function" || Object.prototype.toString.call(s) === "[object Object]" && !vue.isVNode(s);
}
function getItemTypeName(item) {
  let itemType = item.type;
  const divTag = item.props?.is;
  if (itemType === "div" && divTag) {
    if (divTag === "tr") {
      itemType = "tableRow";
    } else if (divTag === "td") {
      itemType = "tableCell";
    } else if (divTag === "ele-table" || divTag === "EleTable") {
      itemType = "table";
    } else if (divTag === "el-carousel" || divTag === "ElCarousel") {
      itemType = "carousel";
    } else if (divTag === "el-carousel-item" || divTag === "ElCarouselItem") {
      itemType = "carouselItem";
    } else if (divTag === "el-icon" || divTag === "ElIcon") {
      itemType = "icon";
    } else if (divTag === "ele-admin-layout" || divTag === "EleAdminLayout") {
      itemType = "adminLayout";
    } else if (divTag === "el-alert" || divTag === "EleAlert") {
      itemType = "alert";
    }
  }
  return itemType;
}
function getItemTypeData(item, itemTypeData$1) {
  const itemType = getItemTypeName(item);
  if (itemType == null) {
    return;
  }
  const typeData = [...itemTypeData$1 || [], ...itemTypeData.defaultItemTypeData].find((d) => d.type === itemType);
  return typeData;
}
function getComponentLegacyProps(item) {
  const result = {};
  const itemType = getItemTypeName(item);
  if (itemType) {
    const options = item.options;
    if (options) {
      if (["select", "multipleSelect", "radio", "radioButton", "checkbox", "checkboxButton", "cascader", "multipleCascader", "mention"].includes(itemType)) {
        result.options = options;
      } else if (["treeSelect", "treeMultipleSelect"].includes(itemType)) {
        result.data = options;
      } else if (["checkCard", "multipleCheckCard"].includes(itemType)) {
        result.items = options;
      } else if (itemType === "autocomplete") {
        result.fetchSuggestions = options;
      }
    }
    if (item.label != null) {
      if (["descriptionsItem", "carouselItem"].includes(itemType)) {
        result.label = item.label;
      } else if (["alert", "collapseItem", "descriptions"].includes(itemType)) {
        result.title = item.label;
      } else if (itemType === "card") {
        result.header = item.label;
      } else if (itemType === "image") {
        result.alt = item.label;
      }
    }
    if (item.prop != null) {
      if (["collapseItem", "carouselItem"].includes(itemType)) {
        result.name = item.prop;
      }
    }
  }
  return result;
}
function getRuleMessage(label, requiredMessage, placeholder, requiredLang) {
  if (typeof requiredMessage === "string" && requiredMessage) {
    return requiredMessage;
  }
  if (typeof placeholder === "string" && placeholder) {
    return placeholder;
  }
  const labelText = label ?? "";
  if (!requiredLang) {
    return labelText;
  }
  return requiredLang.replace(/\{\s*label\s*\}/g, String(labelText));
}
function getComponentRefName(item) {
  const prop = item.prop;
  if (prop == null || prop === "" || String(prop).trim() === "") {
    return `${String(item.key)}Ref`;
  }
  return `${String(prop)}Ref`;
}
function renderProFormItem(props2) {
  const slots = props2.slots || {};
  const formData = props2.model || {};
  const typeData = getItemTypeData(props2.item, props2.itemTypeData);
  const typeSlot = props2.item?.type ? slots[props2.item.type] : void 0;
  if (!typeSlot && !typeData) {
    return;
  }
  const modelValue = props2.item.prop == null ? void 0 : lodashEs.get(formData, props2.item.prop);
  const handleUpdateModelValue = (value) => {
    const propName = props2.item.prop;
    if (propName != null && props2.updateItemValue) {
      props2.updateItemValue(propName, value);
    }
  };
  const propsFunctionParams = {
    item: props2.item,
    modelValue,
    updateModelValue: handleUpdateModelValue,
    isShowFormItem: (cItem) => renderCore.isShowItem(cItem, formData, props2.formItems || [], props2.searchExpand, props2.editable),
    renderChildren: (cItem, cSortDisabled, cContainerSelectable) => renderProFormContent({
      model: formData,
      items: cItem.children,
      rules: props2.rules,
      grid: cItem.grid,
      rowProps: cItem.rowProps,
      parentItem: cItem,
      formItems: props2.formItems,
      searchExpand: props2.searchExpand,
      editable: props2.editable,
      screenSize: props2.screenSize,
      sortDisabled: !!cSortDisabled,
      containerSelectable: !!cContainerSelectable,
      activeItemKey: props2.activeItemKey,
      updateItemValue: props2.updateItemValue,
      updateItemsData: props2.updateItemsData,
      updateActiveItemKey: props2.updateActiveItemKey,
      getAndCacheCode: props2.getAndCacheCode,
      itemTypeData: props2.itemTypeData,
      httpRequest: props2.httpRequest,
      getProFormRefs: props2.getProFormRefs,
      slots,
      requiredLang: props2.requiredLang
    })
  };
  const slotProFormParams = {
    item: props2.item,
    // 替代 items , 兼容旧版
    model: formData,
    rules: props2.rules,
    grid: props2.item?.grid,
    rowProps: props2.item?.rowProps,
    parentItem: props2.item,
    formItems: props2.formItems,
    searchExpand: props2.searchExpand,
    editable: props2.editable,
    screenSize: props2.screenSize,
    activeItemKey: props2.activeItemKey,
    itemTypeData: props2.itemTypeData,
    httpRequest: props2.httpRequest,
    getProFormRefs: props2.getProFormRefs,
    getAndCacheCode: props2.getAndCacheCode,
    updateItemValue: props2.updateItemValue,
    updateItemsData: props2.updateItemsData,
    updateActiveItemKey: props2.updateActiveItemKey,
    slots,
    requiredLang: props2.requiredLang
  };
  const itemSlots = {};
  if (!typeSlot) {
    const itemSlotMap = props2.item.slots || {};
    Object.keys(itemSlotMap).forEach((name) => {
      if (itemSlotMap[name]) {
        const slotFuntion = slots[itemSlotMap[name]];
        if (slotFuntion) {
          itemSlots[name] = (slotProps) => slotFuntion({
            proForm: slotProFormParams,
            ...slotProps || {}
          });
        }
      }
    });
    if (typeData && typeData.reservedSlots) {
      const itemReservedSlots = typeData.reservedSlots(propsFunctionParams);
      Object.keys(itemReservedSlots).forEach((name) => {
        if (itemReservedSlots[name]) {
          itemSlots[name] = itemReservedSlots[name];
        }
      });
    }
    if (!itemSlots.default) {
      const csd = !(props2.item.containerDraggable ?? !typeData?.sortDisabled);
      const isRenderLabel = typeData?.renderLabelText && props2.item.label != null && props2.item.label !== "";
      const isRenderChildren = (!typeData || typeData.isContainer) && (!csd && props2.editable || props2.item.children && props2.item.children.length);
      if (isRenderLabel || isRenderChildren) {
        itemSlots.default = () => {
          const nodes = [];
          if (isRenderLabel && props2.item.label != null) {
            nodes.push(props2.item.label);
          }
          if (isRenderChildren) {
            const contentNode = renderProFormContent({
              model: formData,
              items: props2.item.children,
              rules: props2.rules,
              grid: props2.item.grid,
              rowProps: props2.item.rowProps,
              parentItem: props2.item,
              formItems: props2.formItems,
              searchExpand: props2.searchExpand,
              editable: props2.editable,
              screenSize: props2.screenSize,
              sortDisabled: csd,
              containerSelectable: !!typeData?.containerSelectable,
              activeItemKey: props2.activeItemKey,
              updateItemValue: props2.updateItemValue,
              updateItemsData: props2.updateItemsData,
              updateActiveItemKey: props2.updateActiveItemKey,
              getAndCacheCode: props2.getAndCacheCode,
              itemTypeData: props2.itemTypeData,
              httpRequest: props2.httpRequest,
              getProFormRefs: props2.getProFormRefs,
              slots,
              requiredLang: props2.requiredLang
            });
            if (contentNode) {
              if (Array.isArray(contentNode)) {
                contentNode.forEach((node) => {
                  nodes.push(node);
                });
              } else {
                nodes.push(contentNode);
              }
            }
          }
          return nodes;
        };
      }
    }
  }
  const componentTag = typeData?.component || "div";
  const isDivTag = componentTag === "div" || componentTag === "td";
  const componentPropsData = renderCore.translateJsCode(props2.item.props || {}, formData, props2.formItems || [], props2.searchExpand, props2.httpRequest, props2.getProFormRefs, props2.getAndCacheCode).result;
  const componentNode = typeSlot ? typeSlot({
    item: {
      ...props2.item,
      props: componentPropsData
    },
    model: formData,
    modelValue,
    updateValue: handleUpdateModelValue,
    updatePropValue: props2.updateItemValue,
    itemComponentRef: getComponentRefName(props2.item),
    proForm: slotProFormParams
  }) : vue.h((isDivTag ? props2.item.props?.is : void 0) || componentTag, vue.mergeProps({
    key: props2.key
  }, getComponentLegacyProps(props2.item), typeData?.defaultProps?.(propsFunctionParams) || {}, isDivTag ? common.omit(componentPropsData, ["is"]) : typeData?.type === "col" ? renderCore.getScreenSizeColProps(props2.screenSize, {}, componentPropsData) : componentPropsData, typeData?.reservedProps?.(propsFunctionParams) || {}, {
    ref: getComponentRefName(props2.item)
  }), itemSlots);
  if (typeData?.isContainer || props2.item.itemType === "container" || props2.item.itemType === "view") {
    return componentNode;
  }
  const itemPropsData = renderCore.translateJsCode(props2.item.itemProps || {}, formData, props2.formItems || [], props2.searchExpand, props2.httpRequest, props2.getProFormRefs, props2.getAndCacheCode).result;
  const labelWidth = itemPropsData.labelWidth;
  const formItemLabelWidth = typeof labelWidth === "number" ? `${labelWidth}px` : labelWidth;
  const formItemSlots = common.getMappedSlots(slots, props2.item.itemSlots);
  formItemSlots.default = () => componentNode;
  const iRule = itemPropsData.rules;
  const iRules = iRule ? Array.isArray(iRule) ? iRule : [iRule] : void 0;
  const fRule = props2.rules && props2.item.prop ? lodashEs.get(props2.rules, props2.item.prop) : void 0;
  const fRules = fRule ? Array.isArray(fRule) ? fRule : [fRule] : void 0;
  const formItemRules = iRules || fRules || [];
  const trigger = typeData?.requiredTrigger ?? "change";
  const message = getRuleMessage(props2.item.label, props2.item.requiredMessage, componentPropsData.placeholder, props2.requiredLang);
  if (props2.item.required) {
    formItemRules.unshift({
      required: true,
      message,
      trigger
    });
  }
  return vue.createVNode(elementPlus.ElFormItem, vue.mergeProps({
    "key": props2.key,
    "label": props2.item.label
  }, itemPropsData, {
    "labelWidth": formItemLabelWidth,
    "prop": props2.item.prop,
    "rules": formItemRules
  }), _isSlot(formItemSlots) ? formItemSlots : {
    default: () => [formItemSlots]
  });
}
function renderProFormContent(props2) {
  const nodes = [];
  const slots = props2.slots || {};
  const itemsData = props2.items || [];
  const formData = props2.model || {};
  const ownSlots = ["default", "contentExtra"];
  const getProFormItemNode = (item, isEditable, isSortDisabled) => {
    const itemKey = item.key ?? item.prop;
    const defaultSlot = () => {
      return renderProFormItem({
        key: itemKey,
        item,
        model: formData,
        rules: props2.rules,
        formItems: props2.formItems,
        searchExpand: props2.searchExpand,
        editable: props2.editable,
        screenSize: props2.screenSize,
        activeItemKey: props2.activeItemKey,
        updateItemValue: props2.updateItemValue,
        updateItemsData: props2.updateItemsData,
        updateActiveItemKey: props2.updateActiveItemKey,
        getAndCacheCode: props2.getAndCacheCode,
        itemTypeData: props2.itemTypeData,
        httpRequest: props2.httpRequest,
        getProFormRefs: props2.getProFormRefs,
        slots: common.omit(slots, ownSlots),
        requiredLang: props2.requiredLang
      });
    };
    if (!isEditable) {
      return defaultSlot();
    }
    return vue.createVNode(BuilderWrapper, {
      "key": itemKey,
      "item": item,
      "handle": !isSortDisabled,
      "activeItemKey": props2.activeItemKey,
      "onUpdate:activeItemKey": props2.updateActiveItemKey
    }, {
      default: defaultSlot,
      builderItemHandleContent: slots.builderItemHandleContent,
      builderItemTools: slots.builderItemTools
    });
  };
  const handleUpdateItemsModelValue = (data) => {
    if (props2.updateItemsData) {
      props2.updateItemsData(data, props2.parentItem);
    }
  };
  if (props2.grid) {
    const gridColProps = props2.grid === true ? {
      span: 12
    } : props2.grid;
    const getItemColNode = (item, isEditable, isSortDisabled, className) => {
      let _slot;
      const itemKey = item.key ?? item.prop;
      const itemColProps = renderCore.translateJsCode(item.colProps || {}, formData, props2.formItems || [], props2.searchExpand, props2.httpRequest, props2.getProFormRefs, props2.getAndCacheCode).result;
      return vue.createVNode(elementPlus.ElCol, vue.mergeProps({
        "key": itemKey,
        "class": className
      }, renderCore.getScreenSizeColProps(props2.screenSize, gridColProps, itemColProps)), _isSlot(_slot = getProFormItemNode(item, isEditable, isSortDisabled)) ? _slot : {
        default: () => [_slot]
      });
    };
    const getContentExtraNode = (contentExtraSlot) => {
      let _slot2;
      const itemsLength = (props2.formItems || []).filter((item) => renderCore.isShowItem(item, formData, props2.formItems || [], props2.searchExpand, props2.editable)).length;
      return vue.createVNode(elementPlus.ElCol, renderCore.getScreenSizeColProps(props2.screenSize, props2.autoContentExtraCol ? renderCore.computeContentExtraCol(gridColProps, itemsLength) : {
        span: 24
      }, renderCore.translateJsCode(props2.contentExtraColProps || {}, formData, props2.formItems || [], props2.searchExpand, props2.httpRequest, props2.getProFormRefs, props2.getAndCacheCode).result), _isSlot(_slot2 = contentExtraSlot()) ? _slot2 : {
        default: () => [_slot2]
      });
    };
    if (props2.editable && !props2.sortDisabled) {
      return vue.createVNode(DraggableRow, {
        "itemsData": itemsData,
        "componentData": renderCore.translateJsCode(props2.rowProps || {}, formData, props2.formItems || [], props2.searchExpand, props2.httpRequest, props2.getProFormRefs, props2.getAndCacheCode).result,
        "screenSize": props2.screenSize,
        "gridColProps": gridColProps,
        "formData": formData,
        "formItems": props2.formItems,
        "searchExpand": props2.searchExpand,
        "httpRequest": props2.httpRequest,
        "getProFormRefs": props2.getProFormRefs,
        "getAndCacheCode": props2.getAndCacheCode,
        "autoContentExtraCol": props2.autoContentExtraCol,
        "contentExtraColProps": props2.contentExtraColProps,
        "editable": props2.editable,
        "onUpdateItems": handleUpdateItemsModelValue
      }, {
        item: ({
          element
        }) => getProFormItemNode(element, true, false),
        footer: slots.contentExtra ? slots.contentExtra() : void 0
      });
    }
    itemsData.forEach((item) => {
      const isShow = renderCore.isShowItem(item, formData, props2.formItems || [], props2.searchExpand, props2.editable);
      if (isShow) {
        nodes.push(getItemColNode(item));
      }
    });
    if (slots.contentExtra) {
      nodes.push(getContentExtraNode(slots.contentExtra));
    }
    return vue.createVNode(elementPlus.ElRow, renderCore.translateJsCode(props2.rowProps || {}, formData, props2.formItems || [], props2.searchExpand, props2.httpRequest, props2.getProFormRefs, props2.getAndCacheCode).result, _isSlot(nodes) ? nodes : {
      default: () => [nodes]
    });
  }
  if (props2.editable && !props2.sortDisabled) {
    const footerSlot = () => vue.createVNode(BuilderToolWrapper, {
      "item": props2.parentItem,
      "activeItemKey": props2.activeItemKey,
      "handle": false
    }, {
      builderItemHandleContent: slots.builderItemHandleContent,
      builderItemTools: slots.builderItemTools
    });
    const handleContainerBuilderWrapperClick = (e) => {
      const parentItemKey = props2.parentItem?.key;
      if (props2.containerSelectable && parentItemKey != null) {
        e.stopPropagation();
        if (props2.updateActiveItemKey) {
          props2.updateActiveItemKey(parentItemKey);
        }
      }
    };
    nodes.push(vue.createVNode(VueDraggable, {
      "itemKey": "key",
      "animation": 150,
      "modelValue": itemsData,
      "setData": () => void 0,
      "group": renderCore.sortableGroupName,
      "handle": ".ele-pro-form-builder-item-handle",
      "draggable": ".ele-pro-form-builder-item-wrapper",
      "class": ["ele-pro-form-builder-container-wrapper", {
        "is-selectable": props2.containerSelectable
      }, {
        "is-active": props2.containerSelectable && props2.parentItem && props2.parentItem.key != null && props2.activeItemKey != null && props2.activeItemKey === props2.parentItem.key
      }],
      "onUpdate:modelValue": handleUpdateItemsModelValue,
      "onClick": handleContainerBuilderWrapperClick
    }, {
      item: ({
        element
      }) => getProFormItemNode(element, true),
      footer: props2.containerSelectable && props2.parentItem ? footerSlot : void 0
    }));
  } else {
    itemsData.forEach((item) => {
      if (renderCore.isShowItem(item, formData, props2.formItems || [], props2.searchExpand, props2.editable)) {
        const proFormItemNode = getProFormItemNode(item);
        if (proFormItemNode) {
          if (Array.isArray(proFormItemNode)) {
            proFormItemNode.forEach((node) => {
              nodes.push(node);
            });
          } else {
            nodes.push(proFormItemNode);
          }
        }
      }
    });
  }
  if (slots.contentExtra) {
    const contentExtraNodes = slots.contentExtra();
    if (contentExtraNodes) {
      if (Array.isArray(contentExtraNodes)) {
        contentExtraNodes.forEach((node) => {
          nodes.push(node);
        });
      } else {
        nodes.push(contentExtraNodes);
      }
    }
  }
  return nodes;
}
const ChildrenRender = /* @__PURE__ */ vue.defineComponent({
  name: "ChildrenRender",
  props: props.childrenRenderProps,
  emits: {
    updateItemValue: (_prop, _value) => true,
    updateItemsData: (_items, _parentItem) => true,
    "update:activeItemKey": (_activeKey) => true
  },
  setup(props2, {
    emit,
    slots
  }) {
    const {
      lang
    } = receiver.useLocale("proForm", props2);
    const handleUpdateItemValue = (prop, value) => {
      emit("updateItemValue", prop, value);
    };
    const handleUpdateItemsData = (items, parentItem) => {
      emit("updateItemsData", items, parentItem);
    };
    const handleUpdateActiveItemKey = (activeKey) => {
      emit("update:activeItemKey", activeKey);
    };
    return () => renderProFormContent({
      ...common.omit(props2, ["item"]),
      items: props2.items ?? props2.item?.children,
      // 兼容旧版
      updateItemValue: props2.updateItemValue ?? handleUpdateItemValue,
      updateItemsData: props2.updateItemsData ?? handleUpdateItemsData,
      updateActiveItemKey: props2.updateActiveItemKey ?? handleUpdateActiveItemKey,
      slots: props2.slots ?? slots,
      requiredLang: props2.requiredLang ?? lang.value.required
    });
  }
});
Object.defineProperty(exports, "cloneDeep", {
  enumerable: true,
  get: () => lodashEs.cloneDeep
});
Object.defineProperty(exports, "getValue", {
  enumerable: true,
  get: () => lodashEs.get
});
Object.defineProperty(exports, "mergeValue", {
  enumerable: true,
  get: () => lodashEs.merge
});
Object.defineProperty(exports, "setValue", {
  enumerable: true,
  get: () => lodashEs.set
});
exports.ChildrenRender = ChildrenRender;
exports.getComponentLegacyProps = getComponentLegacyProps;
exports.getComponentRefName = getComponentRefName;
exports.getItemTypeData = getItemTypeData;
exports.getItemTypeName = getItemTypeName;
exports.getRuleMessage = getRuleMessage;
exports.renderProFormContent = renderProFormContent;
exports.renderProFormItem = renderProFormItem;
