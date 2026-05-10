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
        cache-key="CapacityListTable"
      >
        <template #toolbar>
          <btn-items
            :items="[
              { preset: 'add', title: '上车', onClick: () => openBind() }
            ]"
          />
        </template>
        <template #status="{ row }">
          <el-tag v-if="row.status === 1" type="success" size="small">
            绑定中
          </el-tag>
          <el-tag v-else-if="row.status === 0" type="info" size="small">
            已解绑
          </el-tag>
        </template>
        <template #action="{ row }">
          <btn-items
            divider
            type="link"
            :items="
              row.status === 1
                ? [{ title: '下车', type: 'danger', onClick: () => handleUnbind(row) }]
                : []
            "
          />
        </template>
      </ele-pro-table>
    </ele-card>
    <capacity-bind
      v-model:visible="bindVisible"
      @done="reload"
    />
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

  defineOptions({ name: 'CapacityList' });

  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);
  const bindVisible = ref(false);

  const where = reactive<Pick<CapacityParam, 'keyword' | 'status'>>({
    keyword: '',
    status: void 0
  });

  const onSearch = (payload: Pick<CapacityParam, 'keyword' | 'status'>) => {
    where.keyword = payload.keyword ?? '';
    where.status = payload.status;
    tableRef.value?.reload?.({ page: 1 });
  };

  const columns = ref<Columns>([
    { prop: 'driverName', label: '司机姓名', minWidth: 100 },
    { prop: 'driverPhone', label: '手机号', minWidth: 130 },
    { prop: 'plateNumber', label: '车牌号', minWidth: 120 },
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
      prop: 'unboundAt',
      label: '解绑时间',
      minWidth: 170,
      align: 'center'
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

  const datasource: DatasourceFunction = async ({ page, limit }) => {
    const res = await pageCapacities({ ...where, page, limit });
    return { list: res?.list ?? [], count: res?.count ?? res?.total ?? 0 };
  };

  const reload = () => {
    tableRef.value?.reload?.();
  };

  const openBind = () => {
    bindVisible.value = true;
  };

  const handleUnbind = (row: Capacity) => {
    ElMessageBox.confirm(
      `确定要将司机「${row.driverName}」从车辆「${row.plateNumber}」下车吗？`,
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
