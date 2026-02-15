<template>
  <ele-card header="限制选择数量">
    <div style="max-width: 260px">
      <ele-table-select
        multiple
        clearable
        placeholder="请选择"
        value-key="userId"
        label-key="nickname"
        :model-value="selectedValue"
        :table-props="tableProps"
        :popper-width="580"
        :popper-options="{ strategy: 'fixed' }"
        @update:modelValue="updateModelValue"
      />
    </div>
  </ele-card>
</template>

<script lang="ts" setup>
  import { ref, reactive } from 'vue';
  import { EleMessage } from 'ele-admin-plus';
  import { listUsers } from '@/api/system/user';
  import type { TableSelectProps } from 'ele-admin-plus/es/ele-table-select/props';
  type SelectTableProps = Exclude<TableSelectProps['tableProps'], undefined>;

  /** 表格下拉选中值 */
  const selectedValue = ref<number[]>([]);

  /** 表格配置 */
  const tableProps = reactive<SelectTableProps>({
    datasource: [],
    columns: [
      {
        type: 'selection',
        columnKey: 'selection',
        width: 50,
        align: 'center',
        reserveSelection: true
      },
      {
        type: 'index',
        columnKey: 'index',
        width: 50,
        align: 'center'
      },
      {
        prop: 'username',
        label: '用户账号',
        sortable: 'custom'
      },
      {
        prop: 'nickname',
        label: '用户名',
        sortable: 'custom',
        slot: 'nickname'
      },
      {
        prop: 'sexName',
        label: '性别',
        sortable: 'custom',
        width: 80
      }
    ],
    showOverflowTooltip: true,
    toolbar: false,
    pagination: {
      pageSize: 6,
      layout: 'total, prev, pager, next, jumper',
      style: { padding: '0px' }
    },
    rowClickChecked: true
  });

  /** 更新选中数据 */
  const updateModelValue = (selected: number[]) => {
    if (selected && selected.length > 5) {
      EleMessage.error({ message: '最多只能选择 5 个', plain: true });
      selectedValue.value = selected.slice(0, 5);
      return;
    }
    selectedValue.value = selected;
  };

  /** 查询表格数据 */
  listUsers().then((data) => {
    tableProps.datasource = data;
  });
</script>
