<!--
  我发布的

  这里是管理场景，不是浏览场景，所以用表格而不是卡片流：用户来这儿是找某一条
  具体的挂牌做处理（改报价、延长、停止展示），要的是可扫读、可排序的行。

  页签按后端下发的 statusCounts 打角标。角标是这一屏最有用的信息：
  「未通过 2」会让人马上点进去改，而没有角标他根本不知道有条挂牌被驳回了。
-->
<template>
  <div class="eco-mine">
    <div class="eco-mine__bar">
      <el-tabs v-model="activeTab" class="eco-mine__tabs" @tab-change="reload">
        <el-tab-pane v-for="tab in MY_POST_TABS" :key="tab.key" :name="tab.key">
          <template #label>
            {{ tab.label }}
            <span v-if="counts[tab.key]" class="eco-mine__count">
              {{ counts[tab.key] }}
            </span>
          </template>
        </el-tab-pane>
      </el-tabs>
      <div class="eco-mine__tools">
        <el-input
          v-model="keyword"
          clearable
          placeholder="标题、线路或编号"
          class="eco-mine__keyword"
          @keyup.enter="reload"
          @clear="reload"
        />
        <el-button v-if="canPublish" type="primary" @click="emit('publish')">
          {{ postType === PostType.CARGO ? '发布货源' : '发布运力' }}
        </el-button>
      </div>
    </div>

    <ele-pro-table
      ref="tableRef"
      row-key="id"
      :columns="columns"
      :datasource="datasource"
      :show-overflow-tooltip="true"
      :toolbar="false"
      :cache-key="cacheKey"
    >
      <template #empty>
        <eco-empty-state :description="emptyText">
          <el-button v-if="canPublish" type="primary" @click="emit('publish')">
            {{ postType === PostType.CARGO ? '从任务单发布' : '从运力发布' }}
          </el-button>
        </eco-empty-state>
      </template>

      <template #route="{ row }">
        <eco-route-arrow
          compact
          :from-province="row.fromProvince"
          :from-city="row.fromCity"
          :from-district="row.fromDistrict"
          :to-province="row.toProvince"
          :to-city="row.toCity"
          :to-district="row.toDistrict"
          :any-direction="row.anyDirection"
          :destinations="row.destinations"
        />
      </template>

      <template #quantity="{ row }">
        {{ quantityText(row) }}
      </template>

      <template #price="{ row }">
        {{ priceText(row.priceType, row.priceAmount, row.priceNegotiable) }}
      </template>

      <template #status="{ row }">
        <eco-post-status-tag
          :status="row.status"
          :valid-until="row.validUntil"
        />
      </template>

      <template #heat="{ row }">
        <span v-if="row.intentCount" class="eco-mine__heat">
          {{ row.intentCount }} 人想合作
        </span>
        <span v-else class="eco-mine__heat is-quiet">
          {{ row.viewCount ? `${row.viewCount} 次浏览` : '还没人看过' }}
        </span>
      </template>

      <template #action="{ row }">
        <btn-items :divider="true" type="link" :items="actionItems(row)" />
      </template>
    </ele-pro-table>
  </div>
</template>

