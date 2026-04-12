<template>
  <ele-page>
    <log-search @search="onSearch" />
    <ele-card :body-style="{ paddingTop: '8px' }">
      <ele-pro-table
        ref="tableRef"
        row-key="id"
        :columns="columns"
        :datasource="datasource"
        :show-overflow-tooltip="true"
        :highlight-current-row="true"
        cache-key="CapacityLogTable"
      >
        <template #action="{ row }">
          <el-tag v-if="row.action === 1" type="success" size="small">
            上车
          </el-tag>
          <el-tag v-else-if="row.action === 2" type="danger" size="small">
            下车
          </el-tag>
        </template>
      </ele-pro-table>
    </ele-card>
  </ele-page>
</template>

<script lang="ts" setup>
  import { ref, reactive } from 'vue';
  import type { EleProTable } from 'ele-admin-plus';
  import type {
    DatasourceFunction,
    Columns
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import LogSearch from './components/log-search.vue';
  import { pageCapacityLogs } from '@/api/capacity';
  import type { CapacityLogParam } from '@/api/capacity/model';

  defineOptions({ name: 'CapacityLog' });

  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);

  const where = reactive<Pick<CapacityLogParam, 'keyword' | 'action'>>({
    keyword: '',
    action: void 0
  });

  const onSearch = (
    payload: Pick<CapacityLogParam, 'keyword' | 'action'>
  ) => {
    where.keyword = payload.keyword ?? '';
    where.action = payload.action;
    tableRef.value?.reload?.({ page: 1 });
  };

  const columns = ref<Columns>([
    { prop: 'driverName', label: '司机姓名', minWidth: 100 },
    { prop: 'plateNumber', label: '车牌号', minWidth: 120 },
    {
      prop: 'action',
      label: '操作类型',
      width: 100,
      align: 'center',
      slot: 'action'
    },
    {
      prop: 'actionTime',
      label: '操作时间',
      minWidth: 170,
      align: 'center'
    },
    {
      prop: 'operatorName',
      label: '操作人',
      minWidth: 100
    },
    {
      prop: 'remark',
      label: '备注',
      minWidth: 150
    }
  ]);

  const datasource: DatasourceFunction = async ({ page, limit }) => {
    const res = await pageCapacityLogs({ ...where, page, limit });
    return { list: res?.list ?? [], count: res?.count ?? res?.total ?? 0 };
  };
</script>
