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
        <template #plateNumber="{ row }">
          <plate-number-tag
            :text="row.plateNumber"
            :category="row.plateCategory"
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
          <plate-number-tag
            v-if="row.trailerPlateNumber"
            :text="row.trailerPlateNumber"
            :category="row.trailerPlateCategory"
          />
          <span v-else style="color: #999">—</span>
        </template>
        <template #status="{ row }">
          <el-tag
            v-if="row.status === 1"
            type="success"
            size="small"
            :disable-transitions="true"
          >
            正常
          </el-tag>
          <el-tag
            v-else-if="row.status === 0"
            type="info"
            size="small"
            :disable-transitions="true"
          >
            停用
          </el-tag>
          <el-tag
            v-else-if="row.status === 2"
            type="warning"
            size="small"
            :disable-transitions="true"
          >
            维修/保养
          </el-tag>
          <el-tag
            v-else-if="row.status === 3"
            type="warning"
            size="small"
            :disable-transitions="true"
          >
            保险续期
          </el-tag>
          <el-tag
            v-else-if="row.status === 9"
            type="danger"
            size="small"
            :disable-transitions="true"
          >
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
  import PlateNumberTag from '@/components/PlateNumberTag/index.vue';
  import { pageVehicles, removeVehicle } from '@/api/capacity/self_capacity/vehicle';
  import type { Vehicle, VehicleParam } from '@/api/capacity/self_capacity/vehicle/model';
  import { DICT_CODE_VEHICLE_TYPE } from '@/constants/dict-codes';
  import { formatDateTime } from '@/utils/date-util';

  defineOptions({ name: 'ResourceVehicle' });

  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);
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
    {
      prop: 'plateNumber',
      label: '车牌号',
      minWidth: 140,
      slot: 'plateNumber',
      align: 'center'
    },
    {
      prop: 'vehicleType',
      label: '车辆类型',
      minWidth: 100,
      slot: 'vehicleType',
      align: 'center'
    },
    { prop: 'brand', label: '品牌', minWidth: 80, align: 'center' },
    { prop: 'model', label: '型号', minWidth: 110, align: 'center' },
    {
      prop: 'trailerPlateNumber',
      label: '关联挂车',
      minWidth: 140,
      slot: 'trailerPlateNumber',
      align: 'center'
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
      prop: 'createdAt',
      label: '创建时间',
      minWidth: 170,
      align: 'center',
      formatter: (row) => formatDateTime(row.createdAt)
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

  const datasource: DatasourceFunction = async ({
    page,
    limit,
    pages
  }) => {
    const p = page ?? (Number(pages?.page) || 1);
    const l = limit ?? (Number(pages?.limit) || 10);
    const res = await pageVehicles({ ...where, page: p, limit: l });
    const raw = res as { list?: Vehicle[]; count?: number; total?: number };
    return {
      list: raw?.list ?? [],
      count: raw?.count ?? raw?.total ?? 0
    };
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
