<template>
  <el-dialog
    :model-value="visible"
    title="新建客户结算单"
    width="880px"
    top="6vh"
    destroy-on-close
    :close-on-click-modal="false"
    @update:model-value="(v: boolean) => emit('update:visible', v)"
    @open="onOpen"
  >
    <customer-credit-tip :customer-id="form.customerId" :show-link="false" />

    <el-form :model="form" label-width="88px">
      <el-row :gutter="12">
        <el-col :span="8">
          <el-form-item label="客户" required>
            <el-select
              v-model="form.customerId"
              placeholder="请选择客户"
              filterable
              style="width: 100%"
              @change="load"
            >
              <el-option
                v-for="c in customers"
                :key="c.id"
                :value="c.id"
                :label="c.customerName"
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
              placeholder="留空按客户账期推导"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="是否开票">
            <el-switch
              v-model="form.invoiceRequired"
              :active-value="1"
              :inactive-value="0"
              active-text="需要开票"
            />
          </el-form-item>
        </el-col>
      </el-row>
      <el-form-item label="备注">
        <el-input v-model="form.remark" maxlength="200" placeholder="选填" />
      </el-form-item>
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
      <el-table-column label="对账周期" width="190" align="center">
        <template #default="{ row }">
          {{ formatDate(row.periodStart) }} ~ {{ formatDate(row.periodEnd) }}
        </template>
      </el-table-column>
      <el-table-column
        prop="waybillCount"
        label="运单"
        width="72"
        align="center"
      />
      <el-table-column label="对账金额" width="120" align="right">
        <template #default="{ row }">
          ¥ {{ formatMoney(row.plannedAmount) }}
        </template>
      </el-table-column>
      <el-table-column label="可认领" width="120" align="right">
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
            form.customerId
              ? '这个客户没有可结算的对账单，先去客户对账单确认一张'
              : '先选客户，这里会列出已确认且未结清的对账单'
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
  import CustomerCreditTip from '../../components/customer-credit-tip.vue';
  import {
    addSettlement,
    listSettleReconCandidates
  } from '@/api/finance/customer-settlement';
  import type { SettleReconCandidate } from '@/api/finance/customer-settlement/model';
  import type { CustomerSelectItem } from '@/api/partner/customer/model';
  import { formatDate } from '@/utils/date-util';
  import { formatMoney } from '../../status-config';

  defineProps<{ visible: boolean; customers: CustomerSelectItem[] }>();

  const emit = defineEmits<{
    (e: 'update:visible', v: boolean): void;
    (e: 'done', settleId?: number): void;
  }>();

  const loading = ref(false);
  const saving = ref(false);
  const candidates = ref<SettleReconCandidate[]>([]);
  const selected = ref<SettleReconCandidate[]>([]);
  const appliedMap = reactive<Record<number, number | undefined>>({});

  const form = ref<{
    customerId?: number;
    dueDate?: string;
    invoiceRequired: number;
    remark?: string;
  }>({ invoiceRequired: 0 });

  const totalApplied = computed(() =>
    selected.value.reduce(
      (sum, r) => sum + Number(appliedMap[r.reconId] ?? r.availableAmount),
      0
    )
  );

  const isSelected = (reconId: number) =>
    selected.value.some((r) => r.reconId === reconId);

  const onOpen = () => {
    form.value = { invoiceRequired: 0 };
    candidates.value = [];
    selected.value = [];
    Object.keys(appliedMap).forEach((k) => delete appliedMap[Number(k)]);
  };

  const onSelectionChange = (rows: SettleReconCandidate[]) => {
    selected.value = rows;
    // 勾选即默认认领全部未结金额，出纳最常见的就是整张结清
    rows.forEach((r) => {
      if (appliedMap[r.reconId] === void 0) {
        appliedMap[r.reconId] = r.availableAmount;
      }
    });
  };

  const load = async () => {
    if (!form.value.customerId) {
      candidates.value = [];
      return;
    }
    loading.value = true;
    try {
      const res = await listSettleReconCandidates({
        customerId: form.value.customerId
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

  const save = async () => {
    if (!form.value.customerId) {
      EleMessage.warning({ message: '请选择客户', plain: true });
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
      const detail = await addSettlement({
        customerId: form.value.customerId,
        dueDate: form.value.dueDate,
        invoiceRequired: form.value.invoiceRequired,
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
</style>
