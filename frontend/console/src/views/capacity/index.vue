<template>
  <ele-page>
    <capacity-search @search="(where) => reload(where, 1)" />
    <ele-card :body-style="{ paddingTop: '8px' }">
      <ele-pro-table
        ref="tableRef"
        row-key="id"
        :columns="columns"
        :datasource="datasource"
        :show-overflow-tooltip="true"
        :highlight-current-row="true"
        :default-sort="{ prop: 'updatedAt', order: 'descending' }"
        cache-key="PlatformCapacityListTable"
      >
        <template #status="{ row }">
          <el-tag
            v-if="row.status === 1"
            type="success"
            size="small"
            :disable-transitions="true"
          >
            绑定中
          </el-tag>
          <el-tag
            v-else-if="row.status === 0"
            type="info"
            size="small"
            :disable-transitions="true"
          >
            已解绑
          </el-tag>
        </template>
        <template #action="{ row }">
          <el-link type="primary" :underline="false" @click="viewDetail(row)">
            查看
          </el-link>
        </template>
      </ele-pro-table>
    </ele-card>

    <el-dialog
      v-model="detailVisible"
      title="运力详情"
      width="500px"
      draggable
    >
      <el-descriptions :column="1" border v-if="detailData">
        <el-descriptions-item label="司机姓名">
          {{ detailData.driverName }}
        </el-descriptions-item>
        <el-descriptions-item label="手机号">
          {{ detailData.driverPhone }}
        </el-descriptions-item>
        <el-descriptions-item label="车牌号">
          {{ detailData.plateNumber }}
        </el-descriptions-item>
        <el-descriptions-item label="所属企业">
          {{ detailData.tenantName }}
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag
            v-if="detailData.status === 1"
            type="success"
            size="small"
          >
            绑定中
          </el-tag>
          <el-tag
            v-else-if="detailData.status === 0"
            type="info"
            size="small"
          >
            已解绑
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="绑定时间">
          {{ detailData.boundAt }}
        </el-descriptions-item>
        <el-descriptions-item label="解绑时间">
          {{ detailData.unboundAt || '—' }}
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
  import CapacitySearch from './components/capacity-search.vue';
  import { pagePlatformCapacities, getPlatformCapacity } from '@/api/capacity';
  import type {
    PlatformCapacity,
    PlatformCapacityParam
  } from '@/api/capacity/model';

  defineOptions({ name: 'PlatformCapacityList' });

  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);
  const detailVisible = ref(false);
  const detailData = ref<PlatformCapacity | null>(null);

  const columns = ref<Columns>([
    {
      type: 'index',
      columnKey: 'index',
      width: 50,
      align: 'center'
    },
    {
      prop: 'driverName',
      label: '司机姓名',
      minWidth: 100
    },
    {
      prop: 'driverPhone',
      label: '手机号',
      minWidth: 130
    },
    {
      prop: 'plateNumber',
      label: '车牌号',
      minWidth: 120
    },
    {
      prop: 'tenantName',
      label: '所属企业',
      minWidth: 160
    },
    {
      prop: 'status',
      label: '状态',
      width: 100,
      align: 'center',
      slot: 'status'
    },
    {
      prop: 'boundAt',
      label: '绑定时间',
      minWidth: 170,
      align: 'center'
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
    const res = await pagePlatformCapacities({ ...where, ...orders, ...pages });
    const raw = res as { list?: PlatformCapacity[]; count?: number; total?: number };
    return {
      list: raw?.list ?? [],
      count: raw?.count ?? raw?.total ?? 0
    };
  };

  const reload = (where?: PlatformCapacityParam, page?: number) => {
    tableRef.value?.reload?.({ where, page });
  };

  const viewDetail = async (row: PlatformCapacity) => {
    try {
      const data = await getPlatformCapacity(row.id!);
      detailData.value = data ?? row;
    } catch {
      detailData.value = row;
    }
    detailVisible.value = true;
  };
</script>
