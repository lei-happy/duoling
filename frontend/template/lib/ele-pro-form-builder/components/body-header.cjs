"use strict";
const vue = require("vue");
const elementPlus = require("element-plus");
const index = require("../../icons/index");
const util = require("../util");
const PreviewModal = require("./preview-modal");
const ImportModal = require("./import-modal");
const CodePreview = require("./code-preview");
const _hoisted_1 = { class: "ele-pro-form-builder-header" };
const _hoisted_2 = { class: "ele-pro-form-builder-screen-radio" };
const _hoisted_3 = { class: "ele-pro-form-builder-header-left" };
const _hoisted_4 = { class: "ele-pro-form-builder-header-tools" };
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "BodyHeader" },
  __name: "body-header",
  props: {
    currentScreen: {},
    undoDisabled: { type: Boolean },
    redoDisabled: { type: Boolean },
    formProps: {},
    headerTools: { type: [Boolean, Array] },
    proFormComponent: {},
    jsonEditerComponent: {},
    codeViewerComponent: {},
    componentData: {},
    itemTypeData: {},
    httpRequest: {}
  },
  emits: ["update:currentScreen", "undo", "redo", "clear", "previewFormSubmit", "importData"],
  setup(__props, { emit: __emit }) {
    const ownSlots = ["headerTools"];
    const props = __props;
    const emit = __emit;
    const previewVisible = vue.ref(false);
    const importVisible = vue.ref(false);
    const isImport = vue.ref(false);
    const codeVisible = vue.ref(false);
    const headerRightToolNames = vue.computed(() => {
      if (typeof props.headerTools === "undefined" || props.headerTools === true) {
        return util.defaultHeaderRightTools;
      }
      if (!props.headerTools) {
        return [];
      }
      return props.headerTools;
    });
    const handleUpdateScreen = (size) => {
      emit("update:currentScreen", size);
    };
    const handleUndo = () => {
      if (!props.undoDisabled) {
        emit("undo");
      }
    };
    const handleRedo = () => {
      if (!props.redoDisabled) {
        emit("redo");
      }
    };
    const handleClear = () => {
      emit("clear");
    };
    const handleOpenPreview = () => {
      previewVisible.value = true;
    };
    const handlePreviewFormSubmit = (data) => {
      emit("previewFormSubmit", data);
    };
    const handleOpenImport = () => {
      importVisible.value = true;
      isImport.value = true;
    };
    const handleOpenExport = () => {
      importVisible.value = true;
      isImport.value = false;
    };
    const handleImportData = (data) => {
      emit("importData", data);
    };
    const handleOpenCode = () => {
      codeVisible.value = true;
    };
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("div", _hoisted_1, [
        vue.createElementVNode("div", _hoisted_2, [
          (vue.openBlock(true), vue.createElementBlock(vue.Fragment, null, vue.renderList(vue.unref(util.screenItems), (item) => {
            return vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElIcon), {
              key: item.value,
              class: vue.normalizeClass(["ele-pro-form-builder-header-tool ele-pro-form-builder-screen-icon", { "is-active": item.value === __props.currentScreen }]),
              onClick: ($event) => handleUpdateScreen(item.value)
            }, {
              default: vue.withCtx(() => [
                (vue.openBlock(), vue.createBlock(vue.resolveDynamicComponent(item.icon), {
                  style: vue.normalizeStyle(item.iconStyle)
                }, null, 8, ["style"]))
              ]),
              _: 2
            }, 1032, ["class", "onClick"]);
          }), 128))
        ]),
        vue.createElementVNode("div", _hoisted_3, [
          vue.createVNode(vue.unref(elementPlus.ElIcon), {
            class: vue.normalizeClass(["ele-pro-form-builder-header-tool ele-pro-form-builder-header-tool-undo", { "is-disabled": __props.undoDisabled }]),
            title: "撤销",
            onClick: handleUndo
          }, {
            default: vue.withCtx(() => [
              vue.createVNode(vue.unref(index.RollbackOutlined))
            ]),
            _: 1
          }, 8, ["class"]),
          vue.createVNode(vue.unref(elementPlus.ElIcon), {
            class: vue.normalizeClass(["ele-pro-form-builder-header-tool ele-pro-form-builder-header-tool-redo", { "is-disabled": __props.redoDisabled }]),
            title: "恢复",
            onClick: handleRedo
          }, {
            default: vue.withCtx(() => [
              vue.createVNode(vue.unref(index.RecoverOutlined))
            ]),
            _: 1
          }, 8, ["class"])
        ]),
        vue.createElementVNode("div", _hoisted_4, [
          (vue.openBlock(true), vue.createElementBlock(vue.Fragment, null, vue.renderList(headerRightToolNames.value, (toolName) => {
            return vue.openBlock(), vue.createElementBlock(vue.Fragment, { key: toolName }, [
              toolName === "import" ? (vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElButton), {
                key: 0,
                text: true,
                icon: vue.unref(index.UploadOutlined),
                onClick: handleOpenImport
              }, {
                default: vue.withCtx(() => [..._cache[3] || (_cache[3] = [
                  vue.createTextVNode(" 导入 ", -1)
                ])]),
                _: 1
              }, 8, ["icon"])) : toolName === "export" ? (vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElButton), {
                key: 1,
                text: true,
                icon: vue.unref(index.DownloadOutlined),
                onClick: handleOpenExport
              }, {
                default: vue.withCtx(() => [..._cache[4] || (_cache[4] = [
                  vue.createTextVNode(" 导出 ", -1)
                ])]),
                _: 1
              }, 8, ["icon"])) : toolName === "clear" ? (vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElButton), {
                key: 2,
                text: true,
                type: "danger",
                icon: vue.unref(index.DeleteOutlined),
                onClick: handleClear
              }, {
                default: vue.withCtx(() => [..._cache[5] || (_cache[5] = [
                  vue.createTextVNode(" 清空 ", -1)
                ])]),
                _: 1
              }, 8, ["icon"])) : toolName === "preview" ? (vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElButton), {
                key: 3,
                text: true,
                type: "primary",
                icon: vue.unref(index.EyeOutlined),
                onClick: handleOpenPreview
              }, {
                default: vue.withCtx(() => [..._cache[6] || (_cache[6] = [
                  vue.createTextVNode(" 预览 ", -1)
                ])]),
                _: 1
              }, 8, ["icon"])) : toolName === "code" ? (vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElButton), {
                key: 4,
                text: true,
                type: "primary",
                icon: vue.unref(index.CodeOutlined),
                onClick: handleOpenCode
              }, {
                default: vue.withCtx(() => [..._cache[7] || (_cache[7] = [
                  vue.createTextVNode(" 生成代码 ", -1)
                ])]),
                _: 1
              }, 8, ["icon"])) : vue.createCommentVNode("", true)
            ], 64);
          }), 128)),
          vue.renderSlot(_ctx.$slots, "headerTools")
        ]),
        headerRightToolNames.value && headerRightToolNames.value.includes("preview") ? (vue.openBlock(), vue.createBlock(PreviewModal, {
          key: 0,
          modelValue: previewVisible.value,
          "onUpdate:modelValue": _cache[0] || (_cache[0] = ($event) => previewVisible.value = $event),
          formProps: __props.formProps,
          proFormComponent: __props.proFormComponent,
          itemTypeData: __props.itemTypeData,
          httpRequest: __props.httpRequest,
          onPreviewFormSubmit: handlePreviewFormSubmit
        }, vue.createSlots({ _: 2 }, [
          vue.renderList(Object.keys(_ctx.$slots).filter((k) => !ownSlots.includes(k)), (name) => {
            return {
              name,
              fn: vue.withCtx((slotProps) => [
                vue.renderSlot(_ctx.$slots, name, vue.normalizeProps(vue.guardReactiveProps(slotProps || {})))
              ])
            };
          })
        ]), 1032, ["modelValue", "formProps", "proFormComponent", "itemTypeData", "httpRequest"])) : vue.createCommentVNode("", true),
        headerRightToolNames.value && (headerRightToolNames.value.includes("import") || headerRightToolNames.value.includes("export")) ? (vue.openBlock(), vue.createBlock(ImportModal, {
          key: 1,
          modelValue: importVisible.value,
          "onUpdate:modelValue": _cache[1] || (_cache[1] = ($event) => importVisible.value = $event),
          config: __props.formProps,
          isImport: isImport.value,
          jsonEditerComponent: __props.jsonEditerComponent,
          onImportData: handleImportData
        }, null, 8, ["modelValue", "config", "isImport", "jsonEditerComponent"])) : vue.createCommentVNode("", true),
        headerRightToolNames.value && headerRightToolNames.value.includes("code") ? (vue.openBlock(), vue.createBlock(CodePreview, {
          key: 2,
          modelValue: codeVisible.value,
          "onUpdate:modelValue": _cache[2] || (_cache[2] = ($event) => codeVisible.value = $event),
          config: __props.formProps,
          componentData: __props.componentData,
          codeViewerComponent: __props.codeViewerComponent
        }, null, 8, ["modelValue", "config", "componentData", "codeViewerComponent"])) : vue.createCommentVNode("", true)
      ]);
    };
  }
});
module.exports = _sfc_main;
