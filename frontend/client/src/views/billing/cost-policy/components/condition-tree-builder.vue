<template>
  <div class="cond-group" :class="{ 'cond-group--nested': !isRoot }">
    <div class="cond-group__head">
      <el-radio-group v-model="model.logic" size="small">
        <el-radio-button label="and">且(全部满足)</el-radio-button>
        <el-radio-button label="or">或(任一满足)</el-radio-button>
      </el-radio-group>
      <el-button
        v-if="!isRoot"
        link
        type="danger"
        size="small"
        @click="emit('remove')"
      >
        删除分组
      </el-button>
    </div>

    <div class="cond-group__body">
      <template v-for="(child, idx) in children" :key="idx">
        <!-- 分组：递归 -->
        <condition-tree-builder
          v-if="isGroup(child)"
          :node="child"
          :condition-types="conditionTypes"
          :is-root="false"
          @remove="removeChild(idx)"
        />
        <!-- 叶子：条件编辑行 -->
        <div v-else class="cond-leaf">
          <el-select
            v-model="child.type"
            placeholder="条件类型"
            size="small"
            class="cond-leaf__type"
            @change="onTypeChange(child)"
          >
            <el-option
              v-for="ct in conditionTypes"
              :key="ct.key"
              :label="ct.label"
              :value="ct.key"
            />
          </el-select>

          <!-- 字段选择（带 fields 的条件类型：text_contains/vehicle_attr/... ） -->
          <el-select
            v-if="descriptor(child.type)?.fields?.length"
            v-model="child.field"
            placeholder="字段"
            size="small"
            class="cond-leaf__field"
          >
            <el-option
              v-for="f in descriptor(child.type)!.fields"
              :key="f.value"
              :label="f.label"
              :value="f.value"
            />
          </el-select>

          <!-- 操作符 -->
          <el-select
            v-if="operators(child.type).length > 1"
            v-model="child.op"
            placeholder="操作"
            size="small"
            class="cond-leaf__op"
          >
            <el-option
              v-for="op in operators(child.type)"
              :key="op"
              :label="opLabel(op)"
              :value="op"
            />
          </el-select>

          <!-- 值输入：按 valueType 动态渲染 -->
          <template v-if="child.type === 'region_route'">
            <el-input-number
              v-model="child.originRegionId"
              :min="1"
              size="small"
              controls-position="right"
              placeholder="起点行政区ID"
              class="cond-leaf__num"
            />
            <el-input-number
              v-model="child.destinationRegionId"
              :min="1"
              size="small"
              controls-position="right"
              placeholder="终点行政区ID"
              class="cond-leaf__num"
            />
            <el-switch
              v-model="child.bidirectional"
              :active-value="1"
              :inactive-value="0"
              inline-prompt
              active-text="双向"
              inactive-text="单向"
            />
          </template>
          <template v-else-if="isRangeType(child) && child.op === 'between'">
            <el-input-number
              v-model="rangeLo[idx]"
              size="small"
              controls-position="right"
              placeholder="下限"
              class="cond-leaf__num"
              @change="syncRange(child, idx)"
            />
            <span class="cond-leaf__tilde">~</span>
            <el-input-number
              v-model="rangeHi[idx]"
              size="small"
              controls-position="right"
              placeholder="上限"
              class="cond-leaf__num"
              @change="syncRange(child, idx)"
            />
          </template>
          <el-input-number
            v-else-if="isNumberValue(child)"
            v-model="child.value as number"
            size="small"
            controls-position="right"
            placeholder="值"
            class="cond-leaf__num"
          />
          <el-input
            v-else
            v-model="child.value as string"
            size="small"
            placeholder="值"
            class="cond-leaf__val"
          />

          <el-switch
            v-model="child.negate"
            inline-prompt
            active-text="非"
            inactive-text="是"
          />
          <el-button link type="danger" size="small" @click="removeChild(idx)">
            删除
          </el-button>
        </div>
      </template>

      <div class="cond-group__actions">
        <el-button size="small" @click="addLeaf">+ 条件</el-button>
        <el-button size="small" @click="addGroup">+ 分组</el-button>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
  import { computed, reactive } from 'vue';
  import type {
    ConditionNode,
    ConditionType
  } from '@/api/billing/cost-policy/model';

  defineOptions({ name: 'ConditionTreeBuilder' });

  const props = withDefaults(
    defineProps<{
      node: ConditionNode;
      conditionTypes: ConditionType[];
      isRoot?: boolean;
    }>(),
    { isRoot: true }
  );

  const emit = defineEmits<{ (e: 'remove'): void }>();

  // 以本地引用操作同一个响应式对象（避免直接以 prop 名赋值触发 no-mutating-props）
  const model = props.node;
  if (!model.logic) model.logic = 'and';
  if (!Array.isArray(model.children)) model.children = [];

  const children = computed(() => model.children as ConditionNode[]);

  // between 区间的临时上下限缓存（value 存 [lo, hi]）
  const rangeLo = reactive<Record<number, number | undefined>>({});
  const rangeHi = reactive<Record<number, number | undefined>>({});
  children.value.forEach((c, i) => {
    if (Array.isArray(c.value)) {
      rangeLo[i] = c.value[0] as number;
      rangeHi[i] = c.value[1] as number;
    }
  });

  const isGroup = (n: ConditionNode) =>
    n.logic !== undefined || n.children !== undefined;

  const descriptor = (type?: string) =>
    props.conditionTypes.find((c) => c.key === type);

  const operators = (type?: string) => descriptor(type)?.operators || ['eq'];

  const OP_LABELS: Record<string, string> = {
    eq: '等于',
    ne: '不等于',
    in: '属于',
    nin: '不属于',
    contains: '包含',
    gte: '≥',
    lte: '≤',
    gt: '>',
    lt: '<',
    between: '区间',
    match: '匹配'
  };
  const opLabel = (op: string) => OP_LABELS[op] || op;

  const NUMBER_TYPES = [
    'mileage_range',
    'quantity_range',
    'vehicle_brand',
    'vehicle_series',
    'carrier',
    'capacity',
    'driver',
    'enterprise',
    'carrier_type'
  ];
  const isRangeType = (n: ConditionNode) =>
    n.type === 'mileage_range' || n.type === 'quantity_range';
  const isNumberValue = (n: ConditionNode) =>
    NUMBER_TYPES.includes(n.type || '') && n.op !== 'in' && n.op !== 'nin';

  const syncRange = (child: ConditionNode, idx: number) => {
    child.value = [rangeLo[idx] ?? null, rangeHi[idx] ?? null];
  };

  const onTypeChange = (child: ConditionNode) => {
    const d = descriptor(child.type);
    child.op = d?.operators?.[0] || 'eq';
    child.value = null;
    child.field = d?.fields?.length ? d.fields[0].value : undefined;
    if (child.type === 'region_route') {
      child.originRegionId = null;
      child.destinationRegionId = null;
      child.bidirectional = 0;
    }
  };

  const addLeaf = () => {
    const first = props.conditionTypes[0];
    const leaf: ConditionNode = {
      type: first?.key || 'text_contains',
      op: first?.operators?.[0] || 'contains',
      value: null
    };
    if (first?.fields?.length) leaf.field = first.fields[0].value;
    if (leaf.type === 'region_route') {
      leaf.originRegionId = null;
      leaf.destinationRegionId = null;
      leaf.bidirectional = 0;
    }
    children.value.push(leaf);
  };

  const addGroup = () => {
    children.value.push({ logic: 'and', children: [] });
  };

  const removeChild = (idx: number) => {
    children.value.splice(idx, 1);
  };
</script>

<style scoped>
  .cond-group {
    width: 100%;
  }
  .cond-group--nested {
    border: 1px dashed var(--el-border-color);
    border-radius: 6px;
    padding: 8px;
    margin: 6px 0;
    background: var(--el-fill-color-lighter);
  }
  .cond-group__head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 8px;
  }
  .cond-group__body {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  .cond-leaf {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 6px;
  }
  .cond-leaf__type {
    width: 140px;
  }
  .cond-leaf__field {
    width: 130px;
  }
  .cond-leaf__op {
    width: 90px;
  }
  .cond-leaf__num {
    width: 120px;
  }
  .cond-leaf__val {
    width: 160px;
  }
  .cond-leaf__tilde {
    color: var(--el-text-color-secondary);
  }
  .cond-group__actions {
    display: flex;
    gap: 8px;
  }
</style>
