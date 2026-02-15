<template>
  <div>
    <ele-pro-table
      ref="tableRef"
      row-key="userId"
      :columns="columns"
      :datasource="datasource"
      :show-overflow-tooltip="true"
      :highlight-current-row="true"
      :export-config="{ fileName: '用户数据', datasource: exportSource }"
      :print-config="{ datasource: exportSource }"
      @row-contextmenu="handleRowContextmenu"
    />
    <ele-dropdown
      ref="ctxMenuDropdownRef"
      trigger="click"
      :trigger-keys="[]"
      :icon-props="{ size: 15 }"
      :popper-options="{
        strategy: 'fixed',
        modifiers: [{ name: 'offset', options: { offset: [0, -12] } }]
      }"
      :persistent="false"
      component-type="pro"
      :prevent-contextmenu="true"
      :virtual-triggering="true"
      :virtual-ref="ctxMenuDropdownVirtualRef"
      :disabled="!ctxMenuDropdownItems.length"
      :items="ctxMenuDropdownItems"
      :popper-style="ctxMenuDropdownStyle"
      @command="handleItemCommand"
    />
  </div>
</template>

<script lang="ts" setup>
  import { ref, reactive, nextTick, markRaw } from 'vue';
  import { EleMessage } from 'ele-admin-plus';
  import type { EleDropdownInstance } from 'ele-admin-plus/es/ele-app/plus';
  import type { DropdownItem } from 'ele-admin-plus/es/ele-dropdown/types';
  import type { EleProTable } from 'ele-admin-plus';
  import type {
    DatasourceFunction,
    Column
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import {
    LockOutlined,
    EditOutlined,
    DeleteOutlined,
    DownloadOutlined,
    LinkOutlined
  } from '@/components/icons';
  import { pageUsers, listUsers } from '@/api/system/user';
  import type { User } from '@/api/system/user/model';

  /** 表格实例 */
  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);

  /** 表格列配置 */
  const columns = ref<Column[]>([
    {
      type: 'index',
      columnKey: 'index',
      width: 50,
      align: 'center'
    },
    {
      prop: 'username',
      label: '用户账号',
      sortable: 'custom',
      minWidth: 140
    },
    {
      prop: 'nickname',
      label: '用户名',
      sortable: 'custom',
      minWidth: 140
    },
    {
      prop: 'sexName',
      label: '性别',
      sortable: 'custom',
      width: 110,
      align: 'center'
    },
    {
      prop: 'createTime',
      label: '创建时间',
      sortable: 'custom',
      minWidth: 180,
      align: 'center'
    }
  ]);

  /** 表格数据源 */
  const datasource: DatasourceFunction = ({ pages, orders, filters }) => {
    return pageUsers({ ...orders, ...filters, ...pages });
  };

  /** 导出和打印全部数据的数据源 */
  const exportSource: DatasourceFunction = ({ orders, filters }) => {
    return listUsers({ ...orders, ...filters });
  };

  /** 右键菜单组件 */
  const ctxMenuDropdownRef = ref<EleDropdownInstance>(null);

  /** 右键菜单数据 */
  const ctxMenuDropdownItems = ref<DropdownItem[]>([]);

  /** 右键菜单虚拟触发节点 */
  const ctxMenuDropdownVirtualRef = ref<any>();

  /** 当前打开的右键菜单对应的数据 */
  let ctxMenuCurrentData: User | null = null;

  /** 右键菜单调整位置 */
  const ctxMenuDropdownStyle = reactive({ marginLeft: '0px' });

  /** 获取右键菜单数据 */
  const getContextMenus = (_item: User) => {
    return [
      { title: '重置密码', command: 'psw', icon: markRaw(LockOutlined) },
      { title: '修改用户', command: 'edit', icon: markRaw(EditOutlined) },
      {
        title: '导出用户',
        command: 'export',
        icon: markRaw(DownloadOutlined),
        children: [
          {
            title: '导出XLS',
            command: 'exportXlsx',
            icon: markRaw(LinkOutlined)
          },
          {
            title: '导出CSV',
            command: 'exportCsv',
            icon: markRaw(LinkOutlined)
          },
          {
            title: '导出HTML',
            command: 'exportHtml',
            icon: markRaw(LinkOutlined)
          }
        ]
      },
      {
        title: '删除用户',
        command: 'del',
        icon: markRaw(DeleteOutlined),
        danger: true,
        divided: true
      }
    ];
  };

  /** 打开右键菜单 */
  const openCtxMenuDropdown = (triggerEl: any, row: User) => {
    ctxMenuDropdownRef.value && ctxMenuDropdownRef.value.handleClose();
    nextTick(() => {
      ctxMenuCurrentData = row;
      ctxMenuDropdownItems.value = getContextMenus(row) || [];
      ctxMenuDropdownVirtualRef.value = triggerEl;
      if (ctxMenuDropdownItems.value.length) {
        nextTick(() => {
          ctxMenuDropdownRef.value && ctxMenuDropdownRef.value.handleOpen();
        });
      }
    });
  };

  /** 右键菜单项点击事件 */
  const handleItemCommand = (command: string) => {
    const row = ctxMenuCurrentData;
    if (row == null) {
      return;
    }
    if (command === 'psw') {
      EleMessage.info({
        message: `点击了重置密码: ${row.nickname}`,
        plain: true
      });
    } else if (command === 'edit') {
      EleMessage.info({ message: `点击了修改: ${row.nickname}`, plain: true });
    } else if (command === 'del') {
      EleMessage.info({ message: `点击了删除: ${row.nickname}`, plain: true });
    } else if (command === 'exportXlsx') {
      EleMessage.info({
        message: `点击了导出XLS: ${row.nickname}`,
        plain: true
      });
    } else if (command === 'exportCsv') {
      EleMessage.info({
        message: `点击了导出CSV: ${row.nickname}`,
        plain: true
      });
    } else if (command === 'exportHtml') {
      EleMessage.info({
        message: `点击了导出HTML: ${row.nickname}`,
        plain: true
      });
    }
  };

  /** 表格行右键事件 */
  const handleRowContextmenu = (row: User, _column: Column, e: MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    const rowEl = e.currentTarget as HTMLElement;
    const rect = rowEl.getBoundingClientRect();
    ctxMenuDropdownStyle.marginLeft = `${e.clientX - rect.left - rect.width / 2}px`;
    tableRef.value?.setCurrentRow?.(row);
    openCtxMenuDropdown(rowEl, row);
  };
</script>
