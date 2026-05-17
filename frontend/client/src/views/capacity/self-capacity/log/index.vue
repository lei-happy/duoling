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
        <template #plateNumber="{ row }">
          <plate-number-tag
            :text="row.plateNumber"
            :category="row.plateCategory"
          />
        </template>
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
  import PlateNumberTag from '@/components/PlateNumberTag/index.vue';
  import { formatDateTime, getLast7DaysDateTimeRange } from '@/utils/date-util';
  import { pageCapacityLogs } from '@/api/capacity/self_capacity/log';
  import type { CapacityLogParam } from '@/api/capacity/self_capacity/log/model';

  defineOptions({ name: 'CapacityLog' });

  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);

  const defaultLogTimeRange = getLast7DaysDateTimeRange();
  const where = reactive<
    Pick<
      CapacityLogParam,
      | 'keyword'
      | 'action'
      | 'operatorName'
      | 'actionTimeStart'
      | 'actionTimeEnd'
    >
  >({
    keyword: '',
    action: void 0,
    operatorName: '',
    actionTimeStart: defaultLogTimeRange[0],
    actionTimeEnd: defaultLogTimeRange[1]
  });

  const onSearch = (payload: Pick<
      CapacityLogParam,
      | 'keyword'
      | 'action'
      | 'operatorName'
      | 'actionTimeStart'
      | 'actionTimeEnd'
    >) => {
    where.keyword = payload.keyword ?? '';
    where.action = payload.action;
    where.operatorName = payload.operatorName ?? '';
    where.actionTimeStart = payload.actionTimeStart ?? '';
    where.actionTimeEnd = payload.actionTimeEnd ?? '';
    tableRef.value?.reload?.({ page: 1 });
  };

  const columns = ref<Columns>([
    {
      prop: 'driverCode',
      label: '驾驶员编号',
      minWidth: 90,
      formatter: (row) => row.driverCode ?? '-'
    },
    { prop: 'driverName', label: '驾驶员姓名', minWidth: 100 },
    {
      prop: 'driverPhone',
      label: '驾驶员手机号',
      minWidth: 130,
      formatter: (row) => row.driverPhone ?? '-'
    },
    {
      prop: 'plateNumber',
      label: '车牌号',
      minWidth: 120,
      slot: 'plateNumber'
    },
    {
      prop: 'action',
      label: '操作类型',
      width: 100,
      align: 'center',
      slot: 'action'
    },
    {
      prop: 'remark',
      label: '备注',
      minWidth: 210,
      showOverflowTooltip: {
        enterable: true,
        popperClass: 'capacity-log-remark-tooltip'
      }
    },
    {
      prop: 'operatorName',
      label: '操作人',
      minWidth: 90,
      align: 'center'
    },
    {
      prop: 'actionTime',
      label: '操作时间',
      minWidth: 150,
      align: 'center',
      formatter: (row) => formatDateTime(row.actionTime)
    }
  ]);

  const datasource: DatasourceFunction = async ({ page, limit }) => {
    const res = await pageCapacityLogs({ ...where, page, limit });
    return { list: res?.list ?? [], count: res?.count ?? res?.total ?? 0 };
  };
</script>

<style>
  /**
   * 备注列溢出气泡：限制宽高、换行、内部滚动，避免长备注撑满屏幕
   * popper 挂载到 body，需非 scoped
   */
  .capacity-log-remark-tooltip {
    max-width: min(440px, 92vw) !important;
    box-sizing: border-box;
  }

  .capacity-log-remark-tooltip .el-tooltip__content,
  .capacity-log-remark-tooltip .el-popper__content {
    max-width: min(440px, 92vw);
    max-height: 280px;
    overflow-y: auto;
    overflow-x: hidden;
    padding: 8px 10px;
    line-height: 1.5;
    word-break: break-word;
    overflow-wrap: anywhere;
    white-space: pre-wrap;
    box-sizing: border-box;
  }
</style>
