<!-- 生态运营 - 挂牌审核 -->
<template>
  <ele-page>
    <!-- 积压：先看清今天欠了多少，再决定从哪个队列开始 -->
    <div class="eco-audit-stats">
      <ele-card
        v-for="card in statCards"
        :key="card.key"
        class="eco-audit-stats__item"
        :class="{ 'is-alert': card.alert && card.value > 0 }"
        :body-style="{ padding: '14px 16px' }"
        @click="card.onClick"
      >
        <div class="eco-audit-stats__value">{{ card.value }}</div>
        <div class="eco-audit-stats__label">{{ card.label }}</div>
        <div class="eco-audit-stats__desc">{{ card.desc }}</div>
      </ele-card>
    </div>

    <ele-card :body-style="{ paddingBottom: '0' }">
      <el-form inline @submit.prevent="() => reload(1)">
        <el-form-item label="关键字">
          <el-input
            clearable
            v-model="where.keyword"
            placeholder="按编号或标题搜索"
            style="width: 190px"
            @keyup.enter="() => reload(1)"
          />
        </el-form-item>
        <el-form-item label="类型">
          <el-select
            clearable
            v-model="where.postType"
            placeholder="全部"
            style="width: 110px"
          >
            <el-option
              v-for="t in options.postTypes"
              :key="t.value"
              :label="t.label"
              :value="t.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="发布方">
          <el-input
            clearable
            v-model="where.tenantCode"
            placeholder="企业编码"
            style="width: 150px"
            @keyup.enter="() => reload(1)"
          />
        </el-form-item>
        <template v-if="activeTab === 'all'">
          <el-form-item label="挂牌状态">
            <el-select
              clearable
              multiple
              collapse-tags
              v-model="where.statuses"
              placeholder="全部"
              style="width: 200px"
            >
              <el-option
                v-for="s in options.postStatuses"
                :key="s.value"
                :label="s.label"
                :value="s.value"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="审核状态">
            <el-select
              clearable
              multiple
              collapse-tags
              v-model="where.auditStatuses"
              placeholder="全部"
              style="width: 200px"
            >
              <el-option
                v-for="s in options.auditStatuses"
                :key="s.value"
                :label="s.label"
                :value="s.value"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="进队时间">
            <el-date-picker
              v-model="submittedRange"
              type="datetimerange"
              value-format="YYYY-MM-DD HH:mm:ss"
              start-placeholder="开始"
              end-placeholder="结束"
              style="width: 340px"
            />
          </el-form-item>
        </template>
        <el-form-item>
          <el-checkbox v-model="where.flaggedOnly">只看有可疑标记</el-checkbox>
          <el-checkbox
            v-if="activeTab !== 'spot'"
            v-model="where.overdueOnly"
            style="margin-left: 12px"
          >
            只看已超时
          </el-checkbox>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="() => reload(1)">查询</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>
    </ele-card>

    <div class="eco-audit-body">
      <ele-card class="eco-audit-main" :body-style="{ paddingTop: '4px' }">
        <el-tabs v-model="activeTab" @tab-change="onTabChange">
          <el-tab-pane name="pending">
            <template #label>
              待人工审核
              <span
                v-if="backlog.pending"
                class="eco-audit-tab-count"
                :class="{ 'is-alert': backlog.pendingOverdue > 0 }"
              >
                {{ backlog.pending }}
              </span>
            </template>
          </el-tab-pane>
          <el-tab-pane name="spot">
            <template #label>
              免审待抽检
              <span
                v-if="backlog.spotCheckPending"
                class="eco-audit-tab-count"
                :class="{ 'is-alert': backlog.spotCheckOverdue > 0 }"
              >
                {{ backlog.spotCheckPending }}
              </span>
            </template>
          </el-tab-pane>
          <el-tab-pane label="全部挂牌" name="all" />
        </el-tabs>

        <div v-if="activeTab === 'pending'" class="eco-audit-batch">
          <el-checkbox
            :model-value="allSelected"
            :indeterminate="someSelected"
            @change="toggleAll"
          >
            本页全选
          </el-checkbox>
          <span class="eco-audit-batch__count">
            已选 {{ selectedIds.length }} 条
          </span>
          <el-button
            type="primary"
            plain
            size="small"
            :disabled="!selectedIds.length"
            @click="batchApprove"
          >
            批量通过
          </el-button>
          <span class="eco-audit-batch__tip">
            单次最多 {{ options.batchApproveLimit }} 条。批量只走「通过」，
            有问题的请逐条驳回。
          </span>
        </div>

        <div v-loading="loading" class="eco-audit-list">
          <post-card
            v-for="row in list"
            :key="row.post.id"
            :row="row"
            :mode="activeTab"
            :selectable="activeTab === 'pending'"
            :selected="selectedIds.includes(row.post.id)"
            :active="focused?.id === row.post.id"
            :flag-labels="flagLabels"
            @update:selected="(v) => toggleOne(row.post.id, v)"
            @focus="focused = row.post"
            @detail="openDetail(row.post)"
            @approve="approve(row.post)"
            @reject="openDeny('reject', row.post)"
            @force-delist="openDeny('force-delist', row.post)"
            @spot-pass="spotPass(row.post)"
            @spot-fail="openDeny('spot-fail', row.post)"
          />
          <el-empty
            v-if="!loading && !list.length"
            :image-size="90"
            :description="emptyText"
          />
        </div>

        <el-pagination
          v-model:current-page="page"
          v-model:page-size="limit"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          background
          class="eco-audit-pager"
          @size-change="() => reload(1)"
          @current-change="loadList"
        />
      </ele-card>

      <ele-card
        class="eco-audit-side"
        header="发布方档案"
        :body-style="{ paddingTop: '8px' }"
      >
        <tenant-profile
          :tenant-code="focused?.ownerTenantCode"
          @changed="refreshAll"
        />
      </ele-card>
    </div>

    <audit-detail
      v-model="detailVisible"
      :post-id="detailPostId"
      :flag-labels="flagLabels"
      @action="onDetailAction"
    />
  </ele-page>
