<!-- 角色选择 -->
<template>
  <EleTableSelect
    v-bind="{
      ...emitProps,
      ...omit($props, ['viewType', 'itemIcon', 'componentLang'])
    }"
    :popperTitle="popperTitle ?? lang.title"
    popperClass="ele-role-select-modal ele-modal-show-header-border ele-modal-show-footer-border"
    :popperProps="{ flexTable: 'auto', loading, ...(popperProps || {}) }"
    :selectStyle="isPickerMode ? 'none' : selectStyle"
    :validateEvent="!isPickerMode"
    :tableProps="{
      toolbar: false,
      showOverflowTooltip: true,
      rowClickChecked: multiple,
      columns: columns,
      datasource: tableData,
      ...(tableProps || {})
    }"
    :wrapperComponent="BodyWrapper"
    :wrapperComponentProps="{
      multiple: multiple,
      popperType: popperType,
      itemIcon: itemIcon,
      lang: lang,
      onSearch: handleSearch,
      onBodyMounted: handleBodyMounted
    }"
    ref="tableSelectRef"
  >
    <template v-for="name in Object.keys($slots)" #[name]="slotProps">
      <slot :name="name" v-bind="slotProps || {}"></slot>
    </template>
  </EleTableSelect>
</template>

<script lang="ts" setup>
  import type { PropType } from 'vue';
  import { ref, unref, computed } from 'vue';
  import { mapTree } from 'ele-admin-plus';
  import { omit } from 'ele-admin-plus/es/utils/common';
  import { useComponentEvents } from 'ele-admin-plus/es/utils/hook';
  import type { UserComponent } from 'ele-admin-plus/es/ele-app/types';
  import type { EleTableSelectInstance } from 'ele-admin-plus/es/ele-app/plus';
  import type { PopperType } from 'ele-admin-plus/es/ele-basic-select/types';
  import type { Columns } from 'ele-admin-plus/es/ele-pro-table/types';
  import {
    tableSelectProps,
    tableSelectEmits
  } from 'ele-admin-plus/es/ele-table-select/props';
  import { useComponentLang } from '@/utils/use-component-lang';
  import BodyWrapper from './components/body-wrapper.vue';
  import {
    roleIdField,
    roleNameField,
    roleTableColumns,
    listRoleApi
  } from './config';
  import type { RoleSelectLocale, Role, RoleParam } from './types';

  defineOptions({ name: 'RoleSelect' });

  const props = defineProps({
    ...tableSelectProps,
    popperWidth: { type: [Number, String], default: 980 },
    popperHeight: { type: [Number, String], default: 680 },
    valueKey: { type: String, default: roleIdField },
    labelKey: { type: String, default: roleNameField },
    popperType: { type: String as PropType<PopperType>, default: 'modal' },
    /** 显示模式 */
    viewType: String as PropType<'select' | 'picker'>,
    /** 已选列表项图标组件 */
    itemIcon: [String, Object, Function] as PropType<UserComponent>,
    /** 自定义文案 */
    componentLang: { type: Object as PropType<Partial<RoleSelectLocale>> }
  });

  const emit = defineEmits(tableSelectEmits);

  const { emitProps } = useComponentEvents(tableSelectEmits, emit);

  const { lang } = useComponentLang<RoleSelectLocale>(
    {
      zh_CN: {
        title: '角色选择',
        clear: '清空',
        selected: '已选择 ',
        selectedUnit: ' 个',
        labelRoleName: '角色名称',
        labelRoleCode: '角色标识',
        labelComments: '备注',
        labelCreateTime: '创建时间'
      },
      zh_TW: {
        title: '角色選擇',
        clear: '清空',
        selected: '已選擇 ',
        selectedUnit: ' 個',
        labelRoleName: '角色名稱',
        labelRoleCode: '角色標識',
        labelComments: '備註',
        labelCreateTime: '創建時間'
      },
      en: {
        title: 'Role select',
        clear: 'Clear',
        selected: 'Selected ',
        selectedUnit: ' items',
        labelRoleName: 'RoleName',
        labelRoleCode: 'RoleCode',
        labelComments: 'Comments',
        labelCreateTime: 'CreateTime'
      }
    },
    props
  );

  /** 表格下拉组件 */
  const tableSelectRef = ref<EleTableSelectInstance>(null);

  /** 表格数据请求状态 */
  const loading = ref(false);

  /** 表格数据 */
  const tableData = ref<Role[]>([]);

  /** 表格列配置 */
  const columns = computed<Columns>(() => {
    const cols: Columns = [];
    if (props.multiple) {
      cols.push({
        type: 'selection',
        columnKey: 'selection',
        width: 48,
        align: 'center',
        showOverflowTooltip: false,
        reserveSelection: true
      });
    }
    cols.push({
      type: 'index',
      columnKey: 'index',
      width: 48,
      align: 'center'
    });
    return [
      ...cols,
      ...mapTree(roleTableColumns, (c) => ({
        ...c,
        label: (c.label ? lang.value[c.label] : void 0) ?? c.label
      }))
    ];
  });

  /** 是否是选择器模式 */
  const isPickerMode = computed(() => {
    return props.viewType === 'picker';
  });

  /** 搜索 */
  const handleSearch = (where: RoleParam) => {
    if (!props.tableProps?.datasource) {
      reload(where);
      return;
    }
    const tableRef = unref(tableSelectRef.value?.tableRef);
    if (tableRef) {
      tableRef.reload({ page: 1, where });
    }
  };

  /** 查询表格数据 */
  const reload = (where?: RoleParam) => {
    if (props.tableProps?.datasource) {
      return;
    }
    loading.value = true;
    listRoleApi(where || {})
      .then((data) => {
        tableData.value = data;
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

  defineExpose({ tableSelectRef, reload });
</script>

<style lang="scss">
  @use 'ele-admin-plus/es/style/util.scss' as *;
  @use 'ele-admin-plus/es/ele-pro-table/style/css-var.scss' as *;

  /* 弹框 */
  .ele-role-select-modal {
    .ele-modal-body,
    .ele-drawer-body {
      padding: 0;
    }

    &.ele-table-select-popper .ele-popover-body {
      padding: 0;

      & > .ele-role-select-wrapper {
        height: 100%;
      }
    }
  }

  .ele-role-select-wrapper {
    flex: auto;
    display: flex;
  }

  /* 表格 */
  .ele-role-select-body {
    flex: 1;
    padding: 12px 16px 0 16px;
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
    overflow: hidden;

    @include flex-auto-pro-table();

    & > .ele-pro-table {
      padding-bottom: 10px;

      & > .ele-pro-table-footer > .ele-pagination {
        padding-top: 0;
      }

      .el-table__row {
        cursor: pointer;
      }
    }

    & > .ele-role-select-search {
      margin-bottom: 4px;
    }

    .el-form-item {
      margin-bottom: 8px;
    }
  }

  /* 选中列表 */
  .ele-role-select-right {
    width: 180px;
    flex-shrink: 0;
    box-sizing: border-box;
    border-left: 1px solid elVar('border-color', 'light');
    display: flex;
    flex-direction: column;
  }

  .ele-role-select-right-header {
    flex-shrink: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 10px;
    box-sizing: border-box;
  }

  .ele-role-select-right-title {
    flex: 1;
    width: 100%;
    overflow: hidden;
    padding-right: 8px;
    box-sizing: border-box;
    font-size: 13px;
  }

  .ele-role-select-right-clear {
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

  .ele-role-select-right-body {
    flex: 1 1 60px;
    padding: 0 10px;
    box-sizing: border-box;
    user-select: none;
    overflow: auto;

    &.is-sortable .ele-role-select-right-item {
      cursor: move;
    }
  }

  /* 选中列表项 */
  .ele-role-select-right-item {
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

  .ele-role-select-right-label {
    flex: 1;
    line-height: 16px;
    margin-left: 4px;
    word-break: break-all;
    overflow: hidden;
  }

  .ele-role-select-right-icon {
    flex-shrink: 0;
    width: 24px;
    height: 24px;
    font-size: 16px;
  }

  .ele-role-select-right-del {
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
    .ele-role-select-body > .ele-pro-table {
      padding-bottom: 8px;
    }

    .ele-role-select-wrapper {
      flex-direction: column;
    }

    .ele-role-select-right {
      width: auto;
      border-left: none;
      border-top: 1px solid elVar('border-color', 'light');
    }

    .ele-role-select-right-body {
      flex: none;
      display: flex;
      min-height: 42px;
      overflow: auto;
    }

    .ele-role-select-right-item {
      width: max-content;

      & + .ele-role-select-right-item {
        margin-left: 8px;
      }
    }

    .ele-role-select-right-header {
      padding-top: 8px;
      padding-bottom: 8px;
      flex-direction: row;

      & > .ele-role-select-right-title,
      & > .ele-role-select-right-clear {
        width: auto;
        margin: 0;
      }
    }
  }
</style>
