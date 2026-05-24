<template>
  <PageContainer title="我的任务" :show-tabbar="true" :hide-back="true">
    <van-tabs v-model:active="tabIndex" sticky animated swipeable @change="onTabChange">
      <van-tab
        v-for="(t, idx) in VISIBLE_STATUS_TABS"
        :key="idx"
        :title="t.label"
      />
    </van-tabs>

    <div class="task-list">
      <van-pull-refresh v-model="refreshing" @refresh="onRefresh">
        <van-list
          v-model:loading="loading"
          :finished="finished"
          finished-text="没有更多了"
          :error="error"
          error-text="请求失败，点击重试"
          @load="onLoad"
        >
          <TaskCard
            v-for="item in list"
            :key="item.id"
            :task="item"
            @click="goDetail(item.id)"
          />
          <van-empty v-if="list.length === 0 && !loading" description="暂无任务" />
        </van-list>
      </van-pull-refresh>
    </div>
  </PageContainer>
</template>

<script setup lang="ts">
import { onActivated, onMounted, ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import PageContainer from '@/components/PageContainer.vue';
import TaskCard from '@/components/TaskCard.vue';
import { listMyTasks, type TaskListItem } from '@/api/task';
import { VISIBLE_STATUS_TABS } from './status-config';

defineOptions({ name: 'TaskList' });

const route = useRoute();
const router = useRouter();

const tabIndex = ref(0);
const list = ref<TaskListItem[]>([]);
const loading = ref(false);
const finished = ref(false);
const refreshing = ref(false);
const error = ref(false);
const page = ref(1);
const pageSize = 15;

onMounted(() => {
  syncTabFromQuery();
});

onActivated(() => {
  syncTabFromQuery();
});

function syncTabFromQuery() {
  const s = route.query.status as string | undefined;
  if (s !== undefined && s !== '') {
    const idx = VISIBLE_STATUS_TABS.findIndex((t) => String(t.value ?? '') === s);
    if (idx >= 0) tabIndex.value = idx;
  }
}

watch(tabIndex, () => {
  reload();
});

async function onLoad() {
  try {
    error.value = false;
    const status = VISIBLE_STATUS_TABS[tabIndex.value]?.value;
    const res = await listMyTasks({ status, page: page.value, pageSize });
    list.value.push(...res.list);
    page.value += 1;
    finished.value = list.value.length >= res.total;
  } catch (e) {
    error.value = true;
    console.error(e);
  } finally {
    loading.value = false;
  }
}

function reload() {
  page.value = 1;
  list.value = [];
  finished.value = false;
  loading.value = true;
  onLoad();
}

function onRefresh() {
  refreshing.value = true;
  reload();
  setTimeout(() => (refreshing.value = false), 400);
}

function onTabChange() {
  reload();
}

function goDetail(id: number) {
  router.push(`/task/${id}`);
}
</script>

<style lang="scss" scoped>
.task-list {
  padding-top: $spacing-sm;
  padding-bottom: $spacing-lg;
  min-height: calc(100vh - 90px);
}
</style>
