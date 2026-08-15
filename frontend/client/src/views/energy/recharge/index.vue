<template>
  <ele-page>
    <ele-card :body-style="{ paddingBottom: 0 }">
      <el-form :inline="true" @submit.prevent="">
        <el-form-item>
          <el-button type="primary" @click="openAdd">登记充值</el-button>
        </el-form-item>
      </el-form>
    </ele-card>
    <ele-card>
      <el-table :data="list" v-loading="loading" border>
        <el-table-column prop="docNo" label="单号" min-width="160" />
        <el-table-column prop="accountName" label="能源账户" min-width="140" />
        <el-table-column prop="plannedAmount" label="充值金额" width="120" />
        <el-table-column prop="actualAmount" label="实付金额" width="120" />
        <el-table-column prop="bankAccountLabel" label="付款账户" min-width="140" />
        <el-table-column prop="paymentReference" label="回单号" min-width="140" />
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            {{ RECHARGE_STATUSES[row.status] || row.status }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.status !== 3 && row.status !== 4"
              link
              type="primary"
              @click="openPay(row)"
            >
              登记入账
            </el-button>
            <el-button
              v-if="row.status !== 3 && row.status !== 4"
              link
              type="danger"
              @click="openCancel(row)"
            >
              撤销
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pager">
        <el-pagination
          :current-page="page"
          :total="total"
          layout="total, prev, pager, next"
          @current-change="(p: number) => { page = p; fetchData(); }"
        />
      </div>
    </ele-card>

    <el-dialog v-model="addVisible" title="登记充值" width="520px" :close-on-click-modal="false">
      <el-form ref="addRef" :model="addForm" :rules="addRules" label-width="108px">
        <el-form-item label="能源账户" prop="accountId">
          <el-select v-model="addForm.accountId" filterable style="width: 100%">
            <el-option
              v-for="a in accounts"
              :key="a.id"
              :label="`${a.accountName}（余额 ${a.ledgerBalance ?? 0}）`"
              :value="a.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="充值金额" prop="plannedAmount">
          <el-input-number
            v-model="addForm.plannedAmount"
            :min="0.01"
            :precision="2"
            :step="100"
            controls-position="right"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="充值时间">
          <el-date-picker
            v-model="addForm.rechargeTime"
            type="datetime"
            value-format="YYYY-MM-DD HH:mm:ss"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="付款账户">
          <el-input v-model.trim="addForm.bankAccountLabel" placeholder="公司打出的银行账户名称" />
        </el-form-item>
        <el-form-item label="回单号">
          <el-input v-model.trim="addForm.paymentReference" placeholder="银行回单 / 付款凭证号" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model.trim="addForm.remark" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="saveAdd">保存草稿</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="payVisible" title="登记入账" width="480px" :close-on-click-modal="false">
      <el-alert
        type="warning"
        :closable="false"
        title="确认已经向供应商打款后，再入账。入账后会增加能源账户余额。"
        style="margin-bottom: 16px"
      />
      <el-form ref="payRef" :model="payForm" label-width="108px">
        <el-form-item label="实付金额">
          <el-input-number
            v-model="payForm.actualAmount"
            :min="0.01"
            :precision="2"
            controls-position="right"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="付款账户">
          <el-input v-model.trim="payForm.bankAccountLabel" />
        </el-form-item>
        <el-form-item label="回单号">
          <el-input v-model.trim="payForm.paymentReference" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="payVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="savePay">确认入账</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="cancelVisible" title="撤销充值单" width="480px" :close-on-click-modal="false">
      <el-form ref="cancelRef" :model="cancelForm" :rules="cancelRules" label-width="96px">
        <el-form-item label="撤销原因" prop="reason">
          <el-input
            v-model.trim="cancelForm.reason"
            type="textarea"
            :rows="3"
            placeholder="至少写 5 个字，说明为什么撤销"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="cancelVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="saveCancel">确认撤销</el-button>
      </template>
    </el-dialog>
  </ele-page>
</template>

<script lang="ts" setup>
  import { onMounted, reactive, ref } from 'vue';
  import type { FormInstance, FormRules } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import { addRecharge, cancelRecharge, pageRecharges, payRecharge } from '@/api/energy';
  import { RECHARGE_STATUSES, asPage } from '../_shared/options';
  import { useEnergyLookups } from '../_shared/use-lookups';

  defineOptions({ name: 'EnergyRecharge' });

  const loading = ref(false);
  const saving = ref(false);
  const list = ref<any[]>([]);
  const total = ref(0);
  const page = ref(1);
  const { accounts, loadAccounts } = useEnergyLookups();

  const addVisible = ref(false);
  const payVisible = ref(false);
  const cancelVisible = ref(false);
  const addRef = ref<FormInstance>();
  const payRef = ref<FormInstance>();
  const cancelRef = ref<FormInstance>();
  const addForm = reactive<any>({ plannedAmount: 0 });
  const payForm = reactive<any>({ id: 0 });
  const cancelForm = reactive<any>({ id: 0, reason: '' });

  const addRules: FormRules = {
    accountId: [{ required: true, message: '请选择能源账户', trigger: 'change' }],
    plannedAmount: [{ required: true, message: '请填写充值金额', trigger: 'change' }]
  };
  const cancelRules: FormRules = {
    reason: [
      { required: true, message: '请填写撤销原因', trigger: 'blur' },
      { min: 5, message: '撤销原因至少 5 个字', trigger: 'blur' }
    ]
  };

  const fetchData = async () => {
    loading.value = true;
    try {
      const res = asPage(await pageRecharges({ page: page.value, limit: 20 }));
      list.value = res.list;
      total.value = res.count;
    } catch (e: any) {
      EleMessage.error({ message: e.message || '加载充值单失败，请重试', plain: true });
    } finally {
      loading.value = false;
    }
  };

  const openAdd = async () => {
    await loadAccounts();
    Object.assign(addForm, {
      accountId: undefined,
      plannedAmount: undefined,
      rechargeTime: '',
      bankAccountLabel: '',
      paymentReference: '',
      remark: ''
    });
    addVisible.value = true;
  };

  const saveAdd = async () => {
    await addRef.value?.validate();
    saving.value = true;
    try {
      await addRecharge(addForm);
      EleMessage.success({ message: '已登记充值单，确认打款后再入账', plain: true });
      addVisible.value = false;
      fetchData();
    } catch (e: any) {
      if (e?.message) EleMessage.error({ message: e.message, plain: true });
    } finally {
      saving.value = false;
    }
  };

  const openPay = (row: any) => {
    Object.assign(payForm, {
      id: row.id,
      actualAmount: row.plannedAmount,
      bankAccountLabel: row.bankAccountLabel || '',
      paymentReference: row.paymentReference || ''
    });
    payVisible.value = true;
  };

  const savePay = async () => {
    saving.value = true;
    try {
      await payRecharge(payForm.id, payForm);
      EleMessage.success({ message: '已入账到能源账户', plain: true });
      payVisible.value = false;
      fetchData();
    } catch (e: any) {
      EleMessage.error({ message: e.message || '入账失败，请重试', plain: true });
    } finally {
      saving.value = false;
    }
  };

  const openCancel = (row: any) => {
    Object.assign(cancelForm, { id: row.id, reason: '' });
    cancelVisible.value = true;
  };

  const saveCancel = async () => {
    await cancelRef.value?.validate();
    saving.value = true;
    try {
      await cancelRecharge(cancelForm.id, { reason: cancelForm.reason });
      EleMessage.success({ message: '已撤销充值单', plain: true });
      cancelVisible.value = false;
      fetchData();
    } catch (e: any) {
      EleMessage.error({ message: e.message || '撤销失败，请重试', plain: true });
    } finally {
      saving.value = false;
    }
  };

  onMounted(fetchData);
</script>
<style scoped>
  .pager {
    display: flex;
    justify-content: flex-end;
    margin-top: 12px;
  }
</style>