</template>

<script lang="ts" setup>
  import { computed, onMounted, reactive, ref } from 'vue';
  import { ElMessageBox } from 'element-plus';
  import { EleMessage, useModal } from 'ele-admin-plus';
  import {
    approvePost,
    batchApprovePosts,
    getAuditBacklog,
    getAuditOptions,
    pageAllPosts,
    pagePendingPosts,
    pageSpotCheckPosts,
    spotCheckPass
  } from '@/api/ecosystem/audit';
  import type {
    AuditBacklog,
    AuditOptions,
    AuditPost,
    AuditPostParam,
    AuditQueueRow
  } from '@/api/ecosystem/audit/model';
  import TenantProfile from '@/views/ecosystem/components/tenant-profile.vue';
  import PostCard from './components/post-card.vue';
  import AuditDetail from './components/audit-detail.vue';

  defineOptions({ name: 'EcoPostAudit' });

  type QueueTab = 'pending' | 'spot' | 'all';

  const { openModal } = useModal();

  const loading = ref(false);
  const activeTab = ref<QueueTab>('pending');
  const list = ref<AuditQueueRow[]>([]);
  const total = ref(0);
  const page = ref(1);
  const limit = ref(20);
  const selectedIds = ref<number[]>([]);
  const focused = ref<AuditPost | null>(null);
  const detailVisible = ref(false);
  const detailPostId = ref<number | null>(null);
  const submittedRange = ref<[string, string] | null>(null);

  const backlog = ref<AuditBacklog>({
    pending: 0,
    pendingOverdue: 0,
    pendingFlagged: 0,
    spotCheckPending: 0,
    spotCheckOverdue: 0,
    slaMinutes: 120,
    warnMinutes: 60
  });

  const options = ref<AuditOptions>({
    rejectReasons: [],
    postStatuses: [],
    auditStatuses: [],
    postTypes: [],
    precheckFlags: [],
    batchApproveLimit: 50,
    spotCheckHours: 24
  });

  /** 预检标记的中文名由后端下发，前端不自己编 */
  const flagLabels = computed(() =>
    options.value.precheckFlags.reduce<Record<string, string>>((acc, item) => {
      acc[String(item.value)] = item.label;
      return acc;
    }, {})
  );

  const where = reactive<{
    keyword?: string;
    postType?: number;
    tenantCode?: string;
    flaggedOnly: boolean;
    overdueOnly: boolean;
    statuses: number[];
    auditStatuses: number[];
  }>({
    keyword: '',
    postType: void 0,
    tenantCode: '',
    flaggedOnly: false,
    overdueOnly: false,
    statuses: [],
    auditStatuses: []
  });

  const statCards = computed(() => [
    {
      key: 'pending',
      label: '待人工审核',
      value: backlog.value.pending,
      desc: `目标 ${backlog.value.slaMinutes / 60} 小时内处理完`,
      alert: false,
      onClick: () => jump('pending', {})
    },
    {
      key: 'overdue',
      label: '已超时',
      value: backlog.value.pendingOverdue,
      desc: '等待已超过承诺时长',
      alert: true,
      onClick: () => jump('pending', { overdueOnly: true })
    },
    {
      key: 'flagged',
      label: '有可疑标记',
      value: backlog.value.pendingFlagged,
      desc: '预检标了红，建议优先看',
      alert: true,
      onClick: () => jump('pending', { flaggedOnly: true })
    },
    {
      key: 'spot',
      label: '免审待抽检',
      value: backlog.value.spotCheckPending,
      desc: `上架后 ${options.value.spotCheckHours} 小时内抽检`,
      alert: false,
      onClick: () => jump('spot', {})
    },
    {
      key: 'spotOverdue',
      label: '抽检已超时',
      value: backlog.value.spotCheckOverdue,
      desc: '队列按上架时间正序，这些排在最前',
      alert: true,
      onClick: () => jump('spot', {})
    }
  ]);

  const emptyText = computed(() => {
    if (activeTab.value === 'pending') {
      return '待审队列已经清空，辛苦了';
    }
    if (activeTab.value === 'spot') {
      return '没有待抽检的挂牌';
    }
    return '没有符合条件的挂牌，换个条件试试';
  });

  const allSelected = computed(
    () => !!list.value.length && selectedIds.value.length === list.value.length
  );

  const someSelected = computed(
    () => !!selectedIds.value.length && !allSelected.value
  );

  const buildParams = (): AuditPostParam => {
    const params: AuditPostParam = {
      page: page.value,
      limit: limit.value,
      keyword: where.keyword || void 0,
      postType: where.postType,
      tenantCode: where.tenantCode || void 0,
      flaggedOnly: where.flaggedOnly || void 0
    };
    if (activeTab.value !== 'spot') {
      params.overdueOnly = where.overdueOnly || void 0;
    }
    if (activeTab.value === 'all') {
      params.statuses = where.statuses.length ? where.statuses : void 0;
      params.auditStatuses = where.auditStatuses.length
        ? where.auditStatuses
        : void 0;
      params.submittedFrom = submittedRange.value?.[0];
      params.submittedTo = submittedRange.value?.[1];
    }
    return params;
  };

  const loadList = () => {
    const params = buildParams();
    const query =
      activeTab.value === 'pending'
        ? pagePendingPosts(params)
        : activeTab.value === 'spot'
          ? pageSpotCheckPosts(params)
          : pageAllPosts(params);
    loading.value = true;
    selectedIds.value = [];
    query
      .then((data) => {
        loading.value = false;
        list.value = data.list;
        total.value = data.total ?? data.count ?? 0;
      })
      .catch((e) => {
        loading.value = false;
        EleMessage.error({ message: e.message, plain: true });
      });
  };

  const loadBacklog = () => {
    getAuditBacklog()
      .then((data) => {
        backlog.value = data;
      })
      .catch(() => {
        // 数字卡取不到不影响审核，静默即可，不要用报错打断运营
      });
  };

  const reload = (target?: number) => {
    page.value = target ?? page.value;
    loadList();
  };

  const refreshAll = () => {
    loadList();
    loadBacklog();
  };

  const onTabChange = () => {
    selectedIds.value = [];
    reload(1);
  };

  const jump = (
    tab: QueueTab,
    filters: { overdueOnly?: boolean; flaggedOnly?: boolean }
  ) => {
    activeTab.value = tab;
    where.overdueOnly = !!filters.overdueOnly;
    where.flaggedOnly = !!filters.flaggedOnly;
    reload(1);
  };

  const resetSearch = () => {
    where.keyword = '';
    where.postType = void 0;
    where.tenantCode = '';
    where.flaggedOnly = false;
    where.overdueOnly = false;
    where.statuses = [];
    where.auditStatuses = [];
    submittedRange.value = null;
    reload(1);
  };

  const toggleOne = (id: number, selected: boolean) => {
    const next = new Set(selectedIds.value);
    if (selected) {
      if (next.size >= options.value.batchApproveLimit) {
        EleMessage.warning({
          message: `一次最多选 ${options.value.batchApproveLimit} 条，先把这批处理完吧`,
          plain: true
        });
        return;
      }
      next.add(id);
    } else {
      next.delete(id);
    }
    selectedIds.value = [...next];
  };

  const toggleAll = (checked: any) => {
    if (!checked) {
      selectedIds.value = [];
      return;
    }
    selectedIds.value = list.value
      .slice(0, options.value.batchApproveLimit)
      .map((row) => row.post.id);
  };

  const openDetail = (post: AuditPost) => {
    focused.value = post;
    detailPostId.value = post.id;
    detailVisible.value = true;
  };

  const approve = (post: AuditPost) => {
    const msg = EleMessage.loading({
      message: '正在通过并上架，请稍候…',
      plain: true
    });
    approvePost(post.id)
      .then(({ message }) => {
        msg.close();
        EleMessage.success({ message: message || '已上架', plain: true });
        refreshAll();
      })
      .catch((e) => {
        msg.close();
        EleMessage.error({ message: e.message, plain: true });
      });
  };

  const spotPass = (post: AuditPost) => {
    const msg = EleMessage.loading({
      message: '正在记录抽检结果，请稍候…',
      plain: true
    });
    spotCheckPass(post.id)
      .then(({ message }) => {
        msg.close();
        EleMessage.success({
          message: message || '已记为抽检通过',
          plain: true
        });
        refreshAll();
      })
      .catch((e) => {
        msg.close();
        EleMessage.error({ message: e.message, plain: true });
      });
  };

  const openDeny = (
    mode: 'reject' | 'force-delist' | 'spot-fail',
    post: AuditPost
  ) => {
    openModal({
      custom: true,
      asyncComponent: () => import('./components/deny-modal.vue'),
      componentProps: {
        mode,
        post,
        reasons: options.value.rejectReasons,
        onDone: () => refreshAll()
      }
    });
  };

  const onDetailAction = (
    name: 'approve' | 'reject' | 'force-delist' | 'spot-pass' | 'spot-fail',
    post: AuditPost
  ) => {
    if (name === 'approve') {
      approve(post);
    } else if (name === 'spot-pass') {
      spotPass(post);
    } else {
      openDeny(name === 'reject' ? 'reject' : name, post);
    }
  };

  const batchApprove = () => {
    const ids = [...selectedIds.value];
    ElMessageBox.confirm(
      '这些挂牌会直接进入大厅展示。请确认已经逐条看过内容，批量通过没有二次确认的机会。',
      `确定通过选中的 ${ids.length} 条挂牌吗？`,
      { type: 'warning', draggable: true, confirmButtonText: '确定通过' }
    )
      .then(() => {
        const msg = EleMessage.loading({
          message: '正在批量通过，请稍候…',
          plain: true
        });
        batchApprovePosts(ids)
          .then(({ result, message }) => {
            msg.close();
            refreshAll();
            if (result?.failed?.length) {
              // 部分失败必须逐条说清楚，否则运营会以为全都没生效然后重复点
              ElMessageBox.alert(
                result.failed
                  .map((f) => `${f.postNo || f.postId}：${f.message}`)
                  .join('\n'),
                `已通过 ${result.successCount} 条，${result.failed.length} 条没通过`,
                { type: 'warning', draggable: true }
              ).catch(() => {});
              return;
            }
            EleMessage.success({
              message:
                message ||
                `已通过 ${result?.successCount ?? ids.length} 条挂牌`,
              plain: true
            });
          })
          .catch((e) => {
            msg.close();
            EleMessage.error({ message: e.message, plain: true });
          });
      })
      .catch(() => {});
  };

  onMounted(() => {
    getAuditOptions()
      .then((data) => {
        options.value = data;
      })
      .catch((e) => {
        EleMessage.error({ message: e.message, plain: true });
      });
    loadBacklog();
    loadList();
  });
