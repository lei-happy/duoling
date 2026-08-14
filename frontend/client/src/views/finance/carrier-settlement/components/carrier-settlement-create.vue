<template>
  <el-dialog
    :model-value="visible"
    title="新建承运商结算单"
    width="920px"
    top="6vh"
    destroy-on-close
    :close-on-click-modal="false"
    @update:model-value="(v: boolean) => emit('update:visible', v)"
    @open="onOpen"
  >
    <el-form :model="form" label-width="88px">
      <el-row :gutter="12">
        <el-col :span="8">
          <el-form-item label="承运商" required>
            <el-select
              v-model="form.carrierId"
              placeholder="请选择承运商"
              filterable
              style="width: 100%"
              @change="onCarrierChange"
            >
              <el-option
                v-for="c in carriers"
                :key="c.id"
                :value="c.id"
                :label="c.carrierName"
              />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="付款账户">
            <el-select
              v-model="form.settlementAccountId"
              placeholder="留空取默认账户"
              clearable
              style="width: 100%"
            >
              <el-option
                v-for="a in accounts"
                :key="a.accountId"
                :value="a.accountId"
                :label="accountLabel(a)"
              />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="到期日">
            <el-date-picker
              v-model="form.dueDate"
              type="date"
              value-format="YYYY-MM-DD"
              placeholder="约定的付款日"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
      </el-row>
      <el-row :gutter="12">
        <el-col :span="8">
          <el-form-item label="纯抵账">
            <el-switch
              v-model="form.isOffsetOnly"
              :active-value="1"
              :inactive-value="0"
              active-text="预付已覆盖，不实付"
            />
          </el-form-item>
        </el-col>
        <el-col :span="16">
          <el-form-item label="备注">
            <el-input
              v-model="form.remark"
              maxlength="200"
              placeholder="选填"
            />
          </el-form-item>
        </el-col>
      </el-row>
    </el-form>

    <div class="cand-head">
      <span class="cand-title">可结算的已确认对账单</span>
      <span class="cand-tip">
        已选 {{ selected.length }} 张，认领合计 ¥
        {{ formatMoney(totalApplied) }}
      </span>
    </div>

    <el-table
      :data="candidates"
      v-loading="loading"
      height="300"
      row-key="reconId"
      size="small"
      @selection-change="onSelectionChange"
    >
      <el-table-column type="selection" width="42" />
      <el-table-column prop="docNo" label="对账单号" min-width="160" />
      <el-table-column label="对账周期" width="180" align="center">
        <template #default="{ row }">
          {{ formatDate(row.periodStart) }} ~ {{ formatDate(row.periodEnd) }}
        </template>
      </el-table-column>
      <el-table-column
        prop="taskCount"
        label="任务"
        width="70"
        align="center"
      />
      <el-table-column label="毛额" width="110" align="right">
        <template #default="{ row }">
          ¥ {{ formatMoney(row.grossAmountTotal) }}
        </template>
      </el-table-column>
      <el-table-column label="已预付" width="100" align="right">
        <template #default="{ row }">
          <span v-if="row.prepaidOffsetTotal" class="offset">
            {{ formatMoney(row.prepaidOffsetTotal) }}
          </span>
          <span v-else class="muted">--</span>
        </template>
      </el-table-column>
      <el-table-column label="可认领" width="110" align="right">
        <template #default="{ row }">
          ¥ {{ formatMoney(row.availableAmount) }}
        </template>
      </el-table-column>
      <el-table-column label="本单认领" width="150" align="right">
        <template #default="{ row }">
          <el-input-number
            v-model="appliedMap[row.reconId]"
            :min="0"
            :max="row.availableAmount"
            :precision="2"
            :controls="false"
            size="small"
            :disabled="!isSelected(row.reconId)"
            style="width: 130px"
          />
        </template>
      </el-table-column>
      <template #empty>
        <div class="cand-empty">
          {{
            form.carrierId
              ? '这个承运商没有可结算的对账单，先去承运商对账单确认一张'
              : '先选承运商，这里会列出已确认且未结清的对账单'
          }}
        </div>
      </template>
    </el-table>

    <template #footer>
      <el-button @click="emit('update:visible', false)">取消</el-button>
      <el-button type="primary" :loading="saving" @click="save">
        生成结算单
      </el-button>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
  import { computed, reactive, ref } from 'vue';
  import { EleMessage } from 'ele-admin-plus';
  import {
    addCarrierSettle,
    listCarrierAccounts,
    listSettleReconCandidates
  } from '@/api/finance/carrier-settlement';
  import type {
    CarrierAccount,
    CarrierSettleReconCandidate
  } from '@/api/finance/carrier-settlement/model';
  import type { CarrierSelectItem } from '@/api/partner/carrier/model';
  import { formatDate } from '@/utils/date-util';
  import { formatMoney } from '../../status-config';

  defineProps<{ visible: boolean; carriers: CarrierSelectItem[] }>();

  const emit = defineEmits<{
    (e: 'update:visible', v: boolean): void;
    (e: 'done', settleId?: number): void;
  }>();

  const loading = ref(false);
  const saving = ref(false);
  const candidates = ref<CarrierSettleReconCandidate[]>([]);
  const selected = ref<CarrierSettleReconCandidate[]>([]);
  const accounts = ref<CarrierAccount[]>([]);
  const appliedMap = reactive<Record<number, number | undefined>>({});

  const form = ref<{
    carrierId?: number;
    settlementAccountId?: number;
    dueDate?: string;
    isOffsetOnly: number;
    remark?: string;
  }>({ isOffsetOnly: 0 });

  const totalApplied = computed(() =>
    selected.value.reduce(
      (sum, r) => sum + Number(appliedMap[r.reconId] ?? r.availableAmount),
      0
    )
  );

  const isSelected = (reconId: number) =>
    selected.value.some((r) => r.reconId === reconId);

  const accountLabel = (a: CarrierAccount) =>
    [a.accountLabel, a.bankAccountMasked, a.isDefault ? '默认' : '']
      .filter(Boolean)
      .join(' · ');

  const onOpen = () => {
    form.value = { isOffsetOnly: 0 };
    candidates.value = [];
    selected.value = [];
    accounts.value = [];
    Object.keys(appliedMap).forEach((k) => delete appliedMap[Number(k)]);
  };

  const onSelectionChange = (rows: CarrierSettleReconCandidate[]) => {
    selected.value = rows;
    // 勾选即默认认领全部未结金额，最常见的就是整张结清
    rows.forEach((r) => {
      if (appliedMap[r.reconId] === void 0) {
        appliedMap[r.reconId] = r.availableAmount;
      }
    });
  };

  const onCarrierChange = async () => {
    await Promise.all([load(), loadAccounts()]);
  };

  const load = async () => {
    if (!form.value.carrierId) {
      candidates.value = [];
      return;
    }
    loading.value = true;
    try {
      const res = await listSettleReconCandidates({
        carrierId: form.value.carrierId
      });
      candidates.value = res?.list ?? [];
    } catch (e: unknown) {
      const msg =
        (e as { message?: string }).message || '对账单加载失败，请重试';
      EleMessage.error({ message: msg, plain: true });
    } finally {
      loading.value = false;
    }
  };

  const loadAccounts = async () => {
    if (!form.value.carrierId) {
      accounts.value = [];
      return;
    }
    try {
      accounts.value = await listCarrierAccounts(form.value.carrierId);
      const def = accounts.value.find((a) => a.isDefault === 1);
      if (def) form.value.settlementAccountId = def.accountId;
    } catch {
      // 账户下拉失败不阻断建单，后端会按默认账户兜底
    }
  };

  const save = async () => {
    if (!form.value.carrierId) {
      EleMessage.warning({ message: '请选择承运商', plain: true });
      return;
    }
    if (!selected.value.length) {
      EleMessage.warning({ message: '请勾选要结算的对账单', plain: true });
      return;
    }
    const invalid = selected.value.find(
      (r) => Number(appliedMap[r.reconId] ?? r.availableAmount) <= 0
    );
    if (invalid) {
      EleMessage.warning({
        message: `对账单「${invalid.docNo}」的认领金额要大于 0`,
        plain: true
      });
      return;
    }
    saving.value = true;
    try {
      const detail = await addCarrierSettle({
        carrierId: form.value.carrierId,
        settlementAccountId: form.value.settlementAccountId,
        dueDate: form.value.dueDate,
        isOffsetOnly: form.value.isOffsetOnly,
        remark: form.value.remark,
        recons: selected.value.map((r) => ({
          reconId: r.reconId,
          appliedAmount: Number(appliedMap[r.reconId] ?? r.availableAmount)
        }))
      });
      EleMessage.success({
        message: `已生成结算单，合计 ¥ ${formatMoney(detail?.plannedAmount)}`,
        plain: true
      });
      emit('update:visible', false);
      emit('done', detail?.id);
    } catch (e: unknown) {
      const msg = (e as { message?: string }).message || '生成失败，请稍后重试';
      EleMessage.error({ message: msg, plain: true });
    } finally {
      saving.value = false;
    }
  };
</script>

<style lang="scss" scoped>
  .cand-head {
    display: flex;
    align-items: center;
    margin-bottom: 8px;
  }

  .cand-title {
    font-weight: 600;
  }

  .cand-tip {
    margin-left: auto;
    color: var(--el-text-color-secondary);
    font-size: 13px;
  }

  .cand-empty {
    padding: 24px 0;
    color: var(--el-text-color-secondary);
  }

  .offset {
    color: var(--el-color-info);
    font-variant-numeric: tabular-nums;
  }

  .muted {
    color: var(--el-text-color-secondary);
  }
</style>
