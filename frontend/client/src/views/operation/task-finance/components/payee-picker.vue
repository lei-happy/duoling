<template>
  <div class="payee-picker">
    <el-row :gutter="12">
      <el-col :span="6">
        <el-form-item label="收款类型" prop="payeeType">
          <el-select
            v-model="local.payeeType"
            :disabled="disabled"
            @change="onTypeChange"
          >
            <el-option
              v-for="o in PAYEE_TYPE_OPTIONS"
              :key="o.value"
              :value="o.value"
              :label="o.label"
            />
          </el-select>
        </el-form-item>
      </el-col>

      <!-- 司机 -->
      <template v-if="local.payeeType === 1">
        <el-col :span="9">
          <el-form-item label="选择司机" prop="payeeId">
            <el-select
              v-model="local.payeeId"
              filterable
              remote
              clearable
              :disabled="disabled"
              :remote-method="searchDrivers"
              placeholder="搜索司机姓名/手机"
              @change="onDriverChange"
            >
              <el-option
                v-for="d in drivers"
                :key="d.id"
                :value="d.id!"
                :label="`${d.name} / ${d.phone}`"
              />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="9">
          <el-form-item label="收款账户">
            <el-select
              v-model="local.payeeAccountId"
              :disabled="disabled || !local.payeeId"
              clearable
              placeholder="可不指定"
            >
              <el-option
                v-for="a in driverAccounts"
                :key="a.id"
                :value="a.id!"
                :label="`${a.accountName} (${maskBank(a.accountNo)})`"
              />
            </el-select>
          </el-form-item>
        </el-col>
      </template>

      <!-- 承运商 -->
      <template v-else-if="local.payeeType === 2">
        <el-col :span="9">
          <el-form-item label="选择承运商" prop="payeeId">
            <el-select
              v-model="local.payeeId"
              filterable
              remote
              clearable
              :disabled="disabled"
              :remote-method="searchCarriers"
              placeholder="搜索承运商"
              @change="onCarrierChange"
            >
              <el-option
                v-for="c in carriers"
                :key="c.id"
                :value="c.id!"
                :label="c.carrierName"
              />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="9">
          <el-form-item label="结算账户">
            <el-select
              v-model="local.payeeAccountId"
              :disabled="disabled || !local.payeeId"
              clearable
              placeholder="可不指定"
            >
              <el-option
                v-for="s in settlements"
                :key="s.id"
                :value="s.id!"
                :label="`${s.accountLabel} - ${maskBank(s.bankAccount)}`"
              />
            </el-select>
          </el-form-item>
        </el-col>
      </template>

      <!-- 其他/自由文本 -->
      <template v-else>
        <el-col :span="9">
          <el-form-item label="收款人姓名" required>
            <el-input v-model="local.payeeName" :disabled="disabled" />
          </el-form-item>
        </el-col>
        <el-col :span="9">
          <el-form-item label="账号（脱敏）">
            <el-input
              v-model="local.payeeBankAccountMasked"
              :disabled="disabled"
              placeholder="如 6228 **** **** 1234"
            />
          </el-form-item>
        </el-col>
      </template>
    </el-row>
  </div>
</template>

<script lang="ts" setup>
  import { reactive, ref, watch } from 'vue';
  import { selectCarriers, listSettlements } from '@/api/partner/carrier';
  import { pageDrivers, listDriverAccounts } from '@/api/capacity/self-capacity/driver';
  import type { CarrierSelectItem, CarrierSettlement } from '@/api/partner/carrier/model';
  import type { Driver, DriverAccount } from '@/api/capacity/self-capacity/driver/model';
  import { PAYEE_TYPE_OPTIONS } from '../status-config';

  export interface PayeeFormData {
    payeeType: number;
    payeeId?: number | null;
    payeeName?: string;
    payeeAccountType?: number | null;
    payeeAccountId?: number | null;
    payeeBankName?: string;
    payeeBankAccountMasked?: string;
  }

  const props = defineProps<{
    modelValue: PayeeFormData;
    disabled?: boolean;
  }>();
  const emit = defineEmits<{
    (e: 'update:modelValue', v: PayeeFormData): void;
  }>();

  const local = reactive<PayeeFormData>({ ...(props.modelValue || { payeeType: 1 }) });

  watch(
    () => props.modelValue,
    (v) => Object.assign(local, v || {}),
    { deep: true }
  );
  watch(
    () => ({ ...local }),
    (v) => emit('update:modelValue', v),
    { deep: true }
  );

  const drivers = ref<Driver[]>([]);
  const driverAccounts = ref<DriverAccount[]>([]);
  const carriers = ref<CarrierSelectItem[]>([]);
  const settlements = ref<CarrierSettlement[]>([]);

  const searchDrivers = async (kw: string) => {
    try {
      const res = await pageDrivers({ keyword: kw, page: 1, limit: 20 });
      drivers.value = res?.list || [];
    } catch {
      drivers.value = [];
    }
  };

  const onDriverChange = async (id: number) => {
    const d = drivers.value.find((x) => x.id === id);
    if (d) {
      local.payeeName = d.name;
    }
    local.payeeAccountId = null;
    if (id) {
      try {
        driverAccounts.value = await listDriverAccounts(id);
        const def = driverAccounts.value[0];
        if (def?.id) {
          local.payeeAccountId = def.id;
          local.payeeAccountType = 1;
        }
      } catch {
        driverAccounts.value = [];
      }
    } else {
      driverAccounts.value = [];
    }
  };

  const searchCarriers = async (kw: string) => {
    try {
      carriers.value = await selectCarriers(kw);
    } catch {
      carriers.value = [];
    }
  };

  const onCarrierChange = async (id: number) => {
    const c = carriers.value.find((x) => x.id === id);
    if (c) {
      local.payeeName = c.carrierName;
    }
    local.payeeAccountId = null;
    if (id) {
      try {
        settlements.value = await listSettlements(id);
        const def = settlements.value.find((s) => s.isDefault === 1)
          || settlements.value[0];
        if (def?.id) {
          local.payeeAccountId = def.id;
          local.payeeAccountType = 2;
        }
      } catch {
        settlements.value = [];
      }
    } else {
      settlements.value = [];
    }
  };

  const onTypeChange = () => {
    local.payeeId = null;
    local.payeeAccountId = null;
    local.payeeName = '';
    local.payeeBankName = '';
    local.payeeBankAccountMasked = '';
    driverAccounts.value = [];
    settlements.value = [];
    if (local.payeeType === 1 && drivers.value.length === 0) searchDrivers('');
    if (local.payeeType === 2 && carriers.value.length === 0) searchCarriers('');
  };

  const maskBank = (no?: string) => {
    if (!no) return '';
    const s = no.trim();
    if (s.length <= 8) return s;
    return `${s.slice(0, 4)}****${s.slice(-4)}`;
  };

  /** 重置选择器：用于详情打开后，根据 modelValue 加载候选列表 */
  const init = async (defaults?: {
    driverId?: number | null;
    carrierId?: number | null;
  }) => {
    if (local.payeeType === 1) {
      await searchDrivers('');
      if (defaults?.driverId) {
        try {
          driverAccounts.value = await listDriverAccounts(defaults.driverId);
        } catch {
          driverAccounts.value = [];
        }
      }
    } else if (local.payeeType === 2) {
      await searchCarriers('');
      if (defaults?.carrierId) {
        try {
          settlements.value = await listSettlements(defaults.carrierId);
        } catch {
          settlements.value = [];
        }
      }
    }
  };
  defineExpose({ init });
</script>
