<!-- 新建开票申请：先挑客户与结算单，再补票面信息 -->
<template>
  <el-dialog
    :model-value="visible"
    title="新建开票申请"
    width="900px"
    top="6vh"
    destroy-on-close
    :close-on-click-modal="false"
    @update:model-value="(v: boolean) => emit('update:visible', v)"
    @open="onOpen"
  >
    <el-form :model="form" label-width="88px">
      <el-row :gutter="12">
        <el-col :span="8">
          <el-form-item label="客户" required>
            <el-select
              v-model="form.customerId"
              placeholder="请选择客户"
              filterable
              style="width: 100%"
              @change="loadCandidates"
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
          <el-form-item label="发票类型">
            <el-select v-model="form.invoiceType" style="width: 100%">
              <el-option
                v-for="o in INVOICE_TYPE_OPTIONS"
                :key="o.value"
                :value="o.value"
                :label="o.label"
              />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="税率">
            <el-input-number
              v-model="form.taxRate"
              :min="0"
              :max="100"
              :precision="2"
              :controls="false"
              placeholder="百分数，公路运输一般填 9"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
      </el-row>
      <el-row :gutter="12">
        <el-col :span="8">
          <el-form-item label="开票主体">
            <business-entity-select
              v-model="form.sellerEntityId"
              placeholder="选填，默认取结算单主体"
            />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="购方名称">
            <el-input
              v-model="form.buyerTitle"
              placeholder="留空按客户档案抬头"
              maxlength="100"
            />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="购方税号">
            <el-input
              v-model="form.buyerTaxNo"
              placeholder="留空按客户统一社会信用代码"
              maxlength="30"
            />
          </el-form-item>
        </el-col>
      </el-row>
      <el-form-item label="备注">
        <el-input
          v-model="form.remark"
          placeholder="选填，会打印在发票备注栏"
          maxlength="500"
        />
      </el-form-item>
    </el-form>

    <div class="cand-head">
      <span class="cand-title">可开票的结算单</span>
      <el-input
        v-model="keyword"
        placeholder="结算单号"
        clearable
        size="small"
        style="width: 180px"
        @change="loadCandidates"
      />
      <span class="cand-tip">
        已选 {{ selected.length }} 张，开票金额合计 ¥
        {{ formatMoney(selectedAmount) }}
      </span>
    </div>

    <el-table
      ref="tableRef"
      :data="candidates"
      v-loading="loading"
      height="300"
      row-key="settleId"
      size="small"
      @selection-change="onSelectionChange"
    >
      <el-table-column type="selection" width="42" reserve-selection />
      <el-table-column prop="docNo" label="结算单号" min-width="170" />
      <el-table-column label="结算金额" width="120" align="right">
        <template #default="{ row }">
          ¥ {{ formatMoney(row.plannedAmount) }}
        </template>
      </el-table-column>
      <el-table-column label="已开票" width="120" align="right">
        <template #default="{ row }">
          ¥ {{ formatMoney(row.invoicedAmount) }}
        </template>
      </el-table-column>
      <el-table-column label="本次可开" width="120" align="right">
        <template #default="{ row }">
          <span class="avail">¥ {{ formatMoney(row.availableAmount) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="账期" width="110" align="center">
        <template #default="{ row }">{{ row.dueDate || '--' }}</template>
      </el-table-column>
      <el-table-column label="要求开票" width="100" align="center">
        <template #default="{ row }">
          {{ row.invoiceRequired === 1 ? '是' : '否' }}
        </template>
      </el-table-column>
      <template #empty>
        <div class="cand-empty">
          {{
            form.customerId
              ? '这个客户没有可开票的结算单，可能票已开齐或结算单还没审批'
              : '先选客户，这里会列出可开票的结算单'
          }}
        </div>
      </template>
    </el-table>

    <template #footer>
      <el-button @click="emit('update:visible', false)">取消</el-button>
      <el-button type="primary" :loading="saving" @click="save">
        生成开票申请
      </el-button>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
  import { computed, ref, watch } from 'vue';
  import { EleMessage } from 'ele-admin-plus';
  import BusinessEntitySelect from '@/components/BusinessEntitySelect/index.vue';
  import {
    createCustomerInvoice,
    listInvoiceSettleCandidates
  } from '@/api/finance/customer-invoice';
  import type { InvoiceSettleCandidate } from '@/api/finance/customer-invoice/model';
  import type { CustomerSelectItem } from '@/api/partner/customer/model';
  import { formatMoney, INVOICE_TYPE_OPTIONS } from '../../status-config';

  const props = defineProps<{
    visible: boolean;
    customerId?: number;
    customers: CustomerSelectItem[];
  }>();

  const emit = defineEmits<{
    (e: 'update:visible', v: boolean): void;
    (e: 'done', invoiceId?: number): void;
  }>();

  const tableRef = ref();
  const loading = ref(false);
  const saving = ref(false);
  const keyword = ref('');
  const candidates = ref<InvoiceSettleCandidate[]>([]);
  const selected = ref<InvoiceSettleCandidate[]>([]);

  const form = ref<{
    customerId?: number;
    invoiceType: number;
    taxRate?: number;
    sellerEntityId?: number;
    buyerTitle?: string;
    buyerTaxNo?: string;
    remark?: string;
  }>({ invoiceType: 2, taxRate: 9 });

  const selectedAmount = computed(() =>
    selected.value.reduce((sum, r) => sum + Number(r.availableAmount || 0), 0)
  );

  const onOpen = () => {
    form.value = {
      customerId: props.customerId,
      invoiceType: 2,
      taxRate: 9
    };
    keyword.value = '';
    candidates.value = [];
    selected.value = [];
    tableRef.value?.clearSelection?.();
    if (props.customerId) loadCandidates();
  };

  watch(
    () => props.customerId,
    (v) => {
      if (props.visible && v) {
        form.value.customerId = v;
        loadCandidates();
      }
    }
  );

  const onSelectionChange = (rows: InvoiceSettleCandidate[]) => {
    selected.value = rows;
  };

  const loadCandidates = async () => {
    if (!form.value.customerId) {
      candidates.value = [];
      return;
    }
    loading.value = true;
    try {
      const res = await listInvoiceSettleCandidates({
        customerId: form.value.customerId,
        keyword: keyword.value || void 0
      });
      candidates.value = res?.list ?? [];
    } catch (e: unknown) {
      EleMessage.error({
        message:
          (e as { message?: string }).message || '结算单加载失败，请重试',
        plain: true
      });
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
      EleMessage.warning({ message: '请勾选要开票的结算单', plain: true });
      return;
    }
    saving.value = true;
    try {
      const detail = await createCustomerInvoice({
        customerId: form.value.customerId,
        allocations: selected.value.map((r) => ({ settleId: r.settleId })),
        invoiceType: form.value.invoiceType,
        taxRate: form.value.taxRate,
        sellerEntityId: form.value.sellerEntityId,
        buyerTitle: form.value.buyerTitle,
        buyerTaxNo: form.value.buyerTaxNo,
        remark: form.value.remark
      });
      EleMessage.success({
        message: `已生成开票申请，含 ${selected.value.length} 张结算单`,
        plain: true
      });
      emit('update:visible', false);
      emit('done', detail?.id);
    } catch (e: unknown) {
      EleMessage.error({
        message: (e as { message?: string }).message || '生成失败，请稍后重试',
        plain: true
      });
    } finally {
      saving.value = false;
    }
  };
</script>

<style lang="scss" scoped>
  .cand-head {
    display: flex;
    align-items: center;
    gap: 12px;
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

  .avail {
    font-weight: 600;
    color: var(--el-color-primary);
  }
</style>
