<template>
  <ele-page>
    <vehicle-search @search="onSearch" />
    <ele-card :body-style="{ paddingTop: '8px' }">
      <ele-pro-table
        ref="tableRef"
        row-key="id"
        :columns="columns"
        :datasource="datasource"
        :show-overflow-tooltip="true"
        v-model:selections="selections"
        :highlight-current-row="true"
        cache-key="ResourceVehicleTable"
      >
        <template #toolbar>
          <btn-items
            :items="[
              { preset: 'add', title: '新增车辆', onClick: () => openEdit() }
            ]"
          />
        </template>
        <template #vehicleType="{ row }">
          <dict-data
            type="text"
            :code="dictCodeVehicleType"
            :model-value="row.vehicleType"
          />
        </template>
        <template #trailerPlateNumber="{ row }">
          <span v-if="row.trailerPlateNumber">{{
            row.trailerPlateNumber
          }}</span>
          <span v-else style="color: #999">—</span>
        </template>
        <template #status="{ row }">
          <el-tag v-if="row.status === 1" type="success" size="small">
            正常
          </el-tag>
          <el-tag v-else-if="row.status === 0" type="info" size="small">
            停用
          </el-tag>
          <el-tag v-else-if="row.status === 2" type="warning" size="small">
            维修/保养
          </el-tag>
          <el-tag v-else-if="row.status === 3" type="warning" size="small">
            保险续期
          </el-tag>
          <el-tag v-else-if="row.status === 9" type="danger" size="small">
            已报废
          </el-tag>
        </template>
        <template #action="{ row }">
          <btn-items
            divider
            type="link"
            :items="[
              { preset: 'edit', onClick: () => openEdit(row) },
              { preset: 'del', onClick: () => remove(row) }
            ]"
          />
        </template>
      </ele-pro-table>
    </ele-card>
    <vehicle-edit
      v-model:visible="editVisible"
      :data="editData"
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
  import VehicleEdit from './components/vehicle-edit.vue';
  import VehicleSearch from './components/vehicle-search.vue';
  import DictData from '@/components/DictData/index.vue';
  import { pageVehicles, removeVehicle } from '@/api/capacity/self_capacity/vehicle';
  import type { Vehicle, VehicleParam } from '@/api/capacity/self_capacity/vehicle/model';
  import { DICT_CODE_VEHICLE_TYPE } from '@/constants/dict-codes';

  defineOptions({ name: 'ResourceVehicle' });

  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);
  const selections = ref<Vehicle[]>([]);
  const editVisible = ref(false);
  const editData = ref<Vehicle | null>(null);
  const dictCodeVehicleType = DICT_CODE_VEHICLE_TYPE;

  const where = reactive<
    Pick<VehicleParam, 'keyword' | 'status' | 'vehicleType'>
  >({
    keyword: '',
    status: void 0,
    vehicleType: void 0
  });

  const onSearch = (
    payload: Pick<VehicleParam, 'keyword' | 'status' | 'vehicleType'>
  ) => {
    where.keyword = payload.keyword ?? '';
    where.status = payload.status;
    where.vehicleType = payload.vehicleType;
    tableRef.value?.reload?.({ page: 1 });
  };

  const columns = ref<Columns>([
    { prop: 'plateNumber', label: '车牌号', minWidth: 120 },
    {
      prop: 'vehicleType',
      label: '车辆类型',
      minWidth: 100,
      slot: 'vehicleType'
    },
    { prop: 'brand', label: '品牌', minWidth: 80 },
    { prop: 'model', label: '型号', minWidth: 80 },
    {
      prop: 'loadCapacity',
      label: '载重(吨)',
      minWidth: 90,
      align: 'center'
    },
    {
      prop: 'trailerPlateNumber',
      label: '关联挂车',
      minWidth: 120,
      slot: 'trailerPlateNumber'
    },
    {
      prop: 'insuranceExpire',
      label: '保险到期',
      minWidth: 110,
      align: 'center'
    },
    {
      prop: 'inspectionExpire',
      label: '年检到期',
      minWidth: 110,
      align: 'center'
    },
    {
      prop: 'status',
      label: '状态',
      width: 100,
      align: 'center',
      slot: 'status'
    },
    {
      columnKey: 'action',
      label: '操作',
      width: 160,
      align: 'center',
      slot: 'action',
      hideInPrint: true,
      hideInExport: true,
      fixed: 'right'
    }
  ]);

  const datasource: DatasourceFunction = async ({ page, limit }) => {
    const res = await pageVehicles({ ...where, page, limit });
    return { list: res?.list ?? [], count: res?.count ?? 0 };
  };

  const reload = () => {
    tableRef.value?.reload?.();
  };

  const openEdit = (row?: Vehicle) => {
    editData.value = row ?? null;
    editVisible.value = true;
  };

  const remove = (row: Vehicle) => {
    ElMessageBox.confirm(`确定要删除车辆"${row.plateNumber}"吗?`, '系统提示', {
      type: 'warning',
      draggable: true
    })
      .then(() => {
        const loading = EleMessage.loading({
          message: '请求中..',
          plain: true
        });
        removeVehicle(row.id!)
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
