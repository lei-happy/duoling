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
        cache-key="ResourceTrailerTable"
      >
        <template #toolbar>
          <el-form :model="where" class="ele-bg-wrap" inline>
            <el-form-item>
              <el-input
                v-model="where.keyword"
                placeholder="挂车车牌号"
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
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="openEdit()">
                新增挂车
              </el-button>
            </el-form-item>
          </el-form>
        </template>
        <template #vehiclePlateNumber="{ row }">
          <span v-if="row.vehiclePlateNumber">
            {{ row.vehiclePlateNumber }}
          </span>
          <span v-else style="color: #999">—</span>
        </template>
        <template #status="{ row }">
          <el-tag v-if="row.status === 1" type="success" size="small">
            正常
          </el-tag>
          <el-tag v-else type="info" size="small">停用</el-tag>
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
    <trailer-edit
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
  import TrailerEdit from './components/trailer-edit.vue';
  import { pageTrailers, removeTrailer } from '@/api/resource/trailer';
  import type { Trailer } from '@/api/resource/trailer/model';

  defineOptions({ name: 'ResourceTrailer' });

  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);
  const selections = ref<Trailer[]>([]);
  const editVisible = ref(false);
  const editData = ref<Trailer | null>(null);
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
    { prop: 'plateNumber', label: '挂车车牌号', minWidth: 130 },
    { prop: 'trailerType', label: '挂车类型', minWidth: 110 },
    {
      prop: 'loadCapacity',
      label: '载重(吨)',
      minWidth: 90,
      align: 'center'
    },
    {
      prop: 'volumeCapacity',
      label: '容积(m³)',
      minWidth: 90,
      align: 'center'
    },
    {
      prop: 'parkingSpots',
      label: '车位数',
      minWidth: 80,
      align: 'center'
    },
    {
      prop: 'vehiclePlateNumber',
      label: '关联车辆',
      minWidth: 120,
      slot: 'vehiclePlateNumber'
    },
    {
      prop: 'status',
      label: '状态',
      width: 80,
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
    const res = await pageTrailers({ ...where, page, limit });
    return { list: res?.list ?? [], count: res?.total ?? 0 };
  };

  const reload = () => {
    tableRef.value?.reload?.();
  };

  const openEdit = (row?: Trailer) => {
    editData.value = row ?? null;
    editVisible.value = true;
  };

  const remove = (row: Trailer) => {
    ElMessageBox.confirm(
      `确定要删除挂车"${row.plateNumber}"吗?`,
      '系统提示',
      { type: 'warning', draggable: true }
    )
      .then(() => {
        const loading = EleMessage.loading({
          message: '请求中..',
          plain: true
        });
        removeTrailer(row.id!)
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
