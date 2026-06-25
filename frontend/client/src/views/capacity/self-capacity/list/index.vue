<template>
  <ele-page>
    <capacity-search @search="onSearch" />
    <ele-card :body-style="{ paddingTop: '8px' }">
      <div class="capacity-list-toolbar">
        <btn-items
          :items="[
            {
              preset: 'add',
              title: '新建运力',
              onClick: () => openBind()
            }
          ]"
        />
      </div>

      <el-tabs v-model="activeTab" class="capacity-list-tabs" @tab-change="onTabChange">
        <el-tab-pane label="全部" name="all" />
        <el-tab-pane label="可接单" name="1" />
        <el-tab-pane label="运输中" name="2" />
        <el-tab-pane label="休假" name="3" />
        <el-tab-pane label="停运" name="4" />
        <el-tab-pane label="维修保养中" name="5" />
      </el-tabs>

      <div v-loading="loading" class="capacity-list-body">
        <div v-if="list.length" class="capacity-card-grid">
          <capacity-card
            v-for="item in list"
            :key="item.id"
            :item="item"
            @unbind="handleUnbind"
            @change-status="handleChangeStatus"
            @detail="handleDetail"
          />
        </div>
        <el-empty v-else-if="!loading" description="暂无运力数据" />
      </div>

      <div v-if="total > 0" class="capacity-list-pagination">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[18, 36, 54]"
          layout="total, sizes, prev, pager, next, jumper"
          background
          @current-change="loadData"
          @size-change="onPageSizeChange"
        />
      </div>
    </ele-card>

    <capacity-bind v-model:visible="bindVisible" @done="reload" />
    <flip-modal ref="flipModalRef" width="800px" @closed="onDetailClosed">
      <capacity-detail :data="detailTarget" />
    </flip-modal>

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
  import { ref, reactive, onMounted } from 'vue';
  import { WarningFilled } from '@element-plus/icons-vue';
  import { ElMessageBox } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import CapacitySearch from './components/capacity-search.vue';
  import CapacityBind from './components/capacity-bind.vue';
  import CapacityCard from './components/capacity-card.vue';
  import CapacityDetail from './components/capacity-detail.vue';
  import FlipModal from '@/components/FlipModal/index.vue';
  import PlateNumberTag from '@/components/PlateNumberTag/index.vue';
  import {
    pageCapacities,
    unbindCapacity,
    updateCapacityOperationStatus
  } from '@/api/capacity/self-capacity/list';
  import type {
    Capacity,
    CapacityParam
  } from '@/api/capacity/self-capacity/list/model';

  defineOptions({ name: 'CapacityList' });

  const bindVisible = ref(false);
  const loading = ref(false);
  const list = ref<Capacity[]>([]);
  const total = ref(0);
  const page = ref(1);
  const pageSize = ref(18);
  const activeTab = ref('all');

  const where = reactive<Pick<CapacityParam, 'keyword' | 'operationStatus'>>({
    keyword: '',
    operationStatus: undefined
  });

  const loadData = async () => {
    loading.value = true;
    try {
      const res = await pageCapacities({
        ...where,
        page: page.value,
        limit: pageSize.value
      });
      const raw = res as { list?: Capacity[]; count?: number; total?: number };
      list.value = raw?.list ?? [];
      total.value = raw?.count ?? raw?.total ?? 0;
    } catch (e: unknown) {
      list.value = [];
      total.value = 0;
      const message = e instanceof Error ? e.message : String(e);
      EleMessage.error({ message, plain: true });
    } finally {
      loading.value = false;
    }
  };

  const onSearch = (payload: Pick<CapacityParam, 'keyword'>) => {
    where.keyword = payload.keyword ?? '';
    page.value = 1;
    loadData();
  };

  const onTabChange = (name: string | number) => {
    if (name === 'all') {
      where.operationStatus = undefined;
    } else {
      where.operationStatus = Number(name);
    }
    page.value = 1;
    loadData();
  };

  const onPageSizeChange = () => {
    page.value = 1;
    loadData();
  };

  const reload = () => {
    loadData();
  };

  const openBind = () => {
    bindVisible.value = true;
  };

  const flipModalRef = ref<InstanceType<typeof FlipModal> | null>(null);
  const detailTarget = ref<Capacity | null>(null);

  const handleDetail = (item: Capacity, el: HTMLElement) => {
    detailTarget.value = item;
    flipModalRef.value?.open(el);
  };

  const onDetailClosed = () => {
    detailTarget.value = null;
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

  const STATUS_ACTION_LABEL: Record<number, string> = {
    1: '恢复可接单',
    3: '置为休假',
    4: '置为停运'
  };

  const handleChangeStatus = async (payload: {
    item: Capacity;
    status: number;
  }) => {
    const { item, status } = payload;
    const id = item?.id;
    if (id == null) return;

    const actionLabel = STATUS_ACTION_LABEL[status] ?? '变更状态';
    try {
      await ElMessageBox.confirm(
        `确定将驾驶员「${item.driverName ?? ''}」与车辆「${item.plateNumber ?? ''}」的运力${actionLabel}吗？`,
        '运力状态变更',
        {
          type: 'warning',
          confirmButtonText: '确定',
          cancelButtonText: '取消'
        }
      );
    } catch {
      return;
    }

    try {
      const msg = await updateCapacityOperationStatus(id, {
        operationStatus: status
      });
      EleMessage.success({ message: msg, plain: true });
      reload();
    } catch (e: unknown) {
      const message = e instanceof Error ? e.message : String(e);
      EleMessage.error({ message, plain: true });
    }
  };

  onMounted(() => {
    loadData();
  });
</script>

<style scoped>
  .capacity-list-toolbar {
    display: flex;
    justify-content: flex-start;
    margin-bottom: 4px;
  }

  .capacity-list-tabs {
    margin-bottom: 16px;
  }

  .capacity-list-tabs :deep(.el-tabs__nav-wrap::after) {
    height: 1px;
    background-color: var(--el-border-color-extra-light);
  }

  .capacity-list-tabs :deep(.el-tabs__item) {
    font-size: 15px;
  }

  .capacity-list-body {
    min-height: 200px;
  }

  .capacity-card-grid {
    display: grid;
    grid-template-columns: repeat(6, minmax(0, 1fr));
    gap: 12px;
  }

  @media (max-width: 1600px) {
    .capacity-card-grid {
      grid-template-columns: repeat(5, minmax(0, 1fr));
    }
  }

  @media (max-width: 1280px) {
    .capacity-card-grid {
      grid-template-columns: repeat(4, minmax(0, 1fr));
    }
  }

  @media (max-width: 992px) {
    .capacity-card-grid {
      grid-template-columns: repeat(3, minmax(0, 1fr));
    }
  }

  @media (max-width: 768px) {
    .capacity-card-grid {
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }
  }

  .capacity-list-pagination {
    display: flex;
    justify-content: flex-end;
    margin-top: 16px;
    padding-top: 8px;
  }

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
