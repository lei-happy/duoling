<template>
  <ele-page>
    <feedback-search @search="(where) => reload(where, 1)" />
    <ele-card :body-style="{ paddingTop: '8px' }">
      <ele-pro-table
        ref="tableRef"
        row-key="id"
        :columns="columns"
        :datasource="datasource"
        :show-overflow-tooltip="true"
        :highlight-current-row="true"
        cache-key="UserFeedbackTable"
        @row-click="(row) => openDetail(row)"
      >
        <template #toolbar>
          <el-button type="primary" @click="submitVisible = true">
            我要反馈
          </el-button>
        </template>
        <template #type="{ row }">
          <el-tag size="small" :disable-transitions="true">
            {{ typeLabel(row.feedback_type) }}
          </el-tag>
        </template>
        <template #status="{ row }">
          <el-tag
            :type="statusTagType(row.status)"
            size="small"
            :disable-transitions="true"
          >
            {{ statusLabel(row.status) }}
          </el-tag>
        </template>
        <template #replied="{ row }">
          <span>{{ row.reply ? '有回复' : '暂无' }}</span>
        </template>
      </ele-pro-table>
    </ele-card>

    <feedback-submit-dialog
      v-model="submitVisible"
      @done="onSubmitted"
    />

    <el-drawer
      v-model="detailVisible"
      title="反馈详情"
      size="520px"
      destroy-on-close
    >
      <template v-if="detail">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="类型">
            {{ typeLabel(detail.feedback_type) }}
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag
              :type="statusTagType(detail.status)"
              size="small"
              :disable-transitions="true"
            >
              {{ statusLabel(detail.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item v-if="isAdmin" label="提交人">
            {{ detail.user_name || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="标题">
            {{ detail.title }}
          </el-descriptions-item>
          <el-descriptions-item label="详细说明">
            <div class="feedback-content">{{ detail.content }}</div>
          </el-descriptions-item>
          <el-descriptions-item
            v-if="detail.images?.length"
            label="截图"
          >
            <div class="feedback-images">
              <el-image
                v-for="(url, idx) in detail.images"
                :key="url + idx"
                :src="resolveUploadUrl(url)"
                fit="cover"
                :preview-src-list="detail.images.map(resolveUploadUrl)"
                :initial-index="idx"
                class="feedback-images__item"
              />
            </div>
          </el-descriptions-item>
          <el-descriptions-item label="提交时间">
            {{ detail.created_at || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="官方回复">
            <div v-if="detail.reply" class="feedback-content">
              {{ detail.reply }}
            </div>
            <span v-else class="ele-text-secondary">暂无回复</span>
          </el-descriptions-item>
          <el-descriptions-item v-if="detail.replied_at" label="回复时间">
            {{ detail.replied_at }}
          </el-descriptions-item>
          <el-descriptions-item v-if="detail.handler_name" label="处理人">
            {{ detail.handler_name }}
          </el-descriptions-item>
        </el-descriptions>
      </template>
    </el-drawer>
  </ele-page>
</template>

<script lang="ts" setup>
  import { computed, ref } from 'vue';
  import { EleMessage } from 'ele-admin-plus';
  import type { EleProTable } from 'ele-admin-plus';
  import type {
    DatasourceFunction,
    Columns
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import FeedbackSearch from './components/feedback-search.vue';
  import FeedbackSubmitDialog from './components/feedback-submit-dialog.vue';
  import { getFeedback, pageFeedbacks } from '@/api/feedback';
  import type { Feedback, FeedbackParam } from '@/api/feedback/model';
  import { useUserStore } from '@/store/modules/user';
  import { resolveUploadUrl } from '@/utils/upload-url';

  defineOptions({ name: 'UserFeedback' });

  const userStore = useUserStore();
  const isAdmin = computed(() => userStore.isAdmin);
  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);
  const lastWhere = ref<FeedbackParam>({});
  const submitVisible = ref(false);
  const detailVisible = ref(false);
  const detail = ref<Feedback | null>(null);

  const typeLabel = (t?: number) =>
    ({ 0: '建议', 1: '缺陷', 2: '投诉', 3: '其他' })[t ?? -1] || '-';

  const statusLabel = (s?: number) =>
    ({ 0: '待处理', 1: '处理中', 2: '已解决', 3: '已关闭' })[s ?? -1] || '-';

  const statusTagType = (s?: number) =>
    ({ 0: 'info', 1: 'warning', 2: 'success', 3: 'info' })[s ?? -1] || 'info';

  const columns = computed<Columns>(() => {
    const cols: Columns = [
      { type: 'index', columnKey: 'index', width: 50, align: 'center' },
      {
        prop: 'feedback_type',
        label: '类型',
        width: 90,
        align: 'center',
        slot: 'type'
      },
      {
        prop: 'status',
        label: '状态',
        width: 90,
        align: 'center',
        slot: 'status'
      },
      { prop: 'title', label: '标题', minWidth: 180 }
    ];
    if (isAdmin.value) {
      cols.push({
        prop: 'user_name',
        label: '提交人',
        width: 110,
        formatter: (row: Feedback) => row.user_name || '-'
      });
    }
    cols.push(
      {
        prop: 'reply',
        label: '回复',
        width: 80,
        align: 'center',
        slot: 'replied'
      },
      {
        prop: 'created_at',
        label: '提交时间',
        width: 170,
        align: 'center'
      }
    );
    return cols;
  });

  const datasource: DatasourceFunction = ({ pages, where }) => {
    const query = { ...lastWhere.value, ...(where || {}) };
    return pageFeedbacks({
      ...query,
      page: pages?.page,
      limit: pages?.limit
    });
  };

  const reload = (where?: FeedbackParam, page?: number) => {
    if (where) {
      lastWhere.value = { ...where };
    }
    tableRef.value?.reload?.({ where: lastWhere.value, page });
  };

  const onSubmitted = () => {
    reload(undefined, 1);
  };

  const openDetail = async (row: Feedback) => {
    if (!row.id) return;
    try {
      detail.value = (await getFeedback(row.id)) || null;
      detailVisible.value = true;
    } catch (e: any) {
      EleMessage.error({
        message: e.message || '加载失败，请重试',
        plain: true
      });
    }
  };
</script>

<style scoped>
  .feedback-content {
    white-space: pre-wrap;
    word-break: break-word;
    line-height: 1.6;
  }
  .feedback-images {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }
  .feedback-images__item {
    width: 72px;
    height: 72px;
    border-radius: 4px;
  }
</style>
