<!-- 部门选择 -->
<template>
  <EleTreeSelect
    v-bind="{
      ...emitProps,
      ...omit($props, ['viewType', 'listApi', 'itemIcon', 'componentLang'])
    }"
    :popperTitle="popperTitle ?? lang.title"
    popperClass="ele-department-select-modal ele-modal-show-header-border ele-modal-show-footer-border"
    :popperProps="{ flexTable: true, loading, ...(popperProps || {}) }"
    :selectStyle="isPickerMode ? 'none' : selectStyle"
    :validateEvent="!isPickerMode"
    :treeProps="{
      data: treeData,
      defaultExpandedKeys: treeExpandedKeys,
      height: treeHeight,
      ...(treeProps || {}),
      props: {
        value: departmentIdField,
        label: departmentNameField,
        ...(treeProps?.props || {})
      }
    }"
    :wrapperComponent="BodyWrapper"
    :wrapperComponentProps="{
      multiple: multiple,
      popperType: popperType,
      itemIcon: itemIcon,
      lang: lang,
      onSearch: handleSearch,
      'onUpdate:treeHeight': handleUpdateTreeHeight,
      onBodyMounted: handleBodyMounted
    }"
    ref="treeSelectRef"
  >
    <template
      v-for="name in Object.keys($slots).filter((k) => k !== 'default')"
      #[name]="slotProps"
    >
      <slot :name="name" v-bind="slotProps || {}"></slot>
    </template>
    <template #default="{ node }">
      <el-icon style="margin-right: 4px; vertical-align: -2px">
        <component v-if="itemIcon" :is="itemIcon" />
        <CityOutlined v-else />
      </el-icon>
      <span>{{ node.label }}</span>
    </template>
  </EleTreeSelect>
</template>

<script lang="ts" setup>
  import type { PropType } from 'vue';
  import { ref, unref, computed } from 'vue';
  import { CityOutlined } from 'ele-admin-plus/es/icons';
  import { omit, eachTree, getValue } from 'ele-admin-plus/es/utils/common';
  import { useComponentEvents } from 'ele-admin-plus/es/utils/hook';
  import type { UserComponent } from 'ele-admin-plus/es/ele-app/types';
  import type { EleTreeSelectInstance } from 'ele-admin-plus/es/ele-app/plus';
  import type { PopperType } from 'ele-admin-plus/es/ele-basic-select/types';
  import {
    treeSelectProps,
    treeSelectEmits
  } from 'ele-admin-plus/es/ele-tree-select/props';
  import { useComponentLang } from '@/utils/use-component-lang';
  import BodyWrapper from './components/body-wrapper.vue';
  import {
    departmentIdField,
    departmentNameField,
    listDepartmentApi
  } from './config';
  import type { DepartmentSelectLocale, Organization } from './types';

  defineOptions({ name: 'DepartmentSelect' });

  const props = defineProps({
    ...treeSelectProps,
    popperWidth: { type: [Number, String], default: 720 },
    popperHeight: { type: [Number, String], default: 620 },
    popperType: { type: String as PropType<PopperType>, default: 'modal' },
    /** 显示模式 */
    viewType: String as PropType<'select' | 'picker'>,
    /** 数据源 */
    listApi: Function as PropType<() => Promise<Organization[]>>,
    /** 已选列表项图标组件 */
    itemIcon: [String, Object, Function] as PropType<UserComponent>,
    /** 自定义文案 */
    componentLang: { type: Object as PropType<Partial<DepartmentSelectLocale>> }
  });

  const emit = defineEmits(treeSelectEmits);

  const { emitProps } = useComponentEvents(treeSelectEmits, emit);

  const { lang } = useComponentLang<DepartmentSelectLocale>(
    {
      zh_CN: {
        title: '部门选择',
        clear: '清空',
        selected: '已选择 ',
        selectedUnit: ' 个',
        searchPlaceholder: '输入关键字搜索'
      },
      zh_TW: {
        title: '部門選擇',
        clear: '清空',
        selected: '已選擇 ',
        selectedUnit: ' 個',
        searchPlaceholder: '輸入關鍵字搜尋'
      },
      en: {
        title: 'Department select',
        clear: 'Clear',
        selected: 'Selected ',
        selectedUnit: ' items',
        searchPlaceholder: 'Search by keyword'
      }
    },
    props
  );

  /** 树下拉组件 */
  const treeSelectRef = ref<EleTreeSelectInstance>(null);

  /** 树数据请求状态 */
  const loading = ref(false);

  /** 树数据 */
  const treeData = ref<Organization[]>([]);

  /** 树高度 */
  const treeHeight = ref<number>();

  /** 树组件值字段名 */
  const treeValueField = computed(() => {
    return props.treeProps?.props?.value ?? departmentIdField;
  });

  /** 树展开节点 */
  const treeExpandedKeys = computed(() => {
    const keys: Array<string | number> = [];
    eachTree(treeData.value, (item) => {
      keys.push(getValue<any, Organization>(item, treeValueField.value));
    });
    return keys;
  });

  /** 是否是选择器模式 */
  const isPickerMode = computed(() => {
    return props.viewType === 'picker';
  });

  /** 搜索 */
  const handleSearch = (keyword: string) => {
    const treeRef = unref(treeSelectRef.value?.treeRef);
    if (treeRef) {
      treeRef.filter(keyword);
    }
  };

  /** 更新树组件高度 */
  const handleUpdateTreeHeight = (height: number) => {
    treeHeight.value = height;
  };

  /** 查询树数据 */
  const reload = () => {
    loading.value = true;
    (props.listApi || listDepartmentApi)()
      .then((data) => {
        treeData.value = data;
        loading.value = false;
      })
      .catch((e) => {
        loading.value = false;
        console.error(e);
      });
  };

  /** 内容挂载事件 */
  const handleBodyMounted = () => {
    if (
      isPickerMode.value ||
      ((props.popperProps as any)?.destroyOnClose ?? !props.persistent)
    ) {
      reload();
    }
  };

  /** 弹窗模式首次查询 */
  if (
    !isPickerMode.value &&
    !((props.popperProps as any)?.destroyOnClose ?? !props.persistent)
  ) {
    reload();
  }

  defineExpose({ treeSelectRef, reload });
