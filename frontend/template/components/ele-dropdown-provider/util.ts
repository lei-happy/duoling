import type { InjectionKey } from 'vue';
import { ref, nextTick, provide, inject, shallowRef } from 'vue';
import type {
  EleDropdownInstance,
  EleDropdownPropsAndEmits
} from '../ele-app/plus';
import type { DropdownItem } from '../ele-dropdown/types';
import type { DropdownProvider } from './types';

/**
 * 下拉菜单注入键名
 */
export const DROPDOWN_KEY = Symbol(
  'dropdown'
) as InjectionKey<DropdownProvider>;

/**
 * 提供下拉菜单操作给子组件
 */
export function useDropdownProvider() {
  const dropdownRef = ref<EleDropdownInstance>(null);

  const dropdownVirtualRef = shallowRef<any>();

  const dropdownItems = shallowRef<DropdownItem[]>([]);

  const dropdownProps = shallowRef<EleDropdownPropsAndEmits>({});

  const openDropdown = (
    triggerEl: any,
    items?: DropdownItem[],
    props?: EleDropdownPropsAndEmits
  ) => {
    if (triggerEl == null || dropdownVirtualRef.value === triggerEl) {
      return;
    }
    dropdownRef.value && dropdownRef.value.handleClose();
    nextTick(() => {
      dropdownProps.value = props || {};
      dropdownItems.value = items || [];
      dropdownVirtualRef.value = triggerEl;
      if (dropdownItems.value.length) {
        nextTick(() => {
          dropdownRef.value && dropdownRef.value.handleOpen();
        });
      }
    });
  };

  provide(DROPDOWN_KEY, {
    openDropdown
  });

  return {
    dropdownRef,
    dropdownVirtualRef,
    dropdownItems,
    dropdownProps,
    openDropdown
  };
}

/**
 * 下拉菜单操作
 */
export function useDropdown() {
  return inject(DROPDOWN_KEY, {} as DropdownProvider);
}
