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
      <payee-picker ref="payeeRef" v-model="payee" :disabled="!editable" />

      <el-divider content-position="left">费用项明细</el-divider>
      <finance-item-table
        v-model="form.items"
        :disabled="!editable"
        @total-change="onTotalChange"
      />
    </el-form>

    <!-- 详情时仅展示当前状态对应的语义化主按钮 + 撤销次按钮 -->
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
          <el-button
            v-if="editable"
            type="primary"
            :loading="submitting"
            @click="submit"
          >
            保存
          </el-button>
          <!-- 当前状态唯一的语义化主按钮 -->
          <el-button
            v-if="primaryAction"
            :type="primaryAction.buttonType"
            :loading="submitting"
            v-permission="primaryAction.permission"
            @click="triggerPrimary"
          >
            {{ primaryAction.label }}
          </el-button>
          <!-- 次要动作（撤销） -->
          <el-button
            v-for="act in secondaryActions"
            :key="act.key"
            :type="act.buttonType"
            plain
            :loading="submitting"
            v-permission="act.permission"
            @click="triggerSecondary(act)"
          >
            {{ act.label }}
          </el-button>
        </div>
      </div>
    </template>

    <!-- 标记已支付弹窗（复用工作台抽出的组件） -->
    <action-pay
      v-if="doc"
      v-model:visible="payDialogVisible"
      :docs="[doc]"
      @done="onActionDone"
    />
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
  import ActionPay from '../../task-finance-workbench/components/action-pay.vue';
  import {
    addFinanceDoc,
    approveFinanceDoc,
    cancelFinanceDoc,
    getFinanceDoc,
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
  import {
    getPrimaryFinanceAction,
    getSecondaryFinanceActions
  } from '../task-finance-actions';
  import type { FinanceActionConfig } from '../task-finance-actions';

  const props = defineProps<{
    visible: boolean;
    task: Task;
    docId: number | null;
    /** 新建场景下的预填类型（如生成结算单时传 3） */
    initDocType?: number;
    /** 新建场景下的预填 is_final（如生成最终结算单时传 1） */
    initIsFinal?: number;
  }>();
  const emit = defineEmits<{
    (e: 'update:visible', v: boolean): void;
    (e: 'done'): void;
  }>();

  const formRef = ref<FormInstance | null>(null);
  const payeeRef = ref<{
    init: (d?: { driverId?: number; carrierId?: number }) => void;
  } | null>(null);
  const loading = ref(false);
  const submitting = ref(false);

  const taskInfo = computed(() => props.task);
  const carrierLabel = computed(() => {
    if (!taskInfo.value) return '--';
    return (
      CARRIER_TYPE_MAP[taskInfo.value.carrierType || 1]?.label +
      (taskInfo.value.carrierType === 2
        ? ` · ${taskInfo.value.carrierName || ''}`
        : ` · ${taskInfo.value.mainDriverName || ''} ${taskInfo.value.plateNumber || ''}`)
    );
  });

  const doc = ref<TaskFinanceDoc | null>(null);

  const defaultPayee = (): PayeeFormData => {
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
    docType: props.initDocType ?? 1,
    isFinal: props.initIsFinal ?? 0,
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
    if (!doc.value) return true;
    return doc.value.status === 0 || doc.value.status === 1;
  });

  const dialogTitle = computed(() => {
    if (!doc.value) {
      if ((props.initDocType ?? 1) === 3 && (props.initIsFinal ?? 0) === 1) {
        return '生成最终结算单';
      }
      return '新建费用单';
    }
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
      form.items = (d.items || []).map((it: TaskFinanceItem) => ({ ...it }));
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
        driverId:
          payee.payeeType === 1 ? (payee.payeeId ?? undefined) : undefined,
        carrierId:
          payee.payeeType === 2 ? (payee.payeeId ?? undefined) : undefined
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

  // ============================================
  // 语义化主按钮：根据当前状态确定主动作（提交审批 / 审批通过 / 标记已支付）
  // ============================================
  const primaryAction = computed(() =>
    getPrimaryFinanceAction(doc.value?.status)
  );
  const secondaryActions = computed(() =>
    getSecondaryFinanceActions(doc.value?.status)
  );

  const payDialogVisible = ref(false);

  const triggerPrimary = async () => {
    const act = primaryAction.value;
    if (!act || !doc.value?.id) return;
    if (act.dialog === 'pay') {
      payDialogVisible.value = true;
      return;
    }
    if (act.confirm) {
      await runSimpleAction(act);
    }
  };

  const triggerSecondary = async (act: FinanceActionConfig) => {
    if (!doc.value?.id) return;
    if (act.key === 'cancel') {
      await runCancelAction();
    }
  };

  const runSimpleAction = async (act: FinanceActionConfig) => {
    if (!doc.value?.id) return;
    const confirmMessages: Record<string, string> = {
      submit: `确认提交费用单「${doc.value.docNo}」进行审批？`,
      approve: `确认审批通过费用单「${doc.value.docNo}」？`
    };
    try {
      await ElMessageBox.confirm(
        confirmMessages[act.key] || `确认执行「${act.label}」？`,
        '操作确认',
        { type: 'warning', confirmButtonText: '确定', cancelButtonText: '取消' }
      );
    } catch {
      return;
    }
    submitting.value = true;
    try {
      let updated: TaskFinanceDoc | null = null;
      if (act.key === 'submit') {
        updated = await submitFinanceDoc(doc.value.id);
      } else if (act.key === 'approve') {
        updated = await approveFinanceDoc(doc.value.id);
      }
      if (updated) doc.value = updated;
      EleMessage.success({ message: `${act.label}成功`, plain: true });
      emit('done');
    } catch (e: unknown) {
      const msg = (e as { message?: string }).message || `${act.label}失败`;
      EleMessage.error({ message: msg, plain: true });
    } finally {
      submitting.value = false;
    }
  };

  const runCancelAction = async () => {
    if (!doc.value?.id) return;
    try {
      const { value: reason } = await ElMessageBox.prompt(
        '请输入撤销原因（可选）',
        '撤销费用单',
        { confirmButtonText: '确定', cancelButtonText: '不撤销' }
      );
      submitting.value = true;
      const updated = await cancelFinanceDoc(doc.value.id, reason || undefined);
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

  const onActionDone = async () => {
    if (props.docId) await loadDetail(props.docId);
    emit('done');
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
    flex-wrap: wrap;
  }
</style>
