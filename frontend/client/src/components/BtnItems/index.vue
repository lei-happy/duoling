<!-- 操作按钮 -->
<template>
  <EleButtons v-bind="{ ...emitProps, ...$props }" :items="data">
    <template v-for="name in Object.keys($slots)" #[name]="slotProps">
      <slot :name="name" v-bind="slotProps || {}"></slot>
    </template>
  </EleButtons>
</template>

<script lang="ts" setup>
  import { computed } from 'vue';
  import { mapTree } from 'ele-admin-plus';
  import {
    buttonsProps,
    buttonsEmits
  } from 'ele-admin-plus/es/ele-buttons/props';
  import type {
    ButtonItem,
    ButtonDropdownItem
  } from 'ele-admin-plus/es/ele-buttons/types';
  import { useComponentEvents } from 'ele-admin-plus/es/utils/hook';
  import { usePermission } from '@/utils/use-permission';

  defineOptions({ name: 'BtnItems' });

  const props = defineProps(buttonsProps);

  const emit = defineEmits(buttonsEmits);

  const { emitProps } = useComponentEvents(buttonsEmits, emit);

  const { hasPermission, hasAnyPermission, hasRole, hasAnyRole } =
    usePermission();

  /** 判断是否权限 */
  const isPermission = (item: ButtonItem | ButtonDropdownItem) => {
    let flag = false;
    if (
      !item.permission &&
      !item.anyPermission &&
      !item.role &&
      !item.anyRole
    ) {
      flag = true;
    } else {
      if (item.permission && hasPermission(item.permission)) {
        flag = true;
      } else if (item.anyPermission && hasAnyPermission(item.anyPermission)) {
        flag = true;
      } else if (item.role && hasRole(item.role)) {
        flag = true;
      } else if (item.anyRole && hasAnyRole(item.anyRole)) {
        flag = true;
      }
    }
    if (flag && item.vIf && !item.vIf()) {
      flag = false;
    }
    return flag;
  };

  /** 筛选有权限的数据 */
  const data = computed<ButtonItem[]>(() => {
    const temp: ButtonItem[] = [];
    if (!props.items) {
      return temp;
    }
    props.items.forEach((item) => {
      if (isPermission(item)) {
        if (item.dropdownItems && item.dropdownItems.length) {
          const dItems = mapTree(
            item.dropdownItems,
            (d) => {
              if (isPermission(d)) {
                return {
                  ...d,
                  permission: void 0,
                  anyPermission: void 0,
                  role: void 0,
                  anyRole: void 0,
                  vIf: void 0
                };
              }
            },
            'children',
            'children',
            (d) => {
              if (d.children == null || d.children?.length) {
                return d;
              }
            }
          );
          if (dItems.length) {
            temp.push({ ...item, dropdownItems: dItems });
          }
        } else {
          temp.push({ ...item });
        }
      }
    });
    return temp;
  });
</script>
