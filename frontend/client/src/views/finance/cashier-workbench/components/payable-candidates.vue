<!-- 待打款候选：已审批未入批的应付单，勾选后合成一个打款批次 -->
<template>
  <div>
    <div class="panel-toolbar">
      <el-select
        v-model="docKinds"
        placeholder="单据类型"
        multiple
        collapse-tags
        clearable
        style="width: 240px"
        @change="load"
      >
        <el-option
          v-for="o in PAYABLE_DOC_KIND_OPTIONS"
          :key="o.value"
          :value="o.value"
          :label="o.label"
        />
      </el-select>
      <el-input
        v-model="keyword"
        placeholder="单号/收款方"
        clearable
        style="width: 200px"
        @change="load"
      />
      <el-date-picker
        v-model="dueBefore"
        type="date"
        value-format="YYYY-MM-DD"
        placeholder="账期早于"
        style="width: 150px"
        @change="load"
      />
      <el-button @click="load">刷新</el-button>
      <div class="toolbar-right">
        <span class="toolbar-tip">
          已选 {{ selected.length }} 单，合计 ¥
          {{ formatMoney(selectedAmount) }}
        </span>
        <el-button
          type="primary"
          :disabled="!selected.length"
          v-permission="'finance:cashier-wb:batch-pay'"
          @click="openCreate"
        >
          合成打款批次
        </el-button>
      </div>
    </div>

    <el-table
      ref="tableRef"
      :data="rows"
      v-loading="loading"
      size="small"
      max-height="480"
      :row-key="rowKey"
      @selection-change="onSelectionChange"
    >
      <el-table-column type="selection" width="42" reserve-selection />
      <el-table-column label="单据" min-width="200">
        <template #default="{ row }">
          <div>{{ row.docNo || `#${row.docId}` }}</div>
          <div class="muted">{{ row.docKindLabel }}</div>
        </template>
      </el-table-column>
      <el-table-column label="收款方" min-width="180">
        <template #default="{ row }">
          <div>{{ row.payeeName || '未填收款方' }}</div>
          <div v-if="row.payeeBankAccount" class="muted">
            {{ row.payeeBankName }} {{ row.payeeBankAccount }}
          </div>
          <div v-else class="warn-text">没有收款账号，打款前先补档案</div>
        </template>
      </el-table-column>
      <el-table-column label="应付金额" width="140" align="right">
        <template #default="{ row }">
          <span class="num strong">¥ {{ formatMoney(row.amount) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="账期" width="120" align="center">
        <template #default="{ row }">
          <span :class="{ overdue: isOverdue(row.dueDate) }">
            {{ row.dueDate || '--' }}
          </span>
        </template>
      </el-table-column>
      <el-table-column label="审批时间" width="165" align="center">
        <template #default="{ row }">
          {{ formatDateTime(row.reviewedAt) || '--' }}
        </template>
      </el-table-column>
      <el-table-column prop="remark" label="备注" min-width="140" />
      <template #empty>
        <div class="empty-tip">
          没有待打款的单据。承运商结算单、司机工资单审批通过后会自动出现在这里。
        </div>
      </template>
    </el-table>

    <!-- 合成批次 -->
    <el-dialog v-model="createVisible" title="合成打款批次" width="520px">
      <el-form :model="form" label-width="94px">
        <el-form-item label="付款账户" required>
          <el-select
            v-model="form.bankAccountId"
            placeholder="选一个付款账户"
            filterable
            style="width: 100%"
          >
            <el-option
              v-for="a in accounts"
              :key="a.id"
              :value="a.id"
              :label="`${a.displayLabel || a.accountName}（余额 ${formatMoney(a.balance)}）`"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="付款方式">
          <el-select v-model="form.payMethod" style="width: 100%">
            <el-option
              v-for="o in PAY_METHOD_OPTIONS"
              :key="o.value"
              :value="o.value"
              :label="o.label"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="计划付款日">
          <el-date-picker
            v-model="form.planPayDate"
            type="date"
            value-format="YYYY-MM-DD"
            placeholder="留空表示今天付"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" maxlength="500" />
        </el-form-item>
      </el-form>
      <div class="dialog-sum">
        共 {{ selected.length }} 单，合计 ¥ {{ formatMoney(selectedAmount) }}
      </div>
      <template #footer>
        <el-button @click="createVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="doCreate">
          生成批次
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script lang="ts" setup>
  import { computed, onMounted, reactive, ref } from 'vue';
  import { EleMessage } from 'ele-admin-plus';
  import {
    createPaymentBatch,
    listPayableCandidates
  } from '@/api/finance/payment-batch';
  import type { PayableCandidate } from '@/api/finance/payment-batch/model';
  import { listBankAccountOptions } from '@/api/finance/bank-account';
  import type { BankAccountOption } from '@/api/finance/bank-account/model';
  import { formatDateTime } from '@/utils/date-util';
  import {
    formatMoney,
    PAY_METHOD_OPTIONS,
    PAYABLE_DOC_KIND_OPTIONS
  } from '../../status-config';

  const emit = defineEmits<{ (e: 'done'): void }>();

  const tableRef = ref();
  const loading = ref(false);
  const saving = ref(false);
  const rows = ref<PayableCandidate[]>([]);
  const selected = ref<PayableCandidate[]>([]);
  const docKinds = ref<string[]>([]);
  const keyword = ref('');
  const dueBefore = ref<string | null>(null);
  const accounts = ref<BankAccountOption[]>([]);
  const createVisible = ref(false);

  const form = reactive<{
    bankAccountId?: number;
    payMethod: number;
    planPayDate?: string;
    remark?: string;
  }>({ payMethod: 1 });

  const rowKey = (row: PayableCandidate) => `${row.docKind}:${row.docId}`;

  const selectedAmount = computed(() =>
    selected.value.reduce((sum, r) => sum + Number(r.amount || 0), 0)
  );

  const isOverdue = (due?: string) =>
    !!due && due < new Date().toISOString().slice(0, 10);

  const onSelectionChange = (list: PayableCandidate[]) => {
    selected.value = list;
  };

  const load = async () => {
    loading.value = true;
    try {
      const res = await listPayableCandidates({
        docKinds: docKinds.value.length ? docKinds.value.join(',') : void 0,
        keyword: keyword.value || void 0,
        dueBefore: dueBefore.value || void 0
      });
      rows.value = res?.list ?? [];
    } catch (e: unknown) {
      EleMessage.error({
        message: (e as { message?: string }).message || '加载失败，请重试',
        plain: true
      });
    } finally {
      loading.value = false;
    }
  };

  const openCreate = () => {
    const noAccount = selected.value.filter((r) => !r.payeeBankAccount);
    if (noAccount.length) {
      EleMessage.warning({
        message: `有 ${noAccount.length} 单没有收款账号，可以先建批次，打款前请补齐档案`,
        plain: true
      });
    }
    const def = accounts.value.find((a) => a.isDefaultPay === 1);
    form.bankAccountId = def?.id ?? accounts.value[0]?.id;
    createVisible.value = true;
  };

  const doCreate = async () => {
    if (!form.bankAccountId) {
      EleMessage.warning({ message: '请选择付款账户', plain: true });
      return;
    }
    saving.value = true;
    try {
      await createPaymentBatch({
        docs: selected.value.map((r) => ({
          docKind: r.docKind,
          docId: r.docId
        })),
        bankAccountId: form.bankAccountId,
        payMethod: form.payMethod,
        planPayDate: form.planPayDate,
        remark: form.remark
      });
      EleMessage.success({
        message: `已生成批次，含 ${selected.value.length} 单`,
        plain: true
      });
      createVisible.value = false;
      selected.value = [];
      tableRef.value?.clearSelection?.();
      await load();
      emit('done');
    } catch (e: unknown) {
      EleMessage.error({
        message: (e as { message?: string }).message || '生成失败，请稍后重试',
        plain: true
      });
    } finally {
      saving.value = false;
    }
  };

  onMounted(async () => {
    load();
    try {
      accounts.value = await listBankAccountOptions({ forPay: true });
    } catch {
      // 账户下拉失败时仍可浏览候选
    }
  });
</script>

<style lang="scss" scoped>
  .panel-toolbar {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 10px;
    margin-bottom: 10px;
  }

  .toolbar-right {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-left: auto;
  }

  .toolbar-tip {
    color: var(--el-text-color-secondary);
    font-size: 13px;
  }

  .num {
    font-variant-numeric: tabular-nums;
  }

  .strong {
    font-weight: 600;
  }

  .muted {
    color: var(--el-text-color-secondary);
    font-size: 12px;
  }

  .warn-text {
    color: var(--el-color-warning);
    font-size: 12px;
  }

  .overdue {
    color: var(--el-color-danger);
    font-weight: 600;
  }

  .empty-tip {
    padding: 28px 0;
    color: var(--el-text-color-secondary);
    text-align: center;
  }

  .dialog-sum {
    padding-top: 4px;
    color: var(--el-text-color-secondary);
    font-size: 13px;
  }
</style>
