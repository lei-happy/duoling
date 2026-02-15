"use strict";
const vue = require("vue");
const elementPlus = require("element-plus");
const index$1 = require("../icons/index");
const receiver = require("../ele-config-provider/receiver");
const common = require("../utils/common");
const hook = require("../utils/hook");
const message = require("../utils/message");
const messageBox = require("../utils/message-box");
const ElePage = require("../ele-page/index");
const EleCard = require("../ele-card/index");
const EleProTable = require("../ele-pro-table/index");
const EleProForm = require("../ele-pro-form/index");
const util$1 = require("../ele-pro-form/util");
const EleSplitPanel = require("../ele-split-panel/index");
const util$2 = require("../ele-data-table/util");
const EleButtons = require("../ele-buttons/index");
const TableExtra = require("./components/table-extra");
const PageSide = require("./components/page-side");
const util = require("./util");
const props = require("./props");
function _isSlot(s) {
  return typeof s === "function" || Object.prototype.toString.call(s) === "[object Object]" && !vue.isVNode(s);
}
const index = /* @__PURE__ */ vue.defineComponent({
  name: "EleCrud",
  props: props.crudProps,
  emits: props.crudEmits,
  setup(props2, {
    emit,
    slots,
    expose
  }) {
    const {
      lang
    } = receiver.useLocale("crud", props2);
    const message$1 = message.useMessage({
      plain: true
    });
    const messageBox$1 = messageBox.useMessageBox();
    const defaultSearchFormProps = util.getDefaultSearchFormProps();
    const tableRef = vue.ref(null);
    const selections = vue.ref([]);
    const addVisible = vue.ref(false);
    const addData = vue.ref();
    const editVisible = vue.ref(false);
    const editData = vue.ref();
    const toolbarBtnItems = vue.computed(() => {
      const listConfig = props2.listConfig || {};
      const addBtnProps = listConfig.addBtnProps;
      const delBtnProps = listConfig.delBtnProps;
      const items = [];
      if (addBtnProps !== false) {
        items.push({
          preset: "add",
          props: addBtnProps === true ? void 0 : addBtnProps,
          onClick: () => handleBtnClick("add")
        });
      }
      if (delBtnProps !== false) {
        items.push({
          preset: "delBatch",
          props: delBtnProps === true ? void 0 : delBtnProps,
          onClick: () => handleBtnClick("delSelections")
        });
      }
      return items;
    });
    const actionBtnItems = vue.computed(() => {
      const listConfig = props2.listConfig || {};
      const editLinkProps = listConfig.editLinkProps;
      const delLinkProps = listConfig.delLinkProps;
      const delPopConfirmProps = listConfig.delPopConfirmProps;
      const items = [];
      if (editLinkProps !== false) {
        items.push({
          preset: "edit",
          props: editLinkProps === true ? void 0 : editLinkProps,
          command: "edit"
        });
      }
      if (delLinkProps !== false) {
        const item = {
          preset: "del",
          props: delLinkProps === true ? void 0 : delLinkProps,
          command: "del"
        };
        if (delPopConfirmProps != null && typeof delPopConfirmProps === "object" && delPopConfirmProps.isPopConfirm) {
          item.popconfirmProps = {
            content: lang.value.deleteConfirm,
            popperOptions: {
              strategy: "fixed",
              modifiers: [{
                name: "offset",
                options: {
                  offset: [12, 6]
                }
              }]
            },
            ...common.omit(delPopConfirmProps, ["isPopConfirm"])
          };
          item.command = "delConfirm";
        }
        items.push(item);
      }
      return items;
    });
    const tableColumns = vue.computed(() => {
      const listConfig = props2.listConfig || {};
      const userColumns = listConfig.tableProps?.columns;
      if (userColumns?.length) {
        return userColumns;
      }
      const fields = props2.fields;
      const {
        selectionColumnProps,
        indexColumnProps,
        actionColumnProps
      } = listConfig;
      const columns = [];
      if (selectionColumnProps !== false) {
        columns.push({
          type: "selection",
          columnKey: "selection",
          width: 50,
          align: "center",
          fixed: "left",
          ...(selectionColumnProps === true ? void 0 : selectionColumnProps) || {}
        });
      }
      if (indexColumnProps !== false) {
        columns.push({
          type: "index",
          columnKey: "index",
          width: 50,
          align: "center",
          fixed: "left",
          ...(indexColumnProps === true ? void 0 : indexColumnProps) || {}
        });
      }
      common.mapTree(fields || [], (field) => {
        if (field.hideInList === "flat") {
          return "flatChildren";
        } else if (!field.hideInList) {
          return {
            columnKey: field.key,
            prop: field.prop,
            label: field.label,
            ...field.columnProps || {}
          };
        }
      }).forEach((column) => {
        columns.push(column);
      });
      if (actionColumnProps !== false) {
        columns.push({
          columnKey: "action",
          label: lang.value.action,
          width: 156,
          align: "center",
          fixed: "right",
          slot: "action",
          hideInPrint: true,
          hideInExport: true,
          ...(actionColumnProps === true ? void 0 : actionColumnProps) || {}
        });
      }
      return columns;
    });
    const searchFormProps = vue.computed(() => {
      const searchConfig = (props2.searchConfig === true ? void 0 : props2.searchConfig) || {};
      return searchConfig.formProps || {};
    });
    const searchFormItems = vue.computed(() => {
      const items = searchFormProps.value.items;
      return items?.length ? items : util.getFieldsSearchFormItems(props2.fields);
    });
    const searchFormData = vue.reactive(util$1.getFormInitValue(searchFormItems.value, searchFormProps.value.itemTypeData || props2.itemTypeData, true));
    const searchWhere = vue.ref(util$1.cloneDeep(searchFormData));
    const treeSelectedValue = vue.ref();
    const treeData = vue.ref([]);
    const treeLoading = vue.ref(false);
    const treeErrorMessage = vue.ref();
    const treeSearchkeywords = vue.ref("");
    const splitPanelCollapse = vue.ref(false);
    const [isMobile] = hook.useMobile((mobile) => {
      splitPanelCollapse.value = mobile;
    });
    const codeCache = /* @__PURE__ */ new Map();
    const getAndCacheCode = (code, codeResult) => {
      const cacheResult = codeCache.get(code);
      if (cacheResult) {
        return cacheResult;
      }
      const result = codeResult ?? util.getCodeResult(code, props2.httpRequest);
      codeCache.set(code, result);
      return result;
    };
    const tableDatasource = (params) => {
      const datasource = props2.listConfig?.tableProps?.datasource || props2.listApi;
      if (datasource && Array.isArray(datasource)) {
        return Promise.resolve(datasource);
      }
      const func = typeof datasource === "function" ? datasource : typeof datasource === "string" && datasource.startsWith(util.codeStringPrefix) ? getAndCacheCode(datasource) : void 0;
      const showSide = !!props2.pageConfig?.splitPanelProps;
      if (!func || showSide && treeSelectedValue.value == null) {
        return Promise.resolve([]);
      }
      const where = {};
      if (showSide && treeSelectedValue.value != null) {
        const filterField = props2.pageConfig?.tableFilterField;
        if (filterField) {
          util$1.setValue(where, filterField, treeSelectedValue.value);
        }
      }
      util$1.mergeValue(where, searchWhere.value, params.where);
      return func({
        ...params,
        where
      });
    };
    const getTableSelections = () => {
      return selections.value;
    };
    const handleUpdateSelections = (data) => {
      selections.value = data;
      emit("tableSelectionsChange", data);
    };
    const reloadTable = (page) => {
      tableRef.value?.reload?.({
        page
      });
    };
    const handleUpdateSearchForm = (field, value) => {
      util$1.setValue(searchFormData, field, value);
    };
    const handleSubmitSearchForm = () => {
      selections.value = [];
      searchWhere.value = util$1.cloneDeep(searchFormData);
      reloadTable(1);
    };
    const handleResetSearchForm = () => {
      Object.keys(searchFormData).forEach((key) => {
        searchFormData[key] = void 0;
      });
      util$1.mergeValue(searchFormData, util$1.getFormInitValue(searchFormItems.value, searchFormProps.value.itemTypeData || props2.itemTypeData, true));
      handleSubmitSearchForm();
    };
    const handleBtnClick = (action, item) => {
      if (action === "delConfirm") {
        handleDelete(item ? [item] : void 0);
      } else if (action === "del") {
        const delPopConfirmProps = props2.listConfig?.delPopConfirmProps;
        if (delPopConfirmProps === false) {
          handleDelete(item ? [item] : void 0);
        } else {
          messageBox$1.confirm(lang.value.deleteConfirm, lang.value.deleteConfirmTitle, {
            type: "warning",
            draggable: true,
            ...common.omit(delPopConfirmProps === true ? void 0 : delPopConfirmProps, ["isPopConfirm"])
          }).then(() => {
            handleDelete(item ? [item] : void 0);
          }).catch(() => {
          });
        }
      } else if (action === "edit") {
        editData.value = item;
        editVisible.value = true;
      } else if (action === "add") {
        const filterField = props2.pageConfig?.tableFilterField;
        if (props2.pageConfig?.splitPanelProps && treeSelectedValue.value != null && filterField) {
          const data = {};
          util$1.setValue(data, filterField, treeSelectedValue.value);
          addData.value = data;
        } else {
          addData.value = void 0;
        }
        addVisible.value = true;
      } else if (action === "delSelections") {
        const data = selections.value;
        if (!data.length) {
          message$1.error({
            ...props2.messageOptions || {},
            message: lang.value.deleteBatchTip
          });
          return;
        }
        const delConfirmProps = props2.listConfig?.delConfirmProps;
        if (delConfirmProps === false) {
          handleDelete(data);
        } else {
          messageBox$1.confirm(lang.value.deleteBatchConfirm, lang.value.deleteBatchConfirmTitle, {
            type: "warning",
            draggable: true,
            ...(delConfirmProps === true ? void 0 : delConfirmProps) || {}
          }).then(() => {
            handleDelete(data);
          }).catch(() => {
          });
        }
      }
    };
    const handleDelete = (data) => {
      if (!data || !props2.deleteApi) {
        return;
      }
      const deleteApiFunc = typeof props2.deleteApi === "function" ? props2.deleteApi : props2.deleteApi.startsWith(util.codeStringPrefix) ? getAndCacheCode(props2.deleteApi) : void 0;
      if (!deleteApiFunc) {
        return;
      }
      const loading = message$1.loading({
        ...props2.messageOptions || {},
        message: lang.value.deleteLoading
      });
      const rowKey = props2.listConfig?.tableProps?.rowKey;
      const dataKeys = rowKey ? data.map((row) => util$2.getValue(row, rowKey)) : [];
      deleteApiFunc(dataKeys, data).then((msg) => {
        loading.close();
        message$1.success({
          ...props2.messageOptions || {},
          message: msg ?? lang.value.deleteSuccess
        });
        reloadTable(1);
      }).catch((e) => {
        loading.close();
        if (e != null && typeof e === "string") {
          message$1.error({
            ...props2.messageOptions || {},
            message: e
          });
        } else {
          message$1.error({
            ...props2.messageOptions || {},
            message: e?.message ?? lang.value.deleteError
          });
        }
      });
    };
    const handleAddError = (e) => {
      if (e != null && typeof e === "string") {
        message$1.error({
          ...props2.messageOptions || {},
          message: e
        });
      } else {
        message$1.error({
          ...props2.messageOptions || {},
          message: e?.message ?? lang.value.addError
        });
      }
    };
    const handleEditError = (e) => {
      if (e != null && typeof e === "string") {
        message$1.error({
          ...props2.messageOptions || {},
          message: e
        });
      } else {
        message$1.error({
          ...props2.messageOptions || {},
          message: e?.message ?? lang.value.editError
        });
      }
    };
    const handleAddDone = (msg) => {
      message$1.success({
        ...props2.messageOptions || {},
        message: msg ?? lang.value.editSuccess
      });
      reloadTable(1);
    };
    const handleEditDone = (msg) => {
      message$1.success({
        ...props2.messageOptions || {},
        message: msg ?? lang.value.addSuccess
      });
      reloadTable();
    };
    const handleUpdateAddVisible = (visible) => {
      addVisible.value = visible;
    };
    const handleUpdateEditVisible = (visible) => {
      editVisible.value = visible;
    };
    const handleTreeNodeClick = (nodeValue) => {
      if (isMobile.value) {
        splitPanelCollapse.value = true;
      }
      if (treeSelectedValue.value !== nodeValue) {
        treeSelectedValue.value = nodeValue;
        reloadTable();
      }
    };
    const setTreeData = (data) => {
      treeLoading.value = false;
      treeData.value = data || [];
      if (treeData.value.length) {
        const field = util.getTreeValueField(props2.pageConfig?.sideConfig);
        treeSelectedValue.value = treeData.value[0][field];
        reloadTable();
      } else {
        treeSelectedValue.value = void 0;
      }
    };
    const reloadTree = () => {
      if (!props2.treeListApi || !props2.pageConfig?.splitPanelProps) {
        setTreeData([]);
        return;
      }
      if (Array.isArray(props2.treeListApi)) {
        setTreeData(props2.treeListApi);
        return;
      }
      const treeListApiFunc = typeof props2.treeListApi === "function" ? props2.treeListApi : props2.treeListApi.startsWith(util.codeStringPrefix) ? getAndCacheCode(props2.treeListApi) : void 0;
      if (!treeListApiFunc) {
        return;
      }
      treeLoading.value = true;
      treeListApiFunc().then((data) => {
        setTreeData(data);
      }).catch((e) => {
        treeLoading.value = false;
        if (e != null && typeof e === "string") {
          treeErrorMessage.value = e;
        } else {
          treeErrorMessage.value = e?.message;
        }
      });
    };
    const handleUpdateTreeSearchKeywords = (value) => {
      treeSearchkeywords.value = value;
    };
    const handleUpdateSplitPanelCollapse = (collapse) => {
      splitPanelCollapse.value = collapse;
    };
    const clearCodeCache = () => {
      codeCache.clear();
    };
    const renderSearch = () => {
      if (props2.searchConfig === false) {
        return;
      }
      const searchConfig = (props2.searchConfig === true ? void 0 : props2.searchConfig) || {};
      const cardProps = searchConfig.cardProps;
      const renderForm = () => {
        return vue.h(props2.proFormComponent || EleProForm, {
          ...defaultSearchFormProps,
          itemTypeData: props2.itemTypeData,
          httpRequest: props2.httpRequest,
          screenSize: props2.screenSize,
          ...searchFormProps.value,
          model: searchFormData,
          items: searchFormItems.value,
          onUpdateValue: handleUpdateSearchForm,
          onSubmit: handleSubmitSearchForm,
          onReset: handleResetSearchForm
        }, {
          footer: ({
            submitForm,
            resetForm
          }) => vue.createVNode(EleButtons, {
            "items": [{
              preset: "search",
              props: searchFormProps.value.submitButtonProps,
              onClick: () => submitForm()
            }, {
              preset: "reset",
              props: searchFormProps.value.resetButtonProps,
              onClick: () => resetForm()
            }]
          }, null),
          ...common.getMappedSlots(slots, searchConfig.formSlots, [], [], true)
        });
      };
      if (!cardProps) {
        return renderForm();
      }
      return vue.createVNode(EleCard, vue.mergeProps({
        "searchForm": true
      }, (cardProps === true ? void 0 : cardProps) || {}), {
        ...common.getMappedSlots(slots, searchConfig.cardSlots),
        default: renderForm
      });
    };
    const renderTable = () => {
      const listConfig = props2.listConfig || {};
      const cardProps = listConfig.cardProps;
      const tableProps = listConfig.tableProps || {};
      const renderTb = () => {
        const tSlots = common.getMappedSlots(slots, listConfig.tableSlots, [], ["default"], true);
        const toolbarSlot = tSlots.toolbar;
        tSlots.toolbar = (slotProps) => vue.createVNode(EleButtons, {
          "items": toolbarBtnItems.value
        }, {
          default: toolbarSlot ? toolbarSlot(slotProps) : void 0
        });
        const actionSlot = tSlots.action;
        tSlots.action = (slotProps) => vue.createVNode(EleButtons, {
          "type": "link",
          "divider": true,
          "items": actionBtnItems.value,
          "onItemClick": (command) => handleBtnClick(command, slotProps?.row)
        }, {
          default: actionSlot ? actionSlot(slotProps) : void 0
        });
        const bottomExtraSlot = tSlots.bottomExtra;
        tSlots.bottomExtra = (slotProps) => vue.createVNode(TableExtra, {
          "addVisible": addVisible.value,
          "addData": addData.value,
          "editVisible": editVisible.value,
          "editData": editData.value,
          "addConfig": props2.addConfig,
          "editConfig": props2.editConfig,
          "fields": props2.fields,
          "getAndCacheCode": getAndCacheCode,
          "proFormComponent": props2.proFormComponent,
          "addApi": props2.addApi,
          "editApi": props2.editApi,
          "itemTypeData": props2.itemTypeData,
          "httpRequest": props2.httpRequest,
          "screenSize": props2.screenSize,
          "lang": lang.value,
          "onBtnClick": handleBtnClick,
          "onAddError": handleAddError,
          "onAddDone": handleAddDone,
          "onEditError": handleEditError,
          "onEditDone": handleEditDone,
          "onUpdate:addVisible": handleUpdateAddVisible,
          "onUpdate:editVisible": handleUpdateEditVisible
        }, {
          ...common.omit(slots, ["default"]),
          default: bottomExtraSlot ? bottomExtraSlot(slotProps) : void 0
        });
        const arrayDatasource = tableProps?.datasource == null ? props2.listApi && Array.isArray(props2.listApi) ? props2.listApi : void 0 : Array.isArray(tableProps.datasource) ? tableProps.datasource : void 0;
        return vue.createVNode(EleProTable, vue.mergeProps(tableProps, {
          "ref": tableRef,
          "columns": tableColumns.value,
          "datasource": arrayDatasource || tableDatasource,
          "selections": selections.value,
          "onUpdate:selections": handleUpdateSelections
        }), _isSlot(tSlots) ? tSlots : {
          default: () => [tSlots]
        });
      };
      if (!cardProps) {
        return renderTb();
      }
      return vue.createVNode(EleCard, (cardProps === true ? void 0 : cardProps) || {}, {
        ...common.getMappedSlots(slots, listConfig.cardSlots),
        default: renderTb
      });
    };
    const renderContent = () => {
      const nodes = [];
      const sNodes = renderSearch();
      const tbNodes = renderTable();
      const pageConfig = props2.pageConfig || {};
      const splitPanelProps = pageConfig.splitPanelProps;
      if (!splitPanelProps) {
        if (sNodes) {
          (Array.isArray(sNodes) ? sNodes : [sNodes]).forEach((node) => {
            nodes.push(node);
          });
        }
        if (tbNodes) {
          (Array.isArray(tbNodes) ? tbNodes : [tbNodes]).forEach((node) => {
            nodes.push(node);
          });
        }
      } else {
        const bodyNodes = [];
        if (!pageConfig.splitSearchForm && sNodes) {
          (Array.isArray(sNodes) ? sNodes : [sNodes]).forEach((node) => {
            bodyNodes.push(node);
          });
        }
        if (tbNodes) {
          (Array.isArray(tbNodes) ? tbNodes : [tbNodes]).forEach((node) => {
            bodyNodes.push(node);
          });
        }
        nodes.push(vue.createVNode(EleSplitPanel, vue.mergeProps({
          "size": 258,
          "space": 0,
          "allowCollapse": true,
          "collapseBtnOffset": 2,
          "collapse": splitPanelCollapse.value,
          "class": "ele-crud-split-panel",
          "onUpdate:collapse": handleUpdateSplitPanelCollapse
        }, (splitPanelProps === true ? void 0 : splitPanelProps) || {}), {
          ...common.getMappedSlots(slots, pageConfig.splitPanelSlots),
          default: () => vue.createVNode(PageSide, {
            "sideConfig": pageConfig.sideConfig,
            "data": treeData.value,
            "loading": treeLoading.value,
            "selectedValue": treeSelectedValue.value,
            "errorMessage": treeErrorMessage.value,
            "keywords": treeSearchkeywords.value,
            "lang": lang.value,
            "onTreeNodeClick": handleTreeNodeClick
          }, {
            ...slots
          }),
          sideHeader: pageConfig.sideConfig?.searchProps !== false ? () => {
            let _slot;
            return vue.createVNode(elementPlus.ElInput, vue.mergeProps({
              "placeholder": lang.value.searchPlaceholder,
              "clearable": true,
              "prefixIcon": index$1.SearchOutlined,
              "modelValue": treeSearchkeywords.value,
              "onUpdate:modelValue": handleUpdateTreeSearchKeywords,
              "class": "ele-crud-tree-search"
            }, pageConfig.sideConfig?.searchInputProps || {}), _isSlot(_slot = common.getMappedSlots(slots, pageConfig.sideConfig?.searchInputSlots)) ? _slot : {
              default: () => [_slot]
            });
          } : void 0,
          bodyHeader: pageConfig.splitSearchForm && sNodes ? () => sNodes : void 0,
          body: () => bodyNodes
        }));
      }
      const cardProps = pageConfig.cardProps;
      if (!cardProps) {
        return nodes;
      }
      return vue.createVNode(EleCard, (cardProps === true ? void 0 : cardProps) || {}, {
        ...common.getMappedSlots(slots, pageConfig.cardSlots),
        default: () => nodes
      });
    };
    vue.watch(() => props2.listApi, () => {
      tableRef.value?.setData?.([]);
      handleSubmitSearchForm();
    }, {
      deep: true
    });
    vue.watch(() => props2.treeListApi, () => {
      reloadTree();
    }, {
      deep: true,
      immediate: true
    });
    vue.onBeforeUnmount(() => {
      clearCodeCache();
    });
    const exposeValue = {
      tableRef,
      getTableSelections,
      reloadTree
    };
    expose(exposeValue);
    return () => {
      const pageProps = props2.pageConfig?.pageProps;
      if (!pageProps) {
        return renderContent();
      }
      return vue.createVNode(ElePage, (pageProps === true ? void 0 : pageProps) || {}, {
        default: () => renderContent()
      });
    };
  }
});
module.exports = index;
