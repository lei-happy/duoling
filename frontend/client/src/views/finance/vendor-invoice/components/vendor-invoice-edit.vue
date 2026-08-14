<template>
  <el-dialog
    :model-value="visible"
    :title="invoice ? '修改发票信息' : '登记进项发票'"
    width="820px"
    top="6vh"
    destroy-on-close
    :close-on-click-modal="false"
    @update:model-value="(v: boolean) => emit('update:visible', v)"
    @open="onOpen"
  >
    <el-form :model="form" label-width="94px">
      <el-row :gutter="12">
        <el-col :span="8">
          <el-form-item label="供应商类型" required>
            <el-select
              v-model="form.vendorType"
              :disabled="!!invoice"
              style="width: 100%"
              @change="form.vendorId = void 0"
            >
              <el-option
                v-for="o in VENDOR_TYPE_OPTIONS"
                :key="o.value"
                :value="o.value"
                :label="o.label"
              />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item v-if="form.vendorType === 1" label="承运商">
            <el-select
              v-model="form.vendorId"
              placeholder="请选择承运商"
              filterable
              clearable
              :disabled="!!invoice"
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
          <el-form-item v-else label="供应商名称">
            <el-input
              v-model="form.sellerTitle"
              maxlength="100"
              placeholder="开票方名称"
            />
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
      </el-row>

      <el-row :gutter="12">
        <el-col :span="8">
          <el-form-item label="发票号码" required>
            <el-input
              v-model="form.invoiceNo"
              :disabled="!!invoice"
              maxlength="30"
              placeholder="发票号码"
            />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="发票代码">
            <el-input
              v-model="form.invoiceCode"
              :disabled="!!invoice"
              maxlength="20"
              placeholder="选填"
            />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="开票日期">
            <el-date-picker
              v-model="form.invoiceDate"
              type="date"
              value-format="YYYY-MM-DD"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="12">
        <el-col :span="8">
          <el-form-item label="销方税号">
            <el-input
              v-model="form.sellerTaxNo"
              maxlength="30"
              placeholder="选填"
            />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="购方名称">
            <el-input
              v-model="form.buyerTitle"
              maxlength="100"
              placeholder="我方开票主体"
            />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="购方税号">
            <el-input
              v-model="form.buyerTaxNo"
              maxlength="30"
              placeholder="选填"
            />
          </el-form-item>
        </el-col>
      </el-row>

      <el-divider content-position="left">
        <el-radio-group v-model="multiRate" size="small">
          <el-radio-button :value="false">单一税率</el-radio-button>
          <el-radio-button :value="true">多税率明细</el-radio-button>
        </el-radio-group>
      </el-divider>

      <template v-if="!multiRate">
        <el-row :gutter="12">
          <el-col :span="6">
            <el-form-item label="税率 %">
              <el-input-number
                v-model="form.taxRate"
                :min="0"
                :max="100"
                :precision="2"
                :controls="false"
                style="width: 100%"
                @change="onSingleRateChange"
              />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="价税合计" required>
              <el-input-number
                v-model="form.amountInclTax"
                :min="0.01"
                :precision="2"
                :controls="false"
                style="width: 100%"
                @change="onSingleRateChange"
              />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="不含税额">
              <el-input-number
                v-model="form.amountExclTax"
                :min="0"
                :precision="2"
                :controls="false"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="税额">
              <el-input-number
                v-model="form.taxAmount"
                :min="0"
                :precision="2"
                :controls="false"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <div class="amount-tip">
          填税率与价税合计会自动折算，不平的话可以手工改。三者要满足「不含税额 +
          税额 = 价税合计」。
        </div>
      </template>

      <template v-else>
        <el-table :data="form.items" size="small" max-height="220">
          <el-table-column label="项目" min-width="150">
            <template #default="{ row }">
              <el-input
                v-model="row.itemName"
                size="small"
                placeholder="选填"
              />
            </template>
          </el-table-column>
          <el-table-column label="税率 %" width="110">
            <template #default="{ row }">
              <el-input-number
                v-model="row.taxRate"
                :min="0"
                :max="100"
                :precision="2"
                :controls="false"
                size="small"
                style="width: 100%"
                @change="() => onItemChange(row)"
              />
            </template>
          </el-table-column>
          <el-table-column label="价税合计" width="130">
            <template #default="{ row }">
              <el-input-number
                v-model="row.amountInclTax"
                :min="0"
                :precision="2"
                :controls="false"
                size="small"
                style="width: 100%"
                @change="() => onItemChange(row)"
              />
            </template>
          </el-table-column>
          <el-table-column label="不含税额" width="130">
            <template #default="{ row }">
              <el-input-number
                v-model="row.amountExclTax"
                :min="0"
                :precision="2"
                :controls="false"
                size="small"
                style="width: 100%"
              />
            </template>
          </el-table-column>
          <el-table-column label="税额" width="130">
            <template #default="{ row }">
              <el-input-number
                v-model="row.taxAmount"
                :min="0"
                :precision="2"
                :controls="false"
                size="small"
                style="width: 100%"
              />
            </template>
          </el-table-column>
          <el-table-column label="操作" width="70" align="center">
            <template #default="{ $index }">
              <el-link
                type="danger"
                :underline="false"
                @click="form.items.splice($index, 1)"
              >
                删除
              </el-link>
            </template>
          </el-table-column>
        </el-table>
        <div class="items-foot">
          <el-button size="small" plain @click="addItem">增加一行</el-button>
          <span class="amount-tip">
            价税合计 ¥ {{ formatMoney(itemsTotal) }}，按明细汇总入账
          </span>
        </div>
      </template>

      <el-row :gutter="12" class="mt-12">
        <el-col :span="8">
          <el-form-item label="可否抵扣">
            <el-radio-group v-model="form.deductible">
              <el-radio :value="1">可抵扣</el-radio>
              <el-radio :value="0">不可抵扣</el-radio>
            </el-radio-group>
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="抵扣税期">
            <el-date-picker
              v-model="form.deductPeriod"
              type="month"
              value-format="YYYY-MM"
              placeholder="选填，如 2026-08"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="发票影像">
            <el-input
              v-model="form.attachmentUrl"
              maxlength="500"
              placeholder="选填，附件链接"
            />
          </el-form-item>
        </el-col>
      </el-row>
      <el-form-item label="备注">
        <el-input v-model="form.remark" maxlength="500" placeholder="选填" />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="emit('update:visible', false)">取消</el-button>
      <el-button type="primary" :loading="saving" @click="save">
        {{ invoice ? '保存' : '登记发票' }}
      </el-button>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
  import { computed, ref } from 'vue';
  import { EleMessage } from 'ele-admin-plus';
  import {
    registerVendorInvoice,
    updateVendorInvoice
  } from '@/api/finance/vendor-invoice';
  import type {
    VendorInvoiceDetail,
    VendorInvoiceItemPayload
  } from '@/api/finance/vendor-invoice/model';
  import { selectCarriers } from '@/api/partner/carrier';
  import type { CarrierSelectItem } from '@/api/partner/carrier/model';
  import {
    formatMoney,
    INVOICE_TYPE_OPTIONS,
    VENDOR_TYPE_OPTIONS
  } from '../../status-config';

  type ItemRow = VendorInvoiceItemPayload;

  const props = defineProps<{
    visible: boolean;
    invoice?: VendorInvoiceDetail | null;
  }>();

  const emit = defineEmits<{
    (e: 'update:visible', v: boolean): void;
    (e: 'done', invoiceId?: number): void;
  }>();

  const saving = ref(false);
  const multiRate = ref(false);
  const carriers = ref<CarrierSelectItem[]>([]);

  const form = ref<{
    vendorType: number;
    vendorId?: number;
    sellerTitle?: string;
    sellerTaxNo?: string;
    buyerEntityId?: number;
    buyerTitle?: string;
    buyerTaxNo?: string;
    invoiceType: number;
    invoiceNo: string;
    invoiceCode?: string;
    invoiceDate?: string;
    /** 税率按百分数录入与存储，与后端 `tax_rate` 口径一致 */
    taxRate?: number;
    amountInclTax?: number;
    amountExclTax?: number;
    taxAmount?: number;
    deductible: number;
    deductPeriod?: string;
    attachmentUrl?: string;
    remark?: string;
    items: ItemRow[];
  }>({
    vendorType: 1,
    invoiceType: 2,
    invoiceNo: '',
    deductible: 1,
    items: []
  });

  const itemsTotal = computed(() =>
    form.value.items.reduce((sum, r) => sum + Number(r.amountInclTax || 0), 0)
  );

  const onOpen = async () => {
    const inv = props.invoice;
    if (inv) {
      form.value = {
        vendorType: inv.vendorType,
        vendorId: inv.vendorId,
        sellerTitle: inv.sellerTitle,
        sellerTaxNo: inv.sellerTaxNo,
        buyerEntityId: inv.buyerEntityId,
        buyerTitle: inv.buyerTitle,
        buyerTaxNo: inv.buyerTaxNo,
        invoiceType: inv.invoiceType,
        invoiceNo: inv.invoiceNo,
        invoiceCode: inv.invoiceCode,
        invoiceDate: inv.invoiceDate,
        taxRate: inv.taxRate,
        amountInclTax: inv.amountInclTax,
        amountExclTax: inv.amountExclTax,
        taxAmount: inv.taxAmount,
        deductible: inv.deductible,
        deductPeriod: inv.deductPeriod,
        attachmentUrl: inv.attachmentUrl,
        remark: inv.remark,
        items: (inv.items || []).map((i) => ({
          itemName: i.itemName,
          taxRate: i.taxRate ?? 0,
          amountExclTax: i.amountExclTax,
          taxAmount: i.taxAmount,
          amountInclTax: i.amountInclTax,
          remark: i.remark
        }))
      };
      multiRate.value = inv.isMultiRate === 1;
    } else {
      form.value = {
        vendorType: 1,
        invoiceType: 2,
        invoiceNo: '',
        taxRate: 9,
        deductible: 1,
        items: []
      };
      multiRate.value = false;
    }
    if (!carriers.value.length) {
      try {
        carriers.value = (await selectCarriers()) || [];
      } catch {
        // 承运商下拉拉取失败时仍可手填销方名称
      }
    }
  };

  const onCarrierChange = (id?: number) => {
    const carrier = carriers.value.find((c) => c.id === id);
    if (carrier) form.value.sellerTitle = carrier.carrierName;
  };

  /** 税率 + 价税合计 → 反推不含税与税额，省去手算 */
  const splitAmount = (incl?: number, ratePercent?: number) => {
    if (!incl || ratePercent == null) return null;
    const rate = Number(ratePercent) / 100;
    const excl = Number((incl / (1 + rate)).toFixed(2));
    return { excl, tax: Number((incl - excl).toFixed(2)) };
  };

  const onSingleRateChange = () => {
    const parts = splitAmount(form.value.amountInclTax, form.value.taxRate);
    if (parts) {
      form.value.amountExclTax = parts.excl;
      form.value.taxAmount = parts.tax;
    }
  };

  const onItemChange = (row: ItemRow) => {
    const parts = splitAmount(row.amountInclTax, row.taxRate);
    if (parts) {
      row.amountExclTax = parts.excl;
      row.taxAmount = parts.tax;
    }
  };

  const addItem = () => {
    form.value.items.push({ taxRate: 9 });
  };

  const save = async () => {
    if (!props.invoice && !form.value.invoiceNo.trim()) {
      EleMessage.warning({ message: '请填写发票号码', plain: true });
      return;
    }
    if (multiRate.value && !form.value.items.length) {
      EleMessage.warning({ message: '请至少填一行税率明细', plain: true });
      return;
    }
    if (!multiRate.value && !form.value.amountInclTax) {
      EleMessage.warning({ message: '请填写价税合计', plain: true });
      return;
    }
    const items = multiRate.value ? form.value.items : [];
    const payload = {
      invoiceType: form.value.invoiceType,
      invoiceDate: form.value.invoiceDate,
      sellerTitle: form.value.sellerTitle,
      sellerTaxNo: form.value.sellerTaxNo,
      buyerEntityId: form.value.buyerEntityId,
      buyerTitle: form.value.buyerTitle,
      buyerTaxNo: form.value.buyerTaxNo,
      amountExclTax: multiRate.value ? void 0 : form.value.amountExclTax,
      taxAmount: multiRate.value ? void 0 : form.value.taxAmount,
      amountInclTax: multiRate.value ? void 0 : form.value.amountInclTax,
      taxRate: multiRate.value ? void 0 : form.value.taxRate,
      deductible: form.value.deductible,
      deductPeriod: form.value.deductPeriod,
      attachmentUrl: form.value.attachmentUrl,
      items,
      remark: form.value.remark
    };
    saving.value = true;
    try {
      const detail = props.invoice
        ? await updateVendorInvoice(props.invoice.id, payload)
        : await registerVendorInvoice({
            ...payload,
            invoiceNo: form.value.invoiceNo.trim(),
            invoiceCode: form.value.invoiceCode,
            vendorType: form.value.vendorType,
            vendorId: form.value.vendorId
          });
      EleMessage.success({
        message: props.invoice ? '已保存' : '已登记发票，可以核销到结算单了',
        plain: true
      });
      emit('update:visible', false);
      emit('done', detail?.id);
    } catch (e: unknown) {
      const msg = (e as { message?: string }).message || '保存失败，请稍后重试';
      EleMessage.error({ message: msg, plain: true });
    } finally {
      saving.value = false;
    }
  };
</script>

<style lang="scss" scoped>
  .amount-tip {
    color: var(--el-text-color-secondary);
    font-size: 12px;
  }

  .items-foot {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-top: 8px;
  }

  .mt-12 {
    margin-top: 12px;
  }
</style>
