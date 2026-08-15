<template>
  <ele-page>
    <finance-kpi-cards :cards="kpiCards" />
    <bank-account-search @search="(next) => reload(next, 1)" />
    <ele-card :body-style="{ paddingTop: '8px' }">
      <ele-pro-table
        ref="tableRef"
        row-key="id"
        :columns="columns"
        :datasource="datasource"
        :pagination="{ pageSize: 20 }"
        :show-overflow-tooltip="true"
        :highlight-current-row="true"
        cache-key="FinanceBankAccountTable"
      >
        <template #toolbar>
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
          <btn-items
            divider
            type="link"
            :wrap="false"
            :items="actionItems(row)"
          />
        </template>
      </ele-pro-table>
    </ele-card>

    <bank-account-edit
      v-model:visible="editVisible"
      :account="editing"
      @done="onSaved"
    />
    <bank-account-calibrate
      v-model:visible="calibrateVisible"
      :account="calibrating"
      @done="onSaved"
    />
  </ele-page>
</template>

<script lang="ts" setup>
  import { computed, reactive, ref } from 'vue';
  import { EleMessage } from 'ele-admin-plus';
  import type { EleProTable } from 'ele-admin-plus';
  import { ElMessageBox } from 'element-plus';
  import type {
    ButtonDropdownItem,
    ButtonItem
  } from 'ele-admin-plus/es/ele-buttons/types';
  import type {
    Columns,
    DatasourceFunction
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import {
    DeleteOutlined,
    EditOutlined,
    FundOutlined,
    MinusCircleOutlined
  } from '@/components/icons';
  import BankAccountCalibrate from './components/bank-account-calibrate.vue';
  import BankAccountEdit from './components/bank-account-edit.vue';
  import BankAccountSearch from './components/bank-account-search.vue';
  import FinanceKpiCards from '../components/finance-kpi-cards.vue';
  import type { FinanceKpiCard } from '../components/finance-kpi-cards.vue';
  import {
    getBalanceSummary,
    pageBankAccounts,
    removeBankAccount,
    setBankAccountStatus
  } from '@/api/finance/bank-account';
  import type {
    BankAccountItem,
    BankAccountParam
  } from '@/api/finance/bank-account/model';
  import { buildActionColumnItems } from '../_shared/action-column';
  import { formatMoney } from '../status-config';

  defineOptions({ name: 'FinanceBankAccount' });

  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);
  const where = reactive<BankAccountParam>({});
  const editVisible = ref(false);
  const editing = ref<BankAccountItem | null>(null);
  const calibrateVisible = ref(false);
  const calibrating = ref<BankAccountItem | null>(null);
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
      width: 168,
      minWidth: 168,
      align: 'center',
      slot: 'action',
      hideInPrint: true,
      hideInExport: true,
      fixed: 'right'
    }
  ]);

  const datasource: DatasourceFunction = ({ pages, where: tableWhere }) => {
    loadSummary();
    return pageBankAccounts({ ...(tableWhere || where), ...pages }).then(
      (res) => ({
        list: res?.list ?? [],
        count: res?.count ?? 0
      })
    );
  };

  const reload = (next?: BankAccountParam, page?: number) => {
    if (next) Object.assign(where, next);
    tableRef.value?.reload?.({ where: { ...where }, page });
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

  const actionItems = (row: BankAccountItem): ButtonItem[] => {
    const visible: ButtonDropdownItem[] = [
      {
        title: '编辑',
        icon: EditOutlined,
        permission: 'finance:bank-account:edit',
        onClick: () => openEdit(row)
      },
      {
        title: '余额校准',
        icon: FundOutlined,
        permission: 'finance:bank-account:calibrate',
        onClick: () => {
          calibrating.value = row;
          calibrateVisible.value = true;
        }
      },
      {
        title: row.status === 1 ? '停用' : '启用',
        icon: MinusCircleOutlined,
        permission: 'finance:bank-account:edit',
        onClick: () => toggleStatus(row)
      },
      {
        title: '删除',
        icon: DeleteOutlined,
        permission: 'finance:bank-account:delete',
        divided: true,
        danger: true,
        onClick: () => onRemove(row)
      }
    ];
    return buildActionColumnItems(visible);
  };

  const toggleStatus = async (row: BankAccountItem) => {
    const next = row.status === 1 ? 0 : 1;
    try {
      await ElMessageBox.confirm(
        next === 0
          ? '停用后这个账户不再出现在收付款的账户下拉里，已有流水不受影响。确定停用吗？'
          : '确定重新启用这个账户吗？',
        next === 0 ? '停用账户' : '启用账户',
        { type: 'warning', draggable: true }
      );
    } catch {
      return;
    }
    const loading = EleMessage.loading({
      message: '正在更新账户状态，请稍候…',
      plain: true
    });
    try {
      await setBankAccountStatus(row.id, next);
      EleMessage.success({
        message: next === 1 ? '已启用' : '已停用',
        plain: true
      });
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

  const onRemove = async (row: BankAccountItem) => {
    try {
      await ElMessageBox.confirm(
        `确定删除账户「${row.accountName}」吗？有收付流水的账户不能删，请改为停用。`,
        '删除账户',
        { type: 'warning', draggable: true }
      );
    } catch {
      return;
    }
    const loading = EleMessage.loading({
      message: '正在删除账户，请稍候…',
      plain: true
    });
    try {
      await removeBankAccount(row.id);
      EleMessage.success({ message: '账户已删除', plain: true });
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
