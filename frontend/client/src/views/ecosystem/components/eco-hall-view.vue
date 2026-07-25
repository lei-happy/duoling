<!--
  大厅页面主体（货源 / 运力共用）

  两个大厅除了「找货源 / 找运力」这类措辞，交互完全一致：筛选条、卡片流、
  详情抽屉、我发布的。所以页面主体只有这一份，`cargo-hall` 与 `capacity-hall`
  两个入口只负责传 postType 和各自的发布弹层。

  版本门控统一走 `hasFeature`，不判断版本号：后续调整版本与功能的绑定关系时，
  前端零改动（05 §7.1 的注脚）。
-->
<template>
  <ele-page>
    <el-tabs v-model="activeTab" class="eco-hall__tabs">
      <el-tab-pane :name="'browse'">
        <template #label>
          {{ isCargo ? '找货源' : '找运力' }}
        </template>
      </el-tab-pane>
      <el-tab-pane :name="'mine'">
        <template #label>
          我发布的
          <span v-if="mineCount" class="eco-hall__count">{{ mineCount }}</span>
        </template>
      </el-tab-pane>
    </el-tabs>

    <template v-if="activeTab === 'browse'">
      <eco-hall-filter
        :post-type="postType"
        :filters="filters"
        @search="onSearch"
      />

      <ele-card :body-style="{ paddingTop: '12px' }">
        <div class="eco-hall__toolbar">
          <div class="eco-hall__summary">
            <span v-if="total">
              为你找到 {{ total }} 条{{ isCargo ? '货源' : '运力' }}
            </span>
          </div>
          <div class="eco-hall__toolbar-right">
            <el-select
              v-model="sortBy"
              class="eco-hall__sort"
              @change="loadList(1)"
            >
              <el-option
                v-for="item in sortOptions"
                :key="item.value"
                :label="item.label"
                :value="item.value"
              />
            </el-select>
            <el-button type="primary" @click="onPublishClick">
              {{ isCargo ? '发布货源' : '发布运力' }}
            </el-button>
          </div>
        </div>

        <div v-loading="loading" :element-loading-text="loadingText">
          <div v-if="list.length" class="eco-hall__grid">
            <eco-post-card
              v-for="item in list"
              :key="item.id"
              :post="item"
              :can-contact="canContact"
              @detail="openDetail(item)"
              @upgrade="openUpgrade('intent')"
            />
          </div>
          <eco-empty-state v-else-if="!loading" :description="emptyDescription">
            <el-button v-if="hasCondition" @click="resetAndReload">
              清空筛选条件
            </el-button>
            <el-button type="primary" @click="onPublishClick">
              {{ isCargo ? '发布我的货源' : '发布我的运力' }}
            </el-button>
          </eco-empty-state>
        </div>

        <div v-if="total > 0" class="eco-hall__pagination">
          <el-pagination
            v-model:current-page="page"
            v-model:page-size="pageSize"
            :total="total"
            :page-sizes="[12, 24, 48]"
            layout="total, sizes, prev, pager, next, jumper"
            background
            @current-change="loadList()"
            @size-change="loadList(1)"
          />
        </div>
      </ele-card>
    </template>

    <ele-card v-else :body-style="{ paddingTop: '8px' }">
      <eco-my-posts
        v-if="canPublish"
        ref="mineRef"
        :post-type="postType"
        :can-publish="canPublish"
        @publish="emit('publish')"
        @edit="(post) => emit('edit', post)"
        @detail="openMineDetail"
        @extend="openExtend"
        @counts="onMineCounts"
      />
      <eco-empty-state
        v-else
        :description="
          isCargo
            ? '发布货源需要标准版及以上。升级后就能把吃不下的货交给同行，还能看到谁在关注你的信息。'
            : '发布运力需要标准版及以上。升级后可以把空闲的车挂到大厅，让找车的同行主动找你。'
        "
      >
        <el-button type="primary" @click="openUpgrade('publish')">
          了解版本方案
        </el-button>
      </eco-empty-state>
    </ele-card>

    <eco-post-detail
      v-model:visible="detailVisible"
      :post-id="detailPostId"
      :post-type="postType"
      :mine="detailMine"
      :can-contact="canContact"
      @upgrade="openUpgrade('intent')"
      @edit="onDetailEdit"
      @extend="openExtend"
      @done="refreshAll"
    />

    <eco-extend-modal
      v-model:visible="extendVisible"
      :post="extendPost"
      :day-options="filters?.validDaysOptions"
      @done="refreshAll"
    />

    <eco-upgrade-hint
      v-model:visible="upgradeVisible"
      :scene="upgradeScene"
      :post-type="postType"
    />
  </ele-page>
