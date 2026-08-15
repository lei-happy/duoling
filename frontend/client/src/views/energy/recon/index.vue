<template>
  <ele-page>
    <ele-card>
      <div class="toolbar">
        <el-button type="primary" @click="openBalance">账户余额对账</el-button>
        <el-button @click="openConsumption">消费流水对账</el-button>
      </div>
      <el-table :data="list" v-loading="loading" border>
        <el-table-column prop="docNo" label="对账单号" min-width="160" />
        <el-table-column label="类型" width="100">
          <template #default="{ row }">
            {{ row.reconType === 1 ? '余额' : '流水' }}
          </template>
        </el-table-column>
        <el-table-column prop="internalAmount" label="系统金额" width="120" />
        <el-table-column prop="externalAmount" label="外部金额" width="120" />
        <el-table-column prop="differenceAmount" label="差异" width="110" />
        <el-table-column prop="diffCount" label="差异笔数" width="90" />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openItems(row)">明细</el-button>
            <el-button link type="primary" @click="doSettle(row)">确认核销</el-button>
          </template>
        </el-table-column>
      </el-table>
    </ele-card>

    <el-dialog
      v-model="balanceVisible"
      title="账户余额对账"
      width="480px"
      :close-on-click-modal="false"
    >
      <el-form ref="balanceRef" :model="balanceForm" :rules="balanceRules" label-width="120px">
        <el-form-item label="能源账户" prop="accountId">
          <el-select v-model="balanceForm.accountId" filterable style="width: 100%">
            <el-option
              v-for="a in accounts"
              :key="a.id"
              :label="`${a.accountName}（账面 ${a.ledgerBalance ?? 0}）`"
              :value="a.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="供应商侧余额" prop="supplierBalance">
          <el-input-number
            v-model="balanceForm.supplierBalance"
            :precision="2"
            controls-position="right"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="balanceVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="saveBalance">生成对账单</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="consVisible"
      title="消费流水对账"
      width="560px"
      :close-on-click-modal="false"
    >
      <el-form ref="consRef" :model="consForm" :rules="consRules" label-width="108px">
        <el-form-item label="能源账户">
          <el-select v-model="consForm.accountId" clearable filterable style="width: 100%">
            <el-option
              v-for="a in accounts"
              :key="a.id"
              :label="a.accountName"
              :value="a.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="对账期间" prop="period">
          <el-date-picker
            v-model="consForm.period"
            type="datetimerange"
            value-format="YYYY-MM-DD HH:mm:ss"
            start-placeholder="开始"
            end-placeholder="结束"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="外部账单">
          <el-input
            v-model="consForm.externalText"
            type="textarea"
            :rows="6"
            placeholder="每行一笔：流水号 金额&#10;例如：TXN001 1280.50"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="consVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="saveConsumption">生成对账单</el-button>
      </template>
    </el-dialog>

    <el-drawer v-model="itemVisible" title="对账明细" size="640px">
      <el-table :data="items" border>
        <el-table-column label="结果" width="110">
          <template #default="{ row }">
            {{ RECON_RESULTS[row.reconResult] || row.reconResult }}
          </template>
        </el-table-column>
        <el-table-column prop="externalTransactionId" label="外部流水号" min-width="140" />
        <el-table-column prop="externalAmount" label="外部金额" width="100" />
        <el-table-column prop="internalAmount" label="系统金额" width="100" />
        <el-table-column prop="differenceAmount" label="差异" width="90" />
        <el-table-column label="处理" width="90">
          <template #default="{ row }">
            {{ RECON_PROCESS[row.processStatus] || row.processStatus }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="140">
          <template #default="{ row }">
            <el-button
              v-if="row.processStatus === 'pending' && row.reconResult !== 'MATCHED'"
              link
              type="primary"
              @click="processItem(row, 'confirmed')"
            >
              确认
            </el-button>
            <el-button
              v-if="row.processStatus === 'pending' && row.reconResult !== 'MATCHED'"
              link
              @click="processItem(row, 'ignored')"
            >
              忽略
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-drawer>
  </ele-page>
</template>

<script lang="ts" setup>
  import { onMounted, reactive, ref } from 'vue';
  import type { FormInstance, FormRules } from 'element-plus';
  import { ElMessageBox } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import {
    createBalanceRecon,
    createConsumptionRecon,
    pageRecons,
    processReconItem,
    reconItems,
    settleRecon
  } from '@/api/energy';
  import { RECON_PROCESS, RECON_RESULTS, asPage } from '../_shared/options';
  import { useEnergyLookups } from '../_shared/use-lookups';

  defineOptions({ name: 'EnergyRecon' });

  const loading = ref(false);
  const saving = ref(false);
  const list = ref<any[]>([]);
  const items = ref<any[]>([]);
  const currentReconId = ref(0);
  const { accounts, loadAccounts } = useEnergyLookups();

  const balanceVisible = ref(false);
  const consVisible = ref(false);
  const itemVisible = ref(false);
  const balanceRef = ref<FormInstance>();
  const consRef = ref<FormInstance>();
  const balanceForm = reactive<any>({});
  const consForm = reactive<any>({ period: [], externalText: '' });

  const balanceRules: FormRules = {
    accountId: [{ required: true, message: '请选择能源账户', trigger: 'change' }],
    supplierBalance: [{ required: true, message: '请填写供应商侧余额', trigger: 'change' }]
  };
  const consRules: FormRules = {
    period: [{ required: true, message: '请选择对账期间', trigger: 'change' }]
  };

  const fetchData = async () => {
    loading.value = true;
    try {
      list.value = asPage(await pageRecons({ page: 1, limit: 50 })).list;
    } catch (e: any) {
      EleMessage.error({ message: e.message || '加载对账单失败，请重试', plain: true });
    } finally {
      loading.value = false;
    }
  };

  const openBalance = async () => {
    await loadAccounts();
    Object.assign(balanceForm, { accountId: undefined, supplierBalance: undefined });
    balanceVisible.value = true;
  };

  const saveBalance = async () => {
    await balanceRef.value?.validate();
    saving.value = true;
    try {
      await createBalanceRecon(balanceForm);
      EleMessage.success({ message: '已生成余额对账单', plain: true });
      balanceVisible.value = false;
      fetchData();
    } catch (e: any) {
      if (e?.message) EleMessage.error({ message: e.message, plain: true });
    } finally {
      saving.value = false;
    }
  };

  const openConsumption = async () => {
    await loadAccounts();
    Object.assign(consForm, { accountId: undefined, period: [], externalText: '' });
    consVisible.value = true;
  };

  const saveConsumption = async () => {
    await consRef.value?.validate();
    const [start, end] = consForm.period || [];
    const externalRows = String(consForm.externalText || '')
      .split('\n')
      .map((line: string) => line.trim())
      .filter(Boolean)
      .map((line: string) => {
        const [id, amount] = line.split(/\s+/);
        return { externalTransactionId: id, amount: Number(amount) };
      });
    saving.value = true;
    try {
      await createConsumptionRecon({
        accountId: consForm.accountId,
        start,
        end,
        externalRows
      });
      EleMessage.success({ message: '已生成流水对账单', plain: true });
      consVisible.value = false;
      fetchData();
    } catch (e: any) {
      if (e?.message) EleMessage.error({ message: e.message, plain: true });
    } finally {
      saving.value = false;
    }
  };

  const openItems = async (row: any) => {
    currentReconId.value = row.id;
    items.value = (await reconItems(row.id)) || [];
    itemVisible.value = true;
  };

  const processItem = async (row: any, processStatus: string) => {
    await processReconItem(row.id, { processStatus });
    EleMessage.success({
      message: processStatus === 'ignored' ? '已忽略这条差异' : '已确认这条差异',
      plain: true
    });
    items.value = (await reconItems(currentReconId.value)) || [];
  };

  const doSettle = (row: any) => {
    ElMessageBox.confirm('确认核销这张对账单？未处理的差异需要先确认或忽略。', '核销确认', {
      type: 'warning'
    }).then(async () => {
      await settleRecon(row.id);
      EleMessage.success({ message: '已核销', plain: true });
      fetchData();
    });
  };

  onMounted(fetchData);
</script>
<style scoped>
  .toolbar {
    margin-bottom: 12px;
  }
</style>
