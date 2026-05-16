<template>
  <el-drawer
    :model-value="visible"
    :title="dialogTitle"
    direction="rtl"
    size="900px"
    :destroy-on-close="true"
    :close-on-click-modal="false"
    @update:model-value="(v: boolean) => emit('update:visible', v)"
    @open="onOpen"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="100px"
      v-loading="loading"
    >
      <!-- 任务单摘要 -->
      <el-alert
        v-if="taskInfo"
        type="info"
        :closable="false"
        :title="`任务单 ${taskInfo.taskNo} · 承运方：${carrierLabel}`"
        style="margin-bottom: 12px"
      />

      <el-row :gutter="12">
        <el-col :span="8">
          <el-form-item label="单据类型" prop="docType">
            <el-select v-model="form.docType" :disabled="docId !== null">
              <el-option
                v-for="o in FIN_DOC_TYPE_OPTIONS"
                :key="o.value"
                :value="o.value"
                :label="o.label"
              />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col v-if="form.docType === 3" :span="8">
          <el-form-item label="最终结算单">
            <el-switch
              v-model="form.isFinal"
              :active-value="1"
              :inactive-value="0"
            />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="计划金额" prop="plannedAmount">
            <el-input-number
              v-model="form.plannedAmount"
              :min="0.01"
              :precision="2"
              controls-position="right"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="计划支付时间">
            <el-date-picker
              v-model="form.plannedPayTime"
              type="datetime"
              value-format="YYYY-MM-DDTHH:mm:ss"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="支付方式">
            <el-select v-model="form.payMethod" clearable>
              <el-option
                v-for="o in PAY_METHOD_OPTIONS"
                :key="o.value"
                :value="o.value"
                :label="o.label"
              />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="16">
          <el-form-item label="备注">
            <el-input v-model="form.remark" type="textarea" :rows="1" />
          </el-form-item>
        </el-col>
      </el-row>

      <el-divider content-position="left">收款对象</el-divider>
      <payee-picker
        ref="payeeRef"
        v-model="payee"
        :disabled="!editable"
      />

      <el-divider content-position="left">费用项明细</el-divider>
      <finance-item-table
        v-model="form.items"
        :disabled="!editable"
        @total-change="onTotalChange"
      />
    </el-form>

    <!-- 详情/状态推进时的操作按钮 -->
    <template #footer>
      <div class="finance-edit__footer">
        <div>
          <el-tag
            v-if="doc?.status !== undefined"
            :type="(FIN_STATUS_MAP[doc.status]?.type as any) || 'info'"
            size="large"
          >
            当前状态：{{ FIN_STATUS_MAP[doc.status]?.label }}
          </el-tag>
        </div>
        <div class="finance-edit__btns">
          <el-button @click="emit('update:visible', false)">关闭</el-button>
          <el-button v-if="editable" type="primary" :loading="submitting" @click="submit">
            保存
          </el-button>
          <el-button
            v-if="doc?.status === 0"
            type="warning"
            :loading="submitting"
            @click="onSubmitFlow"
          >
            提交审批
          </el-button>
          <el-button
            v-if="doc?.status === 1"
            type="primary"
            :loading="submitting"
            @click="onApprove"
          >
            审批通过
          </el-button>
          <el-button
            v-if="doc?.status === 2"
            type="success"
            :loading="submitting"
            @click="openPayDialog"
          >
            标记已支付
          </el-button>
          <el-button
            v-if="doc && [0, 1, 2].includes(doc.status!)"
            type="danger"
            :loading="submitting"
            @click="onCancel"
          >
            撤销
          </el-button>
        </div>
      </div>
    </template>

    <!-- 标记已支付弹窗 -->
    <el-dialog
      v-model="payDialogVisible"
      title="标记已支付"
      width="480px"
      destroy-on-close
    >
      <el-form :model="payForm" label-width="110px">
        <el-form-item label="实际金额" required>
          <el-input-number
            v-model="payForm.actualAmount"
            :min="0.01"
            :precision="2"
            controls-position="right"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="支付方式" required>
          <el-select v-model="payForm.payMethod" style="width: 100%">
            <el-option
              v-for="o in PAY_METHOD_OPTIONS"
              :key="o.value"
              :value="o.value"
              :label="o.label"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="支付时间" required>
          <el-date-picker
            v-model="payForm.actualPayTime"
            type="datetime"
            value-format="YYYY-MM-DDTHH:mm:ss"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="凭证 URL">
          <el-input v-model="payForm.payVoucherUrl" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="payForm.remark" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="payDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="onPay">
          确定
        </el-button>
      </template>
    </el-dialog>
  </el-drawer>
</template>

