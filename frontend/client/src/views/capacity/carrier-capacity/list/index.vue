<template>
  <ele-page>
    <ele-card :body-style="{ paddingBottom: 0 }">
      <el-form :inline="true" @submit.prevent>
        <el-form-item label="关键字">
          <el-input
            v-model="where.keyword"
            placeholder="承运商/司机/车牌"
            clearable
            style="width: 200px"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-select
            v-model="where.status"
            placeholder="全部"
            clearable
            style="width: 130px"
          >
            <el-option label="正常" :value="1" />
            <el-option label="停用" :value="2" />
            <el-option label="黑名单" :value="3" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="reload">查询</el-button>
        </el-form-item>
      </el-form>
    </ele-card>

    <ele-card :body-style="{ paddingTop: '8px' }">
      <ele-pro-table
        ref="tableRef"
        row-key="id"
        :columns="columns"
        :datasource="datasource"
        :show-overflow-tooltip="true"
        cache-key="CarrierCapacityTable"
      >
        <template #toolbar>
          <el-button type="primary" @click="openEdit(null)">
            新增承运商运力
          </el-button>
        </template>
        <template #status="{ row }">
          <el-tag v-if="row.status === 1" type="success" size="small">
            正常
          </el-tag>
          <el-tag v-else-if="row.status === 2" type="info" size="small">
            停用
          </el-tag>
          <el-tag v-else type="danger" size="small">黑名单</el-tag>
        </template>
        <template #action="{ row }">
          <el-button type="primary" link @click="openEdit(row.id)">
            编辑
          </el-button>
          <el-button type="danger" link @click="onDelete(row)">删除</el-button>
        </template>
      </ele-pro-table>
    </ele-card>

    <carrier-capacity-edit
      v-model:visible="editVisible"
      :edit-id="editId"
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
  import { formatDate } from '@/utils/date-util';
  import CarrierCapacityEdit from './components/carrier-capacity-edit.vue';
  import {
    pageCarrierCapacities,
    removeCarrierCapacity
  } from '@/api/capacity/carrier-capacity';
  import type { CarrierCapacityParam } from '@/api/capacity/carrier-capacity/model';

  defineOptions({ name: 'CapacityCarrierCapacityList' });

  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);
  const editVisible = ref(false);
  const editId = ref<number | null>(null);

  const where = reactive<Pick<CarrierCapacityParam, 'keyword' | 'status'>>({
    keyword: '',
    status: undefined
  });

  const columns = ref<Columns>([
    { prop: 'carrierCapacityCode', label: '编号', width: 130 },
    { prop: 'carrierName', label: '承运商', minWidth: 140 },
    { prop: 'driverName', label: '司机', minWidth: 90 },
    { prop: 'driverPhone', label: '手机号', minWidth: 120 },
    { prop: 'plateNumber', label: '车牌号', minWidth: 110 },
    {
      prop: 'vehicleTypeLabel',
      label: '车型',
      minWidth: 100,
      formatter: (row) => row.vehicleTypeLabel ?? '-'
    },
    { prop: 'status', label: '状态', width: 90, align: 'center', slot: 'status' },
    {
      prop: 'createdAt',
      label: '建档时间',
      width: 120,
      align: 'center',
      formatter: (row) => formatDate(row.createdAt)
    },
    {
      prop: 'action',
      label: '操作',
      width: 130,
      align: 'center',
      slot: 'action'
    }
  ]);

  const datasource: DatasourceFunction = async ({ page, limit }) => {
    const res = await pageCarrierCapacities({ ...where, page, limit });
    return { list: res?.list ?? [], count: res?.count ?? res?.total ?? 0 };
  };

  const reload = () => {
    tableRef.value?.reload?.({ page: 1 });
  };

  const openEdit = (id: number | null) => {
    editId.value = id;
    editVisible.value = true;
  };

  const onDelete = (row: any) => {
    ElMessageBox.confirm(
      `确定删除「${row.carrierName} - ${row.plateNumber}」的运力档案吗？`,
      '系统提示',
      { type: 'warning', confirmButtonText: '确定', cancelButtonText: '取消' }
    )
      .then(async () => {
        const loading = EleMessage.loading({
          message: '请稍后..',
          plain: true
        });
        try {
          await removeCarrierCapacity(row.id);
          loading.close();
          EleMessage.success({ message: '删除成功', plain: true });
          reload();
        } catch (e: any) {
          loading.close();
          EleMessage.error({ message: e.message, plain: true });
        }
      })
      .catch(() => void 0);
  };
</script>
