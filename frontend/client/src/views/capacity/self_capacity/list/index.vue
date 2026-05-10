<template>
  <ele-page>
    <capacity-search @search="onSearch" />
    <ele-card :body-style="{ paddingTop: '8px' }">
      <ele-pro-table
        ref="tableRef"
        row-key="id"
        :columns="columns"
        :datasource="datasource"
        :show-overflow-tooltip="true"
        :highlight-current-row="true"
        :default-sort="{ prop: 'boundAt', order: 'descending' }"
        cache-key="CapacityListTable"
      >
        <template #toolbar>
          <btn-items
            :items="[
              {
                preset: 'add',
                title: '新建运力',
                onClick: () => openBind()
              }
            ]"
          />
        </template>
        <template #action="{ row }">
          <el-button type="danger" link size="small" @click="handleUnbind(row)">
            下车
          </el-button>
        </template>
      </ele-pro-table>
    </ele-card>
    <capacity-bind v-model:visible="bindVisible" @done="reload" />
  </ele-page>
</template>

<script lang="ts" setup>
  import { ref, reactive } from 'vue';
  import { ElMessageBox } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import type { EleProTable } from 'ele-admin-plus';
  import type {
    DatasourceFunction,
    Columns
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import CapacitySearch from './components/capacity-search.vue';
  import CapacityBind from './components/capacity-bind.vue';
  import { pageCapacities, unbindCapacity } from '@/api/capacity/self_capacity/list';
  import type { Capacity, CapacityParam } from '@/api/capacity/self_capacity/list/model';
  import { formatDateTime } from '@/utils/date-util';

  defineOptions({ name: 'CapacityList' });

  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);
  const bindVisible = ref(false);

  const where = reactive<Pick<CapacityParam, 'keyword'>>({
    keyword: ''
  });

  const onSearch = (payload: Pick<CapacityParam, 'keyword'>) => {
    where.keyword = payload.keyword ?? '';
    tableRef.value?.reload?.({ page: 1 });
  };

  const columns = ref<Columns>([
    { prop: 'driverName', label: '司机姓名', minWidth: 100 },
    { prop: 'driverPhone', label: '手机号', minWidth: 130 },
    { prop: 'plateNumber', label: '车牌号', minWidth: 120 },
    {
      prop: 'boundAt',
      label: '绑定时间',
      minWidth: 170,
      align: 'center',
      formatter: (row) => formatDateTime(row.boundAt)
    },
    {
      columnKey: 'action',
      label: '操作',
      width: 100,
      align: 'center',
      slot: 'action',
      hideInPrint: true,
      hideInExport: true,
      fixed: 'right'
    }
  ]);

  const datasource: DatasourceFunction = async ({ page, limit, pages }) => {
    const p = page ?? (Number(pages?.page) || 1);
    const l = limit ?? (Number(pages?.limit) || 10);
    const res = await pageCapacities({ ...where, page: p, limit: l });
    const raw = res as { list?: Capacity[]; count?: number; total?: number };
    return {
      list: raw?.list ?? [],
      count: raw?.count ?? raw?.total ?? 0
    };
  };

  const reload = () => {
    tableRef.value?.reload?.();
  };

  const openBind = () => {
    bindVisible.value = true;
  };

  const handleUnbind = (row: Capacity) => {
    ElMessageBox.confirm(
      `确定将司机「${row.driverName}」与车辆「${row.plateNumber}」解绑（下车）吗？解绑后可在「变动记录」中查看历史。`,
      '系统提示',
      { type: 'warning', draggable: true }
    )
      .then(() => {
        const loading = EleMessage.loading({
          message: '请求中..',
          plain: true
        });
        unbindCapacity(row.id!)
          .then((msg) => {
            loading.close();
            EleMessage.success({ message: msg, plain: true });
            reload();
          })
          .catch((e) => {
            loading.close();
            EleMessage.error({ message: e.message, plain: true });
          });
      })
      .catch(() => {});
  };
</script>
