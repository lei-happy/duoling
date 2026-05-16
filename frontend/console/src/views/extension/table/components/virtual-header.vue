<template>
  <div>
    <ele-pro-table
      :height="418"
      :virtual="true"
      row-key="userId"
      :columns="columns"
      :datasource="datasource"
      :show-overflow-tooltip="true"
      :pagination="{
        pageSize: 1000,
        pageSizes: [1000, 2000]
      }"
      :border="true"
      :toolbar="{ theme: 'default' }"
      :table-style="{ overflow: 'hidden' }"
      :tools="proTableToolsWithExportPrint"
      :export-config="{ fileName: '用户数据', datasource: exportSource }"
      :print-config="{ datasource: exportSource }"
    />
  </div>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import dayjs from 'dayjs';
  import type {
    DatasourceFunction,
    Columns
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import { proTableToolsWithExportPrint } from '@/config/pro-table-tool-presets';
  const addresses = [
    ['浙江', '杭州', '西湖区'],
    ['江苏', '苏州', '姑苏区'],
    ['江西', '南昌', '青山湖区'],
    ['福建', '泉州', '丰泽区'],
    ['湖北', '武汉', '武昌区'],
    ['安徽', '黄山', '黄山区']
  ];

  interface User {
    userId?: number;
    username?: string;
    nickname?: string;
    createTime?: string;
    province?: string;
    city?: string;
    zone?: string;
  }

  const data: User[] = [];

  /** 表格列配置 */
  const columns = ref<Columns>([
    {
      type: 'index',
      columnKey: 'index',
      width: 68,
      align: 'center',
      fixed: 'left'
    },
    {
      label: '用户账号',
      prop: 'username',
      minWidth: 160,
      sortable: 'custom'
    },
    {
      label: '用户名',
      prop: 'nickname',
      minWidth: 160,
      sortable: 'custom'
    },
    {
      label: '家庭住址',
      prop: 'address',
      align: 'center',
      children: [
        {
          label: '省份',
          prop: 'province',
          width: 120,
          sortable: 'custom'
        },
        {
          label: '城市',
          prop: 'city',
          width: 120,
          sortable: 'custom'
        },
        {
          label: '区域',
          prop: 'zone',
          width: 180,
          sortable: 'custom'
        }
      ]
    },
    {
      label: '创建时间',
      prop: 'createTime',
      width: 180,
      sortable: 'custom',
      align: 'center'
    }
  ]);

  /** 表格数据源 */
  const datasource: DatasourceFunction = async ({ pages, orders }) => {
    await new Promise((resolve) => setTimeout(resolve, 100));
    if (!data.length) {
      Array.from({ length: 2000 }).forEach((_, i) => {
        const userId = i + 1;
        const username = `user-${String(userId).padStart(6, '0')}`;
        const index = Math.floor(
          Math.random() * (0 - addresses.length) + addresses.length
        );
        const [province, city, zone] = addresses[index];
        const item: User = {
          userId,
          username,
          nickname: `用户${userId}`,
          createTime: dayjs()
            .subtract(45 * userId, 's')
            .format('YYYY-MM-DD HH:mm:ss'),
          province,
          city,
          zone
        };
        data.push(item);
      });
    }
    const list = [...data];
    if (orders != null && orders.sort) {
      list.sort((a: any, b: any) => {
        const aValue = a[orders.sort as any];
        const bValue = b[orders.sort as any];
        if (aValue == bValue) {
          return 0;
        }
        const r = aValue < bValue ? -1 : 1;
        return orders.order === 'desc' ? -r : r;
      });
    }
    const start = ((pages.page || 1) - 1) * (pages.limit || 10);
    const end = start + (pages.limit || 10);
    return {
      count: list.length,
      list: list.slice(start, end > list.length ? list.length : end)
    };
  };

  /** 导出和打印全部数据的数据源 */
  const exportSource: DatasourceFunction = async ({ orders }) => {
    const res: any = await datasource({
      orders,
      pages: { page: 1, limit: data.length }
    } as any);
    return res.list;
  };
</script>