<script lang="ts" setup>
  import { computed, reactive, ref } from 'vue';
  import type { EleProTable } from 'ele-admin-plus';
  import type {
    Columns,
    DatasourceFunction
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import { pageMyPosts } from '@/api/ecosystem/post';
  import type { EcoPost } from '@/api/ecosystem/hall/model';
  import {
    EDITABLE_STATUSES,
    MY_POST_TABS,
    PostStatus,
    PostType,
    SUBMITTABLE_STATUSES,
    priceText
  } from '@/config/ecosystem/enums';
  import EcoRouteArrow from './eco-route-arrow.vue';
  import EcoPostStatusTag from './eco-post-status-tag.vue';
  import EcoEmptyState from './eco-empty-state.vue';
  import { usePostActions } from './use-post-actions';

  const props = defineProps<{
    postType: number;
    /** 当前版本是否能发布（lite / ylb 没有这个能力） */
    canPublish: boolean;
  }>();

  const emit = defineEmits<{
    (e: 'publish'): void;
    (e: 'edit', post: EcoPost): void;
    (e: 'detail', post: EcoPost): void;
    (e: 'extend', post: EcoPost): void;
    /** 把页签计数抛给页面，用于「我发布的」入口上的角标 */
    (e: 'counts', counts: Record<string, number>): void;
  }>();

  const { submit, delist, relist } = usePostActions();

  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);
  const activeTab = ref('');
  const keyword = ref('');
  const counts = reactive<Record<string, number>>({});

  const cacheKey = computed(() =>
    props.postType === PostType.CARGO
      ? 'EcosystemMyCargoTable'
      : 'EcosystemMyCapacityTable'
  );

  const emptyText = computed(() =>
    props.postType === PostType.CARGO
      ? '还没发布过货源。配载完成后车不够用？从任务单发布，让同行来接。'
      : '还没发布过运力。有车在等活儿？把空闲的车发到运力大厅，让找车的同行看到。'
  );

  const columns: Columns = [
    {
      prop: 'title',
      label: '信息',
      minWidth: 200,
      formatter: (row: EcoPost) => row.title || row.postNo
    },
    { columnKey: 'route', label: '线路', slot: 'route', minWidth: 190 },
    {
      columnKey: 'quantity',
      label: '规格',
      slot: 'quantity',
      width: 130
    },
    { columnKey: 'price', label: '报价', slot: 'price', width: 150 },
    { columnKey: 'status', label: '状态', slot: 'status', width: 130 },
    {
      prop: 'validUntil',
      label: '展示到',
      width: 140,
      formatter: (row: EcoPost) => row.validUntil || '—'
    },
    { columnKey: 'heat', label: '热度', slot: 'heat', width: 110 },
    {
      columnKey: 'action',
      label: '操作',
      slot: 'action',
      width: 220,
      fixed: 'right',
      align: 'center'
    }
  ];

  const datasource: DatasourceFunction = async ({ pages }) => {
    const result = await pageMyPosts({
      ...pages,
      postType: props.postType,
      statusGroup: activeTab.value || undefined,
      keyword: keyword.value.trim() || undefined
    });
    // 角标跟着当前搜索条件走，所以每次列表刷新都要更新
    Object.keys(counts).forEach((key) => delete counts[key]);
    Object.assign(counts, result.statusCounts ?? {});
    emit('counts', { ...counts });
    return result;
  };

  const reload = () => {
    tableRef.value?.reload?.({ page: 1 });
  };

  function quantityText(row: EcoPost) {
    if (row.postType === PostType.CARGO) {
      return row.totalQuantity
        ? `${row.totalQuantity} ${row.quantityUnit || '台'}`
        : '—';
    }
    const parts: string[] = [];
    if (row.slotCount) parts.push(`${row.slotCount} 位`);
    if (row.truckType) parts.push(row.truckType);
    return parts.join(' ') || '—';
  }

  /**
   * 行操作按状态给，不做「全都列出来再置灰」
   *
   * 置灰的按钮会让人反复点、然后去猜为什么不能点。状态不允许的动作直接不出现，
   * 想知道原因的用户会点开详情——那里有审核结论和下架原因。
   */
  function actionItems(row: EcoPost) {
    const items: any[] = [
      { title: '详情', onClick: () => emit('detail', row) }
    ];
    if (EDITABLE_STATUSES.includes(row.status) && row.sourceId) {
      items.push({ title: '编辑', onClick: () => emit('edit', row) });
    }
    if (SUBMITTABLE_STATUSES.includes(row.status)) {
      items.push({ title: '提交审核', onClick: () => submit(row, reload) });
    }
    if (row.status === PostStatus.LISTED) {
      items.push({ title: '延长', onClick: () => emit('extend', row) });
    }
    if (row.status === PostStatus.DELISTED) {
      items.push({ title: '重新上架', onClick: () => relist(row, reload) });
    }
    if (
      (
        [
          PostStatus.LISTED,
          PostStatus.AUDITING,
          PostStatus.REJECTED,
          PostStatus.DRAFT
        ] as number[]
      ).includes(row.status)
    ) {
      items.push({
        title:
          row.status === PostStatus.DRAFT || row.status === PostStatus.REJECTED
            ? '不发了'
            : '停止展示',
        props: { type: 'danger' },
        onClick: () => delist(row, reload)
      });
    }
    return items;
  }

  defineExpose({ reload });
</script>

<style lang="scss" scoped>
  .eco-mine__bar {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    gap: 12px;
    flex-wrap: wrap;
  }

  .eco-mine__tabs {
    flex: 1 1 auto;
    min-width: 0;

    :deep(.el-tabs__header) {
      margin-bottom: 0;
    }
  }

  .eco-mine__count {
    display: inline-block;
    min-width: 16px;
    margin-left: 2px;
    padding: 0 4px;
    font-size: 11px;
    line-height: 16px;
    text-align: center;
    color: #fff;
    background: var(--el-color-danger);
    border-radius: 8px;
  }

  .eco-mine__tools {
    display: flex;
    align-items: center;
    gap: 8px;
    padding-bottom: 8px;
  }

  .eco-mine__keyword {
    width: 200px;
  }

  .eco-mine__heat {
    color: var(--el-color-warning);

    &.is-quiet {
      color: var(--el-text-color-secondary);
    }
  }
</style>
