<!--
  待认领到账

  银行到账先登记成一笔收款，再认领到具体结算单。系统只按金额接近度推荐，
  实际认领必须由出纳确认，避免自动核销把钱挂到错的结算单上。
-->
<template>
  <div>
    <div class="panel-toolbar">
      <el-input
        v-model="keyword"
        placeholder="收款单号/付款方/流水号"
        clearable
        style="width: 220px"
        @change="load"
      />
      <el-checkbox v-model="onlyUnsettled" @change="load">
        只看还没认领完的
      </el-checkbox>
      <el-button @click="load">刷新</el-button>
      <div class="toolbar-right">
        <el-button
          type="primary"
          v-permission="'finance:cashier-wb:claim-receipt'"
          @click="openCreate"
        >
          登记到账
        </el-button>
      </div>
    </div>

    <el-table :data="rows" v-loading="loading" size="small" max-height="460">
      <el-table-column label="收款单" min-width="170">
        <template #default="{ row }">
          <div>{{ row.docNo }}</div>
          <div class="muted">{{ formatDateTime(row.receivedAt) }}</div>
        </template>
      </el-table-column>
      <el-table-column label="付款方" min-width="160">
        <template #default="{ row }">
          <div>{{ row.customerName || row.payerName || '待确认' }}</div>
          <div v-if="row.bankSerialNo" class="muted">
            流水号 {{ row.bankSerialNo }}
          </div>
        </template>
      </el-table-column>
      <el-table-column label="到账金额" width="130" align="right">
        <template #default="{ row }">
          <span class="num strong">¥ {{ formatMoney(row.plannedAmount) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="已认领" width="130" align="right">
        <template #default="{ row }">
          <span class="num paid">¥ {{ formatMoney(row.settledAmount) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="待认领" width="130" align="right">
        <template #default="{ row }">
          <span class="num pending">
            ¥ {{ formatMoney(row.unsettledAmount) }}
          </span>
        </template>
      </el-table-column>
      <el-table-column label="收款账户" min-width="150">
        <template #default="{ row }">{{
          row.bankAccountLabel || '--'
        }}</template>
      </el-table-column>
      <el-table-column label="操作" width="100" align="center">
        <template #default="{ row }">
          <el-link
            v-if="row.unsettledAmount > 0"
            type="primary"
            :underline="false"
            v-permission="'finance:cashier-wb:claim-receipt'"
            @click="openClaim(row)"
          >
            认领
          </el-link>
          <span v-else class="muted">已认领完</span>
        </template>
      </el-table-column>
      <template #empty>
        <div class="empty-tip">
          没有待认领的到账。银行到账后先点「登记到账」，再认领到结算单。
        </div>
      </template>
    </el-table>

    <div class="panel-pager">
      <el-pagination
        v-model:current-page="page"
        v-model:page-size="limit"
        :total="total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
        @change="load"
      />
    </div>

    <!-- 登记到账 -->
    <el-dialog v-model="createVisible" title="登记到账" width="520px">
      <el-form :model="createForm" label-width="94px">
        <el-form-item label="到账金额" required>
          <el-input-number
            v-model="createForm.amount"
            :min="0.01"
            :precision="2"
            :controls="false"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="到账时间" required>
          <el-date-picker
            v-model="createForm.receivedAt"
            type="datetime"
            value-format="YYYY-MM-DD HH:mm:ss"
            placeholder="按银行回单时间填"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="收款账户">
          <el-select
            v-model="createForm.bankAccountId"
            placeholder="选收到这笔钱的账户"
            filterable
            clearable
            style="width: 100%"
          >
            <el-option
              v-for="a in accounts"
              :key="a.id"
              :value="a.id"
              :label="a.displayLabel || a.accountName"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="收款方式">
          <el-select
            v-model="createForm.receiveMethod"
            clearable
            style="width: 100%"
          >
            <el-option
              v-for="o in RECEIVE_METHOD_OPTIONS"
              :key="o.value"
              :value="o.value"
              :label="o.label"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="客户">
          <el-select
            v-model="createForm.customerId"
            placeholder="认得出就选，认不出可留空"
            filterable
            clearable
            style="width: 100%"
          >
            <el-option
              v-for="c in customers"
              :key="c.id"
              :value="c.id"
              :label="c.customerName"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="付款方名称">
          <el-input
            v-model="createForm.payerName"
            placeholder="银行回单上的付款方"
            maxlength="100"
          />
        </el-form-item>
        <el-form-item label="银行流水号">
          <el-input v-model="createForm.bankSerialNo" maxlength="64" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="createForm.remark" maxlength="500" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="doCreate">
          登记
        </el-button>
      </template>
    </el-dialog>

    <!-- 认领核销 -->
    <el-dialog
      v-model="claimVisible"
      :title="`认领到账 ${current?.docNo || ''}`"
      width="820px"
    >
      <div class="claim-head">
        <span>
          待认领 ¥ {{ formatMoney(current?.unsettledAmount) }}，本次分配
          <span class="num strong">¥ {{ formatMoney(allocatedAmount) }}</span>
        </span>
        <el-button size="small" type="primary" plain @click="autoFill">
          一键按账期填满
        </el-button>
      </div>
      <el-table
        :data="candidates"
        v-loading="claimLoading"
        size="small"
        height="340"
      >
        <el-table-column prop="docNo" label="结算单号" min-width="170" />
        <el-table-column prop="customerName" label="客户" min-width="130" />
        <el-table-column label="应收余额" width="120" align="right">
          <template #default="{ row }">
            ¥ {{ formatMoney(row.unreceivedAmount) }}
          </template>
        </el-table-column>
        <el-table-column label="账期" width="110" align="center">
          <template #default="{ row }">{{ row.dueDate || '--' }}</template>
        </el-table-column>
        <el-table-column label="本次核销" width="180" align="center">
          <template #default="{ row }">
            <el-input-number
              v-model="amounts[row.settleId]"
              :min="0"
              :max="row.unreceivedAmount + (row.appliedByThisReceipt || 0)"
              :precision="2"
              :controls="false"
              size="small"
              style="width: 150px"
            />
          </template>
        </el-table-column>
        <template #empty>
          <div class="empty-tip">
            这个客户没有待收款的结算单，先确认客户或去结算单页面审批
          </div>
        </template>
      </el-table>
      <template #footer>
        <el-button @click="claimVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="doClaim">
          确认认领
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script lang="ts" setup>
  import { computed, onMounted, reactive, ref } from 'vue';
  import { EleMessage } from 'ele-admin-plus';
  import {
    claimReceipt,
    createReceipt,
    listClaimCandidates,
    pageReceipts,
    suggestAllocation
  } from '@/api/finance/receipt';
  import type {
    ReceiptClaimCandidate,
    ReceiptListItem,
    ReceiptPayload
  } from '@/api/finance/receipt/model';
  import { listBankAccountOptions } from '@/api/finance/bank-account';
  import type { BankAccountOption } from '@/api/finance/bank-account/model';
  import { selectCustomers } from '@/api/partner/customer';
  import type { CustomerSelectItem } from '@/api/partner/customer/model';
  import { formatDateTime } from '@/utils/date-util';
  import { formatMoney, RECEIVE_METHOD_OPTIONS } from '../../status-config';

  const emit = defineEmits<{ (e: 'done'): void }>();

  const loading = ref(false);
  const saving = ref(false);
  const rows = ref<ReceiptListItem[]>([]);
  const total = ref(0);
  const page = ref(1);
  const limit = ref(20);
  const keyword = ref('');
  const onlyUnsettled = ref(true);

  const accounts = ref<BankAccountOption[]>([]);
  const customers = ref<CustomerSelectItem[]>([]);

  const createVisible = ref(false);
  const createForm = reactive<ReceiptPayload>({});

  const claimVisible = ref(false);
  const claimLoading = ref(false);
  const current = ref<ReceiptListItem | null>(null);
  const candidates = ref<ReceiptClaimCandidate[]>([]);
  const amounts = ref<Record<number, number>>({});

  const allocatedAmount = computed(() =>
    Object.values(amounts.value).reduce((s, v) => s + Number(v || 0), 0)
  );

  const load = async () => {
    loading.value = true;
    try {
      const res = await pageReceipts({
        page: page.value,
        limit: limit.value,
        keyword: keyword.value || void 0,
        onlyUnsettled: onlyUnsettled.value
      });
      rows.value = res?.list ?? [];
      total.value = res?.count ?? 0;
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
    createForm.amount = void 0;
    createForm.receivedAt = void 0;
    createForm.receiveMethod = 1;
    createForm.customerId = void 0;
    createForm.payerName = void 0;
    createForm.bankSerialNo = void 0;
    createForm.remark = void 0;
    createForm.bankAccountId =
      accounts.value.find((a) => a.isDefaultReceive === 1)?.id ??
      accounts.value[0]?.id;
    createVisible.value = true;
  };

  const doCreate = async () => {
    if (!createForm.amount || createForm.amount <= 0) {
      EleMessage.warning({ message: '请填到账金额', plain: true });
      return;
    }
    if (!createForm.receivedAt) {
      EleMessage.warning({ message: '请填到账时间', plain: true });
      return;
    }
    saving.value = true;
    try {
      const account = accounts.value.find(
        (a) => a.id === createForm.bankAccountId
      );
      await createReceipt({
        ...createForm,
        bankAccountLabel: account?.displayLabel || account?.accountName
      });
      EleMessage.success({ message: '已登记到账，接着认领即可', plain: true });
      createVisible.value = false;
      await load();
      emit('done');
    } catch (e: unknown) {
      EleMessage.error({
        message: (e as { message?: string }).message || '登记失败，请稍后重试',
        plain: true
      });
    } finally {
      saving.value = false;
    }
  };

  const openClaim = async (row: ReceiptListItem) => {
    current.value = row;
    amounts.value = {};
    candidates.value = [];
    claimVisible.value = true;
    claimLoading.value = true;
    try {
      const res = await listClaimCandidates(row.id, { limit: 100 });
      candidates.value = res?.list ?? [];
      candidates.value.forEach((c) => {
        if (c.appliedByThisReceipt) {
          amounts.value[c.settleId] = c.appliedByThisReceipt;
        }
      });
    } catch (e: unknown) {
      EleMessage.error({
        message: (e as { message?: string }).message || '候选加载失败，请重试',
        plain: true
      });
    } finally {
      claimLoading.value = false;
    }
  };

  const autoFill = async () => {
    if (!current.value) return;
    try {
      const res = await suggestAllocation(current.value.id);
      const next: Record<number, number> = {};
      (res?.list ?? []).forEach((x) => {
        next[x.settleId] = Number(x.amount || 0);
      });
      amounts.value = next;
      if (!Object.keys(next).length) {
        EleMessage.info({ message: '没有可自动分配的结算单', plain: true });
      }
    } catch (e: unknown) {
      EleMessage.error({
        message: (e as { message?: string }).message || '推荐失败，请手工填',
        plain: true
      });
    }
  };

  const doClaim = async () => {
    if (!current.value) return;
    const allocations = Object.entries(amounts.value)
      .filter(([, v]) => Number(v) > 0)
      .map(([settleId, v]) => ({
        settleId: Number(settleId),
        amount: Number(v)
      }));
    if (!allocations.length) {
      EleMessage.warning({ message: '请填要核销的金额', plain: true });
      return;
    }
    saving.value = true;
    try {
      await claimReceipt(current.value.id, allocations);
      EleMessage.success({ message: '已完成认领核销', plain: true });
      claimVisible.value = false;
      await load();
      emit('done');
    } catch (e: unknown) {
      EleMessage.error({
        message: (e as { message?: string }).message || '认领失败，请稍后重试',
        plain: true
      });
    } finally {
      saving.value = false;
    }
  };

  onMounted(async () => {
    load();
    try {
      const [accs, custs] = await Promise.all([
        listBankAccountOptions({ forPay: false }),
        selectCustomers()
      ]);
      accounts.value = accs;
      customers.value = custs || [];
    } catch {
      // 下拉数据失败不影响浏览与认领
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
    margin-left: auto;
  }

  .panel-pager {
    display: flex;
    justify-content: flex-end;
    margin-top: 10px;
  }

  .claim-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 10px;
    color: var(--el-text-color-secondary);
    font-size: 13px;
  }

  .num {
    font-variant-numeric: tabular-nums;
  }

  .strong {
    font-weight: 600;
    color: var(--el-text-color-primary);
  }

  .paid {
    color: var(--el-color-success);
  }

  .pending {
    color: var(--el-color-warning);
  }

  .muted {
    color: var(--el-text-color-secondary);
    font-size: 12px;
  }

  .empty-tip {
    padding: 28px 0;
    color: var(--el-text-color-secondary);
    text-align: center;
  }
</style>
