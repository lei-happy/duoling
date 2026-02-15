import type { EleDropdownPropsAndEmits } from '../ele-app/plus';
import type { DropdownItem } from '../ele-dropdown/types';

/**
 * 提供下拉菜单操作给子组件
 */
export interface DropdownProvider {
  openDropdown: (
    triggerEl: any,
    items?: DropdownItem[],
    props?: EleDropdownPropsAndEmits
  ) => void;
}
