<template>
  <ele-page>
    <driver-search @search="(where) => reload(where, 1)" />
    <ele-card :body-style="{ paddingTop: '8px' }">
      <ele-pro-table
        ref="tableRef"
        row-key="id"
        :columns="columns"
        :datasource="datasource"
        :show-overflow-tooltip="true"
        :highlight-current-row="true"
        :default-sort="{ prop: 'updatedAt', order: 'descending' }"
        cache-key="PlatformDriverListTable"
      >
        <template #status="{ row }">
          <el-tag
            v-if="row.status === 1"
            type="success"
            size="small"
            :disable-transitions="true"
          >
            在职
          </el-tag>
          <el-tag
            v-else-if="row.status === 0"
            type="info"
            size="small"
            :disable-transitions="true"
          >
            冻结
          </el-tag>
          <el-tag
            v-else-if="row.status === 2"
            type="danger"
            size="small"
            :disable-transitions="true"
          >
            离职
          </el-tag>
        </template>
        <template #action="{ row }">
          <el-link type="primary" :underline="false" @click="viewDetail(row)">
            查看
          </el-link>
        </template>
      </ele-pro-table>
    </ele-card>

    <!-- 详情弹窗 -->
    <el-dialog
      v-model="detailVisible"
      title="司机详情"
      width="500px"
      draggable
    >
      <el-descriptions :column="1" border v-if="detailData">
        <el-descriptions-item label="司机编号">
          {{ detailData.driverCode }}
        </el-descriptions-item>
        <el-descriptions-item label="姓名">
          {{ detailData.name }}
        </el-descriptions-item>
        <el-descriptions-item label="手机号">
          {{ detailData.phone }}
        </el-descriptions-item>
        <el-descriptions-item label="所属企业">
          {{ detailData.tenantName }}
        </el-descriptions-item>
        <el-descriptions-item label="人事状态">
          <el-tag
            v-if="detailData.status === 1"
            type="success"
            size="small"
          >
            在职
          </el-tag>
          <el-tag
            v-else-if="detailData.status === 0"
            type="info"
            size="small"
          >
            冻结
          </el-tag>
          <el-tag
            v-else-if="detailData.status === 2"
            type="danger"
            size="small"
          >
            离职
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="同步时间">
          {{ detailData.updatedAt }}
        </el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="detailVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </ele-page>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import type { EleProTable } from 'ele-admin-plus';
  import type {
    DatasourceFunction,
    Columns
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import DriverSearch from './components/driver-search.vue';
  import { pagePlatformDrivers, getPlatformDriver } from '@/api/driver';
  import type {
    PlatformDriver,
    PlatformDriverParam
  } from '@/api/driver/model';

  defineOptions({ name: 'PlatformDriverList' });

  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);
  const detailVisible = ref(false);
  const detailData = ref<PlatformDriver | null>(null);

  const columns = ref<Columns>([
    {
      type: 'index',
      columnKey: 'index',
      width: 50,
      align: 'center'
    },
    {
      prop: 'driverCode',
      label: '司机编号',
      minWidth: 120
    },
    {
      prop: 'name',
      label: '姓名',
      minWidth: 90
    },
    {
      prop: 'phone',
      label: '手机号',
      minWidth: 130
    },
    {
      prop: 'tenantName',
      label: '所属企业',
      minWidth: 160
    },
    {
      prop: 'status',
      label: '人事状态',
      width: 100,
      align: 'center',
      slot: 'status'
    },
    {
      prop: 'updatedAt',
      label: '同步时间',
      width: 170,
      align: 'center',
      sortable: 'custom'
    },
    {
      columnKey: 'action',
      label: '操作',
      width: 90,
      align: 'center',
      slot: 'action',
      hideInPrint: true,
      hideInExport: true,
      fixed: 'right'
    }
  ]);

  const datasource: DatasourceFunction = async ({ pages, where, orders }) => {
    const res = await pagePlatformDrivers({ ...where, ...orders, ...pages });
    const raw = res as { list?: PlatformDriver[]; count?: number; total?: number };
    return {
      list: raw?.list ?? [],
      count: raw?.count ?? raw?.total ?? 0
    };
  };

  const reload = (where?: PlatformDriverParam, page?: number) => {
    tableRef.value?.reload?.({ where, page });
  };

  const viewDetail = async (row: PlatformDriver) => {
    try {
      const data = await getPlatformDriver(row.id!);
      detailData.value = data ?? row;
    } catch {
      detailData.value = row;
    }
    detailVisible.value = true;
  };
</script>
