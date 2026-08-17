<!--
  运输路线行程单：按「地点节点 + 路段」编辑，而不是表格行。

  - 节点：起点 / 中转 / 终点，改一处则相邻两段自动咬合
  - 路段：里程（可从线路管理联想）+ 计划装车 / 到达
  - 插入中转：在两节点之间拆段；删除中转：合并相邻段
-->
<template>
  <div class="itin" v-loading="treeLoading">
    <TransitionGroup name="itin-item" tag="div" class="itin-list">
      <div
        v-for="item in spineItems"
        :key="item.key"
        :class="item.wrapClass"
      >
        <template v-if="item.kind === 'node'">
          <div class="itin-rail" aria-hidden="true">
            <span class="itin-dot" />
          </div>
          <div class="itin-node__body">
            <div class="itin-node__head">
              <span class="itin-node__role">{{ item.node.roleLabel }}</span>
              <el-button
                v-if="item.node.role === 'via'"
                type="danger"
                link
                class="itin-node__remove"
                @click="removeVia(item.nodeIdx)"
              >
                删除
              </el-button>
            </div>
            <el-cascader
              :key="cascaderKey(item.node, item.nodeIdx)"
              :model-value="item.node.codes.length ? item.node.codes : undefined"
              :options="treeOptions(item.nodeIdx, item.node.codes)"
              :props="regionCascaderProps"
              :show-all-levels="false"
              filterable
              clearable
              :placeholder="item.node.placeholder"
              class="itin-node__cascader"
              @change="(v: string[] | undefined) => onNodeChange(item.nodeIdx, v)"
            />
          </div>
        </template>
        <template v-else>
          <div class="itin-rail" aria-hidden="true" />
          <div class="itin-leg__body">
            <div class="itin-leg__card">
              <div class="itin-leg__meta">
                <span class="itin-leg__title">第 {{ item.legIdx + 1 }} 段</span>
                <span v-if="legHint(item.legIdx)" class="itin-leg__hint">
                  {{ legHint(item.legIdx) }}
                </span>
              </div>
              <div class="itin-leg__fields">
                <div class="itin-leg__field itin-leg__field--km">
                  <span class="itin-leg__label">里程</span>
                  <el-input-number
                    :model-value="segmentAt(item.legIdx)?.mileage"
                    :min="0"
                    :precision="1"
                    controls-position="right"
                    size="small"
                    placeholder="km"
                    class="itin-leg__mileage"
                    @update:model-value="(v) => onMileageChange(item.legIdx, v)"
                  />
                  <span class="itin-leg__unit">km</span>
                </div>
                <div class="itin-leg__field">
                  <span class="itin-leg__label">计划装车</span>
                  <el-date-picker
                    :model-value="segmentAt(item.legIdx)?.plannedLoadTime"
                    type="datetime"
                    placeholder="选填"
                    value-format="YYYY-MM-DDTHH:mm:ss"
                    size="small"
                    class="itin-leg__time"
                    @update:model-value="
                      (v) => onTimeChange(item.legIdx, 'plannedLoadTime', v)
                    "
                  />
                </div>
                <div class="itin-leg__field">
                  <span class="itin-leg__label">计划到达</span>
                  <el-date-picker
                    :model-value="segmentAt(item.legIdx)?.plannedArriveTime"
                    type="datetime"
                    placeholder="选填"
                    value-format="YYYY-MM-DDTHH:mm:ss"
                    size="small"
                    class="itin-leg__time"
                    @update:model-value="
                      (v) => onTimeChange(item.legIdx, 'plannedArriveTime', v)
                    "
                  />
                </div>
              </div>
            </div>
            <button
              type="button"
              class="itin-insert"
              :disabled="modelValue.length >= MAX_SEGMENTS"
              :title="
                modelValue.length >= MAX_SEGMENTS
                  ? '最多 5 段'
                  : '在这两点之间插入中转'
              "
              @click="insertVia(item.legIdx)"
            >
              <span class="itin-insert__plus">+</span>
              插入中转
            </button>
          </div>
        </template>
      </div>
    </TransitionGroup>

    <p class="itin-foot">
      选定地点后会自动匹配线路里程，没有匹配到可以手填。最多 {{ MAX_SEGMENTS }} 段。
    </p>
  </div>
</template>

