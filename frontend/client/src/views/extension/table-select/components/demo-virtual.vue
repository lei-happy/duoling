<template>
  <ele-card header="虚拟滚动表格">
    <div style="max-width: 260px">
      <ele-table-select
        multiple
        clearable
        placeholder="请选择"
        value-key="userId"
        label-key="nickname"
        v-model="selectedValue"
        :table-props="tableProps"
        :popper-width="580"
        :max-tag-count="5"
        :popper-options="{ strategy: 'fixed' }"
      >
        <template #status="{ row }">
          <ele-dot v-if="row.status == 0" text="正常" size="8px" />
          <ele-dot
            v-else-if="row.status == 1"
            text="冻结"
            type="danger"
            :ripple="false"
            size="8px"
          />
        </template>
      </ele-table-select>
    </div>
    <div style="margin-top: 12px">
      <el-button type="primary" @click="setValue">回显数据</el-button>
    </div>
  </ele-card>
</template>

<script lang="ts" setup>
  import { ref, reactive } from 'vue';
  import type { TableSelectProps } from 'ele-admin-plus/es/ele-table-select/props';
  type SelectTableProps = Exclude<TableSelectProps['tableProps'], undefined>;

  /** 表格下拉选中值 */
  const selectedValue = ref<number[]>([]);

  /** 表格配置 */
  const tableProps = reactive<SelectTableProps>({
    virtual: true,
    height: 288,
    datasource: [],
    columns: [
      {
        type: 'selection',
        columnKey: 'selection',
        width: 50,
        align: 'center',
        fixed: 'left',
        reserveSelection: true
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
        prop: 'sex',
        label: '性别',
        sortable: 'custom',
        width: 80
      },
      {
        prop: 'status',
        label: '状态',
        width: 120,
        sortable: 'custom',
        slot: 'status'
      }
    ],
    showOverflowTooltip: true,
    toolbar: false,
    pagination: {
      pageSize: 1000,
      pageSizes: [1000, 2000],
      layout: 'total, prev, pager, next, sizes',
      teleported: false,
      style: { padding: '0px' }
    },
    rowClickChecked: true
  });

  /** 回显数据 */
  const setValue = () => {
    selectedValue.value = [40, 44, 45];
  };

  /** 查询表格数据 */
  tableProps.datasource = Array.from({ length: 2000 }).map((_, i) => {
    const userId = i + 1;
    const username = `user-${String(userId).padStart(6, '0')}`;
    const random = Math.random();
    return {
      userId,
      username,
      nickname: `用户${userId}`,
      sex: random < 0.8 ? '男' : '女',
      status: random < 0.2 ? '1' : '0'
    };
  });
</script>
