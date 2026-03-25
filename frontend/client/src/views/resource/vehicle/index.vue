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
        cache-key="ResourceVehicleTable"
      >
        <template #toolbar>
          <el-form :model="where" class="ele-bg-wrap" inline>
            <el-form-item>
              <el-input
                v-model="where.keyword"
                placeholder="车牌号/品牌/型号"
                clearable
                @change="reload"
              />
            </el-form-item>
            <el-form-item>
              <el-select
                v-model="where.status"
                placeholder="状态"
                clearable
                @change="reload"
              >
                <el-option label="正常" :value="1" />
                <el-option label="停用" :value="0" />
                <el-option label="维修中" :value="2" />
                <el-option label="已报废" :value="3" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="openEdit()">
                新增车辆
              </el-button>
            </el-form-item>
          </el-form>
        </template>
        <template #status="{ row }">
          <el-tag v-if="row.status === 1" type="success" size="small">
            正常
          </el-tag>
          <el-tag v-else-if="row.status === 0" type="info" size="small">
            停用
          </el-tag>
          <el-tag v-else-if="row.status === 2" type="warning" size="small">
            维修中
          </el-tag>
          <el-tag v-else-if="row.status === 3" type="danger" size="small">
            已报废
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
  import { pageVehicles, removeVehicle } from '@/api/resource/vehicle';
  import type { Vehicle } from '@/api/resource/vehicle/model';

  defineOptions({ name: 'ResourceVehicle' });

  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);
  const selections = ref<Vehicle[]>([]);
  const editVisible = ref(false);
  const editData = ref<Vehicle | null>(null);
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
    { prop: 'plateNumber', label: '车牌号', minWidth: 120 },
    { prop: 'vehicleType', label: '车辆类型', minWidth: 100 },
    { prop: 'brand', label: '品牌', minWidth: 80 },
    { prop: 'model', label: '型号', minWidth: 80 },
    {
      prop: 'loadCapacity',
      label: '载重(吨)',
      minWidth: 90,
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
    ElMessageBox.confirm(
      `确定要删除车辆"${row.plateNumber}"吗?`,
      '系统提示',
      { type: 'warning', draggable: true }
    )
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
