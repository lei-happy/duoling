import { InjectionKey } from 'vue';
import { EleDropdownInstance, EleDropdownPropsAndEmits } from '../ele-app/plus';
import { DropdownItem } from '../ele-dropdown/types';
import { DropdownProvider } from './types';

/**
 * 下拉菜单注入键名
 */
export declare const DROPDOWN_KEY: InjectionKey<DropdownProvider>;
/**
 * 提供下拉菜单操作给子组件
 */
export declare function useDropdownProvider(): {
    dropdownRef: import('vue').Ref<EleDropdownInstance, EleDropdownInstance>;
    dropdownVirtualRef: import('vue').ShallowRef<any, any>;
    dropdownItems: import('vue').ShallowRef<DropdownItem[], DropdownItem[]>;
    dropdownProps: import('vue').ShallowRef<EleDropdownPropsAndEmits, EleDropdownPropsAndEmits>;
    openDropdown: (triggerEl: any, items?: DropdownItem[], props?: EleDropdownPropsAndEmits) => void;
};
/**
 * 下拉菜单操作
 */
export declare function useDropdown(): DropdownProvider;
