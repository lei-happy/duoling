<template>
  <el-drawer
    :title="`成本政策详情 - ${policy?.policyName ?? ''}`"
    :model-value="visible"
    size="920px"
    :close-on-click-modal="false"
    @update:model-value="updateVisible"
  >
    <div v-if="policy" class="cost-policy-detail">
      <el-descriptions :column="2" border size="small">
        <el-descriptions-item label="政策编号">
          {{ policy.policyNo }}
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="statusTag(policy.status).type" size="small">
            {{ statusTag(policy.status).text }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="适用范围">
          {{ scopeLabel(policy.scopeType) }}
          <span v-if="policy.scopeId">#{{ policy.scopeId }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="承运类型">
          {{ carrierLabel(policy.carrierType) }}
        </el-descriptions-item>
        <el-descriptions-item label="生效期">
          {{ policy.effectiveDate }} ~ {{ policy.expiryDate || '长期' }}
        </el-descriptions-item>
        <el-descriptions-item label="优先级">
          {{ policy.priority }}
        </el-descriptions-item>
      </el-descriptions>

      <div class="rule-toolbar">
        <span class="rule-title">费用规则（{{ ruleList.length }}）</span>
        <el-button type="primary" size="small" @click="openRuleEdit()">
          新增规则
        </el-button>
      </div>

      <el-empty
        v-if="!ruleLoading && !ruleList.length"
        description="暂无费用规则"
        :image-size="70"
      />
      <el-collapse v-else v-model="activeNames" v-loading="ruleLoading">
        <el-collapse-item
          v-for="g in groupedRules"
          :key="g.feeType"
          :name="g.feeType"
        >
          <template #title>
            <span class="grp-title">{{ g.feeName }}</span>
            <el-tag
              v-if="g.isRequired"
              type="danger"
              size="small"
              class="grp-tag"
            >
              必算
            </el-tag>
            <el-tag type="info" size="small" class="grp-tag">
              {{ g.rules.length }} 条
            </el-tag>
          </template>

          <el-table :data="g.rules" border size="small">
            <el-table-column label="方向" width="80" align="center">
              <template #default="{ row }">
                <el-tag
                  :type="row.direction === 1 ? 'success' : 'warning'"
                  size="small"
                >
                  {{ row.direction === 1 ? '加项' : '扣减' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="计价方式" width="100" align="center">
              <template #default="{ row }">
                {{ pricingLabel(row.pricingMethod) }}
              </template>
            </el-table-column>
            <el-table-column
              prop="unitPrice"
              label="单价"
              width="90"
              align="right"
            />
            <el-table-column label="适用条件" min-width="200">
              <template #default="{ row }">
                <el-tag v-if="row.conditionsJson" size="small" type="warning">
                  高级
                </el-tag>
                <span class="cond-summary-text">{{ ruleSummary(row) }}</span>
              </template>
            </el-table-column>
            <el-table-column label="状态" width="70" align="center">
              <template #default="{ row }">
                <el-tag
                  :type="row.status === 1 ? 'success' : 'info'"
                  size="small"
                >
                  {{ row.status === 1 ? '启用' : '停用' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column
              label="操作"
              width="170"
              align="center"
              fixed="right"
            >
              <template #default="{ row }">
                <el-button link type="primary" @click="openRuleEdit(row)">
                  编辑
                </el-button>
                <el-button link type="primary" @click="recalc(row)">
                  重算
                </el-button>
                <el-button link type="danger" @click="removeRuleItem(row)">
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-collapse-item>
      </el-collapse>
    </div>

    <cost-rule-edit
      v-if="policy"
      v-model:visible="ruleEditVisible"
      :policy-id="policy.id!"
      :data="ruleEditData"
      :meta="meta"
      @done="loadRules"
    />
  </el-drawer>
</template>

<script lang="ts" setup>
  import { ref, computed, watch } from 'vue';
  import { ElMessageBox } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import CostRuleEdit from './cost-rule-edit.vue';
  import {
    getPolicy,
    listRules,
    removeRule,
    recalculateAffectedByRule
  } from '@/api/billing/cost-policy';
  import type {
    CostPolicy,
    CostRule,
    CostMeta,
    ConditionType
  } from '@/api/billing/cost-policy/model';
  import {
    legacyToConditionTree,
    summarizeCondition
  } from '@/api/billing/cost-policy/model';

  const props = defineProps<{
    visible: boolean;
    policyId: number | null;
    meta: CostMeta;
  }>();

  const emit = defineEmits<{
    (e: 'update:visible', value: boolean): void;
  }>();

  const policy = ref<CostPolicy | null>(null);
  const ruleList = ref<CostRule[]>([]);
  const ruleLoading = ref(false);
  const ruleEditVisible = ref(false);
  const ruleEditData = ref<CostRule | null>(null);
  const activeNames = ref<string[]>([]);

  const typeMap = computed<Record<string, ConditionType>>(() => {
    const m: Record<string, ConditionType> = {};
    (props.meta.conditionTypes || []).forEach((c) => (m[c.key] = c));
    return m;
  });

  const ruleSummary = (row: CostRule): string => {
    const tree = row.conditionsJson || legacyToConditionTree(row);
    return summarizeCondition(tree, typeMap.value);
  };

  interface RuleGroup {
    feeType: string;
    feeName: string;
    isRequired: boolean;
    rules: CostRule[];
  }

  const groupedRules = computed<RuleGroup[]>(() => {
    const metaMap = new Map(props.meta.feeTypes.map((f) => [f.code, f]));
    const byType = new Map<string, CostRule[]>();
    for (const r of ruleList.value) {
      const arr = byType.get(r.feeType) ?? [];
      arr.push(r);
      byType.set(r.feeType, arr);
    }
    const groups: RuleGroup[] = [];
    // 先按 meta 顺序（必算项靠前、语义稳定），再补 meta 之外的费用类型
    for (const ft of props.meta.feeTypes) {
      const rules = byType.get(ft.code);
      if (rules) {
        groups.push({
          feeType: ft.code,
          feeName: ft.name,
          isRequired: ft.isRequired,
          rules
        });
        byType.delete(ft.code);
      }
    }
    for (const [code, rules] of byType) {
      const m = metaMap.get(code);
      groups.push({
        feeType: code,
        feeName: m?.name ?? rules[0]?.feeName ?? code,
        isRequired: !!m?.isRequired,
        rules
      });
    }
    return groups;
  });

  // 规则变化时默认展开所有费用分组
  watch(groupedRules, (groups) => {
    activeNames.value = groups.map((g) => g.feeType);
  });

  const updateVisible = (val: boolean) => emit('update:visible', val);

  const statusTag = (s?: number) => {
    switch (s) {
      case 1:
        return { type: 'success', text: '生效' };
      case 2:
        return { type: 'info', text: '已过期' };
      case 3:
        return { type: 'danger', text: '已终止' };
      default:
        return { type: 'warning', text: '草稿' };
    }
  };
  const scopeLabel = (t: number) =>
    ({ 0: '全局默认', 1: '指定承运商', 2: '指定司机', 3: '指定运力' })[t] ??
    '-';
  const carrierLabel = (t?: number | null) =>
    t == null
      ? '不限'
      : ({ 1: '自有车', 2: '承运商', 3: '社会运力' }[t] ?? '-');
  const pricingLabel = (v: string) =>
    props.meta.pricingMethods.find((p) => p.value === v)?.label ?? v;

  const loadPolicy = async () => {
    if (!props.policyId) return;
    policy.value = await getPolicy(props.policyId);
    ruleList.value = policy.value.rules ?? [];
  };

  const loadRules = async () => {
    if (!props.policyId) return;
    ruleLoading.value = true;
    try {
      ruleList.value = (await listRules(props.policyId)) ?? [];
    } finally {
      ruleLoading.value = false;
    }
  };

  watch(
    () => props.visible,
    (val) => {
      if (val) loadPolicy();
    }
  );

  const openRuleEdit = (row?: CostRule) => {
    ruleEditData.value = row ?? null;
    ruleEditVisible.value = true;
  };

  const removeRuleItem = (row: CostRule) => {
    ElMessageBox.confirm(
      `确定删除费用规则「${row.feeName || row.feeType}」吗？`,
      '系统提示',
      { type: 'warning', draggable: true }
    )
      .then(async () => {
        await removeRule(row.id!);
        EleMessage.success({ message: '删除成功', plain: true });
        loadRules();
      })
      .catch(() => {});
  };

  const recalc = (row: CostRule) => {
    ElMessageBox.confirm(
      '将触发该规则受影响任务的批量重算，确定继续？',
      '系统提示',
      { type: 'info', draggable: true }
    )
      .then(async () => {
        const r = await recalculateAffectedByRule(row.id!);
        EleMessage.success({
          message: `已入队 ${r.enqueuedTaskCount}/${r.affectedTaskCount} 个任务`,
          plain: true
        });
      })
      .catch(() => {});
  };
</script>

<style scoped>
  .rule-toolbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin: 16px 0 8px;
  }
  .rule-title {
    font-weight: 600;
  }
  .grp-title {
    font-weight: 600;
  }
  .grp-tag {
    margin-left: 8px;
  }
</style>
