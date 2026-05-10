<template>
  <ele-page>
    <trailer-search @search="onSearch" />
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
          <btn-items
            :items="[
              { preset: 'add', title: '新增挂车', onClick: () => openEdit() }
            ]"
          />
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
  import TrailerSearch from './components/trailer-search.vue';
  import { pageTrailers, removeTrailer } from '@/api/capacity/self_capacity/trailer';
  import type { Trailer, TrailerParam } from '@/api/capacity/self_capacity/trailer/model';

  defineOptions({ name: 'ResourceTrailer' });

  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);
  const selections = ref<Trailer[]>([]);
  const editVisible = ref(false);
  const editData = ref<Trailer | null>(null);
  const where = reactive<Pick<TrailerParam, 'keyword' | 'status'>>({
    keyword: '',
    status: void 0
  });

  const onSearch = (payload: Pick<TrailerParam, 'keyword' | 'status'>) => {
    where.keyword = payload.keyword ?? '';
    where.status = payload.status;
    tableRef.value?.reload?.({ page: 1 });
  };

  const columns = ref<Columns>([
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
    const res = await pageTrailers({ ...where, page: p, limit: l });
    const raw = res as { list?: Trailer[]; count?: number; total?: number };
    return {
      list: raw?.list ?? [],
      count: raw?.count ?? raw?.total ?? 0
    };
  };

  const reload = () => {
    tableRef.value?.reload?.();
  };

  const openEdit = (row?: Trailer) => {
    editData.value = row ?? null;
    editVisible.value = true;
  };

  const remove = (row: Trailer) => {
    ElMessageBox.confirm(`确定要删除挂车"${row.plateNumber}"吗?`, '系统提示', {
      type: 'warning',
      draggable: true
    })
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
