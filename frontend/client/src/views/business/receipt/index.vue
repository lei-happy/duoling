<template>
  <ele-page>
    <ele-card :body-style="{ paddingTop: '8px' }">
      <ele-pro-table
        ref="tableRef"
        row-key="id"
        :columns="columns"
        :datasource="datasource"
        :show-overflow-tooltip="true"
        :highlight-current-row="true"
        cache-key="BusinessReceiptTable"
      >
        <template #toolbar>
          <el-form :model="where" class="ele-bg-wrap" inline>
            <el-form-item>
              <el-input
                v-model="where.keyword"
                placeholder="订单号/客户名称"
                clearable
                @change="reload"
              />
            </el-form-item>
          </el-form>
        </template>
        <template #route="{ row }">
          {{ row.origin }} → {{ row.destination }}
        </template>
        <template #status="{ row }">
          <el-tag v-if="row.status === 3" type="success" size="small">
            已到达
          </el-tag>
          <el-tag v-else-if="row.status === 4" type="success" size="small">
            已签收
          </el-tag>
        </template>
        <template #action="{ row }">
          <el-link
            v-if="row.status === 3"
            type="primary"
            :underline="false"
            @click="handleReceipt(row)"
          >
            确认签收
          </el-link>
          <span v-else>-</span>
        </template>
      </ele-pro-table>
    </ele-card>
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
  import {
    pageReceiptOrders,
    updateOrderStatus
  } from '@/api/business/order';
  import type { Order } from '@/api/business/order/model';

  defineOptions({ name: 'BusinessReceipt' });

  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);
  const where = reactive({
    keyword: ''
  });

  const columns = ref<Columns>([
    { type: 'index', columnKey: 'index', width: 50, align: 'center' },
    { prop: 'orderNo', label: '订单号', minWidth: 160 },
    { prop: 'customerName', label: '客户名称', minWidth: 140 },
    {
      columnKey: 'route',
      label: '路线',
      minWidth: 200,
      slot: 'route'
    },
    { prop: 'plateNumber', label: '车牌号', minWidth: 110 },
    { prop: 'driverName', label: '司机', minWidth: 100 },
    { prop: 'cargoName', label: '货物名称', minWidth: 120 },
    { prop: 'actualDepartTime', label: '实际发车', minWidth: 160 },
    { prop: 'actualArriveTime', label: '实际到达', minWidth: 160 },
    {
      prop: 'status',
      label: '状态',
      width: 90,
      align: 'center',
      slot: 'status'
    },
    {
      columnKey: 'action',
      label: '操作',
      width: 100,
      align: 'center',
      slot: 'action'
    }
  ]);

  const datasource: DatasourceFunction = async ({ page, limit }) => {
    const res = await pageReceiptOrders({ ...where, page, limit });
    return { list: res?.list ?? [], count: res?.count ?? 0 };
  };

  const reload = () => {
    tableRef.value?.reload?.();
  };

  const handleReceipt = (row: Order) => {
    ElMessageBox.confirm(
      `确定订单"${row.orderNo}"已签收吗?`,
      '系统提示',
      { type: 'warning', draggable: true }
    )
      .then(() => {
        const loading = EleMessage.loading({
          message: '请求中..',
          plain: true
        });
        updateOrderStatus(row.id!, { status: 4 })
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
