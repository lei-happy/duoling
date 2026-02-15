"use strict";
const vue = require("vue");
const elementPlus = require("element-plus");
const index = require("../../icons/index");
const _hoisted_1 = {
  key: 0,
  class: "ele-pro-form-builder-style-edit-list"
};
const _hoisted_2 = {
  key: 0,
  class: "ele-pro-form-builder-style-edit-item-body"
};
const _hoisted_3 = { class: "ele-pro-form-builder-style-edit-item-body" };
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "StyleEdit" },
  __name: "style-edit",
  props: {
    modelValue: {},
    isClass: { type: Boolean }
  },
  emits: ["update:modelValue"],
  setup(__props, { emit: __emit }) {
    let itemStartId = 0;
    const props = __props;
    const emit = __emit;
    const data = vue.ref([]);
    const updateModelValue = (value) => {
      if (props.modelValue !== value) {
        emit("update:modelValue", value);
      }
    };
    const updateDataValue = (dataList) => {
      let isChanged = false;
      const temp = [...data.value];
      if (props.isClass) {
        dataList.forEach((d) => {
          const index2 = temp.findIndex((t) => d.value === t.value);
          if (index2 === -1) {
            itemStartId++;
            temp.push({ ...d, id: itemStartId });
            isChanged = true;
          }
        });
        temp.forEach((t, i) => {
          if (t.value != null && t.value.trim().length) {
            if (!dataList.some((d) => d.value === t.value)) {
              temp.splice(i, 1);
              isChanged = true;
            }
          }
        });
      } else {
        dataList.forEach((d) => {
          const index2 = temp.findIndex(
            (t) => d.name === t.name && d.value === t.value
          );
          if (index2 === -1) {
            itemStartId++;
            temp.push({ ...d, id: itemStartId });
            isChanged = true;
          }
        });
        temp.forEach((t, i) => {
          if (t.name != null && t.name.trim().length && t.value != null && t.value.trim().length) {
            if (!dataList.some((d) => d.name === t.name && d.value === t.value)) {
              temp.splice(i, 1);
              isChanged = true;
            }
          }
        });
      }
      if (isChanged) {
        data.value = temp;
      }
    };
    const getDataValue = (dataList, isClass) => {
      if (isClass) {
        const result2 = [];
        dataList.forEach((d) => {
          if (d.value != null && d.value.trim().length) {
            result2.push(d.value);
          }
        });
        return result2.join(" ");
      }
      const result = {};
      dataList.forEach((d) => {
        if (d.name != null && d.name.trim().length && d.value != null && d.value.trim().length) {
          result[d.name] = d.value;
        }
      });
      return result;
    };
    const getValueData = (value, isClass) => {
      const result = [];
      if (isClass) {
        const classValue = value || "";
        classValue.split(" ").forEach((d) => {
          if (d != null && d.trim().length) {
            result.push({ value: d });
          }
        });
        return result;
      }
      const styleValue = value || {};
      Object.keys(styleValue).forEach((k) => {
        const v = styleValue[k];
        if (v != null && !(typeof v === "string" && !v.trim().length)) {
          result.push({ name: k, value: String(v) });
        }
      });
      return result;
    };
    const handleDataListChange = () => {
      updateModelValue(getDataValue(data.value, props.isClass));
    };
    const handleDelete = (index2) => {
      data.value.splice(index2, 1);
      handleDataListChange();
    };
    const handleAdd = () => {
      itemStartId++;
      data.value.push({ name: "", value: "", id: itemStartId });
      handleDataListChange();
    };
    vue.watch(
      () => props.modelValue,
      (value) => {
        updateDataValue(getValueData(value, props.isClass));
      },
      {
        deep: true,
        immediate: true
      }
    );
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock(vue.Fragment, null, [
        data.value && data.value.length ? (vue.openBlock(), vue.createElementBlock("div", _hoisted_1, [
          (vue.openBlock(true), vue.createElementBlock(vue.Fragment, null, vue.renderList(data.value, (item, index$1) => {
            return vue.openBlock(), vue.createElementBlock("div", {
              key: item.id,
              class: "ele-pro-form-builder-style-edit-item"
            }, [
              !__props.isClass ? (vue.openBlock(), vue.createElementBlock("div", _hoisted_2, [
                vue.createVNode(vue.unref(elementPlus.ElInput), {
                  size: "small",
                  modelValue: item.name,
                  "onUpdate:modelValue": ($event) => item.name = $event,
                  onChange: handleDataListChange
                }, null, 8, ["modelValue", "onUpdate:modelValue"])
              ])) : vue.createCommentVNode("", true),
              vue.createElementVNode("div", _hoisted_3, [
                vue.createVNode(vue.unref(elementPlus.ElInput), {
                  size: "small",
                  modelValue: item.value,
                  "onUpdate:modelValue": ($event) => item.value = $event,
                  onChange: handleDataListChange
                }, null, 8, ["modelValue", "onUpdate:modelValue"])
              ]),
              vue.createVNode(vue.unref(elementPlus.ElIcon), {
                class: "ele-pro-form-builder-style-edit-item-del-btn",
                title: "删除",
                onClick: ($event) => handleDelete(index$1)
              }, {
                default: vue.withCtx(() => [
                  vue.createVNode(vue.unref(index.DeleteOutlined))
                ]),
                _: 1
              }, 8, ["onClick"])
            ]);
          }), 128))
        ])) : vue.createCommentVNode("", true),
        vue.createVNode(vue.unref(elementPlus.ElButton), {
          size: "small",
          icon: vue.unref(index.PlusOutlined),
          class: "ele-pro-form-builder-props-fluid-btn is-small-icon",
          onClick: handleAdd
        }, {
          default: vue.withCtx(() => [
            vue.createTextVNode(vue.toDisplayString(__props.isClass ? "添加类名" : "添加样式"), 1)
          ]),
          _: 1
        }, 8, ["icon"])
      ], 64);
    };
  }
});
module.exports = _sfc_main;
