"use strict";
const vue = require("vue");
const elementPlus = require("element-plus");
const hook = require("../utils/hook");
const common = require("../utils/common");
const EleSplitPanel = require("../ele-split-panel/index");
const EleTabBar = require("../ele-tab-bar/index");
const util = require("../ele-pro-form/util");
const buildCore = require("../ele-pro-form-builder/components/build-core");
const EleCrud = require("../ele-crud/index");
const util$1 = require("../ele-crud/util");
const FieldTree = require("./components/field-tree");
const PageConfig = require("./components/page-config");
const TemplateList = require("./components/template-list");
const BodyHeader = require("./components/body-header");
const props = require("./props");
const _hoisted_1 = { class: "ele-crud-builder-tab-body" };
const _hoisted_2 = { class: "ele-crud-builder-body-wrapper" };
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "EleCrudBuilder" },
  __name: "index",
  props: props.crudBuilderProps,
  emits: props.crudBuilderEmits,
  setup(__props) {
    const ownSlots = ["default", "headerTools"];
    const props2 = __props;
    const crudConfig = vue.useModel(props2, "modelValue");
    const leftSideCollapse = vue.ref(false);
    const [isMobile] = hook.useMobile((mobile) => {
      leftSideCollapse.value = mobile;
    });
    const leftTabActive = vue.ref("fields");
    const currentScreen = vue.ref("pc");
    const historyDataList = vue.ref([]);
    const redoDataList = vue.ref([]);
    let storeHistoryTimer = null;
    const stopStoreHistoryTimer = () => {
      if (storeHistoryTimer != null) {
        clearTimeout(storeHistoryTimer);
        storeHistoryTimer = null;
      }
    };
    const getCrudFields = () => {
      return crudConfig.value?.fields || [];
    };
    const setCrudFields = (fields) => {
      if (!crudConfig.value) {
        crudConfig.value = { fields: fields || [] };
        return;
      }
      crudConfig.value.fields = fields || [];
    };
    const getStoreConfigData = () => {
      return buildCore.deepCloneObject(crudConfig.value);
    };
    const setStoreConfigData = (data) => {
      crudConfig.value = data;
    };
    const storeHistory = (delay) => {
      stopStoreHistoryTimer();
      const undoData = getStoreConfigData();
      if (!delay) {
        historyDataList.value.push(undoData);
        redoDataList.value = [];
        return;
      }
      storeHistoryTimer = setTimeout(() => {
        historyDataList.value.push(undoData);
        redoDataList.value = [];
      }, 600);
    };
    const handleDeleteField = (key) => {
      if (key == null) {
        return;
      }
      storeHistory();
      const fieldsData = getCrudFields();
      common.eachTree(fieldsData, (item, index, parent) => {
        if (item.key === key) {
          if (parent) {
            if (parent.children) {
              parent.children.splice(index, 1);
            }
          } else {
            fieldsData.splice(index, 1);
          }
          return false;
        }
      });
    };
    const handleAddField = (field, parentKey, index) => {
      if (!field) {
        return;
      }
      storeHistory();
      if (parentKey == null) {
        if (index != null) {
          const items = getCrudFields();
          setCrudFields([...items.slice(0, index), field, ...items.slice(index)]);
        } else {
          setCrudFields([...getCrudFields(), field]);
          if (crudConfig.value != null) {
            if (field.hideInSearch !== true) {
              const items = util.getValue(
                crudConfig.value,
                "searchConfig.formProps.items"
              );
              if (items != null && Array.isArray(items) && items.length) {
                util.setValue(crudConfig.value, "searchConfig.formProps.items", [
                  ...items,
                  ...util$1.getFieldsSearchFormItems([field])
                ]);
              }
            }
            if (field.hideInAdd !== true) {
              const items = util.getValue(
                crudConfig.value,
                "addConfig.formProps.items"
              );
              if (items != null && Array.isArray(items) && items.length) {
                util.setValue(crudConfig.value, "addConfig.formProps.items", [
                  ...items,
                  ...util$1.getFieldsAddFormItems([field])
                ]);
              }
            }
            if (field.hideInEdit !== true) {
              const items = util.getValue(
                crudConfig.value,
                "editConfig.formProps.items"
              );
              if (items != null && Array.isArray(items) && items.length) {
                util.setValue(crudConfig.value, "editConfig.formProps.items", [
                  ...items,
                  ...util$1.getFieldsEditFormItems([field])
                ]);
              }
            }
          }
        }
        return;
      }
      const parent = common.findTree(getCrudFields(), (item) => item.key === parentKey);
      if (parent) {
        if (parent.children) {
          if (index != null) {
            parent.children.splice(index, 0, field);
          } else {
            parent.children.push(field);
          }
        } else {
          parent.children = [field];
        }
      }
    };
    const handleUpdateField = (field) => {
      if (field == null || field.key == null) {
        return;
      }
      storeHistory();
      common.eachTree(getCrudFields(), (item) => {
        if (item.key === field.key) {
          Object.assign(item, field);
          return false;
        }
      });
    };
    const handleUpdateFieldChildren = (data, parentKey) => {
      storeHistory(true);
      if (parentKey == null) {
        setCrudFields(data);
        return;
      }
      common.eachTree(getCrudFields(), (item) => {
        if (item.key === parentKey) {
          item.children = data;
          return false;
        }
      });
    };
    const handleUpdateConfigField = (field, value, delayStoreHistory) => {
      storeHistory(delayStoreHistory ?? !!field);
      if (!field) {
        const excludeFields = ["fields"];
        const temp = common.omit(value, excludeFields);
        if (!crudConfig.value) {
          const config = {};
          Object.assign(config, temp);
          crudConfig.value = config;
        } else {
          Object.assign(crudConfig.value, temp);
          const valueKeys = Object.keys(temp);
          Object.keys(crudConfig.value).forEach((key) => {
            if (crudConfig.value && !excludeFields.includes(key) && !valueKeys.includes(key) && typeof crudConfig.value[key] !== "undefined") {
              crudConfig.value[key] = void 0;
            }
          });
        }
      } else if (!crudConfig.value) {
        const config = {};
        util.setValue(config, field, value);
        crudConfig.value = config;
      } else {
        util.setValue(crudConfig.value, field, value);
      }
    };
    const handleUpdateFormConfig = (data, type) => {
      if (type === "search") {
        handleUpdateConfigField("searchConfig.formProps", data, false);
      } else if (type === "add") {
        handleUpdateConfigField("addConfig.formProps", data, false);
      } else if (type === "edit") {
        handleUpdateConfigField("editConfig.formProps", data, false);
      }
    };
    const handleUndo = () => {
      const data = historyDataList.value.pop();
      if (!data) {
        return;
      }
      const redoData = getStoreConfigData();
      redoDataList.value.unshift(redoData);
      setStoreConfigData(data);
    };
    const handleRedo = () => {
      const data = redoDataList.value.shift();
      if (!data) {
        return;
      }
      const undoData = getStoreConfigData();
      historyDataList.value.push(undoData);
      setStoreConfigData(data);
    };
    const handleClear = () => {
      if (getCrudFields().length) {
        storeHistory();
        setCrudFields([]);
      }
    };
    const handleImportData = (data) => {
      storeHistory();
      crudConfig.value = { ...data, fields: data.fields || [] };
      if (isMobile.value) {
        leftSideCollapse.value = true;
      }
    };
    vue.onBeforeUnmount(() => {
      stopStoreHistoryTimer();
    });
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createBlock(EleSplitPanel, vue.mergeProps({
        space: 0,
        size: 240,
        allowCollapse: true,
        collapseBtnOffset: 2
      }, _ctx.splitPanelProps || {}, {
        collapse: leftSideCollapse.value,
        "onUpdate:collapse": _cache[2] || (_cache[2] = ($event) => leftSideCollapse.value = $event),
        class: "ele-crud-builder-wrapper"
      }), {
        body: vue.withCtx(() => [
          vue.createElementVNode("div", _hoisted_2, [
            vue.createVNode(BodyHeader, {
              currentScreen: currentScreen.value,
              "onUpdate:currentScreen": _cache[1] || (_cache[1] = ($event) => currentScreen.value = $event),
              undoDisabled: !historyDataList.value.length,
              redoDisabled: !redoDataList.value.length,
              config: vue.unref(crudConfig),
              headerTools: _ctx.headerTools,
              proFormComponent: _ctx.proFormComponent,
              jsonEditerComponent: _ctx.jsonEditerComponent,
              codeViewerComponent: _ctx.codeViewerComponent,
              itemTypeData: _ctx.itemTypeData,
              httpRequest: _ctx.httpRequest,
              onUndo: handleUndo,
              onRedo: handleRedo,
              onClear: handleClear,
              onImportData: handleImportData
            }, vue.createSlots({ _: 2 }, [
              vue.renderList(Object.keys(_ctx.$slots), (name) => {
                return {
                  name,
                  fn: vue.withCtx((slotProps) => [
                    vue.renderSlot(_ctx.$slots, name, vue.normalizeProps(vue.guardReactiveProps(slotProps || {})))
                  ])
                };
              })
            ]), 1032, ["currentScreen", "undoDisabled", "redoDisabled", "config", "headerTools", "proFormComponent", "jsonEditerComponent", "codeViewerComponent", "itemTypeData", "httpRequest"]),
            vue.createElementVNode("div", {
              class: vue.normalizeClass(["ele-crud-builder-body", [
                { "is-pc": currentScreen.value === "pc" },
                { "is-pad": currentScreen.value === "pad" },
                { "is-phone": currentScreen.value === "phone" },
                {
                  "is-show-page-card": !!(vue.unref(crudConfig)?.pageConfig?.pageProps || vue.unref(crudConfig)?.pageConfig?.cardProps || vue.unref(crudConfig)?.listConfig?.cardProps || vue.unref(crudConfig)?.searchConfig && vue.unref(crudConfig).searchConfig !== true && vue.unref(crudConfig).searchConfig.cardProps)
                }
              ]])
            }, [
              !vue.unref(crudConfig) || !vue.unref(crudConfig).fields || !vue.unref(crudConfig).fields.length ? (vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElEmpty), {
                key: 0,
                imageSize: 80,
                class: "ele-crud-builder-form-empty"
              })) : (vue.openBlock(), vue.createBlock(vue.resolveDynamicComponent(_ctx.crudComponent || vue.unref(EleCrud)), vue.mergeProps({
                key: 1,
                proFormComponent: _ctx.proFormComponent,
                itemTypeData: _ctx.itemTypeData,
                httpRequest: _ctx.httpRequest,
                screenSize: currentScreen.value
              }, vue.unref(crudConfig) || {}), vue.createSlots({ _: 2 }, [
                vue.renderList(Object.keys(_ctx.$slots).filter(
                  (k) => !ownSlots.includes(k)
                ), (name) => {
                  return {
                    name,
                    fn: vue.withCtx((slotProps) => [
                      vue.renderSlot(_ctx.$slots, name, vue.normalizeProps(vue.guardReactiveProps(slotProps || {})))
                    ])
                  };
                })
              ]), 1040, ["proFormComponent", "itemTypeData", "httpRequest", "screenSize"]))
            ], 2)
          ])
        ]),
        default: vue.withCtx(() => [
          vue.createVNode(EleTabBar, {
            modelValue: leftTabActive.value,
            "onUpdate:modelValue": _cache[0] || (_cache[0] = ($event) => leftTabActive.value = $event),
            items: [
              { value: "fields", label: "字段列表" },
              { value: "config", label: "页面设置" },
              { value: "templates", label: "模板库" }
            ]
          }, null, 8, ["modelValue"]),
          vue.createElementVNode("div", _hoisted_1, [
            leftTabActive.value === "fields" ? (vue.openBlock(), vue.createBlock(FieldTree, {
              key: 0,
              fields: vue.unref(crudConfig)?.fields,
              fieldEditFormItems: _ctx.fieldEditFormItems,
              proFormComponent: _ctx.proFormComponent,
              jsonEditerComponent: _ctx.jsonEditerComponent,
              itemTypeData: _ctx.itemTypeData,
              httpRequest: _ctx.httpRequest,
              onDeleteField: handleDeleteField,
              onAddField: handleAddField,
              onUpdateField: handleUpdateField,
              onUpdateFieldChildren: handleUpdateFieldChildren
            }, vue.createSlots({ _: 2 }, [
              vue.renderList(Object.keys(_ctx.$slots).filter(
                (k) => !ownSlots.includes(k)
              ), (name) => {
                return {
                  name,
                  fn: vue.withCtx((slotProps) => [
                    vue.renderSlot(_ctx.$slots, name, vue.normalizeProps(vue.guardReactiveProps(slotProps || {})))
                  ])
                };
              })
            ]), 1032, ["fields", "fieldEditFormItems", "proFormComponent", "jsonEditerComponent", "itemTypeData", "httpRequest"])) : leftTabActive.value === "config" ? (vue.openBlock(), vue.createBlock(PageConfig, {
              key: 1,
              config: vue.unref(crudConfig),
              pageConfigFormItems: _ctx.pageConfigFormItems,
              proFormComponent: _ctx.proFormComponent,
              proFormBuilderComponent: _ctx.proFormBuilderComponent,
              proFormBuilderProps: _ctx.proFormBuilderProps,
              codeEditerComponent: _ctx.codeEditerComponent,
              jsonEditerComponent: _ctx.jsonEditerComponent,
              itemTypeData: _ctx.itemTypeData,
              httpRequest: _ctx.httpRequest,
              onUpdateConfigValue: handleUpdateConfigField,
              onUpdateFormConfig: handleUpdateFormConfig
            }, vue.createSlots({ _: 2 }, [
              vue.renderList(Object.keys(_ctx.$slots).filter(
                (k) => !ownSlots.includes(k)
              ), (name) => {
                return {
                  name,
                  fn: vue.withCtx((slotProps) => [
                    vue.renderSlot(_ctx.$slots, name, vue.normalizeProps(vue.guardReactiveProps(slotProps || {})))
                  ])
                };
              })
            ]), 1032, ["config", "pageConfigFormItems", "proFormComponent", "proFormBuilderComponent", "proFormBuilderProps", "codeEditerComponent", "jsonEditerComponent", "itemTypeData", "httpRequest"])) : leftTabActive.value === "templates" ? (vue.openBlock(), vue.createBlock(TemplateList, {
              key: 2,
              templateData: _ctx.templateData,
              onImportData: handleImportData
            }, null, 8, ["templateData"])) : vue.createCommentVNode("", true)
          ])
        ]),
        _: 3
      }, 16, ["collapse"]);
    };
  }
});
module.exports = _sfc_main;
