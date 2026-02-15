"use strict";
Object.defineProperty(exports, Symbol.toStringTag, { value: "Module" });
const common = require("../utils/common");
const renderUtil = require("./components/render-util");
const renderCore = require("./components/render-core");
function isContainerType(item, itemTypeData) {
  const typeData = renderUtil.getItemTypeData(item, itemTypeData);
  return typeData?.isContainer || item.itemType === "container" || item.itemType === "view";
}
function getFormInitValue(items, itemTypeData, excludeUndefined) {
  const init = {};
  common.eachTree(items, (item) => {
    if (item.initValue != null && item.initValue !== "" && item.prop) {
      renderUtil.setValue(init, item.prop, item.initValue);
      return;
    }
    if (item.type && item.prop) {
      if ("tabs" === item.type) {
        const active = item.props?.modelValue ?? item.children?.[0]?.prop;
        renderUtil.setValue(init, item.prop, active);
        return;
      }
      if ("collapse" === item.type) {
        const active = item.props?.modelValue ?? (item.props?.accordion ? item.children?.[0]?.props?.name ?? item.children?.[0]?.prop : []);
        renderUtil.setValue(init, item.prop, active);
        return;
      }
      if ("sliderRange" === item.type) {
        renderUtil.setValue(init, item.prop, [
          item.props?.min ?? 0,
          item.props?.max ?? 100
        ]);
        return;
      }
    }
    if (excludeUndefined || isContainerType(item, itemTypeData) || !item.prop || typeof renderUtil.getValue(init, item.prop) !== "undefined") {
      return;
    }
    renderUtil.setValue(init, item.prop, void 0);
  });
  return init;
}
Object.defineProperty(exports, "ChildrenRender", {
  enumerable: true,
  get: () => renderUtil.ChildrenRender
});
Object.defineProperty(exports, "cloneDeep", {
  enumerable: true,
  get: () => renderUtil.cloneDeep
});
Object.defineProperty(exports, "getValue", {
  enumerable: true,
  get: () => renderUtil.getValue
});
Object.defineProperty(exports, "mergeValue", {
  enumerable: true,
  get: () => renderUtil.mergeValue
});
Object.defineProperty(exports, "setValue", {
  enumerable: true,
  get: () => renderUtil.setValue
});
Object.defineProperty(exports, "sortableGroupName", {
  enumerable: true,
  get: () => renderCore.sortableGroupName
});
exports.getFormInitValue = getFormInitValue;
exports.isContainerType = isContainerType;
