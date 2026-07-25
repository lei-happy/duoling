<!--
  发布货源时选任务单

  只列「待派车」的任务：更早的状态配载还在调整，信息不稳定；已安排承运方的
  不需要再找车。这与后端 CargoDraftBuilder.assert_publishable 的判断一致——
  列表里能看到却发不出去，用户只会以为系统坏了。
-->
<template>
  <div class="eco-picker">
    <div class="eco-picker__bar">
      <el-input
        v-model="keyword"
        clearable
        placeholder="搜任务号、起终点"
        :prefix-icon="Search"
        @change="reload"
      />
    </div>

    <el-table
      v-loading="loading"
      class="eco-picker__table"
      :data="rows"
      height="360"
      highlight-current-row
      @current-change="onPick"
    >
      <el-table-column width="42">
        <template #default="{ row }">
          <el-radio
            :value="row.id"
            :model-value="picked?.id"
            @change="onPick(row)"
          >
            <span></span>
          </el-radio>
        </template>
      </el-table-column>
      <el-table-column label="任务号" prop="taskNo" width="150" />
      <el-table-column label="线路" min-width="200">
        <template #default="{ row }">
          <div class="eco-picker__route">
            <span>{{ row.origin || '—' }}</span>
            <span class="eco-picker__arrow">→</span>
            <span>{{ row.destination || '—' }}</span>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="台数" width="72" align="right">
        <template #default="{ row }">{{ row.totalQuantity ?? '—' }}</template>
      </el-table-column>
      <el-table-column label="计划装车" width="150">
        <template #default="{ row }">{{ row.plannedLoadTime || '—' }}</template>
      </el-table-column>
    </el-table>

    <div class="eco-picker__foot">
      <el-pagination
        v-model:current-page="page"
        layout="total, prev, pager, next"
        :page-size="pageSize"
        :total="total"
        :pager-count="5"
        @current-change="load"
      />
    </div>
  </div>
</template>

<script lang="ts" setup>
  import { onMounted, ref } from 'vue';
  import { Search } from '@element-plus/icons-vue';
  import { EleMessage } from 'ele-admin-plus';
  import { pageTasks } from '@/api/operation/task';
  import type { Task } from '@/api/operation/task/model';

  /** 待派车。与后端「只有还没派车的任务可以发布」对齐 */
  const STATUS_PENDING_DISPATCH = 0;

  const emit = defineEmits<{ (e: 'pick', task: Task): void }>();

  const loading = ref(false);
  const rows = ref<Task[]>([]);
  const keyword = ref('');
  const page = ref(1);
  const pageSize = ref(8);
  const total = ref(0);
  const picked = ref<Task>();

  const load = async () => {
    loading.value = true;
    try {
      const result = await pageTasks({
        page: page.value,
        limit: pageSize.value,
        status: STATUS_PENDING_DISPATCH,
        keyword: keyword.value || void 0
      });
      rows.value = result?.list ?? [];
      total.value = result?.count ?? 0;
    } catch (e: any) {
      EleMessage.error({
        message: e?.message ?? '没能读取任务单，请稍后再试',
        plain: true
      });
    } finally {
      loading.value = false;
    }
  };

  const reload = () => {
    page.value = 1;
    load();
  };

  const onPick = (task?: Task | null) => {
    if (!task?.id) {
      return;
    }
    picked.value = task;
    emit('pick', task);
  };

  onMounted(load);
</script>

<style lang="scss" scoped>
  .eco-picker__bar {
    max-width: 280px;
    margin-bottom: 10px;
  }

  .eco-picker__route {
    display: flex;
    gap: 6px;
    align-items: center;
  }

  .eco-picker__arrow {
    color: var(--el-text-color-placeholder);
  }

  .eco-picker__foot {
    display: flex;
    justify-content: flex-end;
    margin-top: 10px;
  }

  :deep(.el-radio__label) {
    display: none;
  }
</style>
