<template>
  <div>
    <div class="option-wrapper">
      <option-item label="表头背景" :responsive="false">
        <el-switch v-model="toolbarBg" size="small" />
      </option-item>
      <option-item label="显示边框" :responsive="false">
        <el-switch v-model="border" size="small" />
      </option-item>
      <option-item label="显示斑马纹" :responsive="false">
        <el-switch v-model="stripe" size="small" />
      </option-item>
      <option-item label="显示表头" :responsive="false">
        <el-switch v-model="showHeader" size="small" />
      </option-item>
      <option-item label="显示表尾合计行" :responsive="false">
        <el-switch v-model="showSummary" size="small" />
      </option-item>
      <option-item label="行点击高亮" :responsive="false">
        <el-switch v-model="highlightCurrentRow" size="small" />
      </option-item>
      <option-item label="行点击勾选" :responsive="false">
        <el-switch v-model="rowClickChecked" size="small" />
      </option-item>
    </div>
    <ele-pro-table
      :height="418"
      :virtual="true"
      row-key="userId"
      :columns="columns"
      :datasource="datasource"
      :show-overflow-tooltip="true"
      :highlight-current-row="highlightCurrentRow"
      :row-click-checked="rowClickChecked"
      v-model:selections="selections"
      v-model:current="current"
      :pagination="{
        pageSize: 2000,
        pageSizes: [1000, 2000, 5000, 10000]
      }"
      :toolbar="{ theme: toolbarBg ? 'default' : 'plain' }"
      :border="border"
      :stripe="stripe"
      :show-header="showHeader"
      :show-summary="showSummary"
      :summary-method="getSummaries"
      :tools="proTableToolsWithExportPrint"
      :export-config="{ fileName: '用户数据', datasource: exportSource }"
      :print-config="{ datasource: exportSource }"
    >
      <template #toolbar>
        <el-button type="primary" class="ele-btn-icon" @click="getSelections">
          获取多选行数据
        </el-button>
        <el-button
          v-if="highlightCurrentRow"
          type="primary"
          class="ele-btn-icon"
          @click="getCurrent"
        >
          获取单选行数据
        </el-button>
      </template>
      <template #roles="{ row }">
        <el-tag
          v-for="item in row.roles"
          :key="item"
          size="small"
          :disable-transitions="true"
          style="margin-right: 6px"
        >
          {{ item }}
        </el-tag>
      </template>
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
      <template #action="{ row }">
        <el-link type="primary" underline="never" @click="openEdit(row)">
          修改
        </el-link>
        <el-divider direction="vertical" />
        <el-link type="danger" underline="never" @click="remove(row)">
          删除
        </el-link>
      </template>
    </ele-pro-table>
  </div>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import dayjs from 'dayjs';
  import { EleMessage } from 'ele-admin-plus';
  import type {
    DatasourceFunction,
    Columns
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import { proTableToolsWithExportPrint } from '@/config/pro-table-tool-presets';
  import OptionItem from '@/views/extension/avatar/components/option-item.vue';

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
      type: 'selection',
      columnKey: 'selection',
      width: 52,
      align: 'center',
      fixed: 'left'
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
      label: '角色',
      prop: 'roles',
      slot: 'roles',
      minWidth: 160,
      filters: [
        { text: '管理员', value: '管理员' },
        { text: '普通用户', value: '普通用户' },
        { text: '游客', value: '游客' }
      ],
      filterMultiple: true,
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
      label: '邮箱',
      prop: 'email',
      minWidth: 180,
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
      label: '出生日期',
      prop: 'birthday',
      width: 160,
      align: 'center',
      sortable: 'custom'
    },
    {
      label: '创建时间',
      prop: 'createTime',
      width: 180,
      sortable: 'custom',
      align: 'center'
    },
    {
      columnKey: 'action',
      label: '操作',
      width: 160,
      align: 'center',
      slot: 'action',
      fixed: 'right',
      hideInPrint: true,
      hideInExport: true
    }
  ]);

  /** 表格数据源 */
  const datasource: DatasourceFunction = async ({ pages, filter, orders }) => {
    await new Promise((resolve) => setTimeout(resolve, 100));
    if (!data.length) {
      Array.from({ length: 10000 }).forEach((_, i) => {
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
    const rolesFilter = filter.roles?.length ? filter.roles : null;
    const statusFilter = filter.status?.length ? filter.status : null;
    const list = data.filter((d) => {
      if (rolesFilter != null) {
        if (!d.roles || !d.roles.some((r) => rolesFilter.includes(r))) {
          return false;
        }
      }
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

  /** 表格多选选中数据 */
  const selections = ref<User[]>([]);

  /** 表格单选选中数据 */
  const current = ref<User | null>(null);

  /** 更多配置 */
  const toolbarBg = ref(false);
  const border = ref(false);
  const stripe = ref(false);
  const showHeader = ref(true);
  const showSummary = ref(true);
  const highlightCurrentRow = ref(false);
  const rowClickChecked = ref(false);

  /** 打开编辑弹窗 */
  const openEdit = (row: User) => {
    EleMessage.success({ message: `编辑: ${row.nickname}`, plain: true });
  };

  /** 删除单个 */
  const remove = (row: User) => {
    EleMessage.error({ message: `删除: ${row.nickname}`, plain: true });
  };

  /** 表尾合计行 */
  const getSummaries = ({ columns, data }) => {
    const sums: string[] = [];
    let labelFlag = false;
    columns.forEach((column: any, i: number) => {
      if (column.property === 'sex') {
        const num = data.filter((d: User) => d.sex == '女').length;
        sums[i] = ((num / data.length) * 100).toFixed(2) + '% (女)';
        labelFlag = true;
      } else if (column.property === 'status') {
        sums[i] = data.filter((d: User) => d.status == '1').length + ' (冻结)';
        labelFlag = true;
      } else if (
        !labelFlag &&
        column?.type !== 'selection' &&
        column?.type !== 'index'
      ) {
        sums[i] = '合计';
        labelFlag = true;
      }
    });
    return sums;
  };

  /** 获取多选行数据 */
  const getSelections = () => {
    console.log(JSON.parse(JSON.stringify(selections.value)));
    EleMessage.success({
      message: `共 ${selections.value.length} 条数据已打印在控制台`,
      plain: true
    });
  };

  /** 获取选中行数据 */
  const getCurrent = () => {
    if (!current.value) {
      EleMessage.success({ message: '未选中任何数据', plain: true });
    } else {
      console.log(JSON.parse(JSON.stringify(current.value)));
      EleMessage.success({
        message: current.value.nickname + '的数据已打印在控制台',
        plain: true
      });
    }
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

<style lang="scss" scoped>
  .option-wrapper {
    display: flex;
    align-items: flex-start;
    flex-wrap: wrap;
    padding-top: 12px;

    :deep(.option-item) {
      margin: 0 20px 8px 0;

      .option-item-label + .option-item-body {
        padding-left: 4px;
      }
    }
  }
</style>
