<template>
  <ele-page>
    <ele-card :body-style="{ paddingTop: '8px' }">
      <ele-pro-table
        ref="tableRef"
        row-key="id"
        :columns="columns"
        :datasource="datasource"
        :show-overflow-tooltip="true"
        v-model:selections="selections"
        :highlight-current-row="true"
        cache-key="BusinessOrderTable"
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
            <el-form-item>
              <el-select
                v-model="where.status"
                placeholder="订单状态"
                clearable
                @change="reload"
              >
                <el-option label="待派车" :value="0" />
                <el-option label="已派车" :value="1" />
                <el-option label="运输中" :value="2" />
                <el-option label="已到达" :value="3" />
                <el-option label="已签收" :value="4" />
                <el-option label="已完成" :value="5" />
                <el-option label="已取消" :value="6" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="openEdit()">
                新增订单
              </el-button>
            </el-form-item>
          </el-form>
        </template>
        <template #route="{ row }">
          {{ row.origin }} → {{ row.destination }}
        </template>
        <template #status="{ row }">
          <el-tag v-if="row.status === 0" type="info" size="small">
            待派车
          </el-tag>
          <el-tag v-else-if="row.status === 1" type="primary" size="small">
            已派车
          </el-tag>
          <el-tag v-else-if="row.status === 2" type="warning" size="small">
            运输中
          </el-tag>
          <el-tag v-else-if="row.status === 3" type="success" size="small">
            已到达
          </el-tag>
          <el-tag v-else-if="row.status === 4" type="success" size="small">
            已签收
          </el-tag>
          <el-tag v-else-if="row.status === 5" type="success" size="small">
            已完成
          </el-tag>
          <el-tag v-else-if="row.status === 6" type="danger" size="small">
            已取消
          </el-tag>
        </template>
        <template #action="{ row }">
          <el-link type="primary" :underline="false" @click="openEdit(row)">
            编辑
          </el-link>
          <el-divider direction="vertical" />
          <el-link type="danger" :underline="false" @click="remove(row)">
            删除
          </el-link>
        </template>
      </ele-pro-table>
    </ele-card>
    <order-edit v-model:visible="editVisible" :data="editData" @done="reload" />
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
  import OrderEdit from './components/order-edit.vue';
  import { pageOrders, removeOrder } from '@/api/business/order';
  import type { Order } from '@/api/business/order/model';

  defineOptions({ name: 'BusinessOrder' });

  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);
  const selections = ref<Order[]>([]);
  const editVisible = ref(false);
  const editData = ref<Order | null>(null);
  const where = reactive({
    keyword: '',
    status: undefined as number | undefined
  });

  const columns = ref<Columns>([
    {
      type: 'selection',
      columnKey: 'selection',
      width: 50,
      align: 'center'
    },
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
    { prop: 'freightAmount', label: '运费(元)', minWidth: 100, align: 'right' },
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
      width: 130,
      align: 'center',
      slot: 'action'
    }
  ]);

  const datasource: DatasourceFunction = async ({ page, limit }) => {
    const res = await pageOrders({ ...where, page, limit });
    return { list: res?.list ?? [], count: res?.count ?? 0 };
  };

  const reload = () => {
    tableRef.value?.reload?.();
  };

  const openEdit = (row?: Order) => {
    editData.value = row ?? null;
    editVisible.value = true;
  };

  const remove = (row: Order) => {
    ElMessageBox.confirm(`确定要删除订单"${row.orderNo}"吗?`, '系统提示', {
      type: 'warning',
      draggable: true
    })
      .then(() => {
        const loading = EleMessage.loading({
          message: '请求中..',
          plain: true
        });
        removeOrder(row.id!)
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
