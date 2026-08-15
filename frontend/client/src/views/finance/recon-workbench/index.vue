<template>
  <ele-page>
    <finance-kpi-cards :cards="kpiCards" @select="onKpiSelect" />

    <ele-card :body-style="{ paddingTop: '8px' }">
      <el-tabs v-model="activeTab" @tab-change="onTabChange">
        <el-tab-pane name="candidates">
          <template #label>
            <span>
              候选池
              <el-badge
                v-if="summary?.pendingCustomerCount"
                :value="summary.pendingCustomerCount"
                type="primary"
                class="tab-badge"
              />
            </span>
          </template>
        </el-tab-pane>
        <el-tab-pane name="dirty">
          <template #label>
            <span>
              待重核
              <el-badge
                v-if="summary?.dirtyReconCount"
                :value="summary.dirtyReconCount"
                type="warning"
                class="tab-badge"
              />
            </span>
          </template>
        </el-tab-pane>
        <el-tab-pane name="diffs">
          <template #label>
            <span>
              差异待办
              <el-badge
                v-if="summary?.openDiffCount"
                :value="summary.openDiffCount"
                type="danger"
                class="tab-badge"
              />
            </span>
          </template>
        </el-tab-pane>
        <el-tab-pane name="unsigned">
          <template #label>
            <span>
              待客户回签
              <el-badge
                v-if="summary?.pendingSignCount"
                :value="summary.pendingSignCount"
                type="primary"
                class="tab-badge"
              />
            </span>
          </template>
        </el-tab-pane>
      </el-tabs>

      <el-form label-width="0" class="search-form tab-toolbar" @submit.prevent>
        <el-input
          v-if="activeTab === 'candidates'"
          v-model="keyword"
          placeholder="客户名称"
          clearable
          style="width: 200px"
          @change="loadList"
        />
        <div v-if="activeTab === 'diffs'" class="search-flags">
          <el-checkbox v-model="onlyBlocking" @change="loadList">
            只看阻断确认的差异
          </el-checkbox>
        </div>
        <span class="toolbar-tip">{{ tabTip }}</span>
        <btn-items
          :items="[{ preset: 'search', title: '刷新', onClick: reloadAll }]"
        />
      </el-form>

      <!-- 候选池：待对账运单按客户归堆，选客户再去建单 -->
      <el-table
        v-if="activeTab === 'candidates'"
        :data="groups"
        v-loading="loading"
        size="small"
      >
        <el-table-column prop="customerName" label="客户" min-width="200">
          <template #default="{ row }">
            {{ row.customerName || `客户 ${row.customerId}` }}
          </template>
        </el-table-column>
        <el-table-column
          prop="waybillCount"
          label="待对账运单"
          width="120"
          align="center"
        />
        <el-table-column label="运费合计" width="150" align="right">
          <template #default="{ row }">
            <span class="num">¥ {{ formatMoney(row.freightAmount) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" align="center" fixed="right">
          <template #default="{ row }">
            <btn-items
              :items="candidateActions(row)"
              type="link"
              :wrap="false"
              divider
            />
          </template>
        </el-table-column>
        <template #empty>
          <div class="empty-tip">
            当前没有待对账的运单，交车后的运单会自动出现在这里
          </div>
        </template>
      </el-table>

      <!-- 待重核 / 待回签共用对账单列表 -->
      <el-table
        v-else-if="activeTab === 'dirty' || activeTab === 'unsigned'"
        :data="recons"
        v-loading="loading"
        size="small"
      >
        <el-table-column prop="docNo" label="对账单号" min-width="170" />
        <el-table-column prop="customerName" label="客户" min-width="160" />
        <el-table-column label="对账周期" width="190" align="center">
          <template #default="{ row }">
            {{ row.periodStart }} ~ {{ row.periodEnd }}
          </template>
        </el-table-column>
        <el-table-column label="金额" width="130" align="right">
          <template #default="{ row }">
            <span class="num">¥ {{ formatMoney(row.plannedAmount) }}</span>
          </template>
        </el-table-column>
        <el-table-column
          v-if="activeTab === 'dirty'"
          label="脏行 / 差异"
          width="120"
          align="center"
        >
          <template #default="{ row }">
            <span class="warn">{{ row.dirtyLineCount }}</span>
            <span class="muted"> / </span>
            <span :class="{ danger: row.diffOpenCount > 0 }">
              {{ row.diffOpenCount }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag
              :type="(RECON_STATUS_MAP[row.status]?.type as any) || 'info'"
              size="small"
            >
              {{ row.statusLabel }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" align="center" fixed="right">
          <template #default="{ row }">
            <btn-items
              :items="reconActions(row)"
              type="link"
              :wrap="false"
              divider
            />
          </template>
        </el-table-column>
        <template #empty>
          <div class="empty-tip">
            {{
              activeTab === 'dirty'
                ? '没有需要重核的对账单，业务侧数据都与对账行一致'
                : '没有等待客户回签的对账单'
            }}
          </div>
        </template>
      </el-table>

      <!-- 差异待办：跨对账单的未处置差异 -->
      <el-table v-else :data="diffs" v-loading="loading" size="small">
        <el-table-column prop="reconDocNo" label="所属对账单" min-width="160">
          <template #default="{ row }">
            <el-link
              type="primary"
              :underline="false"
              @click="openDetail(row.reconId)"
            >
              {{ row.reconDocNo || `对账单 ${row.reconId}` }}
            </el-link>
          </template>
        </el-table-column>
        <el-table-column prop="bizDocNo" label="业务单据" min-width="150">
          <template #default="{ row }">
            {{ row.bizDocNo || `${row.bizDocTypeLabel || ''} ${row.bizDocId}` }}
          </template>
        </el-table-column>
        <el-table-column
          prop="diffTypeLabel"
          label="差异类型"
          width="110"
          align="center"
        />
        <el-table-column label="严重度" width="90" align="center">
          <template #default="{ row }">
            <el-tag
              :type="row.severity === 2 ? 'danger' : 'warning'"
              size="small"
              effect="plain"
            >
              {{ row.severityLabel || (row.severity === 2 ? '阻断' : '提示') }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="应为 / 实为" min-width="200">
          <template #default="{ row }">
            <span class="muted">{{ row.expectedValue || '--' }}</span>
            <span class="muted"> → </span>
            <span>{{ row.actualValue || '--' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="差异金额" width="120" align="right">
          <template #default="{ row }">
            <span class="num">
              {{ row.diffAmount ? `¥ ${formatMoney(row.diffAmount)}` : '--' }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" align="center" fixed="right">
          <template #default="{ row }">
            <btn-items
              :items="diffActions(row)"
              type="link"
              :wrap="false"
            />
          </template>
        </el-table-column>
        <template #empty>
          <div class="empty-tip">没有待处置的差异</div>
        </template>
      </el-table>
    </ele-card>

    <recon-create
      v-model:visible="createVisible"
      :customer-id="createCustomerId"
      :customers="customers"
      @done="onCreated"
    />

    <recon-detail
      v-model:visible="detailVisible"
      :recon-id="detailId"
      @changed="reloadAll"
    />

    <recon-sign
      v-if="signId"
      v-model:visible="signVisible"
      :recon-id="signId"
      @done="reloadAll"
    />

    <recon-diff-resolve
      v-model:visible="resolveVisible"
      :diff="resolveDiff"
      @done="reloadAll"
    />
  </ele-page>
</template>

<script lang="ts" setup>
  import { computed, onMounted, ref } from 'vue';
  import { useRouter } from 'vue-router';
  import { ElMessageBox } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import type {
    ButtonDropdownItem,
    ButtonItem
  } from 'ele-admin-plus/es/ele-buttons/types';
  import {
    CheckOutlined,
    EyeOutlined,
    FormOutlined,
    PlusOutlined,
    SyncOutlined
  } from '@/components/icons';
  import { buildActionColumnItems } from '../_shared/action-column';
  import FinanceKpiCards from '../components/finance-kpi-cards.vue';
  import type { FinanceKpiCard } from '../components/finance-kpi-cards.vue';
  import ReconCreate from '../customer-recon/components/recon-create.vue';
  import ReconDetail from '../customer-recon/components/recon-detail.vue';
  import ReconSign from '../customer-recon/components/recon-sign.vue';
  import ReconDiffResolve from '../components/recon-diff-resolve.vue';
  import {
    getReconWorkbenchSummary,
    listPendingWaybillGroups,
    listWorkbenchDiffs
  } from '@/api/finance/recon-workbench';
  import type {
    PendingWaybillGroup,
    ReconWorkbenchSummary
  } from '@/api/finance/recon-workbench';
  import {
    checkRecon,
    pageRecons,
    recalcRecon
  } from '@/api/finance/customer-recon';
  import type {
    ReconDiff,
    ReconListItem
  } from '@/api/finance/customer-recon/model';
  import { selectCustomers } from '@/api/partner/customer';
  import type { CustomerSelectItem } from '@/api/partner/customer/model';
  import { formatMoney, RECON_STATUS_MAP } from '../status-config';

  defineOptions({ name: 'FinanceReconWorkbench' });

  const router = useRouter();

  type TabName = 'candidates' | 'dirty' | 'diffs' | 'unsigned';

  const activeTab = ref<TabName>('candidates');
  const loading = ref(false);
  const keyword = ref('');
  const onlyBlocking = ref(false);

  const summary = ref<ReconWorkbenchSummary | null>(null);
  const groups = ref<PendingWaybillGroup[]>([]);
  const recons = ref<ReconListItem[]>([]);
  const diffs = ref<ReconDiff[]>([]);
  const customers = ref<CustomerSelectItem[]>([]);

  const createVisible = ref(false);
  const createCustomerId = ref<number | undefined>(void 0);
  const detailVisible = ref(false);
  const detailId = ref<number | null>(null);
  const signVisible = ref(false);
  const signId = ref<number | null>(null);
  const resolveVisible = ref(false);
  const resolveDiff = ref<ReconDiff | null>(null);

  const TAB_TIPS: Record<TabName, string> = {
    candidates: '已交车、未挂对账单的运单按客户归堆，攒够一批就建单',
    dirty: '业务侧数据变过的对账单，重核后再确认',
    diffs: '阻断类差异不处置就无法确认对账单',
    unsigned: '已确认待客户盖章回传的对账单'
  };

  const tabTip = computed(() => TAB_TIPS[activeTab.value]);

  const kpiCards = computed<FinanceKpiCard[]>(() => {
    const s = summary.value;
    return [
      {
        key: 'candidates',
        label: '待对账运单',
        value: s?.pendingWaybillCount ?? 0,
        unit: '单',
        type: 'primary',
        clickable: true,
        hint: `${s?.pendingCustomerCount ?? 0} 个客户 · ¥ ${formatMoney(
          s?.pendingWaybillAmount ?? 0
        )}`
      },
      {
        key: 'dirty',
        label: '待重核对账单',
        value: s?.dirtyReconCount ?? 0,
        unit: '张',
        type: 'warning',
        clickable: true,
        hint: '业务侧改过数，需要重新核对'
      },
      {
        key: 'diffs',
        label: '未处置差异',
        value: s?.openDiffCount ?? 0,
        unit: '条',
        type: 'danger',
        clickable: true,
        hint: `其中阻断 ${s?.blockingDiffCount ?? 0} 条 · 涉及 ¥ ${formatMoney(
          s?.openDiffAmount ?? 0
        )}`
      },
      {
        key: 'unsigned',
        label: '待客户回签',
        value: s?.pendingSignCount ?? 0,
        unit: '张',
        type: 'info',
        clickable: true,
        hint: `¥ ${formatMoney(s?.pendingSignAmount ?? 0)}`
      },
      {
        key: 'confirmed',
        label: '本期已确认',
        value: s?.confirmedThisMonthCount ?? 0,
        unit: '张',
        type: 'success',
        hint: `${s?.monthStart || '本月'} 起 · ¥ ${formatMoney(
          s?.confirmedThisMonthAmount ?? 0
        )}`
      }
    ];
  });

  const loadSummary = async () => {
    try {
      summary.value = (await getReconWorkbenchSummary()) ?? null;
    } catch (e: unknown) {
      const msg = (e as { message?: string }).message || '统计加载失败，请重试';
      EleMessage.error({ message: msg, plain: true });
    }
  };

  const loadList = async () => {
    loading.value = true;
    try {
      if (activeTab.value === 'candidates') {
        const res = await listPendingWaybillGroups({
          keyword: keyword.value || void 0
        });
        groups.value = res?.list ?? [];
      } else if (activeTab.value === 'diffs') {
        const res = await listWorkbenchDiffs({
          onlyBlocking: onlyBlocking.value || void 0
        });
        diffs.value = res?.list ?? [];
      } else {
        const res = await pageRecons(
          activeTab.value === 'dirty'
            ? { onlyDirty: true, limit: 100 }
            : { status: 2, onlyUnsigned: true, limit: 100 }
        );
        recons.value = res?.list ?? [];
      }
    } catch (e: unknown) {
      const msg = (e as { message?: string }).message || '列表加载失败，请重试';
      EleMessage.error({ message: msg, plain: true });
    } finally {
      loading.value = false;
    }
  };

  const reloadAll = async () => {
    await Promise.all([loadSummary(), loadList()]);
  };

  const onTabChange = () => {
    loadList();
  };

  const onKpiSelect = (key: string) => {
    if (key === 'confirmed') return;
    activeTab.value = key as TabName;
    loadList();
  };

  const candidateActions = (row: PendingWaybillGroup): ButtonItem[] =>
    buildActionColumnItems([
      {
        title: '生成对账单',
        icon: PlusOutlined,
        permission: 'finance:recon-wb:gen-recon',
        onClick: () => openCreate(row.customerId)
      },
      {
        title: '去台账',
        icon: EyeOutlined,
        onClick: () => gotoLedger(row.customerId)
      }
    ]);

  const reconActions = (row: ReconListItem): ButtonItem[] => {
    const visible: ButtonDropdownItem[] = [
      {
        title: '详情',
        icon: EyeOutlined,
        onClick: () => openDetail(row.id)
      }
    ];
    if (activeTab.value === 'dirty') {
      visible.push(
        {
          title: '重新核对',
          icon: SyncOutlined,
          permission: 'finance:recon-wb:recheck',
          onClick: () => recheck(row)
        },
        {
          title: '回灌重算',
          icon: CheckOutlined,
          permission: 'finance:recon-wb:recalc',
          onClick: () => recalc(row)
        }
      );
    } else {
      visible.push({
        title: '登记回签',
        icon: FormOutlined,
        permission: 'finance:cust-recon:customer-sign',
        onClick: () => openSign(row.id)
      });
    }
    return buildActionColumnItems(visible);
  };

  const diffActions = (row: ReconDiff): ButtonItem[] =>
    buildActionColumnItems([
      {
        title: '处置',
        icon: FormOutlined,
        permission: 'finance:recon-wb:raise-diff',
        onClick: () => openResolve(row)
      }
    ]);

  const openCreate = (customerId: number) => {
    createCustomerId.value = customerId;
    createVisible.value = true;
  };

  const onCreated = (reconId?: number) => {
    reloadAll();
    if (reconId) openDetail(reconId);
  };

  const openDetail = (reconId?: number) => {
    if (!reconId) return;
    detailId.value = reconId;
    detailVisible.value = true;
  };

  const openSign = (reconId: number) => {
    signId.value = reconId;
    signVisible.value = true;
  };

  const openResolve = (diff: ReconDiff) => {
    resolveDiff.value = diff;
    resolveVisible.value = true;
  };

  const gotoLedger = (customerId: number) => {
    router.push({ path: '/finance/customer-recon', query: { customerId } });
  };

  const run = async (
    action: () => Promise<unknown>,
    texts: { loading: string; success: string; fail: string }
  ) => {
    const l = EleMessage.loading({ message: texts.loading, plain: true });
    try {
      await action();
      l.close();
      EleMessage.success({ message: texts.success, plain: true });
      await reloadAll();
    } catch (e: unknown) {
      l.close();
      const msg = (e as { message?: string }).message || texts.fail;
      EleMessage.error({ message: msg, plain: true });
    }
  };

  const recheck = async (row: ReconListItem) => {
    const l = EleMessage.loading({
      message: '正在重新核对，请稍候…',
      plain: true
    });
    try {
      const report = await checkRecon(row.id);
      l.close();
      const open = report?.diffs?.length ?? 0;
      if (open) {
        EleMessage.warning({
          message: `核对完成，发现 ${open} 条差异，请在差异待办里处置`,
          plain: true
        });
      } else {
        EleMessage.success({ message: '核对完成，没有发现差异', plain: true });
      }
      await reloadAll();
    } catch (e: unknown) {
      l.close();
      const msg = (e as { message?: string }).message || '核对失败，请稍后重试';
      EleMessage.error({ message: msg, plain: true });
    }
  };

  const recalc = async (row: ReconListItem) => {
    try {
      await ElMessageBox.confirm(
        `将按计费引擎的最新结果刷新对账单「${row.docNo}」的脏行金额，人工调整会保留。`,
        '回灌重算',
        { type: 'warning', confirmButtonText: '重算', cancelButtonText: '取消' }
      );
    } catch {
      return;
    }
    await run(() => recalcRecon(row.id), {
      loading: '正在回灌重算，请稍候…',
      success: '已按最新计费结果刷新',
      fail: '重算失败，请稍后重试'
    });
  };

  onMounted(async () => {
    await reloadAll();
    try {
      customers.value = (await selectCustomers()) || [];
    } catch {
      // 客户下拉只服务建单弹窗，拉不到不影响工作台
    }
  });
</script>

<style lang="scss" scoped>
  @use '../_shared/ui.scss';

  .tab-badge {
    margin-left: 2px;
    vertical-align: middle;
  }

  .tab-toolbar {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 10px;
  }

  .toolbar-tip {
    margin-left: auto;
    color: var(--el-text-color-secondary);
    font-size: 12px;
  }

  .num {
    font-variant-numeric: tabular-nums;
  }

  .warn {
    color: var(--el-color-warning);
  }

  .danger {
    color: var(--el-color-danger);
  }

  .muted {
    color: var(--el-text-color-secondary);
  }

  .empty-tip {
    padding: 28px 0;
    color: var(--el-text-color-secondary);
    text-align: center;
  }
</style>
