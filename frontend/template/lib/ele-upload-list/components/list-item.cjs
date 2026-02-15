"use strict";
const vue = require("vue");
const elementPlus = require("element-plus");
const index = require("../../icons/index");
const _hoisted_1 = ["title"];
const _hoisted_2 = {
  key: 0,
  class: "ele-upload-thumbnail"
};
const _hoisted_3 = { class: "ele-upload-thumbnail-text" };
const _hoisted_4 = {
  key: 0,
  class: "ele-upload-progress"
};
const _hoisted_5 = { class: "ele-upload-text" };
const _hoisted_6 = ["title"];
const _hoisted_7 = { class: "ele-upload-tool-text" };
const _hoisted_8 = {
  key: 1,
  class: "ele-upload-tools"
};
const _hoisted_9 = ["title"];
const _hoisted_10 = { class: "ele-upload-tool-text" };
const _hoisted_11 = ["title"];
const _hoisted_12 = { class: "ele-upload-tool-text" };
const _hoisted_13 = ["title"];
const _hoisted_14 = {
  key: 3,
  class: "ele-upload-handle"
};
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "ListItem" },
  __name: "list-item",
  props: {
    /** 数据 */
    item: {
      type: Object,
      required: true
    },
    /** 是否只读 */
    readonly: Boolean,
    /** 是否禁用 */
    disabled: Boolean,
    /** 是否可拖拽排序 */
    sortable: Boolean,
    /** 图片属性 */
    imageProps: Object,
    /** 进度条属性 */
    progressProps: Object,
    /** 预读图片文件 */
    imageObjectUrls: Array,
    /** 是否开启底部预览和修改的操作按钮 */
    tools: Boolean,
    /** 列表样式 */
    listType: String,
    /** 国际化 */
    locale: {
      type: Object,
      required: true
    }
  },
  emits: {
    itemClick: (_item) => true,
    remove: (_item) => true,
    edit: (_item) => true,
    preview: (_item) => true,
    retry: (_item) => true
  },
  setup(__props, { emit: __emit }) {
    const props = __props;
    const emit = __emit;
    const imageUrl = vue.computed(() => {
      if (props.item.thumbnail && props.item.thumbnail !== true) {
        return props.item.thumbnail;
      }
      if (props.item.url) {
        return props.item.url;
      }
      if (!props.item.file || !props.imageObjectUrls) {
        return;
      }
      return props.imageObjectUrls.find((d) => d.file === props.item.file)?.url;
    });
    const uploadProgress = vue.computed(() => {
      const progress = props.item.progress;
      if (!progress || progress < 0) {
        return 0;
      }
      return progress > 100 ? 100 : progress;
    });
    const handleItemClick = () => {
      emit("itemClick", props.item);
    };
    const handleRemove = () => {
      emit("remove", props.item);
    };
    const handleEdit = () => {
      emit("edit", props.item);
    };
    const handlePreview = () => {
      emit("preview", props.item);
    };
    const handleRetry = () => {
      emit("retry", props.item);
    };
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("div", {
        title: __props.item.name,
        class: "ele-upload-item",
        onClick: handleItemClick
      }, [
        vue.renderSlot(_ctx.$slots, "thumbnail", {
          item: __props.item,
          imageUrl: imageUrl.value
        }, () => [
          __props.listType === "file" || __props.item.thumbnail === false || !imageUrl.value ? (vue.openBlock(), vue.createElementBlock("div", _hoisted_2, [
            vue.createVNode(vue.unref(elementPlus.ElIcon), { class: "ele-upload-thumbnail-icon" }, {
              default: vue.withCtx(() => [
                vue.createVNode(vue.unref(index.FileOutlined))
              ]),
              _: 1
            }),
            vue.createElementVNode("div", _hoisted_3, vue.toDisplayString(__props.item.name || __props.item.url), 1)
          ])) : (vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElImage), vue.mergeProps({
            key: 1,
            fit: "contain",
            class: "ele-upload-image"
          }, __props.imageProps || {}, { src: imageUrl.value }), null, 16, ["src"]))
        ]),
        vue.renderSlot(_ctx.$slots, "itemExtra", { item: __props.item }),
        __props.item.status === "uploading" || __props.item.status === "exception" ? (vue.openBlock(), vue.createElementBlock("div", _hoisted_4, [
          vue.renderSlot(_ctx.$slots, "progress", { item: __props.item }, () => [
            vue.createElementVNode("div", _hoisted_5, vue.toDisplayString(__props.item.status == "exception" ? __props.locale.exception : __props.locale.uploading), 1),
            vue.createVNode(vue.unref(elementPlus.ElProgress), vue.mergeProps({
              showText: false,
              strokeWidth: __props.listType === "file" ? 2 : void 0,
              status: __props.item.status === "exception" ? "exception" : void 0,
              class: "ele-upload-progress-bar"
            }, __props.progressProps || {}, { percentage: uploadProgress.value }), null, 16, ["strokeWidth", "status", "percentage"]),
            !__props.disabled && __props.item.status === "exception" ? (vue.openBlock(), vue.createElementBlock("div", {
              key: 0,
              title: __props.locale.retry,
              class: "ele-upload-tool ele-upload-retry",
              onClick: vue.withModifiers(handleRetry, ["stop"])
            }, [
              vue.createVNode(vue.unref(elementPlus.ElIcon), { class: "ele-upload-tool-icon" }, {
                default: vue.withCtx(() => [
                  vue.createVNode(vue.unref(index.SyncOutlined))
                ]),
                _: 1
              }),
              vue.createElementVNode("div", _hoisted_7, vue.toDisplayString(__props.locale.retry), 1)
            ], 8, _hoisted_6)) : vue.createCommentVNode("", true)
          ])
        ])) : __props.tools && !__props.readonly && !__props.disabled && !__props.item.readonly ? (vue.openBlock(), vue.createElementBlock("div", _hoisted_8, [
          vue.createElementVNode("div", {
            title: __props.locale.preview,
            class: "ele-upload-tool",
            onClick: vue.withModifiers(handlePreview, ["stop"])
          }, [
            vue.createVNode(vue.unref(elementPlus.ElIcon), { class: "ele-upload-tool-icon" }, {
              default: vue.withCtx(() => [
                vue.createVNode(vue.unref(index.EyeOutlined))
              ]),
              _: 1
            }),
            vue.createElementVNode("div", _hoisted_10, vue.toDisplayString(__props.locale.preview), 1)
          ], 8, _hoisted_9),
          vue.createElementVNode("div", {
            title: __props.locale.edit,
            class: "ele-upload-tool",
            onClick: vue.withModifiers(handleEdit, ["stop"])
          }, [
            vue.createVNode(vue.unref(elementPlus.ElIcon), { class: "ele-upload-tool-icon" }, {
              default: vue.withCtx(() => [
                vue.createVNode(vue.unref(index.EditOutlined))
              ]),
              _: 1
            }),
            vue.createElementVNode("div", _hoisted_12, vue.toDisplayString(__props.locale.edit), 1)
          ], 8, _hoisted_11)
        ])) : vue.createCommentVNode("", true),
        !__props.readonly && !__props.disabled && !__props.item.readonly ? (vue.openBlock(), vue.createElementBlock("div", {
          key: 2,
          title: __props.locale.remove,
          class: "ele-upload-tool ele-upload-remove",
          onClick: vue.withModifiers(handleRemove, ["stop"])
        }, [
          vue.renderSlot(_ctx.$slots, "remove", { item: __props.item }, () => [
            vue.createVNode(vue.unref(elementPlus.ElIcon), { class: "ele-upload-tool-icon" }, {
              default: vue.withCtx(() => [
                vue.createVNode(vue.unref(index.CloseOutlined))
              ]),
              _: 1
            })
          ])
        ], 8, _hoisted_13)) : vue.createCommentVNode("", true),
        __props.sortable ? (vue.openBlock(), vue.createElementBlock("div", _hoisted_14)) : vue.createCommentVNode("", true)
      ], 8, _hoisted_1);
    };
  }
});
module.exports = _sfc_main;
