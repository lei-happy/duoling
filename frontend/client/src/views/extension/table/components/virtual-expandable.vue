<template>
  <div>
    <ele-pro-table
      :height="378"
      :virtual="true"
      row-key="userId"
      :columns="columns"
      :datasource="datasource"
      :show-overflow-tooltip="true"
      :pagination="{
        pageSize: 1000,
        pageSizes: [1000, 2000]
      }"
      :export-config="{ fileName: '用户数据', datasource: exportSource }"
      :print-config="{ datasource: exportSource }"
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
      <template #expand="{ row }">
        <div style="padding: 12px 16px 12px 32px">
          <div>
            <span>角&emsp;&emsp;色：</span>
            <span>
              <el-tag
                v-for="item in row.roles"
                :key="item"
                size="small"
                :disable-transitions="true"
                style="margin-right: 6px"
              >
                {{ item }}
              </el-tag>
            </span>
          </div>
          <div style="margin-top: 12px">
            <span>出生日期：</span>
            <span>{{ row.birthday }}</span>
          </div>
          <div style="margin-top: 12px">
            <span>邮箱账户：</span>
            <span>{{ row.email }}</span>
          </div>
        </div>
      </template>
    </ele-pro-table>
  </div>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import dayjs from 'dayjs';
  import type {
    DatasourceFunction,
    Columns
  } from 'ele-admin-plus/es/ele-pro-table/types';

  interface User {
    userId?: number;
    username?: string;
    nickname?: string;
    sex?: string;
    roles?: string[];
    phone?: string;
    email?: string;
    birthday?: string;
    createTime?: string;
    status?: string;
  }

  const data: User[] = [];

  /** 表格列配置 */
  const columns = ref<Columns>([
    {
      type: 'expand',
      columnKey: 'expand',
      width: 52,
      align: 'center',
      slot: 'expand',
      fixed: 'left',
      formatter: (row) => {
        return [
          `角色：${row.roles.join()}`,
          `出生日期：${row.birthday}`,
          `邮箱账户：${row.email}`
        ].join('\n');
      }
    },
    {
      type: 'index',
      columnKey: 'index',
      width: 68,
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
      label: '性别',
      prop: 'sex',
      width: 120,
      sortable: 'custom',
      align: 'center'
    },
    {
      label: '手机号码',
      prop: 'phone',
      minWidth: 160,
      sortable: 'custom',
      align: 'center'
    },
    {
      prop: 'status',
      label: '状态',
      width: 120,
      sortable: 'custom',
      slot: 'status',
      align: 'center',
      filters: [
        { text: '正常', value: '0' },
        { text: '冻结', value: '1' }
      ],
      filterMultiple: false,
      formatter: (row) => (row.status == 0 ? '正常' : '冻结')
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
  const datasource: DatasourceFunction = async ({ pages, filter, orders }) => {
    await new Promise((resolve) => setTimeout(resolve, 100));
    if (!data.length) {
      Array.from({ length: 2000 }).forEach((_, i) => {
        const userId = i + 1;
        const username = `user-${String(userId).padStart(6, '0')}`;
        const random = Math.random();
        const item: User = {
          userId,
          username,
          nickname: `用户${userId}`,
          sex: random < 0.8 ? '男' : '女',
          roles: [random < 0.3 ? '管理员' : '普通用户'],
          phone: String(12345678900 + userId),
          email: username + '@eleadmin.com',
          status: random < 0.2 ? '1' : '0',
          birthday: dayjs()
            .subtract(3 * userId, 'h')
            .format('YYYY-MM-DD'),
          createTime: dayjs()
            .subtract(45 * userId, 's')
            .format('YYYY-MM-DD HH:mm:ss')
        };
        data.push(item);
      });
    }
    const statusFilter = filter.status?.length ? filter.status : null;
    const list = data.filter((d) => {
      if (statusFilter != null) {
        if (d.status == null || !statusFilter.includes(d.status)) {
          return false;
        }
      }
      return true;
    });
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
  const exportSource: DatasourceFunction = async ({ filter, orders }) => {
    const res: any = await datasource({
      filter,
      orders,
      pages: { page: 1, limit: data.length }
    } as any);
    return res.list;
  };
</script>
