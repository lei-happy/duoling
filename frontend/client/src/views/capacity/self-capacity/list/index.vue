<template>
  <ele-page>
    <capacity-search @search="onSearch" />
    <ele-card :body-style="{ paddingTop: '8px' }">
      <ele-pro-table
        ref="tableRef"
        row-key="id"
        :columns="columns"
        :datasource="datasource"
        :show-overflow-tooltip="true"
        :highlight-current-row="true"
        :default-sort="{ prop: 'boundAt', order: 'descending' }"
        cache-key="CapacityListTable"
      >
        <template #toolbar>
          <btn-items
            :items="[
              {
                preset: 'add',
                title: '新建运力',
                onClick: () => openBind()
              }
            ]"
          />
        </template>
        <template #plateNumber="{ row }">
          <plate-number-tag
            :text="row.plateNumber"
            :category="row.plateCategory"
          />
        </template>
        <template #trailerPlateNumber="{ row }">
          <plate-number-tag
            v-if="row.trailerPlateNumber"
            :text="row.trailerPlateNumber"
            :category="row.trailerPlateCategory"
          />
          <span v-else style="color: var(--el-text-color-placeholder)">—</span>
        </template>
        <template #action="{ row }">
          <el-button type="danger" link size="small" @click="handleUnbind(row)">
            下车
          </el-button>
        </template>
      </ele-pro-table>
    </ele-card>
    <capacity-bind v-model:visible="bindVisible" @done="reload" />

    <el-dialog
      v-model="unbindVisible"
      title="系统提示"
      width="520px"
      align-center
      destroy-on-close
      :close-on-click-modal="false"
      append-to-body
      class="capacity-unbind-dialog-wrap"
      @closed="onUnbindDialogClosed"
    >
      <div class="capacity-unbind-dialog-body">
        <el-icon class="capacity-unbind-dialog-icon" :size="22">
          <WarningFilled />
        </el-icon>
        <div class="capacity-unbind-dialog-main">
          <p class="capacity-unbind-dialog-msg">
            确定将驾驶员
            <strong class="capacity-unbind-name">{{
              unbindTarget?.driverName
            }}</strong>
            与车辆
            <plate-number-tag
              class="capacity-unbind-plate-inline"
              :text="unbindTarget?.plateNumber"
              :category="unbindTarget?.plateCategory"
            />
            解绑吗？解绑后可在「变更记录」中查看历史。
          </p>
          <el-input
            v-model.trim="unbindRemark"
            type="textarea"
            :rows="3"
            resize="none"
            maxlength="500"
            show-word-limit
            placeholder="请填写下车备注"
            class="capacity-unbind-remark-input"
          />
        </div>
      </div>
      <template #footer>
        <el-button @click="unbindVisible = false">取消</el-button>
        <el-button
          type="primary"
          :loading="unbindLoading"
          @click="confirmUnbind"
        >
          确定
        </el-button>
      </template>
    </el-dialog>
  </ele-page>
</template>

<script lang="ts" setup>
  import { ref, reactive } from 'vue';
  import { WarningFilled } from '@element-plus/icons-vue';
  import { EleMessage } from 'ele-admin-plus';
  import type { EleProTable } from 'ele-admin-plus';
  import type {
    DatasourceFunction,
    Columns
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import CapacitySearch from './components/capacity-search.vue';
  import CapacityBind from './components/capacity-bind.vue';
  import PlateNumberTag from '@/components/PlateNumberTag/index.vue';
  import {
    pageCapacities,
    unbindCapacity
  } from '@/api/capacity/self_capacity/list';
  import type {
    Capacity,
    CapacityParam
  } from '@/api/capacity/self_capacity/list/model';
  import { formatDateTime } from '@/utils/date-util';

  defineOptions({ name: 'CapacityList' });

  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);
  const bindVisible = ref(false);

  const where = reactive<Pick<CapacityParam, 'keyword'>>({
    keyword: ''
  });

  const onSearch = (payload: Pick<CapacityParam, 'keyword'>) => {
    where.keyword = payload.keyword ?? '';
    tableRef.value?.reload?.({ page: 1 });
  };

  const columns = ref<Columns>([
    { prop: 'driverName', label: '驾驶员姓名', minWidth: 100 },
    { prop: 'driverPhone', label: '手机号', minWidth: 130 },
    {
      prop: 'plateNumber',
      label: '车牌号',
      minWidth: 120,
      slot: 'plateNumber'
    },
    {
      prop: 'trailerPlateNumber',
      label: '挂车',
      minWidth: 120,
      slot: 'trailerPlateNumber'
    },
    {
      prop: 'boundAt',
      label: '绑定时间',
      minWidth: 170,
      align: 'center',
      formatter: (row) => formatDateTime(row.boundAt)
    },
    {
      columnKey: 'action',
      label: '操作',
      width: 100,
      align: 'center',
      slot: 'action',
      hideInPrint: true,
      hideInExport: true,
      fixed: 'right'
    }
  ]);

  const datasource: DatasourceFunction = async ({ page, limit, pages }) => {
    const p = page ?? (Number(pages?.page) || 1);
    const l = limit ?? (Number(pages?.limit) || 10);
    const res = await pageCapacities({ ...where, page: p, limit: l });
    const raw = res as { list?: Capacity[]; count?: number; total?: number };
    return {
      list: raw?.list ?? [],
      count: raw?.count ?? raw?.total ?? 0
    };
  };

  const reload = () => {
    tableRef.value?.reload?.();
  };

  const openBind = () => {
    bindVisible.value = true;
  };

  const unbindVisible = ref(false);
  const unbindTarget = ref<Capacity | null>(null);
  const unbindRemark = ref('');
  const unbindLoading = ref(false);

  function onUnbindDialogClosed() {
    unbindTarget.value = null;
    unbindRemark.value = '';
  }

  const handleUnbind = (row: Capacity) => {
    unbindTarget.value = row;
    unbindRemark.value = '';
    unbindVisible.value = true;
  };

  const confirmUnbind = async () => {
    const row = unbindTarget.value;
    const id = row?.id;
    if (id == null) return;

    const remark = unbindRemark.value.trim();
    unbindLoading.value = true;
    try {
      const msg = await unbindCapacity(id, remark ? { remark } : {});
      EleMessage.success({ message: msg, plain: true });
      unbindVisible.value = false;
      reload();
    } catch (e: unknown) {
      const message = e instanceof Error ? e.message : String(e);
      EleMessage.error({ message, plain: true });
    } finally {
      unbindLoading.value = false;
    }
  };
</script>

<style scoped>
  .capacity-unbind-dialog-body {
    display: flex;
    gap: 12px;
    align-items: flex-start;
  }

  .capacity-unbind-dialog-icon {
    flex-shrink: 0;
    margin-top: 2px;
    color: var(--el-color-warning);
  }

  .capacity-unbind-dialog-main {
    flex: 1;
    min-width: 0;
  }

  .capacity-unbind-dialog-msg {
    margin: 0 0 12px;
    font-size: 14px;
    line-height: 1.75;
    color: var(--el-text-color-regular);
  }

  .capacity-unbind-name {
    margin: 0 2px;
    padding: 0 4px;
    font-weight: 700;
    color: var(--el-color-primary);
    border-radius: 4px;
    background: var(--el-color-primary-light-9);
  }

  .capacity-unbind-plate-inline {
    margin: 0 4px;
    vertical-align: middle;
  }

  .capacity-unbind-remark-input :deep(.el-textarea__inner) {
    box-sizing: border-box;
  }
</style>