</script>

<style lang="scss">
  @use 'ele-admin-plus/es/style/util.scss' as *;
  @use 'ele-admin-plus/es/ele-pro-table/style/css-var.scss' as *;

  /* 弹框 */
  .ele-department-select-modal {
    .ele-modal-body,
    .ele-drawer-body {
      padding: 0;
    }

    &.ele-tree-select-popper .ele-popover-body {
      padding: 0;

      & > .ele-department-select-wrapper {
        height: 100%;
      }
    }
  }

  .ele-department-select-wrapper {
    flex: 1;
    display: flex;
    overflow: hidden;
  }

  /* 树 */
  .ele-department-select-body {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;

    & > .ele-department-select-search {
      flex-shrink: 0;
      padding: 12px 16px;
      box-sizing: border-box;
    }

    & > .ele-department-tree-wrapper {
      flex: 1;
      overflow: hidden;
      box-sizing: border-box;

      & > .el-tree > .el-vl__wrapper {
        padding: 0 calc(#{eleVar('tree', 'item-radius')} * 4);
        #{eleVarName('tree', 'expand-margin')}: 0 2px 0
          calc(10px - #{eleVar('tree', 'item-radius')} * 2);

        & > .el-tree-virtual-list {
          will-change: scroll-position !important;
        }
      }
    }
  }

  /* 选中列表 */
  .ele-department-select-right {
    width: 180px;
    flex-shrink: 0;
    box-sizing: border-box;
    border-left: 1px solid elVar('border-color', 'light');
    display: flex;
    flex-direction: column;
  }

  .ele-department-select-right-header {
    flex-shrink: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 10px;
    box-sizing: border-box;
  }

  .ele-department-select-right-title {
    flex: 1;
    width: 100%;
    overflow: hidden;
    padding-right: 8px;
    box-sizing: border-box;
    font-size: 13px;
  }

  .ele-department-select-right-clear {
    width: 100%;
    padding: 0 6px;
    margin-top: 6px;
    border-radius: elVar('border-radius', 'base');
    border: 1px dashed elVar('color-danger');
    box-sizing: border-box;
    font-size: 12px;
    line-height: 20px;
    user-select: none;

    &:hover {
      border-color: elVar('color-danger', 'light-5');
    }
  }

  .ele-department-select-right-body {
    flex: 1;
    padding: 0 10px;
    box-sizing: border-box;
    user-select: none;
    overflow: auto;

    &.is-sortable .ele-department-select-right-item {
      cursor: move;
    }
  }

  /* 选中列表项 */
  .ele-department-select-right-item {
    flex-shrink: 0;
    display: flex;
    align-items: center;
    padding: 4px;
    margin-bottom: 8px;
    border: 1px solid elVar('border-color');
    border-radius: elVar('border-radius', 'base');
    transition: border-color 0.2s;
    box-sizing: border-box;

    &:hover {
      border-color: elVar('color-primary', 'light-3');
    }

    &.sortable-chosen {
      background: elVar('bg-color');
    }

    &.sortable-ghost {
      opacity: 0;
    }

    &.sortable-fallback {
      opacity: 1 !important;
    }
  }

  .ele-department-select-right-label {
    flex: 1;
    line-height: 16px;
    margin-left: 4px;
    word-break: break-all;
    overflow: hidden;
  }

  .ele-department-select-right-icon {
    flex-shrink: 0;
    width: 24px;
    height: 24px;
    font-size: 16px;
  }

  .ele-department-select-right-del {
    flex-shrink: 0;
    width: 18px;
    height: 18px;
    font-size: 12px;
    color: elVar('color-danger');
    border-radius: elVar('border-radius', 'small');
    transition: all 0.2s;
    cursor: pointer;

    &:hover {
      background: elVar('fill-color', 'light');
    }
  }

  /* 移动端适配 */
  @media screen and (max-width: 767.99px) {
    .ele-department-select-body > .ele-pro-table {
      padding-bottom: 8px;
    }

    .ele-department-select-wrapper {
      flex-direction: column;
    }

    .ele-department-select-right {
      width: auto;
      border-left: none;
      border-top: 1px solid elVar('border-color', 'light');
    }

    .ele-department-select-right-body {
      flex: none;
      display: flex;
      min-height: 42px;
      overflow: auto;
    }

    .ele-department-select-right-item {
      width: max-content;

      & + .ele-department-select-right-item {
        margin-left: 8px;
      }
    }

    .ele-department-select-right-header {
      padding-top: 8px;
      padding-bottom: 8px;
      flex-direction: row;

      & > .ele-department-select-right-title,
      & > .ele-department-select-right-clear {
        width: auto;
        margin: 0;
      }
    }
  }
</style>
