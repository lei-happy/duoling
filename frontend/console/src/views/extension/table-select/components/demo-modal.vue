<template>
  <ele-card header="弹窗模式、抽屉模式">
    <div style="margin: 0 0 8px 0">弹窗模式:</div>
    <div style="max-width: 260px">
      <ele-table-select
        multiple
        clearable
        placeholder="请选择"
        value-key="userId"
        label-key="nickname"
        v-model="selectedValue"
        :table-props="tableProps"
        :popper-width="720"
        popper-type="modal"
        popper-title="请选择"
      >
        <!-- 角色列 -->
        <template #roles="{ row }">
          <el-tag
            v-for="item in row.roles"
            :key="item.roleId"
            size="small"
            :disable-transitions="true"
          >
            {{ item.roleName }}
          </el-tag>
        </template>
      </ele-table-select>
    </div>
    <div style="margin: 32px 0 8px 0">抽屉模式:</div>
    <div style="max-width: 260px">
      <ele-table-select
        multiple
        clearable
        placeholder="请选择"
        value-key="userId"
        label-key="nickname"
        v-model="selectedValue2"
        :table-props="tableProps"
        :popper-width="720"
        popper-type="drawer"
        popper-title="请选择"
        :popperProps="{
          flexTable: 'auto',
          bodyStyle: { paddingBottom: '10px' }
        }"
      >
        <!-- 角色列 -->
        <template #roles="{ row }">
          <el-tag
            v-for="item in row.roles"
            :key="item.roleId"
            size="small"
            :disable-transitions="true"
          >
            {{ item.roleName }}
          </el-tag>
        </template>
      </ele-table-select>
    </div>
  </ele-card>
</template>

<script lang="ts" setup>
  import { ref, reactive } from 'vue';
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
      },
      {
        columnKey: 'roles',
        label: '角色',
        slot: 'roles'
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

  /** 查询表格数据 */
  listUsers().then((data) => {
    tableProps.datasource = data;
  });

  /** 表格下拉选中值 */
  const selectedValue2 = ref<number[]>([]);
</script>