<script lang="ts" setup>
  import { computed, onMounted, ref, watch } from 'vue';
  import type { CascaderProps } from 'element-plus';
  import { getRegionNavTree } from '@/api/basic-data/region';
  import type { RegionNavNode } from '@/api/basic-data/region/model';
  import { lookupRouteDistance } from '@/api/operation/task';
  import type { TaskSegment } from '@/api/operation/task/model';
  import {
    findLeafRegionByCodePath,
    resolveRegionCodePath
  } from '@/utils/region-nav-tree';

  const MAX_SEGMENTS = 5;

  type NodeRole = 'start' | 'via' | 'end';

  type SegmentRow = TaskSegment & {
    _mileageFromRoute?: string;
  };

  interface RouteNodeView {
    key: string;
    role: NodeRole;
    roleLabel: string;
    placeholder: string;
    codes: string[];
  }

  type SpineItem =
    | {
        kind: 'node';
        key: string;
        wrapClass: string;
        nodeIdx: number;
        node: RouteNodeView;
        legIdx?: undefined;
      }
    | {
        kind: 'leg';
        key: string;
        wrapClass: string;
        nodeIdx: number;
        legIdx: number;
        node?: undefined;
      };

  const props = defineProps<{
    modelValue: TaskSegment[];
  }>();
  const emit = defineEmits<{
    (e: 'update:modelValue', value: TaskSegment[]): void;
  }>();

  const regionTree = ref<RegionNavNode[]>([]);
  const treeLoading = ref(false);
  const mileageInflight = new Set<string>();
  const optionsCache = new Map<string, RegionNavNode[]>();

  const regionCascaderProps: CascaderProps = {
    value: 'code',
    label: 'name',
    children: 'children',
    emitPath: true,
    checkStrictly: true
  };

  function cloneRegionTree(nodes: RegionNavNode[]): RegionNavNode[] {
    return nodes.map((n) => ({
      ...n,
      children: n.children?.length ? cloneRegionTree(n.children) : n.children
    }));
  }

  function treeOptions(nodeIdx: number, codes: string[]): RegionNavNode[] {
    if (!regionTree.value.length) return [];
    const key = codes.length
      ? `f-${nodeIdx}-${codes.join('.')}`
      : `e-${nodeIdx}`;
    let tree = optionsCache.get(key);
    if (!tree) {
      tree = cloneRegionTree(regionTree.value);
      optionsCache.set(key, tree);
    }
    return tree;
  }

  function cascaderKey(node: RouteNodeView, nodeIdx: number): string {
    return `${node.role}-${nodeIdx}-${node.codes.join('.') || 'empty'}`;
  }

  function resetCascaderTrees() {
    optionsCache.clear();
  }

  const rows = computed(() => props.modelValue as SegmentRow[]);

  const nodes = computed<RouteNodeView[]>(() => {
    const segs = rows.value;
    if (!segs.length) return [];
    const tree = regionTree.value;
    const list: RouteNodeView[] = [
      {
        key: 'node-start',
        role: 'start',
        roleLabel: '起点',
        placeholder: '选择起点',
        codes: resolveRegionCodePath(tree, {
          code: segs[0]!.fromCode,
          regionId: segs[0]!.fromRegionId,
          location: segs[0]!.fromLocation
        })
      }
    ];
    segs.forEach((s, i) => {
      const isLast = i === segs.length - 1;
      list.push({
        key: isLast ? 'node-end' : `node-via-${i}`,
        role: isLast ? 'end' : 'via',
        roleLabel: isLast ? '终点' : '中转',
        placeholder: isLast ? '选择终点' : '选择中转地',
        codes: resolveRegionCodePath(tree, {
          code: s.toCode,
          regionId: s.toRegionId,
          location: s.toLocation
        })
      });
    });
    return list;
  });

  const spineItems = computed<SpineItem[]>(() => {
    const items: SpineItem[] = [];
    nodes.value.forEach((node, nodeIdx) => {
      items.push({
        kind: 'node',
        key: node.key,
        wrapClass: `itin-node itin-node--${node.role}`,
        nodeIdx,
        node
      });
      if (nodeIdx < nodes.value.length - 1) {
        items.push({
          kind: 'leg',
          key: `leg-${nodeIdx}`,
          wrapClass: 'itin-leg',
          nodeIdx,
          legIdx: nodeIdx
        });
      }
    });
    return items;
  });

  function segmentAt(idx: number): SegmentRow | undefined {
    return rows.value[idx];
  }

  function legHint(idx: number): string {
    const s = rows.value[idx];
    if (!s?._mileageFromRoute || s.mileage == null) return '';
    return `来自线路管理 · 可改`;
  }

  function blankSegment(no: number): SegmentRow {
    return {
      segmentNo: no,
      fromLocation: '',
      toLocation: ''
    };
  }

  function renumber(arr: SegmentRow[]): SegmentRow[] {
    return arr.map((s, i) => ({ ...s, segmentNo: i + 1 }));
  }

  function emitRows(next: SegmentRow[]) {
    emit('update:modelValue', renumber(next));
  }

  function ensureMinSegment() {
    if (props.modelValue.length) return;
    emitRows([blankSegment(1)]);
  }

  function joinRegionName(codes: string[] | undefined): string {
    if (!codes?.length) return '';
    const names: string[] = [];
    let list = regionTree.value;
    for (const code of codes) {
      const node = list.find((n) => n.code === code);
      if (!node) break;
      names.push(node.name);
      list = node.children ?? [];
    }
    return names.join('/');
  }

  function applyPlace(
    target: SegmentRow,
    side: 'from' | 'to',
    codes: string[] | undefined
  ) {
    if (codes?.length) {
      const leaf = findLeafRegionByCodePath(regionTree.value, codes);
      const location = joinRegionName(codes);
      const code = codes[codes.length - 1];
      if (side === 'from') {
        target.fromLocation = location;
        target.fromCode = code;
        target.fromRegionId = leaf?.regionId ?? undefined;
      } else {
        target.toLocation = location;
        target.toCode = code;
        target.toRegionId = leaf?.regionId ?? undefined;
      }
    } else if (side === 'from') {
      target.fromLocation = '';
      target.fromCode = undefined;
      target.fromRegionId = undefined;
    } else {
      target.toLocation = '';
      target.toCode = undefined;
      target.toRegionId = undefined;
    }
    target.mileage = undefined;
    target._mileageFromRoute = undefined;
  }

  const onNodeChange = (nodeIdx: number, codes: string[] | undefined) => {
    const next = rows.value.map((s) => ({ ...s }));
    if (nodeIdx > 0) {
      const prev = next[nodeIdx - 1];
      if (prev) applyPlace(prev, 'to', codes);
    }
    if (nodeIdx < next.length) {
      const cur = next[nodeIdx];
      if (cur) applyPlace(cur, 'from', codes);
    }
    emitRows(next);
    if (nodeIdx > 0) void tryAutoFillMileage(nodeIdx - 1);
    if (nodeIdx < next.length) void tryAutoFillMileage(nodeIdx);
  };

  const insertVia = (legIdx: number) => {
    if (props.modelValue.length >= MAX_SEGMENTS) return;
    const current = rows.value[legIdx];
    if (!current) return;
    const left: SegmentRow = {
      ...current,
      toLocation: '',
      toCode: undefined,
      toRegionId: undefined,
      mileage: undefined,
      plannedArriveTime: undefined,
      _mileageFromRoute: undefined
    };
    const right: SegmentRow = {
      segmentNo: legIdx + 2,
      fromLocation: '',
      fromCode: undefined,
      fromRegionId: undefined,
      toLocation: current.toLocation,
      toCode: current.toCode,
      toRegionId: current.toRegionId,
      mileage: undefined,
      plannedLoadTime: undefined,
      plannedArriveTime: current.plannedArriveTime,
      remark: current.remark
    };
    const next = [...rows.value];
    next.splice(legIdx, 1, left, right);
    resetCascaderTrees();
    emitRows(next);
  };

  const removeVia = (nodeIdx: number) => {
    if (nodeIdx <= 0 || nodeIdx >= rows.value.length) return;
    if (rows.value.length <= 1) return;
    const left = rows.value[nodeIdx - 1];
    const right = rows.value[nodeIdx];
    if (!left || !right) return;
    const merged: SegmentRow = {
      ...left,
      toLocation: right.toLocation,
      toCode: right.toCode,
      toRegionId: right.toRegionId,
      plannedArriveTime: right.plannedArriveTime,
      mileage: undefined,
      _mileageFromRoute: undefined
    };
    const next = [...rows.value];
    next.splice(nodeIdx - 1, 2, merged);
    resetCascaderTrees();
    emitRows(next);
    void tryAutoFillMileage(nodeIdx - 1);
  };

  const onMileageChange = (idx: number, value: number | undefined) => {
    const next = rows.value.map((s) => ({ ...s }));
    const cur = next[idx];
    if (!cur) return;
    cur.mileage = value ?? undefined;
    cur._mileageFromRoute = undefined;
    emitRows(next);
  };

  const onTimeChange = (
    idx: number,
    field: 'plannedLoadTime' | 'plannedArriveTime',
    value: string | Date | number | string[] | null | undefined
  ) => {
    const next = rows.value.map((s) => ({ ...s }));
    const cur = next[idx];
    if (!cur) return;
    cur[field] = typeof value === 'string' ? value : undefined;
    emitRows(next);
  };

  async function tryAutoFillMileage(idx: number) {
    const r = rows.value[idx];
    if (!r?.fromRegionId || !r.toRegionId) return;
    if (r.mileage != null) return;
    const key = `${r.fromRegionId}-${r.toRegionId}`;
    if (mileageInflight.has(key)) return;
    mileageInflight.add(key);
    try {
      const match = await lookupRouteDistance({
        originRegionId: r.fromRegionId,
        destinationRegionId: r.toRegionId
      });
      if (!match || match.distance == null) return;
      const latest = (props.modelValue as SegmentRow[])[idx];
      if (!latest || latest.mileage != null) return;
      if (
        latest.fromRegionId !== r.fromRegionId ||
        latest.toRegionId !== r.toRegionId
      ) {
        return;
      }
      const next = (props.modelValue as SegmentRow[]).map((s) => ({ ...s }));
      const cur = next[idx];
      if (!cur || cur.mileage != null) return;
      cur.mileage = match.distance;
      cur._mileageFromRoute = match.routeName;
      emitRows(next);
    } catch {
      // 联想失败保持静默，允许手填
    } finally {
      mileageInflight.delete(key);
    }
  }

  function autofillEmptyMileages() {
    rows.value.forEach((s, i) => {
      if (s.fromRegionId && s.toRegionId && s.mileage == null) {
        void tryAutoFillMileage(i);
      }
    });
  }

  /** 只有地名时，用地区树补全 code / regionId，便于联想里程和保存 */
  function hydrateMissingRegionIds() {
    if (!regionTree.value.length) return;
    const next = rows.value.map((s) => ({ ...s }));
    let changed = false;
    for (const s of next) {
      if (!s.fromRegionId || !s.fromCode) {
        const codes = resolveRegionCodePath(regionTree.value, {
          code: s.fromCode,
          regionId: s.fromRegionId,
          location: s.fromLocation
        });
        const leaf = findLeafRegionByCodePath(regionTree.value, codes);
        if (leaf && codes.length) {
          const code = codes[codes.length - 1];
          if (s.fromCode !== code || s.fromRegionId !== leaf.regionId) {
            s.fromCode = code;
            s.fromRegionId = leaf.regionId;
            if (!s.fromLocation) s.fromLocation = joinRegionName(codes);
            changed = true;
          }
        }
      }
      if (!s.toRegionId || !s.toCode) {
        const codes = resolveRegionCodePath(regionTree.value, {
          code: s.toCode,
          regionId: s.toRegionId,
          location: s.toLocation
        });
        const leaf = findLeafRegionByCodePath(regionTree.value, codes);
        if (leaf && codes.length) {
          const code = codes[codes.length - 1];
          if (s.toCode !== code || s.toRegionId !== leaf.regionId) {
            s.toCode = code;
            s.toRegionId = leaf.regionId;
            if (!s.toLocation) s.toLocation = joinRegionName(codes);
            changed = true;
          }
        }
      }
    }
    if (changed) emitRows(next);
  }

  onMounted(async () => {
    treeLoading.value = true;
    try {
      regionTree.value = (await getRegionNavTree()) ?? [];
      resetCascaderTrees();
    } catch {
      regionTree.value = [];
      resetCascaderTrees();
    } finally {
      treeLoading.value = false;
    }
    ensureMinSegment();
    hydrateMissingRegionIds();
    autofillEmptyMileages();
  });

  watch(
    () =>
      props.modelValue
        .map(
          (s) =>
            `${s.fromLocation ?? ''}-${s.fromCode ?? ''}-${s.fromRegionId ?? ''}-${s.toLocation ?? ''}-${s.toCode ?? ''}-${s.toRegionId ?? ''}-${s.mileage ?? ''}`
        )
        .join('|'),
    () => {
      hydrateMissingRegionIds();
      autofillEmptyMileages();
    }
  );

  watch(
    () => props.modelValue.length,
    (len) => {
      if (len === 0) ensureMinSegment();
    }
  );
