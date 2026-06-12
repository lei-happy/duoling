<!-- 条件分支配置抽屉（单层 and/or DSL，对齐后端 condition.py） -->
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
          <el-input
            v-model.trim="rule.field"
            placeholder="变量名，如 amount"
            style="width: 130px"
          />
          <el-select v-model="rule.op" style="width: 110px">
            <el-option
              v-for="o in CONDITION_OPS"
              :key="o.value"
              :value="o.value"
              :label="o.label"
            />
          </el-select>
          <el-input v-model="rule.value" placeholder="值" style="flex: 1" />
          <el-icon class="wf-rule-del" @click="removeRule(idx)">
            <Delete />
          </el-icon>
        </div>

        <el-button plain class="wf-add-rule" @click="addRule">
          + 添加条件规则
        </el-button>
        <p class="wf-rule-tip">
          变量名取自业务提交时的字段（variables），如金额 amount、单据类型
          doc_type 等。
        </p>
      </template>
    </el-form>

    <template #footer>
      <el-button type="primary" @click="updateVisible(false)">完成</el-button>
    </template>
  </el-drawer>
</template>

<script lang="ts" setup>
  import { computed } from 'vue';
  import { Delete } from '@element-plus/icons-vue';
  import type { ConditionBranch, ConditionRule } from '@/api/approval/model';
  import { CONDITION_OPS } from '@/api/approval/transform';

  defineProps<{
    visible: boolean;
    /** 是否默认（否则）分支：列表最后一项 */
    isDefault?: boolean;
  }>();

  const emit = defineEmits<{
    (e: 'update:visible', v: boolean): void;
  }>();

  /** 直接编辑画布树中的分支对象（两端共享同一响应式引用） */
  const branch = defineModel<ConditionBranch | null>('branch');

  const updateVisible = (v: boolean) => emit('update:visible', v);

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

  const addRule = () => {
    const c = ensureCond();
    if (c) c.rules.push({ field: '', op: '==', value: '' });
  };

  const removeRule = (idx: number) => {
    branch.value?.condition?.rules.splice(idx, 1);
  };
</script>
