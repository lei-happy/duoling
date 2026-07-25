<!--
  商品车配载选择器（左右布局）

  设计：
  - 左侧：待选计划（按线路/客户分组；同计划合并行，可展开按 cargo 行追加台数；主按钮整单加入）
  - 右侧：已选商品车（车型图 + 台数标签只读；可展开查看「每一台」占位明细）
  - 列表区采用 sticky 分组头，避免嵌套 flex 内部高度塌陷

  业务偏好：相同起终点(线路) > 同品牌车型 > 台数充裕
-->
<template>
  <div
    class="cargo-picker"
    :class="{ 'cargo-picker--page': layout === 'page' }"
  >
    <!-- ========================== 左侧：待选 ========================== -->
    <div class="cargo-picker__left">
      <div class="cargo-picker__panel-header">
        <span class="cargo-picker__panel-title">待选计划</span>
        <el-tag
          size="small"
          type="info"
          effect="plain"
          :title="candidateStatsTitle"
        >
          共 {{ candidateStats.waybillCount }} 单 /
          {{ candidateStats.quantityTotal }} 台
        </el-tag>
        <el-radio-group
          v-model="groupMode"
          size="small"
          class="cargo-picker__group-mode"
        >
          <el-radio-button value="route">按线路</el-radio-button>
          <el-radio-button value="customer">按客户</el-radio-button>
        </el-radio-group>
        <el-tooltip
          v-if="showPaginationTip"
          placement="top"
          :content="paginationTipText"
        >
          <el-icon class="cargo-picker__page-tip-icon" tabindex="-1">
            <QuestionCircleOutlined />
          </el-icon>
        </el-tooltip>
        <div class="cargo-picker__flex-spacer"></div>
        <el-button
          v-if="layout === 'page'"
          link
          type="primary"
          size="small"
          class="cargo-picker__help-btn"
          @click="helpDialogVisible = true"
        >
          <el-icon><InfoFilled /></el-icon>
          操作说明
        </el-button>
        <el-button v-else :icon="Refresh" size="small" @click="loadCandidates">
          刷新
        </el-button>
      </div>

      <div class="cargo-picker__filter">
        <el-input
          v-model="filter.keyword"
          placeholder="计划号 / 客户"
          clearable
          size="small"
          style="width: 170px"
          @change="resetAndLoadCandidates"
        />
        <el-input
          v-model="filter.originKeyword"
          placeholder="起点关键词"
          clearable
          size="small"
          style="width: 140px"
          @change="resetAndLoadCandidates"
        />
        <el-input
          v-model="filter.destinationKeyword"
          placeholder="终点关键词"
          clearable
          size="small"
          style="width: 140px"
          @change="resetAndLoadCandidates"
        />
        <el-input
          v-model="filter.modelKeyword"
          placeholder="品牌/车型"
          clearable
          size="small"
          style="width: 130px"
          @change="resetAndLoadCandidates"
        />
      </div>

      <div v-loading="loading" class="cargo-picker__scroll">
        <el-empty
          v-if="!loading && !groupedCandidates.length"
          description="暂无符合条件的候选计划"
          :image-size="80"
        />

        <div
          v-for="group in groupedCandidates"
          :key="group.key"
          class="cargo-group"
        >
          <div class="cargo-group__header" @click="toggleGroup(group.key)">
            <el-icon
              class="cargo-group__caret"
              :class="{ 'is-collapsed': collapsedGroups.has(group.key) }"
            >
              <CaretBottom />
            </el-icon>
            <div class="cargo-group__header-main">
              <span class="cargo-group__title" :title="group.title">
                {{ group.title }}
              </span>
              <div class="cargo-group__header-extra">
                <span class="cargo-group__meta">
                  {{ group.totalCount }} 条 · {{ group.totalQuantity }} 台
                </span>
                <el-button
                  type="primary"
                  link
                  size="small"
                  :disabled="group.addableQuantity <= 0"
                  @click.stop="quickFillGroup(group)"
                >
                  <el-icon style="margin-right: 2px"><Top /></el-icon>
                  一键全加
                </el-button>
              </div>
            </div>
          </div>

          <div
            v-show="!collapsedGroups.has(group.key)"
            class="cargo-group__body"
          >
            <template v-for="sub in group.subgroups" :key="sub.key">
              <div
                v-if="
                  groupMode === 'customer' &&
                  (group.subgroups.length > 1 ||
                    (sub.title && sub.title.trim()))
                "
                class="cargo-subheader"
              >
                <span class="cargo-subheader__label">{{ sub.title }}</span>
                <span class="cargo-subheader__meta">
                  {{ sub.totalCount }} 条 · {{ sub.totalQuantity }} 台
                </span>
              </div>
              <div
                v-for="mw in sub.mergedRows"
                :key="mw.key"
                class="cargo-merge"
              >
                <div class="cargo-row">
                  <el-button
                    text
                    class="cargo-merge__toggle"
                    @click.stop="
                      toggleMergeExpand(mergeExpandKey(group.key, mw.key))
                    "
                  >
                    <el-icon
                      class="cargo-merge__toggle-icon"
                      :class="{
                        'is-collapsed': !mergeExpandOpen(group.key, mw.key)
                      }"
                    >
                      <CaretBottom />
                    </el-icon>
                  </el-button>
                  <div class="cargo-row__line1-left">
                    <span
                      class="cargo-row__wb"
                      :title="mw.lines[0]?.waybillNo"
                      >{{
                        mw.lines[0]?.waybillNo || `#${mw.lines[0]?.waybillId}`
                      }}</span
                    >
                    <span class="cargo-row__customer">{{
                      mw.lines[0]?.customerName || '—'
                    }}</span>
                  </div>
                  <span
                    v-if="mw.lines[0]?.waybillCreatedAt"
                    class="cargo-row__created"
                    :title="formatDateTime(mw.lines[0]?.waybillCreatedAt)"
                  >
                    {{ formatDateTime(mw.lines[0]?.waybillCreatedAt) }}
                  </span>
                  <div class="cargo-row__line2">
                    <span class="cargo-row__chip">{{
                      mergedModelSummary(mw)
                    }}</span>
                    <span
                      class="cargo-row__dest"
                      :title="mergedEndPointTitle(mw)"
                    >
                      {{ mergedEndPointLabel(mw) }}
                    </span>
                  </div>
                  <div class="cargo-row__action">
                    <span
                      v-if="mergedRemainingTotal(mw) > 0"
                      class="cargo-row__remaining"
                    >
                      剩
                      <span class="cargo-row__remaining-num">{{
                        mergedRemainingTotal(mw)
                      }}</span>
                    </span>
                    <template v-if="!mergedHasPick(mw)">
                      <el-tooltip
                        content="将该计划下本组全部车型按剩余台数一次性加入右侧"
                        placement="top"
                      >
                        <el-button
                          type="primary"
                          size="small"
                          :disabled="mergedRemainingTotal(mw) <= 0"
                          @click="addMerged(mw)"
                        >
                          整单加入
                        </el-button>
                      </el-tooltip>
                    </template>
                    <el-button
                      v-else
                      type="primary"
                      link
                      size="small"
                      @click="removeMerged(mw)"
                    >
                      撤回
                    </el-button>
                  </div>
                </div>
                <div
                  v-show="mergeExpandOpen(group.key, mw.key)"
                  class="cargo-merge__detail"
                >
                  <div
                    v-for="line in mw.lines"
                    :key="line.cargoId"
                    class="cargo-subline"
                  >
                    <div class="cargo-subline__thumb">
                      <el-image
                        :src="seriesImageUrl(line.seriesImage)"
                        fit="cover"
                        class="cargo-subline__img"
                        lazy
                      >
                        <template #error>
                          <div class="cargo-subline__ph">
                            <el-icon :size="18"><Picture /></el-icon>
                          </div>
                        </template>
                      </el-image>
                    </div>
                    <div class="cargo-subline__main">
                      <div class="cargo-subline__model">
                        {{ line.vehicleBrand || '—' }} /
                        {{ line.vehicleModel || '—' }}
                      </div>
                      <div
                        v-if="line.vin"
                        class="cargo-subline__vin"
                        :title="line.vin"
                      >
                        VIN {{ line.vin }}
                      </div>
                      <div class="cargo-subline__ep">
                        {{ endPointLabel(line) }}
                      </div>
                    </div>
                    <div class="cargo-subline__remain">
                      可再配
                      <span class="cargo-subline__remain-num">{{
                        maxIncrementForLine(line)
                      }}</span>
                      台
                    </div>
                    <div class="cargo-subline__act">
                      <template v-if="maxIncrementForLine(line) > 0">
                        <el-input-number
                          :model-value="incrementDraftFor(line)"
                          :min="1"
                          :max="maxIncrementForLine(line)"
                          :precision="0"
                          size="small"
                          class="cargo-subline__inc"
                          controls-position="right"
                          @update:model-value="
                            (v) =>
                              setIncrementDraft(
                                line,
                                v === undefined ? undefined : Number(v)
                              )
                          "
                        />
                        <el-button
                          type="primary"
                          size="small"
                          @click="addCargoIncrement(line)"
                        >
                          加入
                        </el-button>
                      </template>
                      <template v-if="pickedQty(line) > 0">
                        <el-tag size="small" type="info" effect="plain">
                          已选 {{ pickedQty(line) }} 台
                        </el-tag>
                        <el-button
                          type="primary"
                          link
                          size="small"
                          @click="removeCargoLine(line)"
                        >
                          撤回
                        </el-button>
                      </template>
                    </div>
                  </div>
                </div>
              </div>
            </template>
          </div>
        </div>
      </div>

      <div
        v-if="candidateStats.lineCount > CANDIDATE_PAGE_SIZE"
        class="cargo-picker__pagination"
      >
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="CANDIDATE_PAGE_SIZE"
          :total="candidateStats.lineCount"
          :disabled="loading"
          layout="slot, prev, pager, next"
          small
          background
          @current-change="onCandidatePageChange"
        >
          <span class="cargo-picker__page-total">
            共 {{ candidateStats.quantityTotal }} 台 ·
            {{ candidateStats.lineCount }} 条待配明细
          </span>
        </el-pagination>
      </div>
    </div>

    <!-- ========================== 右侧：已选 ========================== -->
    <div class="cargo-picker__right">
      <div class="cargo-picker__panel-header">
        <span class="cargo-picker__panel-title is-primary">已选商品车</span>
        <el-tag size="small" type="primary" effect="dark">
          {{ pickedWaybillCount }} 条 / {{ totalQuantity }} 台
        </el-tag>
        <div class="cargo-picker__flex-spacer"></div>
        <el-button
          type="danger"
          link
          size="small"
          :disabled="!modelValue.length"
          @click="clearAllPicked"
        >
          清空
        </el-button>
      </div>

      <div v-if="modelValue.length" class="cargo-picker__picked-summary">
        <div v-if="dominantRoute" class="cargo-picker__route-banner">
          <span class="cargo-picker__route-banner-label">主线路</span>
          <span class="cargo-picker__route-banner-text" :title="dominantRoute">
            {{ dominantRoute }}
          </span>
        </div>
        <div class="cargo-picker__summary">
          <el-tag
            v-if="dominantModel"
            size="small"
            type="success"
            effect="plain"
            class="cargo-picker__chip"
          >
            主车型：{{ dominantModel }}
          </el-tag>
          <el-tag
            v-if="routeBreakdown.length > 1"
            size="small"
            type="warning"
            effect="plain"
          >
            混线 {{ routeBreakdown.length }} 条
          </el-tag>
        </div>
      </div>
      <div v-else class="cargo-picker__summary">
        <span class="cargo-picker__summary-hint">
          建议优先选同线路、同车型的计划凑成一板
        </span>
      </div>

      <div class="cargo-picker__scroll cargo-picker__scroll--picked">
        <div v-if="!modelValue.length" class="cargo-picker__picked-empty">
          <el-empty description="尚未选入商品车" :image-size="80" />
        </div>
        <div
          v-for="(p, idx) in modelValue"
          :key="`${p.waybillCargoId}_${idx}`"
          class="picked-block"
          :class="{
            'picked-block--main-route':
              dominantRoute && !routeDiffersFromDominant(p),
            'picked-block--alt-route': routeDiffersFromDominant(p)
          }"
        >
          <div class="picked-row">
            <el-button
              text
              class="picked-block__toggle"
              @click="togglePickedExpand(p.waybillCargoId)"
            >
              <el-icon
                class="picked-block__toggle-icon"
                :class="{
                  'is-collapsed': !pickedExpandOpen(p.waybillCargoId)
                }"
              >
                <CaretBottom />
              </el-icon>
            </el-button>
            <div class="picked-row__thumb">
              <el-image
                :src="pickedSeriesImageUrl(p)"
                fit="cover"
                class="picked-row__img"
                lazy
              >
                <template #error>
                  <div class="picked-row__ph">
                    <el-icon :size="20"><Picture /></el-icon>
                  </div>
                </template>
              </el-image>
            </div>
            <div class="picked-row__main">
              <div class="picked-row__line1">
                <el-tooltip
                  :content="pickWaybillLabel(p)"
                  placement="top"
                  :show-after="300"
                >
                  <span class="picked-row__wb">{{ pickWaybillLabel(p) }}</span>
                </el-tooltip>
                <el-tooltip
                  :content="p.customerName || '—'"
                  placement="top"
                  :show-after="300"
                  :disabled="!p.customerName"
                >
                  <span class="picked-row__customer">{{
                    p.customerName || '—'
                  }}</span>
                </el-tooltip>
              </div>
              <div class="picked-row__line2">
                <span class="picked-row__chip picked-row__chip--model">
                  {{ p.vehicleBrand || '—' }} / {{ p.vehicleModel || '—' }}
                </span>
              </div>
              <div
                v-if="routeDiffersFromDominant(p) && routeOfPicked(p)"
                class="picked-row__route-meta"
              >
                <el-tooltip
                  content="与汇总「主线路」不一致"
                  placement="top"
                  :show-after="300"
                >
                  <el-tag size="small" type="warning" effect="plain">
                    异主线路
                  </el-tag>
                </el-tooltip>
                <span class="picked-row__route-meta-text">
                  <el-tooltip
                    :content="routeOfPicked(p)"
                    placement="top"
                    :show-after="300"
                  >
                    <span class="picked-row__route-meta-text-inner">{{
                      routeOfPicked(p)
                    }}</span>
                  </el-tooltip>
                </span>
              </div>
            </div>
            <div class="picked-row__rest">
              <el-tag type="primary" effect="dark" size="small">
                {{ p.quantity }} 台
              </el-tag>
              <el-select
                v-if="segments && segments.length > 1"
                v-model="p.segmentId"
                size="small"
                clearable
                placeholder="跟随主任务"
                class="picked-row__segment"
                @change="emitPickedRefresh"
              >
                <el-option
                  v-for="seg in segments"
                  :key="seg.segmentNo"
                  :value="seg.segmentNo"
                  :label="`第 ${seg.segmentNo} 段`"
                />
              </el-select>
              <el-button
                type="danger"
                link
                size="small"
                :icon="Close"
                @click="removePick(idx)"
              />
            </div>
          </div>
          <div v-show="pickedExpandOpen(p.waybillCargoId)" class="picked-units">
            <div
              v-for="n in p.quantity"
              :key="`${p.waybillCargoId}_u_${n}`"
              class="picked-unit"
            >
              <span class="picked-unit__idx">第 {{ n }} 台</span>
              <div class="picked-unit__img-wrap">
                <el-image
                  :src="pickedSeriesImageUrl(p)"
                  fit="cover"
                  class="picked-unit__img"
                  lazy
                >
                  <template #error>
                    <div class="picked-unit__ph">
                      <el-icon :size="16"><Picture /></el-icon>
                    </div>
                  </template>
                </el-image>
              </div>
              <div class="picked-unit__main">
                <span class="picked-unit__model">
                  {{ p.vehicleBrand || '—' }} / {{ p.vehicleModel || '—' }}
                </span>
                <span
                  v-if="pickedVinOf(p)"
                  class="picked-unit__vin"
                  :title="pickedVinRaw(p)"
                >
                  VIN {{ formatVinDisplay(pickedVinOf(p)) }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <el-dialog
    v-model="helpDialogVisible"
    width="860px"
    align-center
    append-to-body
    destroy-on-close
    class="cargo-picker-help-dialog"
  >
    <template #header>
      <div class="cargo-picker-help-dialog__header">
        <div class="cargo-picker-help-dialog__header-text">
          <div class="cargo-picker-help-dialog__title">配载建单指南</div>
          <div class="cargo-picker-help-dialog__subtitle">
            从待选计划挑选商品车，快速组成一张任务单
          </div>
        </div>
      </div>
    </template>

    <div class="cargo-picker-help-dialog__body">
      <div class="cargo-picker-help-dialog__steps">
        <template v-for="(step, index) in helpSteps" :key="step.title">
          <div class="cargo-picker-help-dialog__step">
            <div class="cargo-picker-help-dialog__step-head">
              <span class="cargo-picker-help-dialog__step-no">{{
                index + 1
              }}</span>
              <div class="cargo-picker-help-dialog__step-icon">
                <el-icon :size="20"><component :is="step.icon" /></el-icon>
              </div>
            </div>
            <div class="cargo-picker-help-dialog__step-title">{{
              step.title
            }}</div>
            <div class="cargo-picker-help-dialog__step-desc">{{
              step.desc
            }}</div>
          </div>
          <div
            v-if="index < helpSteps.length - 1"
            class="cargo-picker-help-dialog__step-arrow"
            aria-hidden="true"
          >
            <el-icon :size="16"><ArrowRight /></el-icon>
          </div>
        </template>
      </div>

      <div class="cargo-picker-help-dialog__extras">
        <div class="cargo-picker-help-dialog__highlight">
          <div class="cargo-picker-help-dialog__highlight-icon">
            <el-icon :size="18"><Opportunity /></el-icon>
          </div>
          <div>
            <div class="cargo-picker-help-dialog__highlight-title"
              >配载技巧</div
            >
            <div class="cargo-picker-help-dialog__highlight-text">
              建议优先选择<strong>同线路、同车型</strong>的计划凑成一板，减少混装与后续调度成本。
            </div>
          </div>
        </div>

        <div class="cargo-picker-help-dialog__glossary">
          <div class="cargo-picker-help-dialog__glossary-head">
            <el-icon :size="16"><DataLine /></el-icon>
            <span>统计与分页</span>
          </div>
          <div class="cargo-picker-help-dialog__glossary-list">
            <div class="cargo-picker-help-dialog__glossary-item">
              <el-tag size="small" type="primary" effect="plain">单</el-tag>
              <span>待配计划数（去重计划号）</span>
            </div>
            <div class="cargo-picker-help-dialog__glossary-item">
              <el-tag size="small" type="success" effect="plain">台</el-tag>
              <span>待配商品车总台数</span>
            </div>
            <div class="cargo-picker-help-dialog__glossary-item">
              <el-tag size="small" type="info" effect="plain">待配明细</el-tag>
              <span
                >底部分页单位；同一计划多车型会拆成多条，台数才是商品车总数</span
              >
            </div>
          </div>
        </div>
      </div>
    </div>

    <template #footer>
      <el-button type="primary" @click="helpDialogVisible = false">
        开始配载
      </el-button>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
  import { computed, markRaw, onMounted, reactive, ref } from 'vue';
  import { EleMessage } from 'ele-admin-plus';
  import {
    ArrowRight,
    CaretBottom,
    Close,
    DataLine,
    DocumentChecked,
    Filter,
    InfoFilled,
    Opportunity,
    Picture,
    Plus,
    Refresh,
    Top
  } from '@element-plus/icons-vue';
  import { QuestionCircleOutlined } from '@/components/icons';
  import { formatDateTime } from '@/utils/date-util';
  import { formatVinDisplay } from '@/utils/vin-util';
  import { listCandidateWaybills } from '@/api/operation/task';
  import type {
    CandidateCargo,
    TaskSegment,
    TaskWaybillItem
  } from '@/api/operation/task/model';

  type PickedItem = TaskWaybillItem & {
    /** 候选行剩余台数（用于已选面板里动态计算最大可输入） */
    _availableRemaining?: number;
    origin?: string;
    destination?: string;
    vin?: string | null;
  };

  type GroupMode = 'route' | 'customer';

  /** 同分组内同一计划合并展示（底层仍为多 cargo 行） */
  interface MergedWaybillRow {
    key: string;
    lines: CandidateCargo[];
  }

  interface SubGroup {
    key: string;
    title: string;
    mergedRows: MergedWaybillRow[];
    totalCount: number;
    totalQuantity: number;
  }

  interface Group {
    key: string;
    title: string;
    subgroups: SubGroup[];
    totalCount: number;
    totalQuantity: number;
    pickedQuantity: number;
    addableQuantity: number;
  }

  const props = withDefaults(
    defineProps<{
      modelValue: PickedItem[];
      segments: TaskSegment[];
      /** dialog：弹框内固定高度；page：独立页全视口高度 */
      layout?: 'dialog' | 'page';
    }>(),
    { layout: 'dialog' }
  );
  const emit = defineEmits<{
    (e: 'update:modelValue', value: PickedItem[]): void;
  }>();

  const CANDIDATE_PAGE_SIZE = 50;

  const helpDialogVisible = ref(false);

  const helpSteps = [
    {
      icon: markRaw(Filter),
      title: '筛选待配计划',
      desc: '按计划号、起终点、品牌车型等条件缩小范围；支持按线路或按客户分组浏览。'
    },
    {
      icon: markRaw(Plus),
      title: '加入商品车',
      desc: '点击「整单加入」或展开后按台数追加；已选商品车显示在右侧面板，可随时撤回。'
    },
    {
      icon: markRaw(DocumentChecked),
      title: '创建任务单',
      desc: '确认右侧已选台数无误后，点击底部「创建任务单」，请到调度工作台继续分配承运。'
    }
  ];

  const candidates = ref<CandidateCargo[]>([]);
  const candidateStats = reactive({
    waybillCount: 0,
    lineCount: 0,
    quantityTotal: 0,
    truncated: false
  });
  const loading = ref(false);
  const currentPage = ref(1);
  const groupMode = ref<GroupMode>('route');
  const collapsedGroups = ref<Set<string>>(new Set());
  /** 左侧：合并计划行内展开（按 cargo 行追加台数） */
  const expandedMergeKeys = ref<Set<string>>(new Set());
  /** 右侧：已选行展开显示「每一台」占位明细 */
  const expandedPickedCargoIds = ref<Set<number>>(new Set());
  /** cargoId → 本次要追加的台数（1..可再配） */
  const pickIncrementDraft = reactive<Record<number, number>>({});

  const filter = reactive({
    keyword: '',
    originKeyword: '',
    destinationKeyword: '',
    modelKeyword: ''
  });

  onMounted(() => {
    resetAndLoadCandidates();
  });

  const loadCandidates = async () => {
    loading.value = true;
    try {
      const res = await listCandidateWaybills({
        keyword: filter.keyword || undefined,
        originKeyword: filter.originKeyword || undefined,
        destinationKeyword: filter.destinationKeyword || undefined,
        modelKeyword: filter.modelKeyword || undefined,
        offset: (currentPage.value - 1) * CANDIDATE_PAGE_SIZE,
        limit: CANDIDATE_PAGE_SIZE
      });
      candidates.value = res.items || [];
      candidateStats.waybillCount = res.waybillCount ?? 0;
      candidateStats.lineCount = res.lineCount ?? 0;
      candidateStats.quantityTotal = res.quantityTotal ?? 0;
      candidateStats.truncated = Boolean(res.truncated);
      collapsedGroups.value = new Set();
    } catch (e: unknown) {
      const msg = (e as { message?: string }).message || '加载候选失败';
      EleMessage.error({ message: msg, plain: true });
    } finally {
      loading.value = false;
    }
  };

  const resetAndLoadCandidates = async () => {
    currentPage.value = 1;
    await loadCandidates();
  };

  const onCandidatePageChange = async (page: number) => {
    currentPage.value = page;
    await loadCandidates();
  };

  const showPaginationTip = computed(
    () => candidateStats.lineCount > CANDIDATE_PAGE_SIZE
  );

  const paginationTipText = computed(
    () =>
      `待配商品车较多，当前仅展示第 ${currentPage.value} 页。左上角是待配计划数与总台数；底部分页按「待配明细」翻页（同一计划多车型会拆成多条），台数才是商品车总数。可先用上方筛选缩小范围，或翻页继续浏览。`
  );

  const candidateStatsTitle = computed(() => {
    if (candidateStats.lineCount <= CANDIDATE_PAGE_SIZE) {
      return `当前筛选条件下共 ${candidateStats.waybillCount} 个待配计划、${candidateStats.quantityTotal} 台商品车（${candidateStats.lineCount} 条待配明细）`;
    }
    return `共 ${candidateStats.waybillCount} 个待配计划、${candidateStats.quantityTotal} 台商品车；列表按每页 ${CANDIDATE_PAGE_SIZE} 条待配明细分页`;
  });

  function routeKeyOf(c: CandidateCargo): string {
    return `${c.origin || '未填'}__${c.destination || '未填'}`;
  }
  function routeTitleOf(c: CandidateCargo): string {
    return `${c.origin || '未填起点'} → ${c.destination || '未填终点'}`;
  }
  function customerKeyOf(c: CandidateCargo): string {
    if (c.customerId != null) {
      return `id:${c.customerId}`;
    }
    return `name:${c.customerName || '未填客户'}`;
  }
  function customerTitleOf(c: CandidateCargo): string {
    return c.customerName || '未填客户';
  }

  /** 行内展示的终点/交车点文案 */
  function endPointLabel(c: CandidateCargo): string {
    const d = c.dealerName?.trim();
    if (d) return d;
    const dest = c.destination?.trim();
    if (dest) return dest;
    return '—';
  }

  function endPointTitle(c: CandidateCargo): string {
    const parts = [c.destination, c.dealerName].filter(
      (x) => x && String(x).trim()
    ) as string[];
    return parts.join(' · ') || '';
  }

  /** 与计划货物明细弹窗一致：相对路径补前缀 */
  function resolveMediaUrl(p?: string | null): string {
    const s = p?.trim();
    if (!s) return '';
    if (s.startsWith('http://') || s.startsWith('https://')) return s;
    return s.startsWith('/') ? s : `/${s}`;
  }

  function seriesImageUrl(p?: string | null): string {
    return resolveMediaUrl(p);
  }

  function mergedLinesRemaining(m: MergedWaybillRow): number {
    return m.lines.reduce((s, c) => s + (c.remainingQuantity || 0), 0);
  }

  /** 同一分组（同线路+同客户 或 同客户+同线路）内按计划号合并 */
  function mergeLinesByWaybill(raw: CandidateCargo[]): MergedWaybillRow[] {
    const map = new Map<number, CandidateCargo[]>();
    for (const c of raw) {
      let lines = map.get(c.waybillId);
      if (!lines) {
        lines = [];
        map.set(c.waybillId, lines);
      }
      lines.push(c);
    }
    const merged: MergedWaybillRow[] = [];
    for (const [waybillId, lines] of map) {
      lines.sort((a, b) => b.remainingQuantity - a.remainingQuantity);
      merged.push({ key: `wb_${waybillId}`, lines });
    }
    merged.sort((a, b) => {
      const d = mergedLinesRemaining(b) - mergedLinesRemaining(a);
      if (d !== 0) return d;
      const wa = a.lines[0]?.waybillNo || '';
      const wb = b.lines[0]?.waybillNo || '';
      return wa.localeCompare(wb, 'zh-CN');
    });
    return merged;
  }

  function mergedModelSummary(m: MergedWaybillRow): string {
    const parts = m.lines.map(
      (l) => `${l.vehicleBrand || '—'} / ${l.vehicleModel || '—'}`
    );
    return [...new Set(parts)].join('、');
  }

  function mergedEndPointLabel(m: MergedWaybillRow): string {
    const labels = m.lines
      .map((l) => endPointLabel(l))
      .filter((x) => x && x !== '—');
    return [...new Set(labels)].join(' · ') || '—';
  }

  function mergedEndPointTitle(m: MergedWaybillRow): string {
    const titles = m.lines
      .map((l) => endPointTitle(l))
      .filter((x) => x && String(x).trim());
    return [...new Set(titles)].join('；') || '';
  }

  const pickedQty = (row: CandidateCargo): number => {
    const p = (props.modelValue || []).find(
      (x) => x.waybillCargoId === row.cargoId
    );
    return p?.quantity || 0;
  };

  function upsertPickedQuantity(
    list: PickedItem[],
    row: CandidateCargo,
    qty: number
  ): PickedItem[] {
    const cap = row.remainingQuantity;
    const q = Math.max(0, Math.min(Math.floor(qty), cap));
    const i = list.findIndex((x) => x.waybillCargoId === row.cargoId);
    const next = [...list];
    if (q <= 0) {
      if (i >= 0) next.splice(i, 1);
      return next;
    }
    const patch = {
      waybillId: row.waybillId,
      waybillCargoId: row.cargoId,
      waybillNo: row.waybillNo,
      customerId: row.customerId,
      customerName: row.customerName,
      vehicleBrand: row.vehicleBrand,
      vehicleModel: row.vehicleModel,
      dealerName: row.dealerName,
      origin: row.origin,
      destination: row.destination,
      vin: row.vin,
      quantity: q,
      _availableRemaining: cap,
      seriesImage: row.seriesImage
    };
    if (i >= 0) {
      next[i] = {
        ...next[i],
        ...patch,
        segmentId: next[i].segmentId,
        seriesImage: row.seriesImage ?? next[i].seriesImage
      };
    } else {
      next.push({
        ...patch,
        segmentId: undefined
      } as PickedItem);
    }
    return next;
  }

  function maxIncrementForLine(row: CandidateCargo): number {
    return Math.max(0, row.remainingQuantity - pickedQty(row));
  }

  function incrementDraftFor(row: CandidateCargo): number {
    const m = maxIncrementForLine(row);
    if (m <= 0) return 1;
    const k = row.cargoId;
    let v = pickIncrementDraft[k];
    if (v == null || v < 1 || v > m) {
      v = Math.min(1, m);
      pickIncrementDraft[k] = v;
    }
    return pickIncrementDraft[k] ?? 1;
  }

  function setIncrementDraft(row: CandidateCargo, v: number | undefined): void {
    const m = maxIncrementForLine(row);
    if (m <= 0) return;
    const n = Math.min(m, Math.max(1, Math.floor(Number(v) || 1)));
    pickIncrementDraft[row.cargoId] = n;
  }

  function addCargoIncrement(row: CandidateCargo): void {
    const inc = incrementDraftFor(row);
    const cur = pickedQty(row);
    const nextQty = Math.min(row.remainingQuantity, cur + inc);
    const list = upsertPickedQuantity(
      [...(props.modelValue || [])],
      row,
      nextQty
    );
    emit('update:modelValue', list);
    const left = Math.max(0, row.remainingQuantity - nextQty);
    if (left <= 0) delete pickIncrementDraft[row.cargoId];
    else pickIncrementDraft[row.cargoId] = Math.min(left, 1);
  }

  function removeCargoLine(row: CandidateCargo): void {
    const list = upsertPickedQuantity([...(props.modelValue || [])], row, 0);
    emit('update:modelValue', list);
    delete pickIncrementDraft[row.cargoId];
  }

  function mergedHasPick(m: MergedWaybillRow): boolean {
    return m.lines.some((c) => pickedQty(c) > 0);
  }

  /** 计划合并行：扣除右侧已选后，仍可再配入的台数 */
  function mergedRemainingTotal(m: MergedWaybillRow): number {
    return m.lines.reduce((s, c) => s + maxIncrementForLine(c), 0);
  }

  const groupedCandidates = computed<Group[]>(() => {
    const list = candidates.value;
    if (!list.length) return [];

    const primary = groupMode.value === 'route' ? routeKeyOf : customerKeyOf;
    const primaryTitle =
      groupMode.value === 'route' ? routeTitleOf : customerTitleOf;
    const secondary = groupMode.value === 'route' ? customerKeyOf : routeKeyOf;
    const secondaryTitle =
      groupMode.value === 'route' ? customerTitleOf : routeTitleOf;

    const pickedMap = new Map<number, number>();
    (props.modelValue || []).forEach((p) => {
      pickedMap.set(p.waybillCargoId, p.quantity || 0);
    });

    type AccSub = { key: string; title: string; raw: CandidateCargo[] };
    type AccGrp = { key: string; title: string; subs: Map<string, AccSub> };

    const groupsMap = new Map<string, AccGrp>();
    for (const c of list) {
      const gKey = primary(c);
      let g = groupsMap.get(gKey);
      if (!g) {
        g = { key: gKey, title: primaryTitle(c), subs: new Map() };
        groupsMap.set(gKey, g);
      }
      const sKey = secondary(c);
      let sg = g.subs.get(sKey);
      if (!sg) {
        sg = { key: sKey, title: secondaryTitle(c), raw: [] };
        g.subs.set(sKey, sg);
      }
      sg.raw.push(c);
    }

    const groups: Group[] = [];
    for (const g of groupsMap.values()) {
      const subgroups: SubGroup[] = [];
      let totalCount = 0;
      let totalQuantity = 0;
      let pickedQuantity = 0;
      let addableQuantity = 0;

      const subsArr = Array.from(g.subs.values());
      for (const sg of subsArr) {
        const mergedRows = mergeLinesByWaybill(sg.raw);
        const sq = mergedRows.reduce((s, m) => s + mergedLinesRemaining(m), 0);
        const sc = mergedRows.length;

        for (const m of mergedRows) {
          for (const c of m.lines) {
            const pickedQ = pickedMap.get(c.cargoId) || 0;
            if (pickedQ > 0) pickedQuantity += pickedQ;
            addableQuantity += Math.max(0, c.remainingQuantity - pickedQ);
          }
        }

        subgroups.push({
          key: sg.key,
          title: sg.title,
          mergedRows,
          totalCount: sc,
          totalQuantity: sq
        });
        totalCount += sc;
        totalQuantity += sq;
      }

      groups.push({
        key: g.key,
        title: g.title,
        subgroups,
        totalCount,
        totalQuantity,
        pickedQuantity,
        addableQuantity
      });
    }

    groups.sort((a, b) => {
      // 不要用 addableQuantity 排序：会随右侧已选变化，导致左侧分组/计划行「跳动」
      const dq = b.totalQuantity - a.totalQuantity;
      if (dq !== 0) return dq;
      return String(a.title).localeCompare(String(b.title), 'zh-CN');
    });
    groups.forEach((g) => {
      g.subgroups.sort((a, b) => {
        const d = b.totalQuantity - a.totalQuantity;
        if (d !== 0) return d;
        return String(a.title).localeCompare(String(b.title), 'zh-CN');
      });
    });
    return groups;
  });

  const toggleGroup = (key: string) => {
    const next = new Set(collapsedGroups.value);
    if (next.has(key)) next.delete(key);
    else next.add(key);
    collapsedGroups.value = next;
  };

  function mergeExpandKey(groupKey: string, mwKey: string): string {
    return `${groupKey}|${mwKey}`;
  }

  function mergeExpandOpen(groupKey: string, mwKey: string): boolean {
    return expandedMergeKeys.value.has(mergeExpandKey(groupKey, mwKey));
  }

  function toggleMergeExpand(key: string): void {
    const next = new Set(expandedMergeKeys.value);
    if (next.has(key)) next.delete(key);
    else next.add(key);
    expandedMergeKeys.value = next;
  }

  function pickedExpandOpen(cargoId: number): boolean {
    return expandedPickedCargoIds.value.has(cargoId);
  }

  function togglePickedExpand(cargoId: number): void {
    const next = new Set(expandedPickedCargoIds.value);
    if (next.has(cargoId)) next.delete(cargoId);
    else next.add(cargoId);
    expandedPickedCargoIds.value = next;
  }

  const emitPickedRefresh = () => {
    emit('update:modelValue', [...(props.modelValue || [])]);
  };

  const addMerged = (m: MergedWaybillRow) => {
    let list = [...(props.modelValue || [])];
    for (const row of m.lines) {
      if (row.remainingQuantity <= 0) continue;
      list = upsertPickedQuantity(list, row, row.remainingQuantity);
    }
    emit('update:modelValue', list);
  };

  const removeMerged = (m: MergedWaybillRow) => {
    let list = [...(props.modelValue || [])];
    for (const row of m.lines) {
      list = upsertPickedQuantity(list, row, 0);
      delete pickIncrementDraft[row.cargoId];
    }
    emit('update:modelValue', list);
  };

  const removePick = (idx: number) => {
    const cur = props.modelValue[idx];
    const next = [...(props.modelValue || [])];
    next.splice(idx, 1);
    if (cur?.waybillCargoId != null) {
      const idSet = new Set(expandedPickedCargoIds.value);
      idSet.delete(cur.waybillCargoId);
      expandedPickedCargoIds.value = idSet;
    }
    emit('update:modelValue', next);
  };

  const clearAllPicked = () => {
    expandedPickedCargoIds.value = new Set();
    emit('update:modelValue', []);
  };

  const quickFillGroup = (group: Group) => {
    let list = [...(props.modelValue || [])];
    let touchedCount = 0;

    group.subgroups.forEach((sg) => {
      sg.mergedRows.forEach((mw) => {
        mw.lines.forEach((row) => {
          if (row.remainingQuantity <= 0) return;
          const before = list.find((x) => x.waybillCargoId === row.cargoId);
          const prevQty = before?.quantity || 0;
          list = upsertPickedQuantity(list, row, row.remainingQuantity);
          const after = list.find((x) => x.waybillCargoId === row.cargoId);
          const newQty = after?.quantity || 0;
          if (newQty > prevQty) {
            touchedCount += 1;
          }
        });
      });
    });

    if (touchedCount === 0) {
      EleMessage.info({ message: '本组候选已全部加入', plain: true });
      return;
    }
    emit('update:modelValue', list);
    const cumulativeQuantity = list.reduce((s, x) => s + (x.quantity || 0), 0);
    EleMessage.success({
      message: `已加入/更新 ${touchedCount} 条，共 ${cumulativeQuantity} 台`,
      plain: true
    });
  };

  const totalQuantity = computed(() =>
    (props.modelValue || []).reduce((s, x) => s + (x.quantity || 0), 0)
  );

  const pickedWaybillCount = computed(() => {
    const ids = new Set(
      (props.modelValue || []).map((x) => x.waybillId).filter(Boolean)
    );
    return ids.size;
  });

  const candidateById = computed(() => {
    const m = new Map<number, CandidateCargo>();
    candidates.value.forEach((c) => m.set(c.cargoId, c));
    return m;
  });

  function pickedSeriesImageUrl(p: PickedItem): string {
    return seriesImageUrl(
      p.seriesImage ?? candidateById.value.get(p.waybillCargoId)?.seriesImage
    );
  }

  function routeOfPicked(p: PickedItem): string {
    const c = candidateById.value.get(p.waybillCargoId);
    const o = p.origin ?? c?.origin ?? '';
    const d = p.destination ?? c?.destination ?? '';
    if (!o && !d) return '';
    return `${o || '未填'} → ${d || '未填'}`;
  }

  function pickedVinOf(p: PickedItem): string {
    return (
      p.vin ??
      candidateById.value.get(p.waybillCargoId)?.vin ??
      ''
    ).trim();
  }

  function pickedVinRaw(p: PickedItem): string {
    return pickedVinOf(p);
  }

  function dominantOf(keyFn: (p: PickedItem) => string): string | null {
    if (!props.modelValue?.length) return null;
    const m = new Map<string, number>();
    props.modelValue.forEach((p) => {
      const k = (keyFn(p) || '').trim();
      if (!k || k === '/' || k === '→' || k === '— / —' || k === '— → —') {
        return;
      }
      m.set(k, (m.get(k) || 0) + (p.quantity || 0));
    });
    if (!m.size) return null;
    let bestKey = '';
    let bestQty = -1;
    m.forEach((q, k) => {
      if (q > bestQty) {
        bestQty = q;
        bestKey = k;
      }
    });
    return bestKey || null;
  }

  const dominantRoute = computed(() => dominantOf(routeOfPicked));
  const dominantModel = computed(() =>
    dominantOf((p) => `${p.vehicleBrand || ''} / ${p.vehicleModel || ''}`)
  );

  const routeBreakdown = computed<string[]>(() => {
    const set = new Set<string>();
    (props.modelValue || []).forEach((p) => {
      const r = routeOfPicked(p);
      if (r) set.add(r);
    });
    return Array.from(set);
  });

  function pickWaybillLabel(p: PickedItem): string {
    return p.waybillNo || `#${p.waybillCargoId}`;
  }

  /** 已选行起讫是否与汇总「主线路」（按台数加权最多）不一致 */
  function routeDiffersFromDominant(p: PickedItem): boolean {
    const dr = dominantRoute.value;
    if (!dr) return false;
    if ((props.modelValue || []).length < 2) return false;
    if (routeBreakdown.value.length <= 1) return false;
    const mine = routeOfPicked(p);
    if (!mine) return false;
    return mine.trim() !== dr.trim();
  }

  defineExpose({ reload: resetAndLoadCandidates });
</script>

<style lang="scss" scoped>
  // ============================================
  // 整体容器：固定高度，左右两栏各自内部滚动
  // ============================================
  .cargo-picker {
    display: grid;
    grid-template-columns: minmax(0, 1.5fr) minmax(400px, 1fr);
    gap: 12px;
    /* 关键：固定容器高度，让两栏 100% 撑高度，内部 overflow 才能生效 */
    height: 480px;
    max-height: calc(100vh - 280px);
  }

  .cargo-picker.cargo-picker--page {
    flex: 1 1 0;
    min-height: 360px;
    height: auto;
    max-height: none;
  }

  .cargo-picker__flex-spacer {
    flex: 1;
  }

  .cargo-picker__left,
  .cargo-picker__right {
    display: flex;
    flex-direction: column;
    gap: 8px;
    min-width: 0;
    min-height: 0;
    border: 1px solid var(--el-border-color-lighter);
    border-radius: 8px;
    background: var(--el-bg-color);
    padding: 10px;
  }

  .cargo-picker__right {
    border-color: var(--el-color-primary-light-7);
    background: var(--el-color-primary-light-9);
  }

  // ============================================
  // 公共：面板头 / 过滤条 / 滚动容器
  // ============================================
  .cargo-picker__panel-header {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-shrink: 0;
  }

  .cargo-picker__panel-title {
    font-size: 14px;
    font-weight: 600;
    color: var(--el-text-color-primary);

    &.is-primary {
      color: var(--el-color-primary);
    }
  }

  .cargo-picker__group-mode {
    flex-shrink: 0;
    margin-left: 4px;
  }

  .cargo-picker__page-tip-icon {
    flex-shrink: 0;
    margin-left: 2px;
    font-size: 15px;
    color: var(--el-text-color-secondary);
    cursor: help;
    vertical-align: middle;

    &:hover {
      color: var(--el-color-primary);
    }
  }

  .cargo-picker__help-btn {
    flex-shrink: 0;

    .el-icon {
      margin-right: 4px;
    }
  }

  .cargo-picker__filter {
    display: flex;
    align-items: center;
    gap: 6px;
    flex-wrap: wrap;
    flex-shrink: 0;
  }

  .cargo-picker__pagination {
    display: flex;
    justify-content: flex-end;
    flex-shrink: 0;
    padding-top: 4px;
    border-top: 1px solid var(--el-border-color-lighter);
  }

  .cargo-picker__page-total {
    margin-right: 8px;
    font-size: 12px;
    color: var(--el-text-color-regular);
    white-space: nowrap;
  }

  .cargo-picker__summary {
    display: flex;
    align-items: center;
    gap: 6px;
    flex-wrap: wrap;
    min-height: 22px;
    flex-shrink: 0;
  }

  .cargo-picker__picked-summary {
    display: flex;
    flex-direction: column;
    gap: 6px;
    flex-shrink: 0;
  }

  .cargo-picker__route-banner {
    display: flex;
    align-items: flex-start;
    gap: 8px;
    padding: 8px 10px;
    border-radius: 8px;
    background: linear-gradient(
      90deg,
      var(--el-color-primary-light-9),
      var(--el-bg-color)
    );
    border: 1px solid var(--el-color-primary-light-7);
  }

  .cargo-picker__route-banner-label {
    flex-shrink: 0;
    padding: 1px 6px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 700;
    line-height: 1.5;
    color: #fff;
    background: var(--el-color-primary);
  }

  .cargo-picker__route-banner-text {
    flex: 1;
    min-width: 0;
    font-size: 13px;
    font-weight: 600;
    line-height: 1.5;
    color: var(--el-color-primary);
    word-break: break-all;
  }

  .cargo-picker__chip {
    max-width: 100%;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .cargo-picker__summary-hint {
    color: var(--el-text-color-secondary);
    font-size: 12px;
  }

  /* 滚动区：flex:1 配 min-height:0 才能在 flex 父容器里正确 overflow */
  .cargo-picker__scroll {
    flex: 1 1 0;
    min-height: 0;
    overflow-y: auto;
    overflow-x: hidden;
    display: flex;
    flex-direction: column;
    gap: 8px;
    padding-right: 4px;
  }

  .cargo-picker__scroll--picked {
    gap: 6px;
  }

  .cargo-picker__picked-empty {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    min-height: 180px;
  }

  // ============================================
  // 左侧：分组卡
  // ============================================
  .cargo-group {
    border: 1px solid var(--el-border-color-lighter);
    border-radius: 8px;
    overflow: hidden;
    background: var(--el-bg-color);
    flex-shrink: 0;
  }

  .cargo-group__header {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 12px;
    background: var(--el-fill-color-light);
    border-bottom: 1px solid var(--el-border-color-lighter);
    cursor: pointer;
    user-select: none;
    position: sticky;
    top: 0;
    z-index: 1;
    transition: background 0.15s;
    &:hover {
      background: var(--el-fill-color);
    }
  }

  .cargo-group__caret {
    flex-shrink: 0;
    font-size: 14px;
    transition: transform 0.2s;
    &.is-collapsed {
      transform: rotate(-90deg);
    }
  }

  .cargo-group__header-main {
    flex: 1;
    min-width: 0;
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .cargo-group__title {
    flex: 1;
    min-width: 0;
    font-weight: 600;
    color: var(--el-text-color-primary);
    font-size: 13px;
    line-height: 1.4;
    white-space: nowrap;
  }

  .cargo-group__header-extra {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-shrink: 0;
  }

  .cargo-group__meta {
    flex-shrink: 0;
    color: var(--el-text-color-secondary);
    font-size: 12px;
    white-space: nowrap;
  }

  .cargo-group__body {
    display: flex;
    flex-direction: column;
  }

  .cargo-subheader {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 4px 14px;
    background: var(--el-fill-color-blank);
    font-size: 12px;
    color: var(--el-text-color-regular);
    border-top: 1px dashed var(--el-border-color-lighter);
    &:first-child {
      border-top: 0;
    }
  }

  .cargo-subheader__label {
    font-weight: 500;
  }

  .cargo-subheader__meta {
    color: var(--el-text-color-secondary);
  }

  .cargo-merge {
    border-top: 1px solid var(--el-fill-color);
    &:first-child {
      border-top: 0;
    }
  }

  .cargo-merge .cargo-row {
    border-top: 0;
  }

  .cargo-merge__toggle {
    grid-column: 1;
    grid-row: 1 / 3;
    align-self: start;
    flex-shrink: 0;
    width: 28px;
    padding: 0;
    margin: 2px 0 0 -4px;
    color: var(--el-text-color-secondary);
  }

  .cargo-merge__toggle-icon {
    font-size: 14px;
    transition: transform 0.2s;
    &.is-collapsed {
      transform: rotate(-90deg);
    }
  }

  .cargo-merge__detail {
    padding: 0 10px 8px 38px;
    background: var(--el-fill-color-blank);
    border-top: 1px dashed var(--el-border-color-extra-light);
  }

  .cargo-subline {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 6px 0;
    border-top: 1px solid var(--el-border-color-extra-light);
    &:first-child {
      border-top: 0;
    }
  }

  .cargo-subline__thumb {
    flex-shrink: 0;
    width: 48px;
    aspect-ratio: 133 / 100;
    border-radius: 6px;
    overflow: hidden;
    border: 1px solid var(--el-border-color-lighter);
    background: var(--el-fill-color);
    line-height: 0;
  }

  .cargo-subline__img {
    width: 100%;
    height: 100%;
    display: block;
  }

  .cargo-subline__thumb :deep(.el-image__inner),
  .cargo-subline__thumb :deep(.el-image__wrapper) {
    width: 100% !important;
    height: 100% !important;
  }

  .cargo-subline__ph {
    width: 100%;
    height: 100%;
    min-height: 0;
    border-radius: 0;
    border: none;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--el-text-color-placeholder);
    background: var(--el-fill-color-light);
  }

  .cargo-subline__main {
    flex: 1;
    min-width: 0;
  }

  .cargo-subline__model {
    font-size: 13px;
    font-weight: 500;
    color: var(--el-text-color-primary);
  }

  .cargo-subline__vin {
    font-size: 12px;
    font-family:
      ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono',
      'Courier New', monospace;
    color: var(--el-text-color-secondary);
    margin-top: 2px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .cargo-subline__ep {
    font-size: 12px;
    color: var(--el-color-primary);
    font-weight: 500;
    margin-top: 2px;
  }

  .cargo-subline__remain {
    flex-shrink: 0;
    font-size: 12px;
    color: var(--el-text-color-secondary);
  }

  .cargo-subline__remain-num {
    font-weight: 700;
    color: var(--el-color-warning);
    margin: 0 2px;
  }

  .cargo-subline__act {
    display: flex;
    align-items: center;
    gap: 6px;
    flex-shrink: 0;
    flex-wrap: wrap;
    justify-content: flex-end;
  }

  .cargo-subline__inc {
    width: 92px;
  }

  // ============================================
  // 行
  // ============================================
  .cargo-row {
    display: grid;
    grid-template-columns: 28px minmax(0, 1fr) auto;
    grid-template-rows: auto auto;
    align-items: center;
    column-gap: 10px;
    row-gap: 4px;
    padding: 8px 14px;
    min-height: 48px;
    border-top: 1px solid var(--el-fill-color);
    transition: background 0.15s;
    &:first-child {
      border-top: 0;
    }
    &:hover {
      background: var(--el-fill-color-lighter);
    }
  }

  .cargo-row__line1-left {
    grid-column: 2;
    grid-row: 1;
    display: flex;
    align-items: center;
    gap: 8px;
    min-width: 0;
  }

  .cargo-row__created {
    grid-column: 3;
    grid-row: 1;
    justify-self: end;
    font-variant-numeric: tabular-nums;
    color: var(--el-text-color-secondary);
    font-size: 12px;
    white-space: nowrap;
  }

  .cargo-row__line2 {
    grid-column: 2;
    grid-row: 2;
    display: flex;
    align-items: center;
    gap: 6px;
    min-width: 0;
  }

  .cargo-row__wb {
    flex-shrink: 0;
    font-variant-numeric: tabular-nums;
    font-weight: 700;
    color: var(--el-text-color-primary);
    font-size: 13px;
  }

  .cargo-row__customer {
    min-width: 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    color: var(--el-text-color-regular);
    font-size: 13px;
  }

  .cargo-row__chip {
    display: inline-flex;
    align-items: center;
    color: var(--el-text-color-regular);
    font-size: 12px;
    background: var(--el-fill-color);
    padding: 1px 6px;
    border-radius: 4px;
    max-width: 280px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .cargo-row__dest {
    color: var(--el-color-primary);
    font-weight: 600;
    font-size: 13px;
    max-width: 220px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .cargo-row__action {
    grid-column: 3;
    grid-row: 2;
    justify-self: end;
    display: flex;
    align-items: center;
    gap: 8px;
    flex-shrink: 0;
  }

  .cargo-row__remaining {
    display: inline-flex;
    align-items: baseline;
    gap: 2px;
    color: var(--el-text-color-secondary);
    font-size: 12px;
    font-weight: 500;
  }

  .cargo-row__remaining-num {
    display: inline-block;
    min-width: 1.25em;
    padding: 0 5px;
    margin-left: 2px;
    font-size: 14px;
    font-weight: 700;
    font-variant-numeric: tabular-nums;
    color: var(--el-color-warning);
    background: var(--el-color-warning-light-9);
    border-radius: 4px;
    line-height: 1.35;
  }

  // ============================================
  // 右侧：已选行
  // ============================================
  .picked-block {
    border-radius: 8px;
    border: 1px solid var(--el-border-color-lighter);
    background: var(--el-bg-color);
    overflow: hidden;
    flex-shrink: 0;

    &--main-route {
      background: var(--el-color-primary-light-8);
      border-color: var(--el-color-primary-light-5);
      box-shadow: inset 3px 0 0 var(--el-color-primary);

      .picked-row__thumb,
      .picked-unit__img-wrap {
        background: transparent;
        border-color: var(--el-color-primary-light-5);
      }

      .picked-row__ph,
      .picked-unit__ph {
        background: var(--el-color-primary-light-8);
      }

      .picked-row__chip {
        color: var(--el-color-primary);
        background: transparent;
        border: 1px solid var(--el-color-primary-light-5);
      }

      .picked-units {
        border-top-color: var(--el-color-primary-light-5);
      }
    }

    &--alt-route {
      background: var(--el-color-warning-light-8);
      border-color: var(--el-color-warning-light-3);
      box-shadow: inset 3px 0 0 var(--el-color-warning);

      .picked-row__thumb,
      .picked-unit__img-wrap {
        background: transparent;
        border-color: var(--el-color-warning-light-3);
      }

      .picked-row__ph,
      .picked-unit__ph {
        background: var(--el-color-warning-light-8);
      }

      .picked-row__chip {
        color: #ad6800;
        background: transparent;
        border: 1px solid var(--el-color-warning-light-3);
      }

      .picked-units {
        border-top-color: var(--el-color-warning-light-3);
      }
    }
  }

  .picked-row {
    display: flex;
    align-items: flex-start;
    gap: 8px;
    padding: 8px 10px;
  }

  .picked-block__toggle {
    flex-shrink: 0;
    width: 26px;
    padding: 0;
    margin-top: 2px;
    color: var(--el-text-color-secondary);
  }

  .picked-block__toggle-icon {
    font-size: 14px;
    transition: transform 0.2s;
    &.is-collapsed {
      transform: rotate(-90deg);
    }
  }

  .picked-row__thumb {
    flex-shrink: 0;
    width: 56px;
    aspect-ratio: 133 / 100;
    border-radius: 8px;
    overflow: hidden;
    border: 1px solid var(--el-border-color-lighter);
    background: var(--el-fill-color);
    line-height: 0;
  }

  .picked-row__img {
    width: 100%;
    height: 100%;
    display: block;
  }

  .picked-row__thumb :deep(.el-image__inner),
  .picked-row__thumb :deep(.el-image__wrapper) {
    width: 100% !important;
    height: 100% !important;
  }

  .picked-row__ph {
    width: 100%;
    height: 100%;
    min-height: 0;
    border-radius: 0;
    border: none;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--el-text-color-placeholder);
    background: var(--el-fill-color-light);
  }

  .picked-units {
    padding: 4px 10px 10px 46px;
    background: transparent;
    border-top: 1px dashed var(--el-border-color-extra-light);
    display: flex;
    flex-direction: column;
    gap: 6px;
  }

  .picked-unit {
    display: flex;
    align-items: flex-start;
    gap: 8px;
    font-size: 12px;
    color: var(--el-text-color-regular);
  }

  .picked-unit__main {
    flex: 1;
    min-width: 0;
    display: flex;
    flex-direction: column;
    gap: 2px;
  }

  .picked-unit__vin {
    font-size: 11px;
    line-height: 1.45;
    font-variant-numeric: tabular-nums;
    color: var(--el-text-color-secondary);
    word-break: break-all;
  }

  .picked-unit__idx {
    flex-shrink: 0;
    width: 48px;
    color: var(--el-text-color-secondary);
  }

  .picked-unit__img-wrap {
    flex-shrink: 0;
    width: 40px;
    aspect-ratio: 133 / 100;
    border-radius: 6px;
    overflow: hidden;
    border: 1px solid var(--el-border-color-lighter);
    background: var(--el-fill-color);
    line-height: 0;
  }

  .picked-unit__img {
    width: 100%;
    height: 100%;
    display: block;
  }

  .picked-unit__img-wrap :deep(.el-image__inner),
  .picked-unit__img-wrap :deep(.el-image__wrapper) {
    width: 100% !important;
    height: 100% !important;
  }

  .picked-unit__ph {
    width: 100%;
    height: 100%;
    min-height: 0;
    border-radius: 0;
    border: none;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--el-text-color-placeholder);
    background: var(--el-fill-color);
  }

  .picked-unit__model {
    line-height: 1.35;
    font-size: 13px;
    color: var(--el-text-color-regular);
  }

  .picked-row__main {
    flex: 1;
    min-width: 0;
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .picked-row__route-meta {
    display: flex;
    align-items: flex-start;
    gap: 6px;
    margin-top: 2px;
    min-width: 0;
  }

  .picked-row__route-meta-text {
    flex: 1;
    min-width: 0;
  }

  .picked-row__route-meta-text-inner {
    display: block;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    font-size: 11px;
    line-height: 1.45;
    color: var(--el-text-color-secondary);
  }

  .picked-row__line1 {
    display: flex;
    align-items: center;
    gap: 8px;
    min-width: 0;
    flex-wrap: nowrap;
  }

  .picked-row__line2 {
    display: flex;
    flex-direction: column;
    align-items: stretch;
    gap: 4px;
    min-width: 0;
  }

  .picked-row__wb {
    flex: 0 1 auto;
    min-width: 0;
    max-width: 58%;
    font-variant-numeric: tabular-nums;
    font-weight: 600;
    font-size: 13px;
    color: var(--el-text-color-primary);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .picked-row__customer {
    flex: 1 1 0;
    min-width: 0;
    color: var(--el-text-color-regular);
    font-size: 13px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .picked-row__chip {
    display: inline-flex;
    align-items: center;
    align-self: flex-start;
    color: var(--el-text-color-regular);
    font-size: 12px;
    background: var(--el-fill-color);
    padding: 1px 6px;
    border-radius: 4px;
    max-width: 100%;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .picked-row__rest {
    display: flex;
    align-items: center;
    gap: 6px;
    flex-shrink: 0;
    align-self: center;
    padding-top: 1px;
  }

  .picked-row__segment {
    width: 130px;
  }

  // ============================================
  // 窄屏堆叠
  // ============================================
  @media (max-width: 900px) {
    .cargo-picker {
      grid-template-columns: 1fr;
      height: auto;
      max-height: none;
    }
    .cargo-picker.cargo-picker--page {
      min-height: 0;
    }
    .cargo-picker__scroll {
      max-height: 320px;
    }
  }
</style>

<style lang="scss">
  .cargo-picker-help-dialog {
    &.el-dialog {
      margin: auto;
    }

    .el-dialog__header {
      padding: 20px 24px 0;
      margin-right: 0;
    }

    .el-dialog__body {
      padding: 16px 24px 8px;
    }

    .el-dialog__footer {
      padding: 8px 24px 20px;
    }
  }

  .cargo-picker-help-dialog__header {
    display: flex;
    align-items: center;
    gap: 14px;
    padding-right: 28px;
  }

  .cargo-picker-help-dialog__badge {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 48px;
    height: 48px;
    border-radius: 12px;
    color: var(--el-color-primary);
    background: linear-gradient(
      135deg,
      var(--el-color-primary-light-8),
      var(--el-color-primary-light-9)
    );
    box-shadow: inset 0 0 0 1px var(--el-color-primary-light-7);
    flex-shrink: 0;
  }

  .cargo-picker-help-dialog__title {
    font-size: 18px;
    font-weight: 600;
    line-height: 1.3;
    color: var(--el-text-color-primary);
  }

  .cargo-picker-help-dialog__subtitle {
    margin-top: 4px;
    font-size: 13px;
    line-height: 1.5;
    color: var(--el-text-color-secondary);
  }

  .cargo-picker-help-dialog__steps {
    display: flex;
    align-items: stretch;
    gap: 0;
  }

  .cargo-picker-help-dialog__step {
    flex: 1;
    min-width: 0;
    display: flex;
    flex-direction: column;
    gap: 8px;
    padding: 16px 14px;
    border-radius: 10px;
    background: var(--el-fill-color-light);
    border: 1px solid var(--el-border-color-lighter);
  }

  .cargo-picker-help-dialog__step-arrow {
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    width: 28px;
    color: var(--el-text-color-placeholder);
  }

  .cargo-picker-help-dialog__step-head {
    display: flex;
    align-items: center;
    gap: 10px;
  }

  .cargo-picker-help-dialog__step-no {
    width: 24px;
    height: 24px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    font-weight: 700;
    color: #fff;
    background: var(--el-color-primary);
    flex-shrink: 0;
  }

  .cargo-picker-help-dialog__step-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 40px;
    height: 40px;
    border-radius: 10px;
    color: var(--el-color-primary);
    background: var(--el-bg-color);
    box-shadow: inset 0 0 0 1px var(--el-border-color-lighter);
    flex-shrink: 0;
  }

  .cargo-picker-help-dialog__step-title {
    font-size: 14px;
    font-weight: 600;
    line-height: 1.4;
    color: var(--el-text-color-primary);
  }

  .cargo-picker-help-dialog__step-desc {
    margin-top: 0;
    font-size: 13px;
    line-height: 1.6;
    color: var(--el-text-color-regular);
  }

  .cargo-picker-help-dialog__extras {
    display: grid;
    grid-template-columns: 1.1fr 1fr;
    gap: 12px;
    margin-top: 14px;
  }

  .cargo-picker-help-dialog__highlight {
    display: flex;
    gap: 12px;
    margin-top: 0;
    height: 100%;
    box-sizing: border-box;
    padding: 12px 14px;
    border-radius: 10px;
    background: linear-gradient(90deg, #fff7e6, #fffbf0);
    border: 1px solid #ffe7ba;
  }

  .cargo-picker-help-dialog__highlight-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    border-radius: 8px;
    color: #d48806;
    background: rgba(255, 255, 255, 0.72);
    flex-shrink: 0;
  }

  .cargo-picker-help-dialog__highlight-title {
    font-size: 13px;
    font-weight: 600;
    color: #ad6800;
  }

  .cargo-picker-help-dialog__highlight-text {
    margin-top: 4px;
    font-size: 13px;
    line-height: 1.6;
    color: #8c5a00;

    strong {
      font-weight: 600;
    }
  }

  .cargo-picker-help-dialog__glossary {
    margin-top: 0;
    height: 100%;
    box-sizing: border-box;
    padding: 12px 14px;
    border-radius: 10px;
    background: var(--el-fill-color-blank);
    border: 1px dashed var(--el-border-color);
  }

  .cargo-picker-help-dialog__glossary-head {
    display: flex;
    align-items: center;
    gap: 6px;
    margin-bottom: 10px;
    font-size: 13px;
    font-weight: 600;
    color: var(--el-text-color-primary);
  }

  .cargo-picker-help-dialog__glossary-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .cargo-picker-help-dialog__glossary-item {
    display: flex;
    align-items: flex-start;
    gap: 8px;
    font-size: 12px;
    line-height: 1.55;
    color: var(--el-text-color-regular);

    .el-tag {
      flex-shrink: 0;
      margin-top: 1px;
    }
  }

  @media (max-width: 768px) {
    .cargo-picker-help-dialog__steps {
      flex-direction: column;
      gap: 8px;
    }

    .cargo-picker-help-dialog__step-arrow {
      display: none;
    }

    .cargo-picker-help-dialog__extras {
      grid-template-columns: 1fr;
    }
  }
</style>
