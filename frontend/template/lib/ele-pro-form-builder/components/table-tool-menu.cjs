"use strict";
const vue = require("vue");
const EleDropdown = require("../../ele-dropdown/index");
const tableUtil = require("./table-util");
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "TableToolMenu" },
  __name: "table-tool-menu",
  props: {
    formItems: {},
    componentData: {}
  },
  emits: ["updateItems"],
  setup(__props, { expose: __expose, emit: __emit }) {
    const props = __props;
    const emit = __emit;
    const dropdownRef = vue.ref();
    const dropdownVirtualRef = vue.ref();
    let tdFormItemId = null;
    const handleUpdateItems = (result) => {
      emit("updateItems", result);
    };
    const handleAddChildren = (formItemId, actionType, position) => {
      const { tableFormItem, tdFormItem } = tableUtil.getTableFormItemByTd(
        formItemId,
        props.formItems
      );
      if (!tableFormItem || !tdFormItem) {
        return;
      }
      const result = (actionType === "addTableCol" ? tableUtil.generateAddTableColData : tableUtil.generateAddTableRowData)(
        tableFormItem,
        props.formItems,
        tdFormItem,
        position,
        props.componentData
      );
      handleUpdateItems(result);
    };
    const handleSplitCell = (formItemId) => {
      const { tableFormItem, tdFormItem } = tableUtil.getTableFormItemByTd(
        formItemId,
        props.formItems
      );
      if (!tableFormItem || !tdFormItem) {
        return;
      }
      const result = tableUtil.getTableSplitEffects(
        tableFormItem,
        props.formItems,
        tdFormItem,
        props.componentData
      );
      handleUpdateItems(result);
    };
    const handleDeleteRow = (formItemId) => {
      const { tableFormItem, trItemIndex } = tableUtil.getTableFormItemByTd(
        formItemId,
        props.formItems
      );
      if (!tableFormItem || trItemIndex == null) {
        return;
      }
      const result = tableUtil.getTableDeleteRowEffects(
        tableFormItem,
        props.formItems,
        trItemIndex,
        props.componentData
      );
      handleUpdateItems(result);
    };
    const handleDeleteCol = (formItemId) => {
      const { tableFormItem, tdFormItem } = tableUtil.getTableFormItemByTd(
        formItemId,
        props.formItems
      );
      if (!tableFormItem || !tdFormItem) {
        return;
      }
      const result = tableUtil.getTableDeleteColEffects(
        tableFormItem,
        props.formItems,
        tdFormItem,
        props.componentData
      );
      handleUpdateItems(result);
    };
    const handleMergeCell = (formItemId, actionType) => {
      const { tableFormItem, tdFormItem } = tableUtil.getTableFormItemByTd(
        formItemId,
        props.formItems
      );
      if (!tableFormItem || !tdFormItem) {
        return;
      }
      const result = (actionType === "mergeBelowCell" ? tableUtil.getTableMergeBelowEffects : tableUtil.getTableMergeRightEffects)(tableFormItem, props.formItems, tdFormItem, props.componentData);
      handleUpdateItems(result);
    };
    const hideTableToolDropdown = () => {
      dropdownRef.value && dropdownRef.value.handleClose();
    };
    const handleTableToolDropdownCommand = (command) => {
      if (tdFormItemId != null) {
        if (command === "insertAboveRow") {
          handleAddChildren(tdFormItemId, "addTableRow", -1);
        } else if (command === "insertBelowRow") {
          handleAddChildren(tdFormItemId, "addTableRow");
        } else if (command === "insertLeftCol") {
          handleAddChildren(tdFormItemId, "addTableCol", -1);
        } else if (command === "insertRightCol") {
          handleAddChildren(tdFormItemId, "addTableCol");
        } else if (command === "mergeRightCell") {
          handleMergeCell(tdFormItemId, "mergeRightCell");
        } else if (command === "mergeBelowCell") {
          handleMergeCell(tdFormItemId, "mergeBelowCell");
        } else if (command === "splitCell") {
          handleSplitCell(tdFormItemId);
        } else if (command === "deleteRow") {
          handleDeleteRow(tdFormItemId);
        } else if (command === "deleteCol") {
          handleDeleteCol(tdFormItemId);
        }
      }
    };
    const openMenu = (formItemId, triggerEl) => {
      hideTableToolDropdown();
      if (!triggerEl) {
        return;
      }
      vue.nextTick(() => {
        tdFormItemId = formItemId;
        dropdownVirtualRef.value = triggerEl;
        vue.nextTick(() => {
          dropdownRef.value && dropdownRef.value.handleOpen();
        });
      });
    };
    const hideMenu = () => {
      hideTableToolDropdown();
    };
    __expose({
      openMenu,
      hideMenu
    });
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createBlock(EleDropdown, {
        triggerKeys: [],
        persistent: false,
        validateEvent: false,
        placement: "bottom-end",
        popperOptions: {
          strategy: "fixed",
          modifiers: [{ name: "offset", options: { offset: [6, 8] } }]
        },
        popperClass: "ele-pro-form-builder-table-tool-dropdown",
        ref_key: "dropdownRef",
        ref: dropdownRef,
        trigger: "click",
        componentType: "pro",
        virtualTriggering: true,
        virtualRef: dropdownVirtualRef.value,
        items: [
          { title: "上方插入行", command: "insertAboveRow" },
          { title: "下方插入行", command: "insertBelowRow" },
          { title: "左侧插入列", command: "insertLeftCol" },
          { title: "右侧插入列", command: "insertRightCol" },
          { title: "合并右侧单元格", command: "mergeRightCell", divided: true },
          { title: "合并下方单元格", command: "mergeBelowCell" },
          { title: "拆分单元格合并", command: "splitCell" },
          {
            title: "删除整行",
            command: "deleteRow",
            divided: true,
            danger: true
          },
          { title: "删除整列", command: "deleteCol", danger: true }
        ],
        onCommand: handleTableToolDropdownCommand
      }, null, 8, ["virtualRef"]);
    };
  }
});
module.exports = _sfc_main;
