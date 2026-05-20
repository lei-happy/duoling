import type { UserComponent } from '../ele-app/types';
import type { ElLinkProps, ElButtonProps } from '../ele-app/el';
import type {
  EleDropdownPropsAndEmits,
  ElePopconfirmPropsAndEmits
} from '../ele-app/plus';
import type { DropdownItem } from '../ele-dropdown/types';

/**
 * 组件类型
 */
export type ButtonItemType = 'button' | 'link';

/**
 * 预设类型
 */
export type ButtonItemPreset =
  | 'search'
  | 'reset'
  | 'searchExpand'
  | 'searchFold'
  | 'add'
  | 'delBatch'
  | 'edit'
  | 'del'
  | 'import'
  | 'export'
  | 'upload'
  | 'download'
  | 'expand'
  | 'fold'
  | 'detail'
  | 'more'
  | 'save'
  | 'cancel'
  | 'confirm';

/**
 * 权限控制字段
 */
export interface ButtonItemPermission {
  /** 有某些权限才展示 */
  permission?: string | string[];
  /** 有任意权限才展示 */
  anyPermission?: string | string[];
  /** 有某些角色才展示 */
  role?: string | string[];
  /** 有任意角色才展示 */
  anyRole?: string | string[];
  /** 显示条件 */
  vIf?: () => boolean;
}

/**
 * 下拉菜单项
 */
export interface ButtonDropdownItem
  extends Omit<DropdownItem, 'children'>, ButtonItemPermission {
  /** 预设类型 */
  preset?: ButtonItemPreset;
  /** 子级 */
  children?: ButtonDropdownItem[];
}

/**
 * 按钮类型项
 */
export interface ButtonItemBase<
  T extends ButtonItemType
> extends ButtonItemPermission {
  /** 文本 */
  title?: string;
  /** 图标 */
  icon?: UserComponent;
  /** 组件类型 */
  type?: T;
  /** 组件属性 */
  props?: T extends 'link' ? ElLinkProps : ElButtonProps;
  /** 预设类型 */
  preset?: ButtonItemPreset;
  /** 点击事件 */
  onClick?: (e: MouseEvent) => void;
  /** 下拉菜单项 */
  dropdownItems?: ButtonDropdownItem[];
  /** 下拉菜单属性 */
  dropdownProps?: EleDropdownPropsAndEmits;
  /** 气泡确认框属性 */
  popconfirmProps?: ElePopconfirmPropsAndEmits;
  /** command */
  command?: any;
  /** key */
  key?: string;
}

/**
 * 按钮项
 */
export type ButtonItem = ButtonItemBase<'button'> | ButtonItemBase<'link'>;

/**
 * 国际化
 */
export interface ButtonsLocale {
  search: string;
  reset: string;
  searchExpand: string;
  searchFold: string;
  add: string;
  delBatch: string;
  edit: string;
  del: string;
  import: string;
  export: string;
  upload: string;
  download: string;
  expand: string;
  fold: string;
  detail: string;
  more: string;
  save: string;
  cancel: string;
  confirm: string;
}
