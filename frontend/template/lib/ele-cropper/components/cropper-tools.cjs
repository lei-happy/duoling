"use strict";
const vue = require("vue");
const elementPlus = require("element-plus");
const index = require("../../icons/index");
const hook = require("../../utils/hook");
const receiver = require("../../ele-config-provider/receiver");
const EleTooltip = require("../../ele-tooltip/index");
const _hoisted_1 = { class: "ele-cropper-tools" };
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "CropperTools" },
  __name: "cropper-tools",
  props: {
    /** 操作按钮布局 */
    tools: String,
    /** 允许上传的图片类型 */
    accept: String,
    /** 是否需要提示组件 */
    tooltip: Boolean,
    /** 提示组件属性 */
    tooltipProps: Object,
    /** 上传按钮点击前的钩子 */
    beforeUploadClick: Function,
    /** 国际化 */
    locale: Object
  },
  emits: {
    zoomIn: () => true,
    zoomOut: () => true,
    moveLeft: () => true,
    moveRight: () => true,
    moveUp: () => true,
    moveDown: () => true,
    rotateLeft: () => true,
    rotateRight: () => true,
    flipX: () => true,
    flipY: () => true,
    reset: () => true,
    upload: (_option) => true,
    ok: () => true
  },
  setup(__props, { emit: __emit }) {
    const props = __props;
    const emit = __emit;
    const TOOL_ICONS = {
      zoomIn: index.ZoomInOutlined,
      zoomOut: index.ZoomOutOutlined,
      moveLeft: index.ArrowLeftOutlined,
      moveRight: index.ArrowRightOutlined,
      moveUp: index.ArrowUpOutlined,
      moveDown: index.ArrowDownOutlined,
      rotateLeft: index.UndoOutlined,
      rotateRight: index.ReloadOutlined,
      flipX: index.SwapOutlined,
      flipY: index.SortOutlined,
      reset: index.SyncOutlined,
      upload: index.UploadOutlined,
      ok: index.CheckOutlined
    };
    const { lang } = receiver.useLocale("cropper", props);
    const [startHideTipTimer, stopHideTipTimer] = hook.useTimer(200);
    const tooltipRef = vue.ref(null);
    const groups = vue.shallowRef([]);
    const tooltipContent = vue.ref("");
    const virtualRef = vue.ref();
    const emitUpload = (data, type) => {
      emit("upload", { data, type });
    };
    const handleUpload = (file) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        const url = e.target?.result;
        if (url != null) {
          emitUpload(url, file.type);
        }
      };
      reader.readAsDataURL(file);
      return false;
    };
    const hideTooltip = () => {
      tooltipRef.value && tooltipRef.value.hide();
    };
    const handleItemHover = (item, e) => {
      const title = lang.value[item.name];
      if (props.tooltip && item.name !== "ok" && title) {
        stopHideTipTimer();
        virtualRef.value = e.currentTarget;
        tooltipContent.value = title;
      }
    };
    const handleClick = (name) => {
      startHideTipTimer(() => {
        hideTooltip();
      });
      emit(name);
    };
    const handleUploadButtonClick = (e) => {
      startHideTipTimer(() => {
        hideTooltip();
      });
      if (props.beforeUploadClick && props.beforeUploadClick(e, emitUpload) === false) {
        e.stopPropagation();
        e.preventDefault();
      }
    };
    vue.watch(
      () => props.tools,
      (tools) => {
        if (!tools) {
          groups.value = [];
          return;
        }
        const names = Object.keys(TOOL_ICONS);
        groups.value = tools.split("|").filter((g) => !!g.trim()).map((g, i) => {
          const items = g.split(",").filter((t) => {
            const name = t.trim();
            return name && names.includes(name);
          }).map((t, j) => {
            const name = t.trim();
            return {
              key: `${i}-${j}-${name}`,
              name,
              icon: vue.markRaw(TOOL_ICONS[name]),
              className: `ele-cropper-${name}`
            };
          });
          return { key: i + g, items };
        });
      },
      { immediate: true }
    );
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("div", _hoisted_1, [
        (vue.openBlock(true), vue.createElementBlock(vue.Fragment, null, vue.renderList(groups.value, (group) => {
          return vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElButtonGroup), {
            key: group.key,
            class: "ele-cropper-tool-item"
          }, {
            default: vue.withCtx(() => [
              (vue.openBlock(true), vue.createElementBlock(vue.Fragment, null, vue.renderList(group.items, (item) => {
                return vue.openBlock(), vue.createElementBlock(vue.Fragment, {
                  key: item.key
                }, [
                  item.name === "upload" ? (vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElUpload), {
                    key: 0,
                    action: "",
                    accept: __props.accept,
                    showFileList: false,
                    beforeUpload: handleUpload,
                    class: "ele-cropper-tool-upload"
                  }, {
                    default: vue.withCtx(() => [
                      vue.createVNode(vue.unref(elementPlus.ElButton), {
                        type: "primary",
                        icon: item.icon,
                        class: vue.normalizeClass(["ele-cropper-tool", item.className]),
                        onMouseover: (e) => handleItemHover(item, e),
                        onClick: handleUploadButtonClick
                      }, null, 8, ["icon", "class", "onMouseover"])
                    ]),
                    _: 2
                  }, 1032, ["accept"])) : (vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElButton), {
                    key: 1,
                    type: "primary",
                    icon: item.icon,
                    class: vue.normalizeClass(["ele-cropper-tool", item.className]),
                    onMouseover: (e) => handleItemHover(item, e),
                    onClick: ($event) => handleClick(item.name)
                  }, {
                    default: vue.withCtx(() => [
                      item.name === "ok" ? (vue.openBlock(), vue.createElementBlock(vue.Fragment, { key: 0 }, [
                        vue.createTextVNode(vue.toDisplayString(vue.unref(lang).ok), 1)
                      ], 64)) : vue.createCommentVNode("", true)
                    ]),
                    _: 2
                  }, 1032, ["icon", "class", "onMouseover", "onClick"]))
                ], 64);
              }), 128))
            ]),
            _: 2
          }, 1024);
        }), 128)),
        vue.createVNode(EleTooltip, vue.mergeProps({
          placement: "top",
          offset: 6
        }, __props.tooltipProps || {}, {
          content: tooltipContent.value,
          virtualRef: virtualRef.value,
          virtualTriggering: true,
          ref_key: "tooltipRef",
          ref: tooltipRef
        }), null, 16, ["content", "virtualRef"])
      ]);
    };
  }
});
module.exports = _sfc_main;
