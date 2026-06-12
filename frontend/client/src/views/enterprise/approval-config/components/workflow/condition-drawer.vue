<!-- 条件分支配置抽屉（字段来自审批场景注册表） -->
<template>
  <el-drawer
    :model-value="visible"
    :size="460"
    title="条件设置"
    :append-to-body="true"
    @update:model-value="updateVisible"
  >
    <el-form v-if="branch" label-position="top">
      <el-form-item label="条件名称">
        <el-input v-model.trim="branch.nodeName" placeholder="请输入条件名称" />
      </el-form-item>

      <template v-if="isDefault">
        <el-alert
          type="info"
          :closable="false"
          show-icon
          title="这是默认分支：当以上条件都不满足时进入此流程，无需设置条件"
        />
      </template>

      <template v-else>
        <el-form-item label="满足关系">
          <el-radio-group v-model="logic">
            <el-radio value="and">且（全部满足）</el-radio>
            <el-radio value="or">或（满足其一）</el-radio>
          </el-radio-group>
        </el-form-item>

        <div v-for="(rule, idx) in rules" :key="idx" class="wf-rule-row">
          <el-select
            v-model="rule.field"
            placeholder="选择条件字段"
            style="width: 140px"
            @change="onFieldChange(rule)"
          >
            <el-option
              v-for="f in conditionFields"
              :key="f.field"
              :value="f.field"
              :label="f.label"
            />
          </el-select>
          <el-select v-model="rule.op" style="width: 110px">
            <el-option
              v-for="o in opsForRule(rule)"
              :key="o.value"
              :value="o.value"
              :label="o.label"
            />
          </el-select>
          <template v-if="fieldMeta(rule.field)?.valueType === 'select'">
            <el-select
              v-model="rule.value"
              placeholder="请选择"
              style="flex: 1"
            >
              <el-option
                v-for="opt in fieldMeta(rule.field)?.options || []"
                :key="String(opt.value)"
                :value="opt.value"
                :label="opt.label"
              />
            </el-select>
          </template>
          <el-input
            v-else-if="fieldMeta(rule.field)?.valueType === 'number'"
            v-model="rule.value"
            type="number"
            placeholder="请输入数值"
            style="flex: 1"
          />
          <el-input
            v-else
            v-model="rule.value"
            placeholder="请输入值"
            style="flex: 1"
          />
          <el-icon class="wf-rule-del" @click="removeRule(idx)">
            <Delete />
          </el-icon>
        </div>

        <el-button plain class="wf-add-rule" @click="addRule">
          + 添加条件规则
        </el-button>
        <p class="wf-rule-tip">
          条件字段由当前审批场景提供，提交审批时由业务侧写入 variables。
        </p>
      </template>
    </el-form>

    <template #footer>
      <el-button type="primary" @click="onConfirm">完成</el-button>
    </template>
  </el-drawer>
</template>

<script lang="ts" setup>
  import { computed } from 'vue';
  import { Delete } from '@element-plus/icons-vue';
  import type { ConditionBranch, ConditionRule } from '@/api/approval/model';
  import { CONDITION_OPS } from '@/api/approval/transform';
  import type { BizConditionField } from '@/views/approval/constants';

  const props = defineProps<{
    visible: boolean;
    /** 是否默认（否则）分支：列表最后一项 */
    isDefault?: boolean;
    /** 当前场景可配置的条件字段 */
    conditionFields?: BizConditionField[];
  }>();

  const emit = defineEmits<{
    (e: 'update:visible', v: boolean): void;
    (e: 'confirm'): void;
  }>();

  const branch = defineModel<ConditionBranch | null>('branch');

  const updateVisible = (v: boolean) => emit('update:visible', v);

  const onConfirm = () => {
    emit('confirm');
    updateVisible(false);
  };

  const fieldMeta = (field?: string) =>
    props.conditionFields?.find((f) => f.field === field);

  const numberOps = CONDITION_OPS.filter((o) =>
    ['==', '!=', '>', '>=', '<', '<='].includes(o.value)
  );
  const setOps = CONDITION_OPS.filter((o) =>
    ['==', '!=', 'in', 'not_in'].includes(o.value)
  );

  const opsForRule = (rule: ConditionRule) => {
    const meta = fieldMeta(rule.field);
    if (meta?.valueType === 'number') return numberOps;
    if (meta?.valueType === 'select') return setOps;
    return CONDITION_OPS;
  };

  const ensureCond = () => {
    if (!branch.value) return null;
    if (!branch.value.condition) {
      branch.value.condition = { logic: 'and', rules: [] };
    }
    return branch.value.condition;
  };

  const logic = computed<'and' | 'or'>({
    get: () => branch.value?.condition?.logic ?? 'and',
    set: (v) => {
      const c = ensureCond();
      if (c) c.logic = v;
    }
  });

  const rules = computed<ConditionRule[]>(
    () => branch.value?.condition?.rules ?? []
  );

  const onFieldChange = (rule: ConditionRule) => {
    rule.value = '';
    const meta = fieldMeta(rule.field);
    if (
      meta?.valueType === 'number' &&
      !numberOps.some((o) => o.value === rule.op)
    ) {
      rule.op = '==';
    }
  };

  const addRule = () => {
    const c = ensureCond();
    if (!c) return;
    const first = props.conditionFields?.[0];
    c.rules.push({
      field: first?.field ?? '',
      op: first?.valueType === 'number' ? '>=' : '==',
      value: ''
    });
  };

  const removeRule = (idx: number) => {
    branch.value?.condition?.rules.splice(idx, 1);
  };
</script>