</template>

<script lang="ts" setup>
  import { computed, onMounted, ref } from 'vue';
  import { EleMessage } from 'ele-admin-plus';
  import { getHallFilters, pageHall } from '@/api/ecosystem/hall';
  import { pageMyPosts } from '@/api/ecosystem/post';
  import type {
    EcoHallFilters,
    EcoHallParam,
    EcoPost
  } from '@/api/ecosystem/hall/model';
  import { useUserStore } from '@/store/modules/user';
  import { PostType } from '@/config/ecosystem/enums';
  import EcoHallFilter from './eco-hall-filter.vue';
  import EcoPostCard from './eco-post-card.vue';
  import EcoPostDetail from './eco-post-detail.vue';
  import EcoEmptyState from './eco-empty-state.vue';
  import EcoUpgradeHint from './eco-upgrade-hint.vue';
  import EcoExtendModal from './eco-extend-modal.vue';
  import EcoMyPosts from './eco-my-posts.vue';

  const props = defineProps<{ postType: number }>();

  const emit = defineEmits<{
    /** 发布新的一条（源单由弹层里选） */
    (e: 'publish'): void;
    /** 编辑已有挂牌 */
    (e: 'edit', post: EcoPost): void;
  }>();

  const userStore = useUserStore();

  const isCargo = computed(() => props.postType === PostType.CARGO);

  /** 发布能力：standard 起有，lite / ylb 没有 */
  const canPublish = computed(() =>
    userStore.hasFeature(
      isCargo.value ? 'ecosystem_cargo_publish' : 'ecosystem_capacity_publish'
    )
  );

  /** 主动联系同行是唯一的付费门槛（pro） */
  const canContact = computed(() => userStore.hasFeature('ecosystem_intent'));

  const activeTab = ref('browse');
  const filters = ref<EcoHallFilters | null>(null);

  const loading = ref(false);
  const list = ref<EcoPost[]>([]);
  const total = ref(0);
  const page = ref(1);
  const pageSize = ref(12);
  const sortBy = ref('latest');
  const where = ref<EcoHallParam>({});

  const mineRef = ref<InstanceType<typeof EcoMyPosts> | null>(null);
  const mineCount = ref(0);

  const detailVisible = ref(false);
  const detailPostId = ref<number | null>(null);
  const detailMine = ref(false);

  const extendVisible = ref(false);
  const extendPost = ref<EcoPost | null>(null);

  const upgradeVisible = ref(false);
  const upgradeScene = ref<'intent' | 'publish'>('intent');

  const loadingText = computed(() =>
    isCargo.value ? '正在为你找货源，请稍候…' : '正在为你找运力，请稍候…'
  );

  const sortOptions = computed(
    () => filters.value?.sortOptions ?? [{ value: 'latest', label: '最新发布' }]
  );

  /** 有筛选条件时的空态说的是「换个条件」，没条件时说的是「大厅还冷清」 */
  const hasCondition = computed(() =>
    Object.entries(where.value).some(([, value]) =>
      Array.isArray(value) ? value.length > 0 : value != null && value !== false
    )
  );

  const emptyDescription = computed(() => {
    const subject = isCargo.value ? '货源' : '运力';
    return hasCondition.value
      ? `这些条件下暂时没有合适的${subject}。换个线路或时间试试，也可以先把自己的信息发上来。`
      : `大厅还比较冷清，你可以先发布自己的${subject}，让同行找到你。`;
  });

  const loadFilters = async () => {
    try {
      filters.value = await getHallFilters(props.postType);
    } catch {
      // 筛选项拿不到不影响浏览：只是货类、计价这些下拉暂时为空
      filters.value = null;
    }
  };

  const loadList = async (resetPage?: number) => {
    if (resetPage) {
      page.value = resetPage;
    }
    loading.value = true;
    try {
      const result = await pageHall(props.postType, {
        ...where.value,
        page: page.value,
        limit: pageSize.value,
        sortBy: sortBy.value
      });
      list.value = result.list ?? [];
      total.value = result.total ?? 0;
    } catch (e: any) {
      list.value = [];
      total.value = 0;
      EleMessage.error({
        message: e?.message ?? '没能加载出来，刷新一下试试',
        plain: true
      });
    } finally {
      loading.value = false;
    }
  };

  const onSearch = (params: EcoHallParam) => {
    where.value = params;
    loadList(1);
  };

  const resetAndReload = () => {
    where.value = {};
    loadList(1);
  };

  const openDetail = (post: EcoPost) => {
    detailMine.value = false;
    detailPostId.value = post.id;
    detailVisible.value = true;
  };

  const openMineDetail = (post: EcoPost) => {
    detailMine.value = true;
    detailPostId.value = post.id;
    detailVisible.value = true;
  };

  const onDetailEdit = (post: EcoPost) => {
    detailVisible.value = false;
    emit('edit', post);
  };

  const openExtend = (post: EcoPost) => {
    extendPost.value = post;
    extendVisible.value = true;
  };

  const openUpgrade = (scene: 'intent' | 'publish') => {
    upgradeScene.value = scene;
    upgradeVisible.value = true;
  };

  /**
   * 发布按钮
   *
   * standard 用户在这一屏会同时看到「可用的发布按钮」和「引导态的我要接单」，
   * 这不是 bug——他能发布、能被找到，只是不能主动出击。引导弹层负责把这件事说清。
   */
  const onPublishClick = () => {
    if (canPublish.value) {
      emit('publish');
      return;
    }
    openUpgrade('publish');
  };

  /**
   * 「我发布的」页签角标
   *
   * 只数需要用户动手的两类：被驳回的（要改）和还是草稿的（要提交）。
   * 用总条数当角标会一直挂着一个红点，挂久了就没人看了。
   */
  const setMineCount = (counts: Record<string, number>) => {
    mineCount.value = (counts.rejected ?? 0) + (counts.draft ?? 0);
  };

  const onMineCounts = (counts: Record<string, number>) => {
    setMineCount(counts);
  };

  /** 进页面时先探一次角标，不用等用户点开「我发布的」才知道有条被驳回了 */
  const loadMineCount = async () => {
    if (!canPublish.value) {
      return;
    }
    try {
      const result = await pageMyPosts({
        page: 1,
        limit: 1,
        postType: props.postType
      });
      setMineCount(result.statusCounts ?? {});
    } catch {
      // 角标探测失败不提示：它只是个提醒，不该打断浏览
    }
  };

  const refreshAll = () => {
    if (activeTab.value === 'browse') {
      loadList();
    }
    mineRef.value?.reload?.();
    loadMineCount();
  };

  onMounted(() => {
    loadFilters();
    loadList();
    loadMineCount();
  });

  defineExpose({
    reload: refreshAll,
    switchToMine: () => (activeTab.value = 'mine')
  });
</script>

<style lang="scss" scoped>
  .eco-hall__tabs {
    margin-bottom: 4px;

    :deep(.el-tabs__header) {
      margin-bottom: 8px;
    }

    :deep(.el-tabs__item) {
      font-size: 15px;
    }
  }

  .eco-hall__count {
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

  .eco-hall__toolbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    flex-wrap: wrap;
    margin-bottom: 12px;
  }

  .eco-hall__summary {
    font-size: 13px;
    color: var(--el-text-color-secondary);
  }

  .eco-hall__toolbar-right {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .eco-hall__sort {
    width: 150px;
  }

  .eco-hall__grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
    gap: 12px;
  }

  .eco-hall__pagination {
    display: flex;
    justify-content: flex-end;
    margin-top: 16px;
  }
</style>
