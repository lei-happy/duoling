import type { PropType, ExtractPropTypes, EmitsToProps } from 'vue';
import { dropdownProps as elDropdownProps } from 'element-plus';
import type { StyleValue } from '../ele-app/types';
import type {
  ElIconProps,
  ElButtonProps,
  ElDropdownInstance
} from '../ele-app/el';
import { omit } from '../utils/common';
import { popoverProps, popoverEmits } from '../ele-popover/props';
import type ProDropdown from './components/pro-dropdown.vue';
import type { DropdownItem } from './types';
const normalizePopoverProps = omit(popoverProps, [
  'title',
  'effect',
  'content',
  'width',
  'placement',
  'disabled',
  'popperOptions',
  'popperClass',
  'showAfter',
  'hideAfter',
  'autoClose',
  'tabindex',
  'teleported',
  'bodyClass',
  'bodyStyle',
  'titleStyle',
  'contentStyle'
]);
const normalizeDropdownProps = omit(elDropdownProps, [
  'onCommand',
  'onClick',
  'onVisibleChange',
  'onVisible-change'
] as unknown as Array<'trigger' | 'size'>);

/**
 * 属性
 */
export const dropdownProps = {
  ...normalizePopoverProps,
  size: String as PropType<ElButtonProps['size']>,
  ...normalizeDropdownProps,
  /** 下拉框渐变动画 */
  transition: {
    type: String,
    default: 'el-zoom-in-top'
  },
  /** 下拉菜单数据 */
  items: Array as PropType<DropdownItem[]>,
  /** 选中的菜单 */
  modelValue: [String, Number, Object] as PropType<DropdownItem['command']>,
  /** 自定义下拉菜单样式 */
  menuStyle: Object as PropType<StyleValue>,
  /** 自定义图标属性 */
  iconProps: Object as PropType<ElIconProps>,
  /** 图标尺寸 */
  iconSize: String as PropType<'small' | 'default'>,
  /** 下拉菜单使用的组件类型 */
  componentType: String as PropType<'pro'>,
  /** 是否阻止下拉菜单的右键事件 */
  preventContextmenu: Boolean,
  /** 内容按钮属性 */
  splitButtonProps: Object as PropType<ElButtonProps>,
  /** 箭头按钮属性 */
  caretButtonProps: Object as PropType<ElButtonProps>,
  /** 是否触发表单验证 */
  validateEvent: {
    type: Boolean,
    default: true
  }
};

export type DropdownProps = ExtractPropTypes<typeof dropdownProps>;

/**
 * 事件
 */
export const dropdownEmits = {
  ...popoverEmits,
  /** 内容按钮点击事件 */
  click: (_e: MouseEvent) => true,
  /** 菜单项点击事件 */
  command: (_command: DropdownItem['command']) => true,
  /** 下拉框显示状态改变事件 */
  visibleChange: (_visible: boolean) => true,
  /** 更新选中值 */
  'update:modelValue': (_value: DropdownItem['command']) => true,
  /** 选中改变的事件 */
  change: (_active: DropdownItem['command']) => true
};

export type DropdownEmitsProps = EmitsToProps<typeof dropdownEmits>;

export type DropdownPropsAndEmits = DropdownProps & DropdownEmitsProps;

/**
 * 属性名
 */
export type ElDropdownPropKeys = Array<keyof typeof normalizeDropdownProps>;

export const elDropdownPropKeys = Object.keys(
  normalizeDropdownProps
) as ElDropdownPropKeys;

/**
 * 下拉菜单组件实例
 */
export type ProDropdownInstance = InstanceType<typeof ProDropdown> | null;

export type DropdownInstance = ElDropdownInstance | ProDropdownInstance;
