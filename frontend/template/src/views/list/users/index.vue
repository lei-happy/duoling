<template>
  <ele-page>
    <ele-card>
      <div>
        “男用户”页面和“女用户”页面是共用的同一个页面,
        通过获取路由参数展示不同的数据, 并且会各自KeepAlive.
      </div>
      <div style="display: flex; align-items: center; margin-top: 16px">
        <div style="padding-right: 16px">路由参数</div>
        <div>sex: {{ userType }}</div>
      </div>
      <div style="display: flex; align-items: center; margin-top: 8px">
        <div style="padding-right: 16px">测试KeepAlive</div>
        <div style="flex: 1; max-width: 220px">
          <el-input v-model="text" placeholder="请输入" />
        </div>
      </div>
    </ele-card>
    <ele-card :body-style="{ paddingTop: '8px' }">
      <ele-pro-table
        ref="tableRef"
        row-key="userId"
        :columns="columns"
        :datasource="datasource"
        :show-overflow-tooltip="true"
        :highlight-current-row="true"
        :pagination="{ pageSize: 5, pageSizes: [5, 10, 20] }"
        :tools="proTableToolsWithExportPrint"
        :export-config="{
          fileName: (userType == '1' ? '男' : '女') + '用户数据',
          datasource: exportSource
        }"
        :print-config="{ datasource: exportSource }"
        :cache-key="`ListUsersTable-${userType}`"
      >
        <template #action="{ row }">
          <el-link type="primary" underline="never" @click="openDetail(row)">
            查看用户详情
          </el-link>
        </template>
      </ele-pro-table>
    </ele-card>
  </ele-page>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import { useRouter, useRoute } from 'vue-router';
  import type {
    DatasourceFunction,
    Columns
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import { proTableToolsWithExportPrint } from '@/config/pro-table-tool-presets';
  import { usePageTab } from '@/utils/use-page-tab';
  import { pageUsers, listUsers } from '@/api/system/user';
  import type { User } from '@/api/system/user/model';

  defineOptions({ name: 'ListUsers' });

  const { push } = useRouter();
  const { path } = useRoute();
  const { addPageTab } = usePageTab();
  /** 获取用户性别类型 */
  const userType = path.substring(path.lastIndexOf('/') + 1);

  /** 表格列配置 */
  const columns = ref<Columns>([
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
      minWidth: 120,
      align: 'center'
    },
    {
      prop: 'nickname',
      label: '用户名',
      sortable: 'custom',
      minWidth: 120,
      align: 'center'
    },
    {
      prop: 'sexName',
      label: '性别',
      sortable: 'custom',
      width: 90,
      align: 'center'
    },
    {
      prop: 'phone',
      label: '手机号',
      sortable: 'custom',
      minWidth: 140,
      align: 'center'
    },
    {
      prop: 'createTime',
      label: '创建时间',
      sortable: 'custom',
      minWidth: 200,
      align: 'center'
    },
    {
      columnKey: 'action',
      label: '操作',
      width: 160,
      align: 'center',
      slot: 'action',
      hideInPrint: true,
      hideInExport: true
    }
  ]);

  /** 表格数据源 */
  const datasource: DatasourceFunction = ({ pages, orders }) => {
    return pageUsers({ ...orders, ...pages, sex: userType });
  };

  /** 输入框 */
  const text = ref('');

  /** 导出和打印全部数据的数据源 */
  const exportSource: DatasourceFunction = ({ orders }) => {
    return listUsers({ ...orders, sex: userType });
  };

  /** 查看详情 */
  const openDetail = (row: User) => {
    const path = `/list/users/details/${userType}/${row.userId}`;
    const sex = userType == '1' ? '男' : '女';
    addPageTab({
      title: `${sex}用户详情[${row.nickname}]`,
      key: path,
      closable: true,
      meta: { icon: 'LinkOutlined' }
    });
    push(path);
  };
</script>