</script>

<style lang="scss" scoped>
  .eco-audit-stats {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 12px;
    margin-bottom: 12px;
  }

  .eco-audit-stats__item {
    margin-bottom: 0 !important;
    cursor: pointer;
    transition: box-shadow 0.2s;

    &:hover {
      box-shadow: var(--el-box-shadow-light);
    }

    &.is-alert .eco-audit-stats__value {
      color: var(--el-color-danger);
    }
  }

  .eco-audit-stats__value {
    font-size: 24px;
    font-weight: 600;
    line-height: 1.2;
    color: var(--el-text-color-primary);
  }

  .eco-audit-stats__label {
    margin-top: 4px;
    font-size: 13px;
    color: var(--el-text-color-regular);
  }

  .eco-audit-stats__desc {
    margin-top: 2px;
    font-size: 12px;
    color: var(--el-text-color-secondary);
  }

  .eco-audit-body {
    display: flex;
    align-items: flex-start;
    gap: 12px;
  }

  .eco-audit-main {
    flex: 1;
    min-width: 0;
  }

  .eco-audit-side {
    width: 340px;
    flex: none;
    position: sticky;
    top: 12px;
  }

  .eco-audit-tab-count {
    margin-left: 4px;
    padding: 0 6px;
    border-radius: 9px;
    font-size: 12px;
    background: var(--el-fill-color-dark);
    color: var(--el-text-color-regular);

    &.is-alert {
      background: var(--el-color-danger-light-8);
      color: var(--el-color-danger);
    }
  }

  .eco-audit-batch {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 10px;
    padding: 8px 12px;
    margin-bottom: 10px;
    border-radius: 6px;
    background: var(--el-fill-color-light);
  }

  .eco-audit-batch__count {
    font-size: 13px;
    color: var(--el-text-color-regular);
  }

  .eco-audit-batch__tip {
    font-size: 12px;
    color: var(--el-text-color-secondary);
  }

  .eco-audit-list {
    min-height: 240px;
  }

  .eco-audit-pager {
    margin-top: 12px;
    justify-content: flex-end;
  }

  @media (max-width: 1400px) {
    .eco-audit-stats {
      grid-template-columns: repeat(3, 1fr);
    }

    .eco-audit-body {
      flex-wrap: wrap;
    }

    .eco-audit-side {
      width: 100%;
      position: static;
    }
  }
</style>
