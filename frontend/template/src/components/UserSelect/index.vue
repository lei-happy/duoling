<!-- 用户选择 -->
<template>
  <EleTableSelect
    v-bind="{
      ...emitProps,
      ...omit($props, ['viewType', 'itemIcon', 'treeListApi', 'componentLang'])
    }"
    :popperTitle="popperTitle ?? lang.title"
    popperClass="ele-user-select-modal ele-modal-show-header-border ele-modal-show-footer-border"
    :popperProps="{ flexTable: 'auto', ...(popperProps || {}) }"
    :selectStyle="isPickerMode ? 'none' : selectStyle"
    selectClass="ele-user-select"
    :validateEvent="!isPickerMode"
    :tableProps="{
      toolbar: false,
      showOverflowTooltip: true,
      rowClickChecked: multiple,
      columns: columns,
      datasource: datasource,
      ...(tableProps || {})
    }"
    :wrapperComponent="BodyWrapper"
    :wrapperComponentProps="{
      multiple: multiple,
      popperType: popperType,
      itemIcon: itemIcon,
      treeListApi: treeListApi,
      lang: lang,
      onSearch: handleSearch
    }"
    ref="tableSelectRef"
  >
    <template v-for="name in Object.keys($slots)" #[name]="slotProps">
      <slot :name="name" v-bind="slotProps || {}"></slot>
    </template>
    <!-- 头像模式 -->
    <template
      v-if="viewType === 'avatar' && !$slots.select"
      #select="{ selected, openPopper, removeItem, clear }"
    >
      <div
        v-for="(item, index) in selected"
        :key="`${index}-${item.value}`"
        class="ele-user-select-item"
        :class="{ 'is-icon': !item.data?.[avatarField] }"
      >
        <div
          class="ele-user-select-item-avatar"
          :class="{ 'is-icon': !item.data?.[avatarField] }"
        >
          <img
            v-if="item.data?.[avatarField]"
            :src="item.data?.[avatarField]"
          />
          <span v-else>
            {{
              item.label && item.label.length > 2
                ? item.label.substring(item.label.length - 2)
                : item.label
            }}
          </span>
          <ElIcon
            class="ele-user-select-item-del"
            @click="multiple ? removeItem(item) : clear()"
          >
            <CloseOutlined />
          </ElIcon>
        </div>
        <div class="ele-user-select-item-name">{{ item.label }}</div>
      </div>
      <div
        v-if="!(!multiple && selected.length)"
        class="ele-user-select-item is-icon-add"
        @click="openPopper()"
      >
        <ElIcon class="ele-user-select-item-avatar">
          <PlusOutlined style="stroke-width: 3" />
        </ElIcon>
      </div>
    </template>
    <!-- 表格状态列插槽 -->
    <template #status="{ row }">
      <el-tag
        v-if="row.status === 0"
        size="small"
        type="primary"
        :disable-transitions="true"
      >
        {{ lang.statusNormal }}
      </el-tag>
      <el-tag
        v-else-if="row.status === 1"
        size="small"
        type="danger"
        :disable-transitions="true"
      >
        {{ lang.statusDisabled }}
      </el-tag>
    </template>
  </EleTableSelect>
</template>

