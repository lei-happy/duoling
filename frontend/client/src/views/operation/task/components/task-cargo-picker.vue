<!--
  商品车配载选择器（左右布局）

  设计：
  - 左侧：待选运单（按线路 / 车型分组），每行点「加入」推到右侧
  - 右侧：已选商品车面板（汇总条 / 数量微调 / 段归属 / 移除 / 清空）
  - 列表区采用 sticky 分组头，避免嵌套 flex 内部高度塌陷

  业务偏好：相同起终点(线路) > 同品牌车型 > 台数充裕
-->
<template>
  <div class="cargo-picker">
    <!-- ========================== 左侧：待选 ========================== -->
    <div class="cargo-picker__left">
      <div class="cargo-picker__panel-header">
        <span class="cargo-picker__panel-title">待选运单</span>
        <el-tag size="small" type="info" effect="plain">
          {{ filteredCandidates.length }} 条 / {{ candidatesTotalQty }} 台
        </el-tag>
        <div class="cargo-picker__flex-spacer" />
        <el-tooltip
          content="智能配载将基于运力、车型、台数自动拼板，即将上线"
          placement="top"
        >
          <el-button type="primary" link disabled size="small">
            <el-icon style="margin-right: 4px"><MagicStick /></el-icon>
            智能配载
          </el-button>
        </el-tooltip>
        <el-button :icon="Refresh" size="small" @click="loadCandidates">
          刷新
        </el-button>
      </div>

      <div class="cargo-picker__filter">
        <el-input
          v-model="filter.keyword"
          placeholder="运单号 / 客户"
          clearable
          size="small"
          style="width: 170px"
          @change="loadCandidates"
        />
        <el-input
          v-model="filter.originKeyword"
          placeholder="起点关键词"
          clearable
          size="small"
          style="width: 140px"
          @change="loadCandidates"
        />
        <el-input
          v-model="filter.destinationKeyword"
          placeholder="终点关键词"
          clearable
          size="small"
          style="width: 140px"
          @change="loadCandidates"
        />
        <el-input
          v-model="filter.modelKeyword"
          placeholder="品牌/车型"
          clearable
          size="small"
          style="width: 130px"
        />
        <div class="cargo-picker__flex-spacer" />
        <el-radio-group v-model="groupMode" size="small">
          <el-radio-button value="route">按线路</el-radio-button>
          <el-radio-button value="model">按车型</el-radio-button>
        </el-radio-group>
      </div>

      <div v-loading="loading" class="cargo-picker__scroll">
        <el-empty
          v-if="!loading && !groupedCandidates.length"
          description="暂无符合条件的候选运单"
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
            <span class="cargo-group__title" :title="group.title">
              {{ group.title }}
            </span>
            <span class="cargo-group__meta">
              {{ group.totalCount }} 条 · {{ group.totalQuantity }} 台
            </span>
            <el-tag
              v-if="group.pickedQuantity > 0"
              size="small"
              type="success"
              effect="plain"
            >
              已选 {{ group.pickedQuantity }} 台
            </el-tag>
            <div class="cargo-picker__flex-spacer" />
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

          <div v-show="!collapsedGroups.has(group.key)" class="cargo-group__body">
            <template
              v-for="sub in group.subgroups"
              :key="sub.key"
            >
              <div
                v-if="group.subgroups.length > 1 || (sub.title && sub.title.trim())"
                class="cargo-subheader"
              >
                <span class="cargo-subheader__label">{{ sub.title }}</span>
                <span class="cargo-subheader__meta">
                  {{ sub.totalCount }} 条 · {{ sub.totalQuantity }} 台
                </span>
              </div>
              <div
                v-for="row in sub.rows"
                :key="row.cargoId"
                class="cargo-row"
                :class="{ 'is-picked': pickedQty(row) > 0 }"
              >
                <div class="cargo-row__main">
                  <div class="cargo-row__line1">
                    <span class="cargo-row__wb" :title="row.waybillNo">{{
                      row.waybillNo || `#${row.cargoId}`
                    }}</span>
                    <span class="cargo-row__customer">{{
                      row.customerName || '—'
                    }}</span>
                  </div>
                  <div class="cargo-row__line2">
                    <span
                      v-if="groupMode === 'route'"
                      class="cargo-row__chip"
                    >
                      {{ row.vehicleBrand || '—' }} /
                      {{ row.vehicleModel || '—' }}
                    </span>
                    <span
                      v-else
                      class="cargo-row__chip"
                      :title="`${row.origin || ''} → ${row.destination || ''}`"
                    >
                      {{ row.origin || '—' }} → {{ row.destination || '—' }}
                    </span>
                    <span
                      v-if="row.dealerName"
                      class="cargo-row__dealer"
                      :title="row.dealerName"
                    >
                      {{ row.dealerName }}
                    </span>
                  </div>
                </div>
                <div class="cargo-row__action">
                  <span class="cargo-row__remaining">
                    剩 <b>{{ row.remainingQuantity }}</b>
                  </span>
                  <el-button
                    v-if="pickedQty(row) === 0"
                    type="primary"
                    size="small"
                    :disabled="row.remainingQuantity <= 0"
                    @click="addRow(row)"
                  >
                    加入
                  </el-button>
                  <template v-else>
                    <el-tag size="small" type="success" effect="dark">
                      已选 {{ pickedQty(row) }}
                    </el-tag>
                    <el-button
                      type="danger"
                      link
                      size="small"
                      @click="removeByRow(row)"
                    >
                      移除
                    </el-button>
                  </template>
                </div>
              </div>
            </template>
          </div>
        </div>
      </div>
    </div>

    <!-- ========================== 右侧：已选 ========================== -->
    <div class="cargo-picker__right">
      <div class="cargo-picker__panel-header">
        <span class="cargo-picker__panel-title is-primary">已选商品车</span>
        <el-tag size="small" type="primary" effect="dark">
          {{ modelValue.length }} 条 / {{ totalQuantity }} 台
        </el-tag>
        <div class="cargo-picker__flex-spacer" />
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

      <div class="cargo-picker__summary">
        <template v-if="modelValue.length">
          <el-tag
            v-if="dominantRoute"
            size="small"
            type="primary"
            effect="plain"
            class="cargo-picker__chip"
          >
            主线路：{{ dominantRoute }}
          </el-tag>
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
        </template>
        <span v-else class="cargo-picker__summary-hint">
          建议优先选同线路、同车型的运单凑成一板
        </span>
      </div>

      <div class="cargo-picker__scroll cargo-picker__scroll--picked">
        <div v-if="!modelValue.length" class="cargo-picker__picked-empty">
          <el-empty description="尚未选入商品车" :image-size="80" />
        </div>
        <div
          v-for="(p, idx) in modelValue"
          :key="`${p.waybillCargoId}_${idx}`"
          class="picked-row"
        >
          <div class="picked-row__main">
            <div class="picked-row__line1">
              <span class="picked-row__wb" :title="p.waybillNo">{{
                p.waybillNo || `#${p.waybillCargoId}`
              }}</span>
              <span class="picked-row__customer">{{
                p.customerName || '—'
              }}</span>
            </div>
            <div class="picked-row__line2">
              <span class="picked-row__chip">
                {{ p.vehicleBrand || '—' }} / {{ p.vehicleModel || '—' }}
              </span>
              <span
                v-if="routeOfPicked(p)"
                class="picked-row__chip"
                :title="routeOfPicked(p)"
              >
                {{ routeOfPicked(p) }}
              </span>
            </div>
          </div>
          <div class="picked-row__rest">
            <el-input-number
              v-model="p.quantity"
              :min="1"
              :max="getMaxForPicked(p)"
              :precision="0"
              controls-position="right"
              size="small"
              class="picked-row__qty"
              @change="syncQuantity(idx)"
            />
            <el-select
              v-if="segments && segments.length > 1"
              v-model="p.segmentId"
              size="small"
              clearable
              placeholder="跟随主任务"
              class="picked-row__segment"
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
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
  import { computed, onMounted, reactive, ref } from 'vue';
  import { EleMessage } from 'ele-admin-plus';
  import {
    CaretBottom,
    Close,
    MagicStick,
    Refresh,
    Top
  } from '@element-plus/icons-vue';
  import { listCandidateWaybills } from '@/api/operation/task';
  import type {
    CandidateCargo,
    TaskSegment,
    TaskWaybillItem
  } from '@/api/operation/task/model';

  type PickedItem = TaskWaybillItem & {
    /** 候选行剩余台数（用于已选面板里动态计算最大可输入） */
    _availableRemaining?: number;
  };

  type GroupMode = 'route' | 'model';

  interface SubGroup {
    key: string;
    title: string;
    rows: CandidateCargo[];
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

  const props = defineProps<{
    modelValue: PickedItem[];
    segments: TaskSegment[];
  }>();
  const emit = defineEmits<{
    (e: 'update:modelValue', value: PickedItem[]): void;
  }>();

  const candidates = ref<CandidateCargo[]>([]);
  const loading = ref(false);
  const groupMode = ref<GroupMode>('route');
  const collapsedGroups = ref<Set<string>>(new Set());

  const filter = reactive({
    keyword: '',
    originKeyword: '',
    destinationKeyword: '',
    modelKeyword: ''
  });

  onMounted(() => {
    loadCandidates();
  });

  const loadCandidates = async () => {
    loading.value = true;
    try {
      candidates.value = await listCandidateWaybills({
        keyword: filter.keyword || undefined,
        originKeyword: filter.originKeyword || undefined,
        destinationKeyword: filter.destinationKeyword || undefined,
        limit: 300
      });
    } catch (e: unknown) {
      const msg = (e as { message?: string }).message || '加载候选失败';
      EleMessage.error({ message: msg, plain: true });
    } finally {
      loading.value = false;
    }
  };

  const filteredCandidates = computed<CandidateCargo[]>(() => {
    const kw = filter.modelKeyword.trim().toLowerCase();
    if (!kw) return candidates.value;
    return candidates.value.filter((c) => {
      const s = `${c.vehicleBrand || ''} ${c.vehicleModel || ''}`.toLowerCase();
      return s.includes(kw);
    });
  });

  const candidatesTotalQty = computed(() =>
    filteredCandidates.value.reduce(
      (s, c) => s + (c.remainingQuantity || 0),
      0
    )
  );

  function routeKeyOf(c: CandidateCargo): string {
    return `${c.origin || '未填'}__${c.destination || '未填'}`;
  }
  function routeTitleOf(c: CandidateCargo): string {
    return `${c.origin || '未填起点'} → ${c.destination || '未填终点'}`;
  }
  function modelKeyOf(c: CandidateCargo): string {
    return `${c.vehicleBrand || '未填'}__${c.vehicleModel || '未填'}`;
  }
  function modelTitleOf(c: CandidateCargo): string {
    return `${c.vehicleBrand || '未填品牌'} / ${c.vehicleModel || '未填车型'}`;
  }

  const groupedCandidates = computed<Group[]>(() => {
    const list = filteredCandidates.value;
    if (!list.length) return [];

    const primary = groupMode.value === 'route' ? routeKeyOf : modelKeyOf;
    const primaryTitle =
      groupMode.value === 'route' ? routeTitleOf : modelTitleOf;
    const secondary = groupMode.value === 'route' ? modelKeyOf : routeKeyOf;
    const secondaryTitle =
      groupMode.value === 'route' ? modelTitleOf : routeTitleOf;

    const pickedMap = new Map<number, number>();
    (props.modelValue || []).forEach((p) => {
      pickedMap.set(p.waybillCargoId, p.quantity || 0);
    });

    const groupsMap = new Map<string, Group>();
    for (const c of list) {
      const gKey = primary(c);
      let g = groupsMap.get(gKey);
      if (!g) {
        g = {
          key: gKey,
          title: primaryTitle(c),
          subgroups: [],
          totalCount: 0,
          totalQuantity: 0,
          pickedQuantity: 0,
          addableQuantity: 0
        };
        groupsMap.set(gKey, g);
      }
      const sKey = secondary(c);
      let sg = g.subgroups.find((x) => x.key === sKey);
      if (!sg) {
        sg = {
          key: sKey,
          title: secondaryTitle(c),
          rows: [],
          totalCount: 0,
          totalQuantity: 0
        };
        g.subgroups.push(sg);
      }
      sg.rows.push(c);
      sg.totalCount += 1;
      sg.totalQuantity += c.remainingQuantity;
      g.totalCount += 1;
      g.totalQuantity += c.remainingQuantity;

      const pickedQ = pickedMap.get(c.cargoId) || 0;
      if (pickedQ > 0) g.pickedQuantity += pickedQ;
      g.addableQuantity += Math.max(0, c.remainingQuantity - pickedQ);
    }

    const groups = Array.from(groupsMap.values());
    groups.sort(
      (a, b) =>
        b.addableQuantity - a.addableQuantity ||
        b.totalQuantity - a.totalQuantity
    );
    groups.forEach((g) => {
      g.subgroups.sort((a, b) => b.totalQuantity - a.totalQuantity);
      g.subgroups.forEach((sg) => {
        sg.rows.sort((a, b) => b.remainingQuantity - a.remainingQuantity);
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

  const pickedQty = (row: CandidateCargo): number => {
    const p = (props.modelValue || []).find(
      (x) => x.waybillCargoId === row.cargoId
    );
    return p?.quantity || 0;
  };

  const addRow = (row: CandidateCargo) => {
    if (row.remainingQuantity <= 0) return;
    const list = [...(props.modelValue || [])];
    const exists = list.find((x) => x.waybillCargoId === row.cargoId);
    if (exists) {
      exists.quantity = row.remainingQuantity;
      exists._availableRemaining = row.remainingQuantity;
    } else {
      list.push({
        waybillId: row.waybillId,
        waybillCargoId: row.cargoId,
        waybillNo: row.waybillNo,
        customerId: row.customerId,
        customerName: row.customerName,
        vehicleBrand: row.vehicleBrand,
        vehicleModel: row.vehicleModel,
        dealerName: row.dealerName,
        quantity: row.remainingQuantity,
        segmentId: undefined,
        _availableRemaining: row.remainingQuantity
      });
    }
    emit('update:modelValue', list);
  };

  const removeByRow = (row: CandidateCargo) => {
    const list = [...(props.modelValue || [])];
    const i = list.findIndex((x) => x.waybillCargoId === row.cargoId);
    if (i >= 0) list.splice(i, 1);
    emit('update:modelValue', list);
  };

  const removePick = (idx: number) => {
    const next = [...(props.modelValue || [])];
    next.splice(idx, 1);
    emit('update:modelValue', next);
  };

  const clearAllPicked = () => {
    emit('update:modelValue', []);
  };

  const getMaxForPicked = (row: PickedItem) => row._availableRemaining ?? 999;

  const syncQuantity = (_idx: number) => {
    emit('update:modelValue', [...(props.modelValue || [])]);
  };

  const quickFillGroup = (group: Group) => {
    const existingMap = new Map<number, PickedItem>();
    (props.modelValue || []).forEach((p) =>
      existingMap.set(p.waybillCargoId, p)
    );

    let touchedCount = 0;
    let addedQuantity = 0;
    const list: PickedItem[] = [...(props.modelValue || [])];

    group.subgroups.forEach((sg) => {
      sg.rows.forEach((row) => {
        if (row.remainingQuantity <= 0) return;
        const existing = existingMap.get(row.cargoId);
        if (existing) {
          if (existing.quantity < row.remainingQuantity) {
            addedQuantity += row.remainingQuantity - existing.quantity;
            existing.quantity = row.remainingQuantity;
            existing._availableRemaining = row.remainingQuantity;
            touchedCount += 1;
          }
        } else {
          list.push({
            waybillId: row.waybillId,
            waybillCargoId: row.cargoId,
            waybillNo: row.waybillNo,
            customerId: row.customerId,
            customerName: row.customerName,
            vehicleBrand: row.vehicleBrand,
            vehicleModel: row.vehicleModel,
            dealerName: row.dealerName,
            quantity: row.remainingQuantity,
            segmentId: undefined,
            _availableRemaining: row.remainingQuantity
          });
          touchedCount += 1;
          addedQuantity += row.remainingQuantity;
        }
      });
    });

    if (touchedCount === 0) {
      EleMessage.info({ message: '本组候选已全部加入', plain: true });
      return;
    }
    emit('update:modelValue', list);
    EleMessage.success({
      message: `已加入/更新 ${touchedCount} 条，共 ${addedQuantity} 台`,
      plain: true
    });
  };

  const totalQuantity = computed(() =>
    (props.modelValue || []).reduce((s, x) => s + (x.quantity || 0), 0)
  );

  const candidateById = computed(() => {
    const m = new Map<number, CandidateCargo>();
    candidates.value.forEach((c) => m.set(c.cargoId, c));
    return m;
  });

  function routeOfPicked(p: PickedItem): string {
    const c = candidateById.value.get(p.waybillCargoId);
    if (!c) return '';
    const o = c.origin || '';
    const d = c.destination || '';
    if (!o && !d) return '';
    return `${o || '未填'} → ${d || '未填'}`;
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

  defineExpose({ reload: loadCandidates });
</script>

<style lang="scss" scoped>
  // ============================================
  // 整体容器：固定高度，左右两栏各自内部滚动
  // ============================================
  .cargo-picker {
    display: grid;
    grid-template-columns: minmax(0, 1.5fr) minmax(340px, 1fr);
    gap: 12px;
    /* 关键：固定容器高度，让两栏 100% 撑高度，内部 overflow 才能生效 */
    height: 480px;
    max-height: calc(100vh - 280px);
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

  .cargo-picker__filter {
    display: flex;
    align-items: center;
    gap: 6px;
    flex-wrap: wrap;
    flex-shrink: 0;
  }

  .cargo-picker__summary {
    display: flex;
    align-items: center;
    gap: 6px;
    flex-wrap: wrap;
    min-height: 22px;
    flex-shrink: 0;
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
    font-size: 14px;
    transition: transform 0.2s;
    &.is-collapsed {
      transform: rotate(-90deg);
    }
  }

  .cargo-group__title {
    font-weight: 600;
    color: var(--el-text-color-primary);
    font-size: 13px;
    max-width: 320px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .cargo-group__meta {
    color: var(--el-text-color-secondary);
    font-size: 12px;
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

  // ============================================
  // 行
  // ============================================
  .cargo-row {
    display: flex;
    align-items: center;
    gap: 10px;
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
    &.is-picked {
      background: var(--el-color-success-light-9);
      box-shadow: inset 3px 0 0 var(--el-color-success);
    }
  }

  .cargo-row__main {
    flex: 1;
    min-width: 0;
    display: flex;
    flex-direction: column;
    gap: 3px;
  }

  .cargo-row__line1 {
    display: flex;
    align-items: center;
    gap: 8px;
    min-width: 0;
    flex-wrap: wrap;
  }

  .cargo-row__line2 {
    display: flex;
    align-items: center;
    gap: 6px;
    min-width: 0;
    flex-wrap: wrap;
  }

  .cargo-row__wb {
    font-variant-numeric: tabular-nums;
    font-weight: 500;
    color: var(--el-text-color-primary);
    font-size: 13px;
  }

  .cargo-row__customer {
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

  .cargo-row__dealer {
    color: var(--el-text-color-secondary);
    font-size: 12px;
    max-width: 180px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .cargo-row__action {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-shrink: 0;
  }

  .cargo-row__remaining {
    color: var(--el-text-color-secondary);
    font-size: 12px;
    b {
      color: var(--el-color-success);
      font-weight: 600;
      margin: 0 2px;
    }
  }

  // ============================================
  // 右侧：已选行
  // ============================================
  .picked-row {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 10px;
    border-radius: 6px;
    background: var(--el-bg-color);
    border: 1px solid var(--el-border-color-lighter);
    flex-shrink: 0;
  }

  .picked-row__main {
    flex: 1;
    min-width: 0;
    display: flex;
    flex-direction: column;
    gap: 3px;
  }

  .picked-row__line1 {
    display: flex;
    align-items: center;
    gap: 8px;
    min-width: 0;
    flex-wrap: wrap;
  }

  .picked-row__line2 {
    display: flex;
    align-items: center;
    gap: 6px;
    min-width: 0;
    flex-wrap: wrap;
  }

  .picked-row__wb {
    font-variant-numeric: tabular-nums;
    font-weight: 500;
    font-size: 13px;
    color: var(--el-text-color-primary);
  }

  .picked-row__customer {
    color: var(--el-text-color-regular);
    font-size: 13px;
  }

  .picked-row__chip {
    display: inline-flex;
    align-items: center;
    color: var(--el-text-color-regular);
    font-size: 12px;
    background: var(--el-fill-color);
    padding: 1px 6px;
    border-radius: 4px;
    max-width: 220px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .picked-row__rest {
    display: flex;
    align-items: center;
    gap: 6px;
    flex-shrink: 0;
  }

  .picked-row__qty {
    width: 100px;
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
    .cargo-picker__scroll {
      max-height: 320px;
    }
  }
</style>
