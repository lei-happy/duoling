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
        cache-key="WaybillTable"
      >
        <template #toolbar>
          <el-form :model="where" class="ele-bg-wrap" inline>
            <el-form-item>
              <el-input
                v-model="where.keyword"
                placeholder="运单编号/客户名称"
                clearable
                @change="reload"
              />
            </el-form-item>
            <el-form-item>
              <el-select
                v-model="where.customerId"
                placeholder="客户筛选"
                filterable
                clearable
                @change="reload"
              >
                <el-option
                  v-for="item in customerOptions"
                  :key="item.id"
                  :label="item.customerName"
                  :value="item.id"
                />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-select
                v-model="where.status"
                placeholder="运单状态"
                clearable
                @change="reload"
              >
                <el-option label="待确认" :value="0" />
                <el-option label="已确认" :value="1" />
                <el-option label="已调度" :value="2" />
                <el-option label="运输中" :value="3" />
                <el-option label="已送达" :value="4" />
                <el-option label="已完成" :value="5" />
                <el-option label="已取消" :value="6" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-select
                v-model="where.freightSource"
                placeholder="运费来源"
                clearable
                @change="reload"
              >
                <el-option label="自动计算" :value="0" />
                <el-option label="手动填写" :value="1" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="openEdit()">
                新增运单
              </el-button>
            </el-form-item>
          </el-form>
        </template>
        <template #route="{ row }">
          {{ row.origin }} → {{ row.destination }}
        </template>
        <template #vehicleInfo="{ row }">
          <span v-if="row.vehicleBrand || row.vehicleModel">
            {{ row.vehicleBrand }}{{ row.vehicleModel ? '/' + row.vehicleModel : '' }}
          </span>
          <span v-else>-</span>
        </template>
        <template #freightSource="{ row }">
          <el-tag v-if="row.freightSource === 0" type="success" size="small">
            自动计算
          </el-tag>
          <el-tag v-else-if="row.freightSource === 1" size="small">
            手动填写
          </el-tag>
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
          <el-link
            v-if="row.status === 0 || row.status === 1"
            type="primary"
            :underline="false"
            @click="openEdit(row)"
          >
            编辑
          </el-link>
          <el-divider
            v-if="row.status === 0"
            direction="vertical"
          />
          <el-link
            v-if="row.status === 0 || row.status === 6"
            type="danger"
            :underline="false"
            @click="remove(row)"
          >
            删除
          </el-link>
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
  import { ref, reactive, onMounted } from 'vue';
  import { ElMessageBox } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import type { EleProTable } from 'ele-admin-plus';
  import type {
    DatasourceFunction,
    Columns
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import WaybillEdit from './components/waybill-edit.vue';
  import { pageWaybills, removeWaybill } from '@/api/waybill';
  import { selectCustomers } from '@/api/partner/customer';
  import type { Waybill } from '@/api/waybill/model';
  import type { CustomerSelectItem } from '@/api/partner/customer/model';

  defineOptions({ name: 'Waybill' });

  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);
  const selections = ref<Waybill[]>([]);
  const editVisible = ref(false);
  const editData = ref<Waybill | null>(null);
  const customerOptions = ref<CustomerSelectItem[]>([]);
  const where = reactive({
    keyword: '',
    customerId: undefined as number | undefined,
    status: undefined as number | undefined,
    freightSource: undefined as number | undefined
  });

  const columns = ref<Columns>([
    {
      type: 'selection',
      columnKey: 'selection',
      width: 50,
      align: 'center'
    },
    { type: 'index', columnKey: 'index', width: 50, align: 'center' },
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
      prop: 'freightSource',
      label: '运费来源',
      width: 100,
      align: 'center',
      slot: 'freightSource'
    },
    { prop: 'dealerName', label: '收车门店', minWidth: 120 },
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
    const res = await pageWaybills({ ...where, page, limit });
    return { list: res?.list ?? [], count: res?.count ?? 0 };
  };

  const reload = () => {
    tableRef.value?.reload?.();
  };

  const openEdit = (row?: Waybill) => {
    editData.value = row ?? null;
    editVisible.value = true;
  };

  const remove = (row: Waybill) => {
    ElMessageBox.confirm(
      `确定要删除运单"${row.waybillNo}"吗?`,
      '系统提示',
      { type: 'warning', draggable: true }
    )
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

  onMounted(async () => {
    try {
      customerOptions.value = (await selectCustomers()) ?? [];
    } catch (_) {
      customerOptions.value = [];
    }
  });
</script>