<script lang="ts" setup>
  import type { PropType } from 'vue';
  import { ref, unref, computed } from 'vue';
  import { CloseOutlined, PlusOutlined } from 'ele-admin-plus/es/icons';
  import { mapTree } from 'ele-admin-plus';
  import { omit } from 'ele-admin-plus/es/utils/common';
  import { useComponentEvents } from 'ele-admin-plus/es/utils/hook';
  import type { UserComponent } from 'ele-admin-plus/es/ele-app/types';
  import type { EleTableSelectInstance } from 'ele-admin-plus/es/ele-app/plus';
  import type { PopperType } from 'ele-admin-plus/es/ele-basic-select/types';
  import type {
    Columns,
    Datasource
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import {
    tableSelectProps,
    tableSelectEmits
  } from 'ele-admin-plus/es/ele-table-select/props';
  import { useComponentLang } from '@/utils/use-component-lang';
  import BodyWrapper from './components/body-wrapper.vue';
  import {
    userIdField,
    userNameField,
    avatarField,
    pageUserApi,
    userTableColumns
  } from './config';
  import type { UserSelectLocale, UserParam, Organization } from './types';

  defineOptions({ name: 'UserSelect' });

  const props = defineProps({
    ...tableSelectProps,
    popperWidth: { type: [Number, String], default: 1140 },
    popperHeight: { type: [Number, String], default: 800 },
    valueKey: { type: String, default: userIdField },
    labelKey: { type: String, default: userNameField },
    popperType: { type: String as PropType<PopperType>, default: 'modal' },
    /** 显示模式 */
    viewType: String as PropType<'select' | 'avatar' | 'picker'>,
    /** 已选列表项图标组件 */
    itemIcon: [String, Object, Function] as PropType<UserComponent>,
    /** 树数据源 */
    treeListApi: Function as PropType<() => Promise<Organization[]>>,
    /** 自定义文案 */
    componentLang: { type: Object as PropType<Partial<UserSelectLocale>> }
  });

  const emit = defineEmits(tableSelectEmits);

  const { emitProps } = useComponentEvents(tableSelectEmits, emit);

  const { lang } = useComponentLang<UserSelectLocale>(
    {
      zh_CN: {
        title: '用户选择',
        searchPlaceholder: '输入部门名称搜索',
        clear: '清空',
        selected: '已选择 ',
        selectedUnit: ' 个',
        labelUsername: '用户账号',
        labelNickname: '用户昵称',
        labelPhone: '手机号码',
        labelOrganizationName: '部门',
        labelStatus: '状态',
        statusNormal: '正常',
        statusDisabled: '冻结'
      },
      zh_TW: {
        title: '用戶選擇',
        searchPlaceholder: '輸入部門名稱搜索',
        clear: '清空',
        selected: '已選擇 ',
        selectedUnit: ' 個',
        labelUsername: '用戶賬號',
        labelNickname: '用戶昵稱',
        labelPhone: '手機號碼',
        labelOrganizationName: '部門',
        labelStatus: '狀態',
        statusNormal: '正常',
        statusDisabled: '凍結'
      },
      en: {
        title: 'User select',
        searchPlaceholder: 'Search by department',
        clear: 'Clear',
        selected: 'Selected ',
        selectedUnit: ' items',
        labelUsername: 'Account',
        labelNickname: 'Username',
        labelPhone: 'Phone',
        labelOrganizationName: 'Department',
        labelStatus: 'Status',
        statusNormal: 'Normal',
        statusDisabled: 'Disabled'
      }
    },
    props
  );

  /** 表格下拉组件 */
  const tableSelectRef = ref<EleTableSelectInstance>(null);

  /** 是否是选择器模式 */
  const isPickerMode = computed(() => {
    return props.viewType === 'picker';
  });

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
      ...mapTree(userTableColumns, (c) => ({
        ...c,
        label: (c.label ? lang.value[c.label] : void 0) ?? c.label
      }))
    ];
  });

  /** 表格数据源 */
  const datasource: Datasource = ({ pages, where }) => {
    return pageUserApi({ ...where, ...pages });
  };

  /** 搜索 */
  const handleSearch = (where?: UserParam) => {
    const tableRef = unref(tableSelectRef.value?.tableRef);
    if (tableRef) {
      tableRef.reload({ page: 1, where });
    }
  };

  defineExpose({ tableSelectRef });
</script>