</script>

<style lang="scss" scoped>
  .itin {
    min-height: 120px;
  }

  .itin-list {
    display: flex;
    flex-direction: column;
  }

  .itin-node,
  .itin-leg {
    display: grid;
    grid-template-columns: 20px minmax(0, 1fr);
    column-gap: 14px;
  }

  .itin-rail {
    position: relative;
    display: flex;
    justify-content: center;
  }

  .itin-node .itin-rail::before,
  .itin-leg .itin-rail::before {
    content: '';
    position: absolute;
    left: 50%;
    width: 2px;
    background: var(--el-color-primary-light-5);
    transform: translateX(-50%);
  }

  .itin-node .itin-rail::before,
  .itin-leg .itin-rail::before {
    top: 0;
    bottom: 0;
  }

  .itin-node--start .itin-rail::before {
    top: 22px;
  }

  .itin-node--end .itin-rail::before {
    bottom: auto;
    height: 22px;
  }

  .itin-dot {
    position: relative;
    z-index: 1;
    width: 10px;
    height: 10px;
    margin-top: 17px;
    border-radius: 50%;
    background: var(--el-color-primary);
    box-shadow: 0 0 0 3px var(--el-color-primary-light-8);
  }

  .itin-node--via .itin-dot {
    background: var(--el-color-primary-light-3);
    box-shadow: 0 0 0 3px var(--el-color-primary-light-9);
  }

  .itin-node--end .itin-dot {
    background: var(--el-text-color-regular);
    box-shadow: 0 0 0 3px var(--el-fill-color);
  }

  .itin-node__body {
    min-width: 0;
    padding-bottom: 4px;
  }

  .itin-node__head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    min-height: 22px;
    margin-bottom: 4px;
  }

  .itin-node__role {
    font-size: 12px;
    line-height: 1;
    color: var(--el-text-color-secondary);
  }

  .itin-node__remove {
    padding: 0;
    height: auto;
  }

  .itin-node__cascader {
    width: 100%;
  }

  .itin-leg__body {
    min-width: 0;
    padding: 8px 0 4px;
  }

  .itin-leg__card {
    padding: 10px 12px;
    border-radius: 8px;
    background: var(--el-fill-color-light);
  }

  .itin-leg__meta {
    display: flex;
    align-items: baseline;
    gap: 8px;
    margin-bottom: 8px;
  }

  .itin-leg__title {
    font-size: 12px;
    font-weight: 600;
    color: var(--el-text-color-regular);
  }

  .itin-leg__hint {
    font-size: 12px;
    color: var(--el-text-color-secondary);
  }

  .itin-leg__fields {
    display: flex;
    flex-wrap: wrap;
    gap: 10px 16px;
    align-items: flex-end;
  }

  .itin-leg__field {
    display: flex;
    flex-direction: column;
    gap: 4px;
    min-width: 0;
  }

  .itin-leg__field--km {
    flex-direction: row;
    align-items: center;
    gap: 6px;
  }

  .itin-leg__label {
    font-size: 12px;
    color: var(--el-text-color-secondary);
    line-height: 1;
  }

  .itin-leg__field--km .itin-leg__label {
    margin-right: 2px;
  }

  .itin-leg__mileage {
    width: 108px;
  }

  .itin-leg__unit {
    font-size: 12px;
    color: var(--el-text-color-secondary);
  }

  .itin-leg__time {
    width: 176px;
  }

  .itin-insert {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    margin-top: 6px;
    padding: 0;
    border: 0;
    background: none;
    font-size: 12px;
    line-height: 22px;
    color: var(--el-color-primary);
    cursor: pointer;
    opacity: 0.72;
    transition:
      opacity 160ms cubic-bezier(0.23, 1, 0.32, 1),
      transform 160ms cubic-bezier(0.23, 1, 0.32, 1);

    &:hover:not(:disabled) {
      opacity: 1;
    }

    &:active:not(:disabled) {
      transform: scale(0.97);
    }

    &:disabled {
      color: var(--el-text-color-disabled);
      cursor: not-allowed;
      opacity: 0.5;
    }
  }

  .itin-insert__plus {
    font-size: 14px;
    font-weight: 600;
    line-height: 1;
  }

  .itin-foot {
    margin: 12px 0 0;
    font-size: 12px;
    line-height: 1.5;
    color: var(--el-text-color-secondary);
  }

  .itin-item-enter-active,
  .itin-item-leave-active {
    transition:
      opacity 180ms cubic-bezier(0.23, 1, 0.32, 1),
      transform 180ms cubic-bezier(0.23, 1, 0.32, 1);
  }

  .itin-item-enter-from,
  .itin-item-leave-to {
    opacity: 0;
    transform: translateY(-6px);
  }

  .itin-item-leave-active {
    display: none;
  }

  @media (prefers-reduced-motion: reduce) {
    .itin-item-enter-active,
    .itin-item-leave-active {
      transition: opacity 120ms ease;
    }

    .itin-item-enter-from,
    .itin-item-leave-to {
      transform: none;
    }

    .itin-insert {
      transition: opacity 120ms ease;
    }
  }
</style>
