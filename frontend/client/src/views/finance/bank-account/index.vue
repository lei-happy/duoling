<template>
  <ele-page>
    <ele-card>
      <finance-kpi-cards :cards="kpiCards" />

      <ele-pro-table
        ref="tableRef"
        row-key="id"
        :columns="columns"
        :datasource="datasource"
        :pagination="{ pageSize: 20 }"
        :show-overflow-tooltip="true"
        cache-key="FinanceBankAccountTable"
      >
        <template #toolbar>
          <el-form :model="where" class="ele-bg-wrap" inline>
            <el-form-item>
              <el-input
                v-model="where.keyword"
                placeholder="账户名/账号/开户行"
                clearable
                style="width: 200px"
                @change="reload()"
              />
            </el-form-item>
            <el-form-item>
              <el-select
                v-model="where.accountType"
                placeholder="账户类型"
                clearable
                style="width: 120px"
                @change="reload()"
              >
                <el-option
                  v-for="o in BANK_ACCOUNT_TYPE_OPTIONS"
                  :key="o.value"
                  :value="o.value"
                  :label="o.label"
                />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-select
                v-model="where.usageScope"
                placeholder="用途"
                clearable
                style="width: 120px"
                @change="reload()"
              >
                <el-option
                  v-for="o in ACCOUNT_USAGE_SCOPE_OPTIONS"
                  :key="o.value"
                  :value="o.value"
                  :label="o.label"
                />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-select
                v-model="where.status"
                placeholder="状态"
                clearable
                style="width: 110px"
                @change="reload()"
              >
                <el-option :value="1" label="启用中" />
                <el-option :value="0" label="已停用" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <btn-items
                :items="[
                  {
                    preset: 'add',
                    title: '新增账户',
                    permission: 'finance:bank-account:create',
                    onClick: () => openEdit(null)
                  }
                ]"
              />
            </el-form-item>
          </el-form>
        </template>

        <template #account="{ row }">
          <div class="strong">{{ row.accountName }}</div>
          <div class="muted">
            {{ row.accountNoMasked || row.accountNo }}
            <template v-if="row.bankName"> · {{ row.bankName }}</template>
          </div>
        </template>

        <template #balance="{ row }">
          <div class="num-cell strong">¥ {{ formatMoney(row.balance) }}</div>
          <div class="muted">{{ row.currency }}</div>
        </template>

        <template #usage="{ row }">
          <el-tag size="small" effect="plain">
            {{ row.usageScopeLabel || '收付通用' }}
          </el-tag>
          <div class="tag-line">
            <el-tag
              v-if="row.isDefaultReceive === 1"
              size="small"
              type="success"
            >
              默认收款
            </el-tag>
            <el-tag v-if="row.isDefaultPay === 1" size="small" type="warning">
              默认付款
            </el-tag>
          </div>
        </template>

        <template #status="{ row }">
          <el-tag :type="row.status === 1 ? 'success' : 'info'" size="small">
            {{ row.status === 1 ? '启用中' : '已停用' }}
          </el-tag>
        </template>

        <template #action="{ row }">
          <el-link
            type="primary"
            :underline="false"
            v-permission="'finance:bank-account:edit'"
            @click="openEdit(row)"
          >
            编辑
          </el-link>
          <el-divider direction="vertical" />
          <el-link
            type="warning"
            :underline="false"
            v-permission="'finance:bank-account:calibrate'"
            @click="openCalibrate(row)"
          >
            余额校准
          </el-link>
          <el-divider direction="vertical" />
          <el-link
            :type="row.status === 1 ? 'danger' : 'success'"
            :underline="false"
            v-permission="'finance:bank-account:edit'"
            @click="toggleStatus(row)"
          >
            {{ row.status === 1 ? '停用' : '启用' }}
          </el-link>
          <el-divider direction="vertical" />
          <el-link
            type="danger"
            :underline="false"
            v-permission="'finance:bank-account:delete'"
            @click="onRemove(row)"
          >
            删除
          </el-link>
        </template>
      </ele-pro-table>
    </ele-card>

    <bank-account-edit
      v-model:visible="editVisible"
      :account="editing"
      @done="onSaved"
    />
  </ele-page>
</template>

