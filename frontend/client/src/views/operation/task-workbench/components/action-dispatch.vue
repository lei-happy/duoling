<!--
  派车弹窗（任务单 status 0 → 1，或已派车后换车）

  自有车 / 社会运力：推荐列表为主路径；右上角搜索过滤。社会运力只选不填，
  司机车牌以运力中心档案为准。社会运力评价推荐落地前先按池列表弱排序。
  承运商：等待 lite 上报；提供调度员代填。
-->
<template>
  <el-dialog
    :model-value="visible"
    :title="title"
    width="760px"
    destroy-on-close
    :close-on-click-modal="false"
    @update:model-value="(v: boolean) => emit('update:visible', v)"
    @open="onOpen"
  >
    <div
      v-if="task"
      class="dispatch-brief"
      :data-type="carrierTypeTone"
      :title="routeFullTitle || undefined"
    >
      <div class="dispatch-brief__route">
        <template v-for="(stop, index) in routeStops" :key="`${stop.cityDistrict}-${index}`">
          <span v-if="index > 0" class="dispatch-brief__arrow" aria-hidden="true">
            →
          </span>
          <span class="dispatch-route-chip">
            <span v-if="stop.province" class="dispatch-route-chip__prov">{{
              stop.province
            }}</span>
            <span class="dispatch-route-chip__city">{{
              stop.cityDistrict
            }}</span>
          </span>
        </template>
      </div>
      <div class="dispatch-brief__meta">
        <span class="dispatch-brief__qty">共 {{ task.totalQuantity || 0 }} 台</span>
        <span class="dispatch-brief__chip" :data-type="carrierTypeTone">
          {{ carrierTypeLabel }}
        </span>
        <span
          v-if="
            form.carrier.carrierType === CARRIER_TYPE.CARRIER &&
            task.carrierName
          "
          class="dispatch-brief__carrier"
        >
          {{ task.carrierName }}
        </span>
        <span class="dispatch-brief__no">{{ task.taskNo }}</span>
      </div>
    </div>

    <el-form
      ref="formRef"
      :model="form"
      label-width="100px"
      v-loading="submitting"
    >
      <template v-if="isListPick">
        <div class="dispatch-rec" :data-type="carrierTypeTone">
          <div class="dispatch-rec__bar">
            <span class="dispatch-rec__title">建议按这个顺序派</span>
            <el-input
              v-model="filterKeyword"
              clearable
              class="dispatch-rec__filter"
              placeholder="搜索全部运力（司机/车牌）"
              @input="onFilterInput"
            >
              <template #prefix>
                <el-icon class="dispatch-rec__search-icon"><Search /></el-icon>
              </template>
            </el-input>
          </div>
          <div
            v-loading="recommendLoading"
            element-loading-text="正在匹配可用运力，请稍候…"
            class="dispatch-rec__list"
          >
            <button
              v-for="item in recommendItems"
              :key="item.capacityId"
              type="button"
              class="dispatch-rec__row"
              :class="{
                'is-selected': pickedResourceId === item.capacityId
              }"
              @click="selectRecommend(item)"
            >
              <span class="dispatch-rec__rank">{{ item.rank }}</span>
              <span class="dispatch-rec__body">
                <span class="dispatch-rec__line">
                  <span class="dispatch-rec__name">{{
                    item.driverName || '未登记司机'
                  }}</span>
                  <span class="dispatch-rec__plate">{{
                    item.plateNumber || '--'
                  }}</span>
                  <el-tag
                    size="small"
                    :type="operationTagType(item)"
                    disable-transitions
                  >
                    {{ operationLabel(item) }}
                  </el-tag>
                </span>
                <span class="dispatch-rec__reason">{{
                  reasonText(item)
                }}</span>
              </span>
            </button>
            <div v-if="!recommendLoading && recommendItems.length === 0" class="dispatch-rec__empty">
              <p>{{ emptyText }}</p>
              <el-button
                v-if="recommendError"
                text
                type="primary"
                @click="loadRecommendations(filterKeyword)"
              >
                重新匹配
              </el-button>
            </div>
          </div>
        </div>

        <div
          class="dispatch-picked"
          :data-type="carrierTypeTone"
          :class="{ 'is-empty': !hasPicked }"
        >
          <template v-if="hasPicked">
            <el-icon class="dispatch-picked__icon"><CircleCheck /></el-icon>
            <div class="dispatch-picked__body">
              <div class="dispatch-picked__meta">
                <span class="dispatch-picked__name">{{
                  selectedItem?.driverName ||
                  form.carrier.mainDriverName ||
                  '未登记司机'
                }}</span>
                <span
                  v-if="
                    selectedItem?.driverPhone || form.carrier.mainDriverPhone
                  "
                  class="dispatch-picked__phone"
                >
                  {{
                    selectedItem?.driverPhone || form.carrier.mainDriverPhone
                  }}
                </span>
                <el-tag
                  v-if="selectedItem"
                  size="small"
                  :type="operationTagType(selectedItem)"
                  disable-transitions
                >
                  {{ operationLabel(selectedItem) }}
                </el-tag>
              </div>
              <div v-if="pickedPlate" class="dispatch-picked__plates">
                <plate-number-tag
                  size="large"
                  :text="pickedPlate"
                  :category="pickedPlateCategory"
                />
                <template v-if="pickedTrailerPlate">
                  <span class="dispatch-picked__plate-plus">+</span>
                  <plate-number-tag
                    size="large"
                    :text="pickedTrailerPlate"
                  />
                </template>
              </div>
            </div>
          </template>
          <template v-else>
            <div class="dispatch-picked__placeholder">
              点上方列表选定运力；名单里没有的，用右上角搜索
            </div>
          </template>
        </div>
      </template>

      <template v-if="form.carrier.carrierType === CARRIER_TYPE.CARRIER">
        <el-alert
          type="info"
          :closable="false"
          style="margin-bottom: 12px"
          :title="`该任务已分配给 ${task?.carrierName || '承运商'}，等待承运商通过 LITE 端上报运力。`"
          description="也可以在下方代填主驾和车牌，点「提交代填运力」直接派车。"
        />
        <div class="dispatch-proxy">
          <div class="dispatch-proxy__title">调度员代填运力</div>
          <el-row :gutter="12">
            <el-col :span="12">
              <el-form-item label="主驾姓名" required>
                <el-input
                  v-model="form.carrier.mainDriverName"
                  placeholder="代填时必填"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="主驾电话" required>
                <el-input
                  v-model="form.carrier.mainDriverPhone"
                  placeholder="代填时必填"
                />
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="12">
            <el-col :span="12">
              <el-form-item label="车牌号" required>
                <el-input
                  v-model="form.carrier.plateNumber"
                  placeholder="代填时必填"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="挂车牌号">
                <el-input v-model="form.carrier.trailerPlateNumber" />
              </el-form-item>
            </el-col>
          </el-row>
        </div>
      </template>

    </el-form>

    <template #footer>
      <el-button @click="emit('update:visible', false)">取消</el-button>
      <template v-if="form.carrier.carrierType === CARRIER_TYPE.CARRIER">
        <el-button :loading="submitting" @click="notifyCarrier">
          通知承运商上报
        </el-button>
        <el-tooltip
          content="请先填齐主驾姓名、电话和车牌"
          placement="top"
          :disabled="hasProxyData"
        >
          <span>
            <el-button
              type="primary"
              :loading="submitting"
              :disabled="!hasProxyData"
              @click="submitProxy"
            >
              提交代填运力
            </el-button>
          </span>
        </el-tooltip>
      </template>
      <el-button v-else type="primary" :loading="submitting" @click="submit">
        {{ confirmLabel }}
      </el-button>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
  import { computed, reactive, ref } from 'vue';
  import type { FormInstance } from 'element-plus';
  import { ElMessageBox } from 'element-plus';
  import { CircleCheck, Search } from '@element-plus/icons-vue';
  import { EleMessage } from 'ele-admin-plus';
  import {
    formatRouteNodesTitle,
    formatRouteTitle,
    parseRegionDisplay
  } from '@/utils/region-display';
  import {
    assignCarrier,
    listCapacityRecommendations
  } from '@/api/operation/task';
  import type {
    CapacityRecommendItem,
    DispatchSelectionFeedback,
    Task,
    TaskCarrierInfo
  } from '@/api/operation/task/model';
  import {
    CARRIER_TYPE,
    CARRIER_TYPE_OPTIONS,
    TASK_STATUS
  } from '../../task/status-config';
  import PlateNumberTag from '@/components/PlateNumberTag/index.vue';
  import type { PlateCategory } from '@/constants/plate-category';

  const OP_IN_TRANSIT = 2;

  const props = defineProps<{
    visible: boolean;
    task: Task | null;
  }>();
  const emit = defineEmits<{
    (e: 'update:visible', v: boolean): void;
    (e: 'done'): void;
  }>();

  const formRef = ref<FormInstance | null>(null);
  const submitting = ref(false);
  const recommendItems = ref<CapacityRecommendItem[]>([]);
  const recommendLoading = ref(false);
  const recommendError = ref(false);
  const filterKeyword = ref('');
  const usedFilter = ref(false);
  const recommendEngine = ref('heuristic_v1');
  const topRecommendedId = ref<number | null>(null);
  const pickedItem = ref<CapacityRecommendItem | null>(null);
  let filterTimer: ReturnType<typeof setTimeout> | null = null;

  const defaultCarrier = (): TaskCarrierInfo => ({
    carrierType: CARRIER_TYPE.SELF,
    capacityId: undefined,
    carrierId: undefined,
    mainDriverName: '',
    mainDriverPhone: '',
    plateNumber: '',
    trailerPlateNumber: '',
    carrierName: '',
    carrierShortName: ''
  });

  const form = reactive({
    carrier: defaultCarrier(),
    isProxy: false
  });

  const isSocial = computed(
    () => form.carrier.carrierType === CARRIER_TYPE.SOCIAL
  );
  const isListPick = computed(
    () =>
      form.carrier.carrierType === CARRIER_TYPE.SELF ||
      form.carrier.carrierType === CARRIER_TYPE.SOCIAL
  );
  const pickedResourceId = computed(() =>
    isSocial.value ? form.carrier.socialDriverId : form.carrier.capacityId
  );
  const toPlateCategory = (raw?: string): PlateCategory | undefined => {
    if (raw === 'BLUE' || raw === 'YELLOW' || raw === 'NEW_ENERGY') {
      return raw;
    }
    return undefined;
  };
  const isReassign = computed(
    () =>
      (props.task?.status ?? TASK_STATUS.PENDING_DISPATCH) ===
        TASK_STATUS.DISPATCHED && !!props.task?.carrierType
  );
  const title = computed(() => (isReassign.value ? '重新派车' : '派车'));
  const confirmLabel = computed(() =>
    isReassign.value ? '确认换车' : '确认派车'
  );
  const routeStops = computed(() => {
    const fromApi = (props.task?.routeNodes ?? [])
      .map((n) => (n ?? '').trim())
      .filter(Boolean);
    const nodes =
      fromApi.length >= 2
        ? fromApi
        : [props.task?.origin, props.task?.destination]
            .map((n) => (n ?? '').trim())
            .filter(Boolean);
    const list = nodes.length ? nodes : ['--'];
    return list.map((raw) => parseRegionDisplay(raw));
  });
  const routeFullTitle = computed(() => {
    const fromApi = formatRouteNodesTitle(props.task?.routeNodes);
    if (fromApi) return fromApi;
    return formatRouteTitle(props.task?.origin, props.task?.destination);
  });

  const hasProxyData = computed(() => {
    const c = form.carrier;
    return !!(
      c.mainDriverName?.trim() &&
      c.mainDriverPhone?.trim() &&
      c.plateNumber?.trim()
    );
  });

  const selectedItem = computed(() => {
    const id = pickedResourceId.value;
    if (pickedItem.value?.capacityId === id) {
      return pickedItem.value;
    }
    return recommendItems.value.find((x) => x.capacityId === id) || null;
  });
  const pickedPlate = computed(
    () => selectedItem.value?.plateNumber || form.carrier.plateNumber || ''
  );
  const pickedPlateCategory = computed(() =>
    toPlateCategory(selectedItem.value?.plateCategory)
  );
  const pickedTrailerPlate = computed(
    () =>
      selectedItem.value?.trailerPlateNumber ||
      form.carrier.trailerPlateNumber ||
      ''
  );

  const hasPicked = computed(
    () => !!pickedResourceId.value && !!(form.carrier.plateNumber || selectedItem.value)
  );

  const selectedSummary = computed(() => {
    const name = form.carrier.mainDriverName?.trim();
    const plate = form.carrier.plateNumber?.trim();
    if (!name && !plate) return '';
    return [name, plate].filter(Boolean).join(' / ');
  });

  const emptyText = computed(() => {
    if (recommendError.value) return '运力列表加载失败，请重试';
    if (filterKeyword.value.trim()) {
      return '运力库里没有找到匹配的司机或车牌，换个关键词再试试';
    }
    return '暂时没有可推荐的运力，用右上角搜索全部运力';
  });

  const carrierTypeLabel = computed(() => {
    const o = CARRIER_TYPE_OPTIONS.find(
      (x) => x.value === form.carrier.carrierType
    );
    return o?.label || '--';
  });
  const carrierTypeTone = computed(() => {
    switch (form.carrier.carrierType) {
      case CARRIER_TYPE.SELF:
        return 'self';
      case CARRIER_TYPE.CARRIER:
        return 'carrier';
      default:
        return 'social';
    }
  });

  const isAssignedOther = (item?: CapacityRecommendItem | null) =>
    Boolean(item?.reasons?.some((r) => r.code === 'ASSIGNED_OTHER'));

  const operationLabel = (item: CapacityRecommendItem | number) => {
    if (typeof item !== 'number' && isAssignedOther(item)) {
      return '已派其他任务';
    }
    const status = typeof item === 'number' ? item : item.operationStatus;
    switch (status) {
      case 1:
        return '可接单';
      case 2:
        return '运输中';
      case 3:
        return '休假';
      case 4:
        return '停运';
      case 5:
        return '维修保养';
      default:
        return '未知';
    }
  };

  const operationTagType = (
    item: CapacityRecommendItem | number
  ): 'success' | 'warning' | 'info' => {
    if (typeof item !== 'number' && isAssignedOther(item)) return 'warning';
    const status = typeof item === 'number' ? item : item.operationStatus;
    if (status === 1) return 'success';
    if (status === 2) return 'warning';
    return 'info';
  };

  const reasonText = (item: CapacityRecommendItem) =>
    (item.reasons || [])
      .map((r) => r.text)
      .filter(Boolean)
      .join(' · ') || '暂无推荐理由';

  const resetRecommendState = () => {
    recommendItems.value = [];
    recommendError.value = false;
    filterKeyword.value = '';
    usedFilter.value = false;
    topRecommendedId.value = null;
    pickedItem.value = null;
    if (filterTimer) {
      clearTimeout(filterTimer);
      filterTimer = null;
    }
  };

  const loadRecommendations = async (keyword = '') => {
    if (!props.task?.id) return;
    recommendLoading.value = true;
    recommendError.value = false;
    try {
      const kw = keyword.trim();
      const res = await listCapacityRecommendations(props.task.id, {
        keyword: kw || undefined,
        limit: kw ? 50 : 20
      });
      recommendEngine.value = res?.engine || 'heuristic_v1';
      recommendItems.value = res?.items || [];
      if (!keyword.trim() && recommendItems.value.length) {
        topRecommendedId.value = recommendItems.value[0].capacityId;
      }
    } catch {
      recommendItems.value = [];
      recommendError.value = true;
    } finally {
      recommendLoading.value = false;
    }
  };

  const onFilterInput = () => {
    usedFilter.value = !!filterKeyword.value.trim();
    if (filterTimer) clearTimeout(filterTimer);
    filterTimer = setTimeout(() => {
      loadRecommendations(filterKeyword.value);
    }, 280);
  };

  const selectRecommend = (item: CapacityRecommendItem) => {
    pickedItem.value = item;
    if (isSocial.value) {
      form.carrier.socialDriverId = item.capacityId;
      form.carrier.capacityId = undefined;
    } else {
      form.carrier.capacityId = item.capacityId;
      form.carrier.socialDriverId = undefined;
    }
    form.carrier.mainDriverName = item.driverName || '';
    form.carrier.mainDriverPhone = item.driverPhone || '';
    form.carrier.mainDriverIdCard = '';
    form.carrier.plateNumber = item.plateNumber || '';
    form.carrier.trailerPlateNumber = item.trailerPlateNumber || '';
  };

  const onOpen = async () => {
    resetRecommendState();
    if (props.task) {
      form.carrier = {
        carrierType: props.task.carrierType || 1,
        capacityId: props.task.capacityId ?? undefined,
        carrierId: props.task.carrierId ?? undefined,
        socialDriverId: props.task.socialDriverId ?? undefined,
        mainDriverName: props.task.mainDriverName || '',
        mainDriverPhone: props.task.mainDriverPhone || '',
        mainDriverIdCard: props.task.mainDriverIdCard || '',
        plateNumber: props.task.plateNumber || '',
        trailerPlateNumber: props.task.trailerPlateNumber || '',
        carrierName: props.task.carrierName || '',
        carrierShortName: props.task.carrierShortName || ''
      };
      form.isProxy = false;
      if (isListPick.value) {
        await loadRecommendations('');
        const preset = recommendItems.value.find(
          (x) => x.capacityId === pickedResourceId.value
        );
        if (preset) pickedItem.value = preset;
      }
    } else {
      form.carrier = defaultCarrier();
      form.isProxy = false;
    }
  };

  const validate = (): string | null => {
    const c = form.carrier;
    if (c.carrierType === CARRIER_TYPE.SELF) {
      if (!c.capacityId) return '请先从列表里选定要派的运力';
    } else if (c.carrierType === CARRIER_TYPE.CARRIER) {
      if (form.isProxy && !hasProxyData.value) {
        return '请填齐主驾姓名、电话和车牌';
      }
    } else if (c.carrierType === CARRIER_TYPE.SOCIAL) {
      if (!c.socialDriverId) return '请先从列表里选定要派的运力';
    }
    return null;
  };

  const buildSelection = (): DispatchSelectionFeedback | undefined => {
    if (!isListPick.value) return undefined;
    const selectedId = pickedResourceId.value ?? null;
    const selected = recommendItems.value.find(
      (x) => x.capacityId === selectedId
    );
    const source: DispatchSelectionFeedback['source'] = usedFilter.value
      ? 'search'
      : 'recommended';
    return {
      engine: recommendEngine.value,
      source,
      shownCapacityIds: recommendItems.value.map((x) => x.capacityId),
      topRecommendedId: topRecommendedId.value,
      selectedCapacityId: selectedId,
      selectedRank: selected?.rank ?? null
    };
  };

  const notifyCarrier = () => {
    EleMessage.info({
      message: '已通知承运商上报运力，请耐心等待。',
      plain: true
    });
    emit('update:visible', false);
  };

  const submitProxy = async () => {
    if (!hasProxyData.value) {
      EleMessage.error({ message: '请填齐主驾姓名、电话和车牌', plain: true });
      return;
    }
    form.isProxy = true;
    await submit();
  };

  const confirmInTransitIfNeeded = async () => {
    const selected = recommendItems.value.find(
      (x) => x.capacityId === pickedResourceId.value
    );
    if (!selected) return true;
    const occupied = isAssignedOther(selected);
    const inTransit = selected.operationStatus === OP_IN_TRANSIT;
    if (!occupied && !inTransit) return true;
    try {
      await ElMessageBox.confirm(
        occupied
          ? '这名司机已派给其他任务，还在待接单或执行中，确认要再派给他吗？'
          : '这辆车还在运输中，确认要派给它吗？',
        '确认派车',
        {
          type: 'warning',
          confirmButtonText: isReassign.value ? '确认换车' : '确认派车',
          cancelButtonText: '再看看'
        }
      );
      return true;
    } catch {
      return false;
    }
  };

  const submit = async () => {
    if (!props.task?.id) {
      emit('update:visible', false);
      return;
    }
    const err = validate();
    if (err) {
      EleMessage.error({ message: err, plain: true });
      return;
    }
    if (isListPick.value) {
      const ok = await confirmInTransitIfNeeded();
      if (!ok) return;
    }

    submitting.value = true;
    try {
      await assignCarrier(props.task.id, {
        carrier: form.carrier,
        isProxy: form.isProxy,
        selection: buildSelection()
      });
      const who = selectedSummary.value;
      EleMessage.success({
        message: who
          ? `已派给 ${who}`
          : isReassign.value
            ? '换车成功'
            : '派车成功',
        plain: true
      });
      emit('done');
      emit('update:visible', false);
    } catch (e: unknown) {
      const msg = (e as { message?: string }).message || '派车没有完成，请稍后重试';
      EleMessage.error({ message: msg, plain: true });
    } finally {
      submitting.value = false;
    }
  };
