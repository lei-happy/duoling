<template>
  <div>
    <ele-pro-table
      row-key="userId"
      :columns="columns"
      :datasource="datasource"
      :show-overflow-tooltip="true"
      :export-config="{ fileName: '用户数据', datasource: exportSource }"
      :print-config="{ datasource: exportSource }"
    >
      <template #expand="{ row }">
        <div style="padding: 12px 16px 12px 32px">
          <div>
            <span>手机号码：</span>
            <span>{{ row.phone }}</span>
          </div>
          <div style="margin-top: 12px">
            <span>所属机构：</span>
            <span>{{ row.organizationName }}</span>
          </div>
          <div style="margin-top: 12px">
            <span>角&emsp;&emsp;色：</span>
            <span>
              <el-tag
                v-for="item in row.roles"
                :key="item.roleId"
                size="small"
                :disable-transitions="true"
              >
                {{ item.roleName }}
              </el-tag>
            </span>
          </div>
          <div style="margin-top: 12px">
            <span>状&emsp;&emsp;态：</span>
            <span>
              <ele-dot v-if="row.status === 0" text="正常" size="8px" />
              <ele-dot
                v-else-if="row.status === 1"
                text="冻结"
                type="danger"
                :ripple="false"
                size="8px"
              />
            </span>
          </div>
        </div>
      </template>
    </ele-pro-table>
  </div>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import type {
    DatasourceFunction,
    Columns
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import { pageUsers, listUsers } from '@/api/system/user';

  /** 表格列配置 */
  const columns = ref<Columns>([
    {
      type: 'expand',
      columnKey: 'expand',
      width: 50,
      align: 'center',
      slot: 'expand',
      formatter: (row) => {
        return [
          `手机号码：${row.phone}`,
          `所属机构：${row.organizationName}`,
          `角色：${row.roles.map((r) => r.roleName).join()}`,
          `状态：${row.status == 0 ? '正常' : '冻结'}`
        ].join('\n');
      }
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
      prop: 'createTime',
      label: '创建时间',
      sortable: 'custom',
      minWidth: 180,
      align: 'center'
    }
  ]);

  /** 表格数据源 */
  const datasource: DatasourceFunction = ({ pages, orders }) => {
    return pageUsers({ ...orders, ...pages });
  };

  /** 导出和打印全部数据的数据源 */
  const exportSource: DatasourceFunction = ({ orders }) => {
    return listUsers({ ...orders });
  };
</script>
