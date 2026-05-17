<!--
  标记已支付弹窗（费用单 status 2 → 3）

  作业语义：出纳完成支付后，录入实际金额/方式/时间/凭证，把费用单标记为"已支付"。
  支持单单和批量；批量时同一金额/方式/时间应用到所有选中费用单。
-->
<template>
  <el-dialog
    :model-value="visible"
    :title="title"
    width="520px"
    destroy-on-close
    :close-on-click-modal="false"
    @update:model-value="(v: boolean) => emit('update:visible', v)"
    @open="onOpen"
  >
    <el-form ref="formRef" :model="form" :rules="rules" label-width="110px">
      <el-form-item label="费用单">
        <div class="action-pay__info">
          <template v-if="docs.length === 1">
            <b>{{ docs[0].docNo }}</b>
            <span class="ele-text-secondary" style="margin-left: 8px">
              {{ docs[0].payeeName || '--' }} · 计划 ¥
              {{ Number(docs[0].plannedAmount || 0).toFixed(2) }}
            </span>
          </template>
          <template v-else>
            <el-tag type="warning" size="small">
              批量支付 {{ docs.length }} 张 · 计划合计 ¥
              {{ plannedTotal }}
            </el-tag>
          </template>
        </div>
      </el-form-item>
      <el-form-item label="实际金额" prop="actualAmount" required>
        <el-input-number
          v-model="form.actualAmount"
          :min="0.01"
          :precision="2"
          controls-position="right"
          style="width: 100%"
        />
        <div
          v-if="docs.length > 1"
          class="ele-text-secondary"
          style="font-size: 12px; margin-top: 4px"
        >
          批量模式下，金额将作为"每张单"的实际金额（按需调整为合计或每张）
        </div>
      </el-form-item>
      <el-form-item label="支付方式" prop="payMethod" required>
        <el-select v-model="form.payMethod" style="width: 100%">
          <el-option
            v-for="o in PAY_METHOD_OPTIONS"
            :key="o.value"
            :value="o.value"
            :label="o.label"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="支付时间" prop="actualPayTime" required>
        <el-date-picker
          v-model="form.actualPayTime"
          type="datetime"
          value-format="YYYY-MM-DDTHH:mm:ss"
          style="width: 100%"
        />
      </el-form-item>
      <el-form-item label="凭证 URL">
        <el-input v-model="form.payVoucherUrl" placeholder="可选" />
      </el-form-item>
      <el-form-item label="备注">
        <el-input v-model="form.remark" type="textarea" :rows="2" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="emit('update:visible', false)">取消</el-button>
      <el-button type="success" :loading="submitting" @click="submit">
        确认已支付
      </el-button>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
  import { computed, reactive, ref } from 'vue';
  import type { FormInstance, FormRules } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import { payFinanceDoc } from '@/api/operation/task-finance';
  import type {
    TaskFinanceDoc,
    TaskFinanceDocListItem
  } from '@/api/operation/task-finance/model';
  import { PAY_METHOD_OPTIONS } from '../../task-finance/status-config';

  type PayableDoc = Pick<
    TaskFinanceDoc | TaskFinanceDocListItem,
    'id' | 'docNo' | 'payeeName' | 'plannedAmount' | 'payMethod'
  >;

  const props = defineProps<{
    visible: boolean;
    docs: PayableDoc[];
  }>();
  const emit = defineEmits<{
    (e: 'update:visible', v: boolean): void;
    (e: 'done'): void;
  }>();

  const formRef = ref<FormInstance | null>(null);
  const submitting = ref(false);

  const form = reactive({
    actualAmount: 0,
    payMethod: 1,
    actualPayTime: '',
    payVoucherUrl: '',
    remark: ''
  });

  const rules: FormRules = {
    actualAmount: [{ required: true, message: '请填写实际金额' }],
    payMethod: [{ required: true, message: '请选择支付方式' }],
    actualPayTime: [{ required: true, message: '请选择支付时间' }]
  };

  const title = computed(() =>
    props.docs.length > 1 ? '批量标记已支付' : '标记已支付'
  );

  const plannedTotal = computed(() =>
    props.docs
      .reduce((sum, d) => sum + Number(d.plannedAmount || 0), 0)
      .toFixed(2)
  );

  const onOpen = () => {
    if (props.docs.length === 1) {
      form.actualAmount = Number(props.docs[0].plannedAmount || 0);
      form.payMethod = props.docs[0].payMethod || 1;
    } else if (props.docs.length > 1) {
      form.actualAmount = 0;
      form.payMethod = 1;
    }
    form.actualPayTime = new Date().toISOString().slice(0, 19);
    form.payVoucherUrl = '';
    form.remark = '';
  };

  const submit = async () => {
    try {
      await formRef.value?.validate();
    } catch {
      return;
    }
    if (!props.docs.length) {
      emit('update:visible', false);
      return;
    }
    submitting.value = true;
    try {
      let failCount = 0;
      for (const d of props.docs) {
        if (!d.id) continue;
        try {
          await payFinanceDoc(d.id, {
            actualAmount: form.actualAmount,
            payMethod: form.payMethod,
            actualPayTime: form.actualPayTime,
            payVoucherUrl: form.payVoucherUrl || undefined,
            remark: form.remark || undefined
          });
        } catch {
          failCount += 1;
        }
      }
      if (failCount > 0) {
        EleMessage.warning({
          message: `已完成 ${props.docs.length - failCount} 张，失败 ${failCount} 张`,
          plain: true
        });
      } else {
        EleMessage.success({ message: '已标记为已支付', plain: true });
      }
      emit('done');
      emit('update:visible', false);
    } finally {
      submitting.value = false;
    }
  };
</script>

<style lang="scss" scoped>
  .action-pay__info {
    line-height: 32px;
  }
</style>
