<template>
  <div class="seg-table">
    <div class="seg-table__title">
      <span>路线分段（{{ modelValue.length }} 段）</span>
      <el-button
        type="primary"
        link
        :icon="Plus"
        :disabled="modelValue.length >= 5"
        @click="addRow"
      >
        新增路段
      </el-button>
    </div>
    <el-alert
      type="info"
      :closable="false"
      show-icon
      style="margin-bottom: 8px"
      title="起点/终点从地区库选择，选定后自动匹配「计费中心 - 线路管理」里维护的里程；未匹配可手动填写。"
    />
    <el-table
      :data="modelValue"
      border
      size="small"
      empty-text="请至少添加 1 段运输"
    >
      <el-table-column label="段" width="50" align="center">
        <template #default="{ $index }">{{ $index + 1 }}</template>
      </el-table-column>
      <el-table-column label="起点（地区库）" min-width="220">
        <template #default="{ row, $index }">
          <el-cascader
            v-model="row._fromCodes"
            :options="regionTree"
            :props="regionCascaderProps"
            :show-all-levels="false"
            filterable
            clearable
            placeholder="选择起点"
            style="width: 100%"
            @change="(v: string[] | undefined) => onFromChange($index, v)"
          />
        </template>
      </el-table-column>
      <el-table-column label="终点（地区库）" min-width="220">
        <template #default="{ row, $index }">
          <el-cascader
            v-model="row._toCodes"
            :options="regionTree"
            :props="regionCascaderProps"
            :show-all-levels="false"
            filterable
            clearable
            placeholder="选择终点"
            style="width: 100%"
            @change="(v: string[] | undefined) => onToChange($index, v)"
          />
        </template>
      </el-table-column>
      <el-table-column label="里程(km)" width="110">
        <template #default="{ row }">
          <el-input-number
            v-model="row.mileage"
            :min="0"
            :precision="1"
            controls-position="right"
            size="small"
            style="width: 100%"
            placeholder="--"
          />
        </template>
      </el-table-column>
      <el-table-column label="计划装车" min-width="170">
        <template #default="{ row }">
          <el-date-picker
            v-model="row.plannedLoadTime"
            type="datetime"
            placeholder="选择"
            value-format="YYYY-MM-DDTHH:mm:ss"
            size="small"
            style="width: 100%"
          />
        </template>
      </el-table-column>
      <el-table-column label="计划到达" min-width="170">
        <template #default="{ row }">
          <el-date-picker
            v-model="row.plannedArriveTime"
            type="datetime"
            placeholder="选择"
            value-format="YYYY-MM-DDTHH:mm:ss"
            size="small"
            style="width: 100%"
          />
        </template>
      </el-table-column>
      <el-table-column label="操作" width="72" align="center">
        <template #default="{ $index }">
          <el-button
            type="danger"
            link
            :disabled="modelValue.length <= 1"
            @click="removeRow($index)"
          >
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script lang="ts" setup>
  import { onMounted, ref, watch } from 'vue';
  import type { CascaderProps } from 'element-plus';
  import { Plus } from '@element-plus/icons-vue';
  import { EleMessage } from 'ele-admin-plus';
  import { getRegionNavTree } from '@/api/basic-data/region';
  import type { RegionNavNode } from '@/api/basic-data/region/model';
  import {
    findLeafRegionByCodePath,
    findRegionCodePath
  } from '@/utils/region-nav-tree';
  import { lookupRouteDistance } from '@/api/operation/task';
  import type { TaskSegment } from '@/api/operation/task/model';

  /** 段表内部用的行类型：在 TaskSegment 之上额外缓存级联回显路径 */
  type SegmentRow = TaskSegment & {
    _fromCodes?: string[];
    _toCodes?: string[];
  };

  const props = defineProps<{
    modelValue: TaskSegment[];
  }>();
  const emit = defineEmits<{
    (e: 'update:modelValue', value: TaskSegment[]): void;
  }>();

  const regionTree = ref<RegionNavNode[]>([]);

  const regionCascaderProps: CascaderProps = {
    value: 'code',
    label: 'name',
    children: 'children',
    emitPath: true,
    checkStrictly: true
  };

  onMounted(async () => {
    try {
      regionTree.value = (await getRegionNavTree()) ?? [];
    } catch {
      regionTree.value = [];
    }
    hydrateExistingCodes();
  });

  watch(
    () => props.modelValue.length,
    () => hydrateExistingCodes()
  );

  /** 回填已有段的 _fromCodes / _toCodes（保存后再次进入或外部传入） */
  function hydrateExistingCodes() {
    if (!regionTree.value.length) return;
    const rows = props.modelValue as SegmentRow[];
    let changed = false;
    rows.forEach((r) => {
      if (!r._fromCodes && r.fromCode) {
        r._fromCodes =
          findRegionCodePath(regionTree.value, r.fromCode) ?? [r.fromCode];
        changed = true;
      }
      if (!r._toCodes && r.toCode) {
        r._toCodes =
          findRegionCodePath(regionTree.value, r.toCode) ?? [r.toCode];
        changed = true;
      }
    });
    if (changed) emit('update:modelValue', [...rows]);
  }

  const renumber = (arr: SegmentRow[]) =>
    arr.map((s, i) => ({ ...s, segmentNo: i + 1 }));

  const addRow = () => {
    if (props.modelValue.length >= 5) return;
    const last = props.modelValue[props.modelValue.length - 1] as
      | SegmentRow
      | undefined;
    const next: SegmentRow = {
      segmentNo: props.modelValue.length + 1,
      fromLocation: last?.toLocation || '',
      fromCode: last?.toCode,
      fromRegionId: last?.toRegionId,
      _fromCodes: last?._toCodes ? [...last._toCodes] : undefined,
      toLocation: '',
      toCode: undefined,
      toRegionId: undefined,
      _toCodes: undefined,
      plannedLoadTime: last?.plannedArriveTime
    };
    emit(
      'update:modelValue',
      renumber([...(props.modelValue as SegmentRow[]), next])
    );
  };

  const removeRow = (idx: number) => {
    if (props.modelValue.length <= 1) return;
    const next = [...(props.modelValue as SegmentRow[])];
    next.splice(idx, 1);
    emit('update:modelValue', renumber(next));
  };

  /** 拼接级联文本（"省/市/区"） */
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

  const onFromChange = (idx: number, codes: string[] | undefined) => {
    const rows = [...(props.modelValue as SegmentRow[])];
    const r = { ...rows[idx] } as SegmentRow;
    if (codes && codes.length) {
      const leaf = findLeafRegionByCodePath(regionTree.value, codes);
      r.fromCode = codes[codes.length - 1];
      r.fromLocation = joinRegionName(codes);
      r.fromRegionId = leaf?.regionId ?? undefined;
      r._fromCodes = [...codes];
    } else {
      r.fromCode = undefined;
      r.fromLocation = '';
      r.fromRegionId = undefined;
      r._fromCodes = undefined;
    }
    rows[idx] = r;
    emit('update:modelValue', rows);
    void tryAutoFillMileage(idx);
  };

  const onToChange = (idx: number, codes: string[] | undefined) => {
    const rows = [...(props.modelValue as SegmentRow[])];
    const r = { ...rows[idx] } as SegmentRow;
    if (codes && codes.length) {
      const leaf = findLeafRegionByCodePath(regionTree.value, codes);
      r.toCode = codes[codes.length - 1];
      r.toLocation = joinRegionName(codes);
      r.toRegionId = leaf?.regionId ?? undefined;
      r._toCodes = [...codes];
    } else {
      r.toCode = undefined;
      r.toLocation = '';
      r.toRegionId = undefined;
      r._toCodes = undefined;
    }
    rows[idx] = r;
    emit('update:modelValue', rows);
    void tryAutoFillMileage(idx);
  };

  /** 起终都齐全时，自动查询「计费中心-线路管理」中的里程并填入 */
  async function tryAutoFillMileage(idx: number) {
    const r = props.modelValue[idx] as SegmentRow | undefined;
    if (!r || !r.fromRegionId || !r.toRegionId) return;
    try {
      const match = await lookupRouteDistance({
        originRegionId: r.fromRegionId,
        destinationRegionId: r.toRegionId
      });
      if (!match) return;
      const rows = [...(props.modelValue as SegmentRow[])];
      const cur = { ...rows[idx] } as SegmentRow;
      if (cur.mileage === undefined || cur.mileage === null) {
        cur.mileage = match.distance ?? undefined;
      }
      rows[idx] = cur;
      emit('update:modelValue', rows);
      if (match.distance !== null && match.distance !== undefined) {
        EleMessage.success({
          message: `已自动填入里程 ${match.distance} km（来源：${match.routeName}）`,
          plain: true
        });
      }
    } catch {
      // 联想失败保持静默，允许用户手动填
    }
  }
</script>

<style lang="scss" scoped>
  .seg-table {
    &__title {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 8px;
    }
  }
</style>
