<template>
  <el-dialog
    :model-value="visible"
    title="核销到结算单"
    width="820px"
    top="8vh"
    destroy-on-close
    :close-on-click-modal="false"
    @update:model-value="(v: boolean) => emit('update:visible', v)"
    @open="onOpen"
  >
    <div class="pick-head">
      <span>
        本票待核销 ¥ {{ formatMoney(unsettledAmount) }}，已分配 ¥
        {{ formatMoney(allocatedTotal) }}
      </span>
      <el-input
        v-model="keyword"
        placeholder="结算单号"
        clearable
        size="small"
        style="width: 180px; margin-left: auto"
        @change="load"
      />
    </div>

    <el-table :data="rows" v-loading="loading" height="340" size="small">
      <el-table-column prop="docNo" label="结算单号" min-width="165" />
      <el-table-column label="结算金额" width="130" align="right">
        <template #default="{ row }">
          <span class="num">¥ {{ formatMoney(row.plannedAmount) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="已收票" width="130" align="right">
        <template #default="{ row }">
          <span class="num">¥ {{ formatMoney(row.invoiceAmountTotal) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="票款缺口" width="130" align="right">
        <template #default="{ row }">
          <span class="num gap">¥ {{ formatMoney(row.gapAmount) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="本次核销" width="150" align="right">
        <template #default="{ row }">
          <el-input-number
            v-model="allocations[row.settleId]"
            :min="0"
            :max="row.gapAmount"
            :precision="2"
            :controls="false"
            size="small"
            style="width: 120px"
          />
        </template>
      </el-table-column>
      <el-table-column label="付款时间" width="120" align="center">
        <template #default="{ row }">
          {{ formatDate(row.paidAt) || '未付款' }}
        </template>
      </el-table-column>
      <template #empty>
        <div class="pick-empty">
          这个供应商暂时没有还缺票的结算单。先在「承运商结算单」建单，再回来核销。
        </div>
      </template>
    </el-table>

    <template #footer>
      <el-button @click="emit('update:visible', false)">取消</el-button>
      <el-button type="primary" :loading="saving" @click="save">
        确认核销
      </el-button>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
  import { computed, ref } from 'vue';
  import { EleMessage } from 'ele-admin-plus';
  import {
    listInvoiceCandidates,
    matchVendorInvoice
  } from '@/api/finance/vendor-invoice';
  import type { InvoiceMatchCandidate } from '@/api/finance/vendor-invoice/model';
  import { formatDate } from '@/utils/date-util';
  import { formatMoney } from '../../status-config';

  const props = defineProps<{
    visible: boolean;
    invoiceId?: number | null;
    unsettledAmount?: number;
  }>();

  const emit = defineEmits<{
    (e: 'update:visible', v: boolean): void;
    (e: 'done'): void;
  }>();

  const loading = ref(false);
  const saving = ref(false);
  const keyword = ref('');
  const rows = ref<InvoiceMatchCandidate[]>([]);
  const allocations = ref<Record<number, number>>({});

  const allocatedTotal = computed(() =>
    Object.values(allocations.value).reduce((sum, v) => sum + Number(v || 0), 0)
  );

  const load = async () => {
    if (!props.invoiceId) return;
    loading.value = true;
    try {
      const res = await listInvoiceCandidates(props.invoiceId, {
        keyword: keyword.value || void 0
      });
      rows.value = res?.list ?? [];
    } catch (e: unknown) {
      const msg =
        (e as { message?: string }).message || '结算单加载失败，请重试';
      EleMessage.error({ message: msg, plain: true });
    } finally {
      loading.value = false;
    }
  };

  const onOpen = async () => {
    keyword.value = '';
    allocations.value = {};
    await load();
    // 常见情形是一票对一单：默认把待核销额度铺到第一张缺票的单上
    const first = rows.value[0];
    if (first) {
      allocations.value[first.settleId] = Math.min(
        Number(props.unsettledAmount || 0),
        Number(first.gapAmount || 0)
      );
    }
  };

  const save = async () => {
    if (!props.invoiceId) return;
    const list = Object.entries(allocations.value)
      .filter(([, v]) => Number(v || 0) > 0)
      .map(([settleId, appliedAmount]) => ({
        settleId: Number(settleId),
        appliedAmount: Number(appliedAmount)
      }));
    if (!list.length) {
      EleMessage.warning({ message: '请填写要核销的金额', plain: true });
      return;
    }
    if (allocatedTotal.value > Number(props.unsettledAmount || 0) + 0.001) {
      EleMessage.warning({
        message: '核销金额超过本票待核销余额，请调小',
        plain: true
      });
      return;
    }
    saving.value = true;
    try {
      await matchVendorInvoice(props.invoiceId, { allocations: list });
      EleMessage.success({
        message: `已核销到 ${list.length} 张结算单`,
        plain: true
      });
      emit('update:visible', false);
      emit('done');
    } catch (e: unknown) {
      const msg = (e as { message?: string }).message || '核销失败，请稍后重试';
      EleMessage.error({ message: msg, plain: true });
    } finally {
      saving.value = false;
    }
  };
</script>

<style lang="scss" scoped>
  .pick-head {
    display: flex;
    align-items: center;
    margin-bottom: 8px;
    color: var(--el-text-color-secondary);
    font-size: 13px;
  }

  .num {
    font-variant-numeric: tabular-nums;
  }

  .gap {
    color: var(--el-color-warning);
  }

  .pick-empty {
    padding: 24px 0;
    color: var(--el-text-color-secondary);
  }
</style>
