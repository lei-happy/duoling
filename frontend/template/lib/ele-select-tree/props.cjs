"use strict";
Object.defineProperty(exports, Symbol.toStringTag, { value: "Module" });
const select = require("element-plus/es/components/select/src/select");
const elTreeProps = {
  data: {
    type: Array,
    default: () => []
  },
  emptyText: {
    type: String
  },
  renderAfterExpand: {
    type: Boolean,
    default: true
  },
  nodeKey: String,
  checkStrictly: Boolean,
  defaultExpandAll: Boolean,
  expandOnClickNode: {
    type: Boolean,
    default: true
  },
  checkOnClickNode: Boolean,
  checkDescendants: {
    type: Boolean,
    default: false
  },
  autoExpandParent: {
    type: Boolean,
    default: true
  },
  defaultCheckedKeys: Array,
  defaultExpandedKeys: Array,
  currentNodeKey: [String, Number],
  renderContent: Function,
  showCheckbox: {
    type: Boolean,
    default: false
  },
  draggable: {
    type: Boolean,
    default: false
  },
  allowDrag: Function,
  allowDrop: Function,
  props: {
    type: Object,
    default: () => ({
      children: "children",
      label: "label",
      disabled: "disabled"
    })
  },
  lazy: {
    type: Boolean,
    default: false
  },
  highlightCurrent: Boolean,
  load: Function,
  filterNodeMethod: Function,
  accordion: Boolean,
  indent: {
    type: Number,
    default: 18
  },
  icon: {
    type: [String, Object, Function]
  }
};
const selectTreeProps = {
  ...select.selectProps,
  ...elTreeProps,
  /** 数据 */
  data: [Array, Function]
};
const selectTreeEmits = {
  "update:modelValue": (_value) => true
};
exports.elTreeProps = elTreeProps;
exports.selectTreeEmits = selectTreeEmits;
exports.selectTreeProps = selectTreeProps;