<script lang="ts" setup>
  import { computed, reactive, ref, watch } from 'vue';
  import type { FormInstance, FormRules } from 'element-plus';
  import { ElMessageBox } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import FinanceItemTable from './finance-item-table.vue';
  import PayeePicker from './payee-picker.vue';
  import type { PayeeFormData } from './payee-picker.vue';
  import {
    addFinanceDoc,
    approveFinanceDoc,
    cancelFinanceDoc,
    getFinanceDoc,
    payFinanceDoc,
    submitFinanceDoc,
    updateFinanceDoc
  } from '@/api/operation/task-finance';
  import type {
    TaskFinanceDoc,
    TaskFinanceDocCreatePayload,
    TaskFinanceItem
  } from '@/api/operation/task-finance/model';
  import type { Task } from '@/api/operation/task/model';
  import {
    FIN_DOC_TYPE_OPTIONS,
    FIN_STATUS_MAP,
    PAY_METHOD_OPTIONS
  } from '../status-config';
  import { CARRIER_TYPE_MAP } from '../../task/status-config';

  const props = defineProps<{
    visible: boolean;
    task: Task;
    docId: number | null;
  }>();
  const emit = defineEmits<{
    (e: 'update:visible', v: boolean): void;
    (e: 'done'): void;
  }>();

  const formRef = ref<FormInstance | null>(null);
  const payeeRef = ref<{ init: (d?: { driverId?: number; carrierId?: number }) => void } | null>(null);
  const loading = ref(false);
  const submitting = ref(false);

  const taskInfo = computed(() => props.task);
  const carrierLabel = computed(() => {
    if (!taskInfo.value) return '--';
    return (
      CARRIER_TYPE_MAP[taskInfo.value.carrierType || 1]?.label
      + (taskInfo.value.carrierType === 2
        ? ` · ${taskInfo.value.carrierName || ''}`
        : ` · ${taskInfo.value.mainDriverName || ''} ${taskInfo.value.plateNumber || ''}`)
    );
  });

  const doc = ref<TaskFinanceDoc | null>(null);

  const defaultPayee = (): PayeeFormData => {
    // 根据任务单 carrier_type 默认推断收款类型
    const ct = props.task?.carrierType || 1;
    if (ct === 2) {
      return {
        payeeType: 2,
        payeeId: props.task?.carrierId ?? null,
        payeeName: props.task?.carrierName || ''
      };
    }
    return {
      payeeType: 1,
      payeeId: null,
      payeeName: props.task?.mainDriverName || ''
    };
  };

  const defaultForm = (): TaskFinanceDocCreatePayload => ({
    docType: 1,
    isFinal: 0,
    payeeType: 1,
    payeeId: null,
    payeeName: '',
    payeeAccountType: null,
    payeeAccountId: null,
    plannedAmount: 0,
    currency: 'CNY',
    payMethod: undefined,
    plannedPayTime: undefined,
    remark: '',
    items: []
  });

  const form = reactive<TaskFinanceDocCreatePayload>(defaultForm());
  const payee = reactive<PayeeFormData>(defaultPayee());

  const editable = computed(() => {
    if (!doc.value) return true; // 新增模式
    return doc.value.status === 0 || doc.value.status === 1;
  });

  const dialogTitle = computed(() => {
    if (!doc.value) return '新建费用单';
    return `费用单 ${doc.value.docNo}`;
  });

  const rules: FormRules = {
    docType: [{ required: true }],
    plannedAmount: [{ required: true, message: '请填写计划金额' }]
  };

  watch(
    () => props.visible,
    async (v) => {
      if (!v) return;
      Object.assign(form, defaultForm());
      Object.assign(payee, defaultPayee());
      doc.value = null;
      if (props.docId) {
        await loadDetail(props.docId);
      }
    }
  );

  const loadDetail = async (id: number) => {
    loading.value = true;
    try {
      const d = await getFinanceDoc(id);
      if (!d) return;
      doc.value = d;
      form.docType = d.docType;
      form.isFinal = d.isFinal ?? 0;
      form.plannedAmount = d.plannedAmount;
      form.payMethod = d.payMethod ?? undefined;
      form.plannedPayTime = d.plannedPayTime;
      form.remark = d.remark || '';
      form.items = (d.items || []).map((it: TaskFinanceItem) => ({
        ...it
      }));
      Object.assign(payee, {
        payeeType: d.payeeType,
        payeeId: d.payeeId,
        payeeName: d.payeeName,
        payeeAccountType: d.payeeAccountType,
        payeeAccountId: d.payeeAccountId,
        payeeBankName: d.payeeBankName,
        payeeBankAccountMasked: d.payeeBankAccountMasked
      });
    } finally {
      loading.value = false;
    }
  };

  const onOpen = () => {
    setTimeout(() => {
      payeeRef.value?.init({
        driverId: payee.payeeType === 1 ? payee.payeeId ?? undefined : undefined,
        carrierId: payee.payeeType === 2 ? payee.payeeId ?? undefined : undefined
      });
    }, 0);
  };

  const onTotalChange = (total: number) => {
    if (!doc.value && (!form.plannedAmount || form.plannedAmount === 0)) {
      form.plannedAmount = Number(total.toFixed(2));
    }
  };

  const submit = async () => {
    try {
      await formRef.value?.validate();
    } catch {
      return;
    }
    if (form.items.length === 0) {
      EleMessage.error({ message: '请至少添加 1 条费用项', plain: true });
      return;
    }
    if (payee.payeeType !== 3 && !payee.payeeId) {
      EleMessage.error({ message: '请选择收款人', plain: true });
      return;
    }
    if (payee.payeeType === 3 && !payee.payeeName?.trim()) {
      EleMessage.error({ message: '请填写收款人姓名', plain: true });
      return;
    }

    submitting.value = true;
    try {
      const payload: TaskFinanceDocCreatePayload = {
        ...form,
        payeeType: payee.payeeType,
        payeeId: payee.payeeId ?? null,
        payeeName: payee.payeeName,
        payeeAccountType: payee.payeeAccountType ?? null,
        payeeAccountId: payee.payeeAccountId ?? null,
        payeeBankName: payee.payeeBankName,
        payeeBankAccountMasked: payee.payeeBankAccountMasked
      };
      if (props.docId) {
        await updateFinanceDoc(props.docId, payload);
        EleMessage.success({ message: '已保存', plain: true });
      } else {
        await addFinanceDoc(props.task.id!, payload);
        EleMessage.success({ message: '已创建', plain: true });
      }
      emit('done');
      emit('update:visible', false);
    } catch (e: unknown) {
      const msg = (e as { message?: string }).message || '保存失败';
      EleMessage.error({ message: msg, plain: true });
    } finally {
      submitting.value = false;
    }
  };

  const onSubmitFlow = async () => {
    if (!props.docId) return;
    submitting.value = true;
    try {
      const updated = await submitFinanceDoc(props.docId);
      doc.value = updated;
      EleMessage.success({ message: '已提交审批', plain: true });
      emit('done');
    } catch (e: unknown) {
      const msg = (e as { message?: string }).message || '操作失败';
      EleMessage.error({ message: msg, plain: true });
    } finally {
      submitting.value = false;
    }
  };

  const onApprove = async () => {
    if (!props.docId) return;
    submitting.value = true;
    try {
      const updated = await approveFinanceDoc(props.docId);
      doc.value = updated;
      EleMessage.success({ message: '审批通过', plain: true });
      emit('done');
    } catch (e: unknown) {
      const msg = (e as { message?: string }).message || '操作失败';
      EleMessage.error({ message: msg, plain: true });
    } finally {
      submitting.value = false;
    }
  };

  const onCancel = async () => {
    if (!props.docId) return;
    try {
      const { value: reason } = await ElMessageBox.prompt(
        '请输入撤销原因（可选）',
        '撤销费用单',
        { confirmButtonText: '确定', cancelButtonText: '不撤销' }
      );
      submitting.value = true;
      const updated = await cancelFinanceDoc(props.docId, reason || undefined);
      doc.value = updated;
      EleMessage.success({ message: '已撤销', plain: true });
      emit('done');
    } catch (e: unknown) {
      const err = e as { message?: string } | string;
      if (err === 'cancel') return;
      const msg = (typeof err === 'object' && err?.message) || '';
      if (msg) EleMessage.error({ message: msg, plain: true });
    } finally {
      submitting.value = false;
    }
  };

  // 标记已支付
  const payDialogVisible = ref(false);
  const payForm = reactive({
    actualAmount: 0,
    payMethod: 1,
    actualPayTime: '',
    payVoucherUrl: '',
    remark: ''
  });

  const openPayDialog = () => {
    if (!doc.value) return;
    payForm.actualAmount = Number(doc.value.plannedAmount || 0);
    payForm.payMethod = doc.value.payMethod || 1;
    payForm.actualPayTime = new Date().toISOString().slice(0, 19);
    payForm.payVoucherUrl = '';
    payForm.remark = '';
    payDialogVisible.value = true;
  };

  const onPay = async () => {
    if (!props.docId) return;
    if (!payForm.actualAmount || payForm.actualAmount <= 0) {
      EleMessage.error({ message: '请填写实际金额', plain: true });
      return;
    }
    if (!payForm.actualPayTime) {
      EleMessage.error({ message: '请选择支付时间', plain: true });
      return;
    }
    submitting.value = true;
    try {
      const updated = await payFinanceDoc(props.docId, {
        actualAmount: payForm.actualAmount,
        payMethod: payForm.payMethod,
        actualPayTime: payForm.actualPayTime,
        payVoucherUrl: payForm.payVoucherUrl || undefined,
        remark: payForm.remark || undefined
      });
      doc.value = updated;
      EleMessage.success({ message: '已支付', plain: true });
      payDialogVisible.value = false;
      emit('done');
    } catch (e: unknown) {
      const msg = (e as { message?: string }).message || '操作失败';
      EleMessage.error({ message: msg, plain: true });
    } finally {
      submitting.value = false;
    }
  };
</script>

<style lang="scss" scoped>
  .finance-edit__footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100%;
  }
  .finance-edit__btns {
    display: flex;
    gap: 8px;
  }
</style>
