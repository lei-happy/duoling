import type { PropType, ExtractPropTypes } from 'vue';
import type { TreeComponentProps } from 'element-plus/es/components/tree/src/tree.type';
import { selectProps as elSelectProps } from 'element-plus/es/components/select/src/select';
import type { SelectTreeData, SelectTreeDataFunction } from './types';

export const elTreeProps = {
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
  defaultCheckedKeys: Array as PropType<
    TreeComponentProps['defaultCheckedKeys']
  >,
  defaultExpandedKeys: Array as PropType<
    TreeComponentProps['defaultExpandedKeys']
  >,
  currentNodeKey: [String, Number] as PropType<string | number>,
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
    type: Object as PropType<TreeComponentProps['props']>,
    default: () => ({
      children: 'children',
      label: 'label',
      disabled: 'disabled'
    })
  },
  lazy: {
    type: Boolean,
    default: false
  },
  highlightCurrent: Boolean,
  load: Function as PropType<TreeComponentProps['load']>,
  filterNodeMethod: Function as PropType<
    TreeComponentProps['filterNodeMethod']
  >,
  accordion: Boolean,
  indent: {
    type: Number,
    default: 18
  },
  icon: {
    type: [String, Object, Function]
  }
};

/**
 * 属性
 */
export const selectTreeProps = {
  ...elSelectProps,
  ...elTreeProps,
  /** 数据 */
  data: [Array, Function] as PropType<SelectTreeData | SelectTreeDataFunction>
};

export type SelectTreeProps = ExtractPropTypes<typeof selectTreeProps>;

/**
 * 事件
 */
export const selectTreeEmits = {
  'update:modelValue': (_value: any) => true
};
