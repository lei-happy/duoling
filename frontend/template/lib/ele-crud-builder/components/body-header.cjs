"use strict";
const vue = require("vue");
const elementPlus = require("element-plus");
const index = require("../../icons/index");
const util$1 = require("../../ele-pro-form-builder/util");
const util = require("../util");
const ImportModal = require("./import-modal");
const CodePreview = require("./code-preview");
const _hoisted_1 = { class: "ele-crud-builder-header" };
const _hoisted_2 = { class: "ele-crud-builder-screen-radio" };
const _hoisted_3 = { class: "ele-crud-builder-header-left" };
const _hoisted_4 = { class: "ele-crud-builder-header-tools" };
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "BodyHeader" },
  __name: "body-header",
  props: {
    currentScreen: {},
    undoDisabled: { type: Boolean },
    redoDisabled: { type: Boolean },
    config: {},
    headerTools: { type: [Boolean, Array] },
    proFormComponent: {},
    jsonEditerComponent: {},
    codeViewerComponent: {},
    itemTypeData: {},
    httpRequest: {}
  },
  emits: ["update:currentScreen", "undo", "redo", "clear", "importData"],
  setup(__props, { emit: __emit }) {
    const props = __props;
    const emit = __emit;
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
          (vue.openBlock(true), vue.createElementBlock(vue.Fragment, null, vue.renderList(vue.unref(util$1.screenItems), (item) => {
            return vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElIcon), {
              key: item.value,
              class: vue.normalizeClass(["ele-crud-builder-header-tool ele-crud-builder-screen-icon", { "is-active": item.value === __props.currentScreen }]),
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
            class: vue.normalizeClass(["ele-crud-builder-header-tool ele-crud-builder-header-tool-undo", { "is-disabled": __props.undoDisabled }]),
            title: "撤销",
            onClick: handleUndo
          }, {
            default: vue.withCtx(() => [
              vue.createVNode(vue.unref(index.RollbackOutlined))
            ]),
            _: 1
          }, 8, ["class"]),
          vue.createVNode(vue.unref(elementPlus.ElIcon), {
            class: vue.normalizeClass(["ele-crud-builder-header-tool ele-crud-builder-header-tool-redo", { "is-disabled": __props.redoDisabled }]),
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
                default: vue.withCtx(() => [..._cache[2] || (_cache[2] = [
                  vue.createTextVNode(" 导入 ", -1)
                ])]),
                _: 1
              }, 8, ["icon"])) : toolName === "export" ? (vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElButton), {
                key: 1,
                text: true,
                icon: vue.unref(index.DownloadOutlined),
                onClick: handleOpenExport
              }, {
                default: vue.withCtx(() => [..._cache[3] || (_cache[3] = [
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
                default: vue.withCtx(() => [..._cache[4] || (_cache[4] = [
                  vue.createTextVNode(" 清空 ", -1)
                ])]),
                _: 1
              }, 8, ["icon"])) : toolName === "code" ? (vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElButton), {
                key: 3,
                text: true,
                type: "primary",
                icon: vue.unref(index.CodeOutlined),
                onClick: handleOpenCode
              }, {
                default: vue.withCtx(() => [..._cache[5] || (_cache[5] = [
                  vue.createTextVNode(" 生成代码 ", -1)
                ])]),
                _: 1
              }, 8, ["icon"])) : vue.createCommentVNode("", true)
            ], 64);
          }), 128)),
          vue.renderSlot(_ctx.$slots, "headerTools")
        ]),
        headerRightToolNames.value && (headerRightToolNames.value.includes("import") || headerRightToolNames.value.includes("export")) ? (vue.openBlock(), vue.createBlock(ImportModal, {
          key: 0,
          modelValue: importVisible.value,
          "onUpdate:modelValue": _cache[0] || (_cache[0] = ($event) => importVisible.value = $event),
          config: __props.config,
          isImport: isImport.value,
          jsonEditerComponent: __props.jsonEditerComponent,
          onImportData: handleImportData
        }, null, 8, ["modelValue", "config", "isImport", "jsonEditerComponent"])) : vue.createCommentVNode("", true),
        headerRightToolNames.value && headerRightToolNames.value.includes("code") ? (vue.openBlock(), vue.createBlock(CodePreview, {
          key: 1,
          modelValue: codeVisible.value,
          "onUpdate:modelValue": _cache[1] || (_cache[1] = ($event) => codeVisible.value = $event),
          config: __props.config,
          codeViewerComponent: __props.codeViewerComponent
        }, null, 8, ["modelValue", "config", "codeViewerComponent"])) : vue.createCommentVNode("", true)
      ]);
    };
  }
});
module.exports = _sfc_main;
