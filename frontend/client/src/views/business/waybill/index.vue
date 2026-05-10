<template>
  <ele-page>
    <waybill-search @search="(w) => reload(w, 1)" />
    <ele-card :body-style="{ paddingTop: '8px' }">
      <ele-pro-table
        ref="tableRef"
        row-key="id"
        :columns="columns"
        :datasource="datasource"
        :show-overflow-tooltip="true"
        :highlight-current-row="true"
        cache-key="WaybillTable"
      >
        <template #toolbar>
          <btn-items
            :items="[
              { preset: 'add', title: '新增运单', onClick: () => openEdit() }
            ]"
          />
        </template>
        <template #route="{ row }">
          {{ row.origin }} → {{ row.destination }}
        </template>
        <template #vehicleInfo="{ row }">
          <span v-if="row.cargoSummary">{{ row.cargoSummary }}</span>
          <span v-else-if="row.vehicleBrand || row.vehicleModel">
            {{ row.vehicleBrand
            }}{{ row.vehicleModel ? '/' + row.vehicleModel : '' }}
          </span>
          <span v-else>-</span>
        </template>
        <template #status="{ row }">
          <el-tag v-if="row.status === 0" type="info" size="small">
            待确认
          </el-tag>
          <el-tag v-else-if="row.status === 1" type="primary" size="small">
            已确认
          </el-tag>
          <el-tag v-else-if="row.status === 2" type="warning" size="small">
            已调度
          </el-tag>
          <el-tag v-else-if="row.status === 3" type="warning" size="small">
            运输中
          </el-tag>
          <el-tag v-else-if="row.status === 4" type="success" size="small">
            已送达
          </el-tag>
          <el-tag v-else-if="row.status === 5" type="success" size="small">
            已完成
          </el-tag>
          <el-tag v-else-if="row.status === 6" type="danger" size="small">
            已取消
          </el-tag>
        </template>
        <template #action="{ row }">
          <btn-items divider type="link" :items="actionItems(row)" />
        </template>
      </ele-pro-table>
    </ele-card>
    <waybill-edit
      v-model:visible="editVisible"
      :data="editData"
      @done="reload"
    />
  </ele-page>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import { ElMessageBox } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import type { EleProTable } from 'ele-admin-plus';
  import type {
    DatasourceFunction,
    Columns
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import WaybillEdit from './components/waybill-edit.vue';
  import WaybillSearch from './components/waybill-search.vue';
  import { pageWaybills, removeWaybill, updateWaybillStatus } from '@/api/waybill';
  import type { Waybill, WaybillParam } from '@/api/waybill/model';
  import { formatDateTime } from '@/utils/date-util';

  defineOptions({ name: 'Waybill' });

  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);
  const editVisible = ref(false);
  const editData = ref<Waybill | null>(null);

  const columns = ref<Columns>([
    { prop: 'waybillNo', label: '运单编号', minWidth: 140 },
    { prop: 'customerName', label: '客户名称', minWidth: 120 },
    {
      columnKey: 'route',
      label: '出发地→目的地',
      minWidth: 180,
      slot: 'route'
    },
    {
      columnKey: 'vehicleInfo',
      label: '品牌/车型',
      minWidth: 120,
      slot: 'vehicleInfo'
    },
    { prop: 'quantity', label: '台数', width: 70, align: 'center' },
    {
      prop: 'freightAmount',
      label: '运费金额',
      minWidth: 100,
      align: 'right'
    },
    {
      prop: 'status',
      label: '状态',
      width: 90,
      align: 'center',
      slot: 'status'
    },
    {
      prop: 'createdAt',
      label: '创建时间',
      width: 170,
      align: 'center',
      formatter: (row) => formatDateTime(row.createdAt)
    },
    {
      columnKey: 'action',
      label: '操作',
      width: 200,
      align: 'center',
      slot: 'action',
      fixed: 'right',
      hideInPrint: true,
      hideInExport: true
    }
  ]);

  const datasource: DatasourceFunction = ({ pages, where }) => {
    return pageWaybills({
      ...(where as WaybillParam | undefined),
      ...pages
    }).then((res) => ({
      list: res?.list ?? [],
      count: res?.count ?? 0
    }));
  };

  const reload = (where?: WaybillParam, page?: number) => {
    tableRef.value?.reload?.({ where, page });
  };

  const actionItems = (row: Waybill) => {
    const items: Array<{ preset?: string; title?: string; onClick: () => void }> = [];
    if (row.status === 0) {
      items.push({ title: '确认', onClick: () => confirmWaybill(row) });
    }
    if (row.status === 0 || row.status === 1) {
      items.push({ preset: 'edit', onClick: () => openEdit(row) });
    }
    if (row.status === 0 || row.status === 6) {
      items.push({ preset: 'del', onClick: () => remove(row) });
    }
    return items;
  };

  const confirmWaybill = (row: Waybill) => {
    ElMessageBox.confirm(
      `确认运单「${row.waybillNo}」？确认后将变为「已确认」状态。`,
      '系统提示',
      { type: 'warning', draggable: true }
    )
      .then(() => {
        const loading = EleMessage.loading({
          message: '请求中..',
          plain: true
        });
        updateWaybillStatus(row.id!, 1)
          .then((msg) => {
            loading.close();
            EleMessage.success({ message: msg, plain: true });
            reload();
          })
          .catch((e: Error) => {
            loading.close();
            EleMessage.error({ message: e.message, plain: true });
          });
      })
      .catch(() => {});
  };

  const openEdit = (row?: Waybill) => {
    editData.value = row ?? null;
    editVisible.value = true;
  };

  const remove = (row: Waybill) => {
    ElMessageBox.confirm(`确定要删除运单"${row.waybillNo}"吗?`, '系统提示', {
      type: 'warning',
      draggable: true
    })
      .then(() => {
        const loading = EleMessage.loading({
          message: '请求中..',
          plain: true
        });
        removeWaybill(row.id!)
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
