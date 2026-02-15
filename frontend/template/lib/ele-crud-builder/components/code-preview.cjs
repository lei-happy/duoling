"use strict";
const vue = require("vue");
const elementPlus = require("element-plus");
const index = require("../../icons/index");
const common = require("../../utils/common");
const hook = require("../../utils/hook");
const EleModal = require("../../ele-modal/index");
const EleTabBar = require("../../ele-tab-bar/index");
const CodeViewer = require("../../ele-pro-form-builder/components/code-viewer");
const codeGenerator = require("./code-generator");
const _hoisted_1 = { class: "ele-crud-builder-code-view" };
const _hoisted_2 = { class: "ele-crud-builder-code-body" };
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "CodePreview" },
  __name: "code-preview",
  props: {
    modelValue: { type: Boolean },
    config: {},
    codeViewerComponent: {}
  },
  emits: ["update:modelValue"],
  setup(__props, { emit: __emit }) {
    const props = __props;
    const emit = __emit;
    const [setCopied, resetCopied, copied] = hook.useTimer(1e3);
    const tabItems = [
      { value: "pro", label: "ProCrud" }
      /* ,
      { value: 'el', label: '' } */
    ];
    const tabActive = vue.ref("pro");
    const codeContent = vue.ref("");
    const generateData = ["", ""];
    const handleUpdateModelValue = (visible) => {
      emit("update:modelValue", visible);
    };
    const setCodeContent = () => {
      codeContent.value = generateData[tabActive.value === "el" ? 1 : 0];
    };
    const handleCopy = () => {
      common.copyText(codeContent.value).then(() => {
        setCopied();
      }).catch((error) => {
        console.error(error);
        resetCopied();
      });
    };
    const handleDownload = () => {
      common.download(codeContent.value, "index.vue", "text/plain;charset=utf-8");
    };
    vue.watch(
      () => props.modelValue,
      (visible) => {
        if (visible) {
          const proCode = codeGenerator.generateProCode(props.config);
          const elCode = codeGenerator.generateElCode(props.config);
          generateData[0] = proCode;
          generateData[1] = elCode;
          setCodeContent();
        }
      }
    );
    vue.watch(tabActive, () => {
      setCodeContent();
    });
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createBlock(EleModal, {
        width: 980,
        maxable: true,
        position: "center",
        title: "生成代码",
        modelValue: __props.modelValue,
        closeOnClickModal: false,
        destroyOnClose: true,
        class: "ele-crud-builder-code-preview",
        "onUpdate:modelValue": handleUpdateModelValue
      }, {
        default: vue.withCtx(() => [
          vue.createElementVNode("div", _hoisted_1, [
            vue.createVNode(EleTabBar, {
              modelValue: tabActive.value,
              "onUpdate:modelValue": _cache[0] || (_cache[0] = ($event) => tabActive.value = $event),
              items: tabItems
            }, {
              extra: vue.withCtx(() => [
                vue.createVNode(vue.unref(elementPlus.ElIcon), {
                  class: vue.normalizeClass(["ele-crud-builder-code-icon-tool", { "is-copied": vue.unref(copied) }]),
                  title: "复制",
                  onClick: handleCopy
                }, {
                  default: vue.withCtx(() => [
                    vue.unref(copied) ? (vue.openBlock(), vue.createBlock(vue.unref(index.CheckOutlined), { key: 0 })) : (vue.openBlock(), vue.createBlock(vue.unref(index.CopyOutlined), { key: 1 }))
                  ]),
                  _: 1
                }, 8, ["class"]),
                vue.createVNode(vue.unref(elementPlus.ElIcon), {
                  class: "ele-crud-builder-code-icon-tool",
                  title: "下载",
                  onClick: handleDownload
                }, {
                  default: vue.withCtx(() => [
                    vue.createVNode(vue.unref(index.DownloadOutlined))
                  ]),
                  _: 1
                })
              ]),
              _: 1
            }, 8, ["modelValue"]),
            vue.createElementVNode("div", _hoisted_2, [
              (vue.openBlock(), vue.createBlock(vue.resolveDynamicComponent(__props.codeViewerComponent || CodeViewer), { code: codeContent.value }, null, 8, ["code"]))
            ])
          ])
        ]),
        _: 1
      }, 8, ["modelValue"]);
    };
  }
});
module.exports = _sfc_main;
