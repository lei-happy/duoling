<template>
  <el-dialog
    :model-value="visible"
    :title="item ? '修改工资项' : '新增工资项'"
    width="520px"
    destroy-on-close
    draggable
    :close-on-click-modal="false"
    @update:model-value="(v: boolean) => emit('update:visible', v)"
    @open="onOpen"
  >
    <div v-if="item" class="finance-identity">
      <div class="finance-identity__name">
        {{ item.itemName || item.itemType }}
      </div>
      <div class="finance-identity__meta">{{ categoryHint }}</div>
    </div>
    <el-form :model="form" label-width="0" class="finance-edit-form">
      <el-form-item v-if="!item">
        <el-select
          v-model="form.itemType"
          filterable
          allow-create
          default-first-option
          placeholder="请选择或输入工资项"
          style="width: 100%"
          @change="onPresetChange"
        >
          <el-option
            v-for="p in PAYROLL_ITEM_PRESETS"
            :key="p.itemType"
            :value="p.itemType"
            :label="p.itemName"
          />
        </el-select>
      </el-form-item>
      <el-form-item>
        <floating-label
          label="请输入项目名称"
          type="input"
          v-model="form.itemName"
          :maxlength="50"
          clearable
        />
      </el-form-item>
      <el-form-item v-if="!item">
        <div class="finance-switch-field">
          <span>加减方向</span>
          <el-radio-group v-model="form.category">
            <el-radio
              v-for="o in PAYROLL_ITEM_CATEGORY_OPTIONS"
              :key="o.value"
              :value="o.value"
            >
              {{ o.label }}
            </el-radio>
          </el-radio-group>
        </div>
      </el-form-item>
      <el-form-item>
        <floating-label
          v-model="form.amount"
          :label="`请输入金额，填正数，${categoryHint}`"
          type="input-number"
          :input-number-min="0.01"
          :input-number-precision="2"
          :input-number-step="10"
        />
      </el-form-item>
      <el-form-item>
        <floating-label
          label="请输入计算说明，选填"
          type="input"
          v-model="form.formula"
          :maxlength="255"
          clearable
        />
      </el-form-item>
      <el-form-item>
        <floating-label
          label="请输入备注，选填"
          type="input"
          v-model="form.remark"
          :maxlength="255"
          clearable
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="emit('update:visible', false)">取消</el-button>
      <el-button type="primary" :loading="saving" @click="save">保存</el-button>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
  import { computed, ref } from 'vue';
  import { EleMessage } from 'ele-admin-plus';
  import FloatingLabel from '@shared/FloatingLabel/index.vue';
  import {
    addPayrollItem,
    updatePayrollItem
  } from '@/api/finance/driver-payroll';
  import type { PayrollItem } from '@/api/finance/driver-payroll/model';
  import {
    PAYROLL_ITEM_CATEGORY_OPTIONS,
    PAYROLL_ITEM_PRESETS
  } from '../../status-config';

  const props = defineProps<{
    visible: boolean;
    payrollId?: number | null;
    item?: PayrollItem | null;
  }>();

  const emit = defineEmits<{
    (e: 'update:visible', v: boolean): void;
    (e: 'done'): void;
  }>();

  const saving = ref(false);
  const form = ref<{
    itemType: string;
    itemName?: string;
    category: number;
    amount?: number;
    formula?: string;
    remark?: string;
  }>({ itemType: '', category: 1 });

  const categoryHint = computed(() => {
    if (form.value.category === 2) return '扣减项会从应发里减掉';
    if (form.value.category === 3) return '抵账项会冲抵实发';
    return '应发项会加进应发合计';
  });

  const onOpen = () => {
    if (props.item) {
      form.value = {
        itemType: props.item.itemType,
        itemName: props.item.itemName,
        category: props.item.category,
        amount: props.item.amount,
        formula: props.item.formula,
        remark: props.item.remark
      };
    } else {
      form.value = { itemType: '', category: 1 };
    }
  };

  const onPresetChange = (value: string) => {
    const preset = PAYROLL_ITEM_PRESETS.find((p) => p.itemType === value);
    if (preset) {
      form.value.itemName = preset.itemName;
      form.value.category = preset.category;
    }
  };

  const save = async () => {
    if (!props.payrollId) return;
    if (!props.item && !form.value.itemType) {
      EleMessage.warning({ message: '请选择或输入工资项', plain: true });
      return;
    }
    if (!form.value.amount || form.value.amount <= 0) {
      EleMessage.warning({ message: '请填写金额', plain: true });
      return;
    }
    saving.value = true;
    try {
      if (props.item) {
        await updatePayrollItem(props.payrollId, props.item.id, {
          amount: form.value.amount,
          itemName: form.value.itemName,
          formula: form.value.formula,
          remark: form.value.remark
        });
      } else {
        await addPayrollItem(props.payrollId, {
          itemType: form.value.itemType,
          itemName: form.value.itemName,
          category: form.value.category,
          amount: form.value.amount,
          formula: form.value.formula,
          remark: form.value.remark
        });
      }
      EleMessage.success({ message: '已保存', plain: true });
      emit('update:visible', false);
      emit('done');
    } catch (e: unknown) {
      const msg = (e as { message?: string }).message || '保存失败，请稍后重试';
      EleMessage.error({ message: msg, plain: true });
    } finally {
      saving.value = false;
    }
  };
</script>

<style lang="scss" scoped>
  @use '../../_shared/ui.scss';
</style>