<script lang="ts" setup>
  import { computed, nextTick, reactive, ref } from 'vue';
  import { EleMessage } from 'ele-admin-plus';
  import type { EleProTable } from 'ele-admin-plus';
  import { ElMessageBox } from 'element-plus';
  import type {
    Columns,
    DatasourceFunction
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import BankAccountEdit from './components/bank-account-edit.vue';
  import FinanceKpiCards from '../components/finance-kpi-cards.vue';
  import type { FinanceKpiCard } from '../components/finance-kpi-cards.vue';
  import {
    calibrateBankAccount,
    getBalanceSummary,
    pageBankAccounts,
    removeBankAccount,
    setBankAccountStatus
  } from '@/api/finance/bank-account';
  import type {
    BankAccountItem,
    BankAccountParam
  } from '@/api/finance/bank-account/model';
  import {
    ACCOUNT_USAGE_SCOPE_OPTIONS,
    BANK_ACCOUNT_TYPE_OPTIONS,
    formatMoney
  } from '../status-config';

  defineOptions({ name: 'FinanceBankAccount' });

  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);
  const where = reactive<BankAccountParam>({});
  const editVisible = ref(false);
  const editing = ref<BankAccountItem | null>(null);
  const summary = ref({ accountCount: 0, balanceTotal: 0 });

  const kpiCards = computed<FinanceKpiCard[]>(() => [
    {
      key: 'count',
      label: '启用账户',
      value: summary.value.accountCount,
      unit: '个',
      type: 'primary'
    },
    {
      key: 'balance',
      label: '账面余额合计',
      value: formatMoney(summary.value.balanceTotal),
      unit: '元',
      type: 'success',
      hint: '收付款登记后自动增减，与银行不一致时用余额校准修正'
    }
  ]);

  const columns = computed<Columns>(() => [
    { columnKey: 'account', label: '账户', minWidth: 220, slot: 'account' },
    {
      prop: 'accountTypeLabel',
      label: '类型',
      width: 100,
      align: 'center'
    },
    {
      columnKey: 'balance',
      label: '账面余额',
      width: 160,
      align: 'right',
      slot: 'balance'
    },
    {
      columnKey: 'usage',
      label: '用途',
      width: 160,
      align: 'center',
      slot: 'usage'
    },
    {
      prop: 'status',
      label: '状态',
      width: 90,
      align: 'center',
      slot: 'status'
    },
    { prop: 'remark', label: '备注', minWidth: 140 },
    {
      columnKey: 'action',
      label: '操作',
      width: 250,
      align: 'center',
      fixed: 'right',
      slot: 'action'
    }
  ]);

  const datasource: DatasourceFunction = ({ pages }) => {
    loadSummary();
    return pageBankAccounts({ ...where, ...pages }).then((res) => ({
      list: res?.list ?? [],
      count: res?.count ?? 0
    }));
  };

  const reload = () => {
    nextTick(() => tableRef.value?.reload?.());
  };

  const loadSummary = async () => {
    try {
      const res = await getBalanceSummary();
      if (res) summary.value = res;
    } catch {
      // 顶部合计失败不打断列表，静默即可
    }
  };

  const openEdit = (account: BankAccountItem | null) => {
    editing.value = account;
    editVisible.value = true;
  };

  const onSaved = () => reload();

  const toggleStatus = async (row: BankAccountItem) => {
    const next = row.status === 1 ? 0 : 1;
    try {
      await ElMessageBox.confirm(
        next === 0
          ? '停用后这个账户不再出现在收付款的账户下拉里，已有流水不受影响。确定停用吗？'
          : '确定重新启用这个账户吗？',
        next === 0 ? '停用账户' : '启用账户',
        { type: 'warning' }
      );
    } catch {
      return;
    }
    const loading = EleMessage.loading('正在更新账户状态，请稍候…');
    try {
      await setBankAccountStatus(row.id, next);
      EleMessage.success(next === 1 ? '已启用' : '已停用');
      reload();
    } catch (e: unknown) {
      EleMessage.error({
        message: (e as { message?: string }).message || '操作失败，请重试',
        plain: true
      });
    } finally {
      loading.close();
    }
  };

  const openCalibrate = async (row: BankAccountItem) => {
    let balance: string | undefined;
    try {
      const step1 = await ElMessageBox.prompt(
        `当前账面余额 ¥ ${formatMoney(row.balance)}，请填银行实际余额`,
        '余额校准',
        {
          inputPattern: /^-?\d+(\.\d{1,2})?$/,
          inputErrorMessage: '请填数字，最多两位小数',
          inputValue: String(row.balance ?? 0)
        }
      );
      balance = step1.value;
    } catch {
      return;
    }
    let reason: string | undefined;
    try {
      const step2 = await ElMessageBox.prompt(
        '校准会留痕，请说明原因（如：银行手续费未登记）',
        '校准原因',
        {
          inputPattern: /.{5,}/,
          inputErrorMessage: '原因至少写 5 个字，方便日后追溯'
        }
      );
      reason = step2.value;
    } catch {
      return;
    }
    const loading = EleMessage.loading('正在校准余额，请稍候…');
    try {
      await calibrateBankAccount(row.id, {
        balance: Number(balance),
        reason: reason as string
      });
      EleMessage.success('余额已校准');
      reload();
    } catch (e: unknown) {
      EleMessage.error({
        message: (e as { message?: string }).message || '校准失败，请重试',
        plain: true
      });
    } finally {
      loading.close();
    }
  };

  const onRemove = async (row: BankAccountItem) => {
    try {
      await ElMessageBox.confirm(
        `确定删除账户「${row.accountName}」吗？有收付流水的账户不能删，请改为停用。`,
        '删除账户',
        { type: 'warning' }
      );
    } catch {
      return;
    }
    const loading = EleMessage.loading('正在删除账户，请稍候…');
    try {
      await removeBankAccount(row.id);
      EleMessage.success('账户已删除');
      reload();
    } catch (e: unknown) {
      EleMessage.error({
        message: (e as { message?: string }).message || '删除失败，请重试',
        plain: true
      });
    } finally {
      loading.close();
    }
  };
</script>

<style lang="scss" scoped>
  .num-cell {
    font-variant-numeric: tabular-nums;
  }

  .strong {
    font-weight: 600;
  }

  .muted {
    color: var(--el-text-color-secondary);
    font-size: 12px;
  }

  .tag-line {
    display: flex;
    justify-content: center;
    gap: 4px;
    margin-top: 4px;
  }
</style>