<style lang="scss">
  @use 'ele-admin-plus/es/style/util.scss' as *;
  @use 'ele-admin-plus/es/ele-pro-table/style/css-var.scss' as *;

  /* 头像列表 */
  .ele-user-select {
    display: flex;
    align-items: flex-start;
    gap: 12px;

    .ele-user-select-item {
      flex-shrink: 0;
      display: flex;
      flex-direction: column;
      align-items: center;
    }

    .ele-user-select-item-avatar {
      width: 42px;
      height: 42px;
      line-height: 42px;
      border-radius: 50%;
      box-sizing: border-box;
      transition: all 0.2s;
      color: #fff;
      font-size: 14px;
      text-align: center;
      position: relative;

      & > img {
        width: 100%;
        height: 100%;
        display: block;
        border-radius: inherit;
      }

      &.is-icon {
        background: elVar('color-primary');
      }
    }

    .ele-user-select-item-name {
      margin-top: 6px;
      max-width: 68px;
      font-size: 13px;
      line-height: 1.2;
      text-align: center;
      word-break: break-all;
    }

    .ele-user-select-item.is-icon-add > .ele-user-select-item-avatar {
      font-size: 19px;
      color: elVar('text-color', 'secondary');
      border: 1px dashed elVar('border-color');
      background: elVar('fill-color', 'lighter');
      cursor: pointer;

      &:hover {
        color: elVar('color-primary');
        border-color: elVar('color-primary');
      }
    }

    .ele-user-select-item-del {
      width: 16px;
      height: 16px;
      color: #fff;
      font-size: 12px;
      border-radius: 50%;
      background: elVar('color-danger');
      border: 1px solid elVar('color-white');
      box-sizing: border-box;
      transition: all 0.2s;
      position: absolute;
      top: -2px;
      right: -6px;
      cursor: pointer;

      &:hover {
        background: elVar('color-danger', 'dark-2');
      }
    }
  }

  /* 弹框 */
  .ele-user-select-modal {
    .ele-modal-body,
    .ele-drawer-body {
      padding: 0;
    }

    &.ele-table-select-popper .ele-popover-body {
      padding: 0;

      & > .ele-user-select-wrapper {
        height: 100%;
      }
    }
  }

  /* 折叠面板 */
  .ele-user-select-wrapper.ele-split-panel {
    & > .ele-split-panel-body {
      flex-direction: row;
    }

    & > .ele-split-panel-wrap > .ele-split-panel-side {
      border-width: 0 1px 0 0;
    }
  }

  /* 树 */
  .ele-user-select-tree-wrapper {
    flex: 1 1 60px;
    padding: 0 0 10px 0;
    box-sizing: border-box;
    overflow: auto;

    .ele-user-select-tree {
      padding: 0 calc(eleVar('tree', 'item-radius') / 2 * 5);
      #{eleVarName('tree', 'item-height')}: 34px;
    }

    .ele-user-select-tree-label > .el-icon {
      margin-right: 4px;
      vertical-align: -2px;
    }
  }

  .ele-user-select-tree-search {
    flex-shrink: 0;
    padding: 12px 10px 10px 10px;
    box-sizing: border-box;
  }

  /* 表格 */
  .ele-user-select-body {
    flex: 1;
    padding: 12px 16px 0 16px;
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
    overflow: hidden;

    @include flex-auto-pro-table();

    & > .ele-pro-table {
      padding-bottom: 10px;

      & > .ele-pro-table-view {
        #{eleVarName('table', 'th-bg')}: elVar('fill-color', 'light');
        #{elVarName('bg-color')}: elVar('bg-color', 'overlay');
      }

      & > .ele-pro-table-footer > .ele-pagination {
        padding-top: 0;
      }

      .el-table__row {
        cursor: pointer;
      }
    }

    & > .ele-user-select-search {
      margin-bottom: 4px;
    }

    .el-form-item {
      margin-bottom: 8px;
    }
  }

  /* 选中列表 */
  .ele-user-select-right {
    width: 180px;
    flex-shrink: 0;
    box-sizing: border-box;
    border-left: 1px solid elVar('border-color', 'light');
    display: flex;
    flex-direction: column;
  }

  .ele-user-select-right-header {
    flex-shrink: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 10px;
    box-sizing: border-box;
  }

  .ele-user-select-right-title {
    flex: 1;
    width: 100%;
    overflow: hidden;
    padding-right: 8px;
    box-sizing: border-box;
    font-size: 13px;
  }

  .ele-user-select-right-clear {
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

  .ele-user-select-right-body {
    flex: 1 1 60px;
    padding: 0 10px;
    box-sizing: border-box;
    user-select: none;
    overflow: auto;

    &.is-sortable .ele-user-select-right-item {
      cursor: move;
    }
  }

  /* 选中列表项 */
  .ele-user-select-right-item {
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

  .ele-user-select-right-label {
    flex: 1;
    line-height: 16px;
    margin-left: 4px;
    word-break: break-all;
    overflow: hidden;
  }

  .ele-user-select-right-avatar {
    flex-shrink: 0;
    width: 28px;
    height: 28px;
    line-height: 28px;
    text-align: center;
    border-radius: elVar('border-radius', 'base');
    background: elVar('fill-color', 'light');

    &.is-icon {
      color: #fff;
      font-size: 12px;
      background: elVar('color-primary');
    }

    & > img {
      width: 100%;
      height: 100%;
      object-fit: contain;
      border-radius: inherit;
    }
  }

  .ele-user-select-right-icon {
    flex-shrink: 0;
    width: 24px;
    height: 24px;
    font-size: 16px;
  }

  .ele-user-select-right-del {
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
    .ele-user-select-body > .ele-pro-table {
      padding-bottom: 8px;
    }

    .ele-user-select-wrapper.ele-split-panel > .ele-split-panel-body {
      flex-direction: column;
    }

    .ele-user-select-right {
      width: auto;
      border-left: none;
      border-top: 1px solid elVar('border-color', 'light');
    }

    .ele-user-select-right-body {
      flex: none;
      display: flex;
      min-height: 46px;
      overflow: auto;
    }

    .ele-user-select-right-item {
      width: max-content;
      max-width: 160px;

      & + .ele-user-select-right-item {
        margin-left: 8px;
      }
    }

    .ele-user-select-right-header {
      padding-top: 8px;
      padding-bottom: 8px;
      flex-direction: row;

      & > .ele-user-select-right-title,
      & > .ele-user-select-right-clear {
        width: auto;
        margin: 0;
      }
    }
  }
</style>