</script>

<style lang="scss" scoped>
  .dispatch-brief {
    margin-bottom: 16px;
    padding: 16px 18px;
    border: 1px solid var(--el-color-primary-light-5);
    border-radius: 12px;
    background: linear-gradient(
      135deg,
      var(--el-color-primary-light-9) 0%,
      var(--el-fill-color-light) 48%,
      var(--el-bg-color) 100%
    );

    &[data-type='social'] {
      border-color: var(--el-color-warning-light-5);
      background: linear-gradient(
        135deg,
        var(--el-color-warning-light-9) 0%,
        var(--el-fill-color-light) 48%,
        var(--el-bg-color) 100%
      );
    }

    &__route {
      display: flex;
      flex-wrap: wrap;
      align-items: flex-end;
      gap: 8px 10px;
      margin-bottom: 12px;
    }

    &__arrow {
      display: inline-flex;
      align-items: center;
      height: 22px;
      font-size: 16px;
      line-height: 22px;
      color: var(--el-text-color-placeholder);
      transform: translateY(-3px);
      user-select: none;
    }

    &__meta {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 8px;
    }

    &__qty {
      display: inline-flex;
      align-items: center;
      padding: 4px 10px;
      border-radius: 999px;
      font-size: 12px;
      font-weight: 600;
      color: var(--el-color-white);
      background: var(--el-color-primary);
    }

    &__no {
      margin-left: auto;
      font-size: 12px;
      font-variant-numeric: tabular-nums;
      color: var(--el-text-color-secondary);
    }

    &__chip {
      display: inline-flex;
      align-items: center;
      height: 22px;
      padding: 0 8px;
      border-radius: 999px;
      font-size: 12px;
      font-weight: 600;
      background: var(--el-bg-color-overlay);
      box-shadow: 0 0 0 1px var(--el-color-primary-light-8);

      &[data-type='self'] {
        color: var(--el-color-primary);
      }

      &[data-type='carrier'] {
        color: var(--el-color-success);
      }

      &[data-type='social'] {
        color: var(--el-color-warning);
        box-shadow: 0 0 0 1px var(--el-color-warning-light-5);
      }
    }

    &__carrier {
      font-size: 12px;
      color: var(--el-text-color-secondary);
    }
  }

  .dispatch-route-chip {
    display: inline-flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 2px;
    max-width: 200px;

    &__prov {
      font-size: 12px;
      line-height: 1.2;
      color: var(--el-text-color-secondary);
    }

    &__city {
      overflow: hidden;
      max-width: 100%;
      font-size: 16px;
      font-weight: 600;
      line-height: 1.35;
      color: var(--el-text-color-primary);
      text-overflow: ellipsis;
      white-space: nowrap;
    }
  }

  .dispatch-rec {
    margin-bottom: 8px;

    &__bar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 8px;
    }

    &__title {
      font-size: 13px;
      font-weight: 600;
      color: var(--el-text-color-primary);
      white-space: nowrap;
    }

    &__filter {
      width: 240px;
    }

    &__search-icon {
      color: var(--el-text-color-placeholder);
    }

    &__list {
      min-height: 180px;
      max-height: 320px;
      overflow: auto;
      border: 1px solid var(--el-border-color-lighter);
      border-radius: 8px;
      background: var(--el-fill-color-blank);
    }

    &__row {
      display: flex;
      align-items: flex-start;
      width: 100%;
      padding: 10px 12px;
      border: 0;
      border-bottom: 1px solid var(--el-border-color-extra-light);
      background: transparent;
      text-align: left;
      cursor: pointer;
      transition: background 0.15s ease;

      &:last-child {
        border-bottom: 0;
      }

      &:hover {
        background: var(--el-fill-color-light);
      }

      &:focus-visible {
        outline: 2px solid var(--el-color-primary);
        outline-offset: -2px;
      }

      &.is-selected {
        background: var(--el-color-primary-light-9);
      }
    }

    &[data-type='social'] {
      .dispatch-rec__row {
        &:focus-visible {
          outline-color: var(--el-color-warning);
        }

        &.is-selected {
          background: var(--el-color-warning-light-9);
        }
      }
    }

    &__rank {
      flex: 0 0 28px;
      margin-top: 1px;
      font-variant-numeric: tabular-nums;
      font-size: 13px;
      font-weight: 600;
      color: var(--el-text-color-secondary);
    }

    &__body {
      min-width: 0;
      flex: 1;
    }

    &__line {
      display: flex;
      align-items: center;
      gap: 8px;
      min-width: 0;
    }

    &__name {
      font-size: 14px;
      font-weight: 600;
      color: var(--el-text-color-primary);
    }

    &__plate {
      font-size: 13px;
      color: var(--el-text-color-regular);
    }

    &__reason {
      display: block;
      margin-top: 4px;
      font-size: 12px;
      line-height: 1.4;
      color: var(--el-text-color-secondary);
    }

    &__empty {
      padding: 36px 16px;
      text-align: center;
      font-size: 13px;
      color: var(--el-text-color-secondary);

      p {
        margin: 0 0 8px;
      }
    }

  }

  .dispatch-picked {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-top: 12px;
    min-height: 64px;
    padding: 12px 14px;
    border-radius: 10px;
    background: var(--el-color-primary-light-9);

    &.is-empty {
      background: var(--el-fill-color-lighter);
    }

    &__icon {
      flex: 0 0 auto;
      font-size: 22px;
      color: var(--el-color-primary);
    }

    &__body {
      min-width: 0;
      flex: 1;
    }

    &__meta {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 8px 12px;
    }

    &__name {
      font-size: 16px;
      font-weight: 700;
      line-height: 1.3;
      color: var(--el-text-color-primary);
    }

    &__phone {
      font-size: 13px;
      font-variant-numeric: tabular-nums;
      color: var(--el-text-color-regular);
    }

    &__plates {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      margin-top: 8px;
    }

    &__plate-plus {
      font-size: 13px;
      font-weight: 600;
      color: var(--el-text-color-secondary);
    }

    &__placeholder {
      font-size: 13px;
      line-height: 1.5;
      color: var(--el-text-color-secondary);
    }

    &[data-type='social']:not(.is-empty) {
      background: var(--el-color-warning-light-9);

      .dispatch-picked__icon {
        color: var(--el-color-warning);
      }
    }
  }

  .dispatch-proxy {
    padding: 12px 12px 0;
    border: 1px solid var(--el-border-color-lighter);
    border-radius: 8px;

    &__title {
      margin-bottom: 8px;
      font-size: 13px;
      font-weight: 600;
      color: var(--el-text-color-primary);
    }
  }

  @media (prefers-reduced-motion: reduce) {
    .dispatch-rec__row {
      transition: none;
    }
  }
</style>
