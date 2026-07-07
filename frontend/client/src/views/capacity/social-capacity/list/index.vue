<template>
  <ele-page>
    <social-capacity-search @search="onSearch" @reset="onFilterReset" />
    <social-capacity-stats-cards
      class="sc-page__cards"
      :stats="stats"
      :active-approval-key="activeApprovalKey"
      :active-status-key="activeStatusKey"
      @select-approval="onSelectApproval"
      @select-status="onSelectStatus"
    />
    <ele-card :body-style="{ paddingTop: '8px' }">
      <div class="sc-list-toolbar">
        <btn-items
          :items="[
            {
              preset: 'add',
              title: '新增运力',
              onClick: () => openEdit()
            }
          ]"
        />
      </div>

      <div v-loading="loading" class="sc-list-body">
        <div v-if="list.length" class="sc-card-grid">
          <social-capacity-card
            v-for="item in list"
            :key="item.id"
            :item="item"
            :menu-items="buildCardMenuItems(item)"
            @action="handleCardAction"
          />
        </div>
        <el-empty v-else-if="!loading" description="暂无社会运力数据" />
      </div>

      <div v-if="total > 0" class="sc-list-pagination">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[18, 36, 54]"
          layout="total, sizes, prev, pager, next, jumper"
          background
          @current-change="loadData"
          @size-change="onPageSizeChange"
        />
      </div>
    </ele-card>

    <social-capacity-edit
      v-model:visible="editVisible"
      :data="editData"
      @done="onMutationDone"
    />
    <social-capacity-detail
      v-model:visible="detailVisible"
      :social-capacity-id="detailId"
    />
    <social-capacity-status
      v-model:visible="statusVisible"
      :row="statusRow"
      @done="onMutationDone"
    />
    <social-capacity-fund-account
      v-model:visible="fundVisible"
      :capacity="fundCapacity"
    />
  </ele-page>
</template>

<script lang="ts" setup>
  import { onActivated, onMounted, ref } from 'vue';
  import { ElMessageBox } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import SocialCapacitySearch from './components/social-capacity-search.vue';
  import SocialCapacityStatsCards from './components/social-capacity-stats-cards.vue';
  import type {
    ApprovalCardKey,
    StatusCardKey
  } from './components/social-capacity-stats-cards.vue';
  import SocialCapacityEdit from './components/social-capacity-edit.vue';
  import SocialCapacityDetail from './components/social-capacity-detail.vue';
  import SocialCapacityStatus from './components/social-capacity-status.vue';
  import SocialCapacityCard from './components/social-capacity-card.vue';
  import type { SocialCapacityCardMenuItem } from './components/social-capacity-card.vue';
  import SocialCapacityFundAccount from './components/social-capacity-fund-account.vue';
  import {
    pageSocialCapacities,
    removeSocialCapacity,
    socialCapacityListStats,
    submitSocialCapacity,
    withdrawSocialCapacity
  } from '@/api/capacity/social-capacity/list';
  import type {
    SocialCapacityListItem,
    SocialCapacityListStats,
    SocialCapacityParam
  } from '@/api/capacity/social-capacity/list/model';
  import { usePermission } from '@/utils/use-permission';

  defineOptions({ name: 'CapacitySocial' });

  const { hasPermission } = usePermission();

  const editVisible = ref(false);
  const editData = ref<SocialCapacityListItem | null>(null);

  const detailVisible = ref(false);
  const detailId = ref<number | undefined>(undefined);

  const statusVisible = ref(false);
  const statusRow = ref<SocialCapacityListItem | null>(null);

  const fundVisible = ref(false);
  const fundCapacity = ref<SocialCapacityListItem | null>(null);

  const searchWhere = ref<SocialCapacityParam>({});
  const stats = ref<SocialCapacityListStats | null>(null);
  const activeApprovalKey = ref<ApprovalCardKey | null>(null);
  const activeStatusKey = ref<StatusCardKey | null>(null);

  const loading = ref(false);
  const list = ref<SocialCapacityListItem[]>([]);
  const total = ref(0);
  const page = ref(1);
  const pageSize = ref(18);

  const APPROVAL_PENDING_PROCESS = '0,1,3';

  const APPROVAL_KEY_TO_FILTER = (
    key: ApprovalCardKey
  ): Pick<SocialCapacityParam, 'approvalStatus' | 'approvalStatusIn'> => {
    if (key === 'pending_process') {
      return {
        approvalStatus: undefined,
        approvalStatusIn: APPROVAL_PENDING_PROCESS
      };
    }
    if (key === 'draft') {
      return { approvalStatus: 0, approvalStatusIn: undefined };
    }
    if (key === 'pending') {
      return { approvalStatus: 1, approvalStatusIn: undefined };
    }
    if (key === 'rejected') {
      return { approvalStatus: 3, approvalStatusIn: undefined };
    }
    if (key === 'approved') {
      return { approvalStatus: 2, approvalStatusIn: undefined };
    }
    return { approvalStatus: undefined, approvalStatusIn: undefined };
  };

  const STATUS_KEY_TO_VALUE: Record<StatusCardKey, number> = {
    inactive: 0,
    active: 1,
    disabled: 2,
    blacklist: 3
  };

  const clearApprovalFilter = (): Pick<
    SocialCapacityParam,
    'approvalStatus' | 'approvalStatusIn'
  > => ({
    approvalStatus: undefined,
    approvalStatusIn: undefined
  });

  const buildStatsParams = (): SocialCapacityParam => ({
    ...searchWhere.value
  });

  const loadStats = async () => {
    try {
      stats.value = (await socialCapacityListStats(buildStatsParams())) ?? null;
    } catch (e: unknown) {
      const msg = (e as { message?: string }).message;
      if (msg) EleMessage.error({ message: msg, plain: true });
    }
  };

  const loadData = async () => {
    loading.value = true;
    try {
      const res = await pageSocialCapacities({
        ...searchWhere.value,
        page: page.value,
        limit: pageSize.value,
        sort: 'createdAt',
        order: 'desc'
      });
      const raw = res as {
        list?: SocialCapacityListItem[];
        count?: number;
        total?: number;
      };
      list.value = raw?.list ?? [];
      total.value = raw?.count ?? raw?.total ?? 0;
    } catch (e: unknown) {
      list.value = [];
      total.value = 0;
      const msg = (e as { message?: string }).message;
      if (msg) EleMessage.error({ message: msg, plain: true });
    } finally {
      loading.value = false;
    }
  };

  const syncCardKeysFromWhere = () => {
    const { approvalStatus, approvalStatusIn } = searchWhere.value;
    if (approvalStatusIn === APPROVAL_PENDING_PROCESS) {
      activeApprovalKey.value = 'pending_process';
    } else if (approvalStatus === 0) {
      activeApprovalKey.value = 'draft';
    } else if (approvalStatus === 1) {
      activeApprovalKey.value = 'pending';
    } else if (approvalStatus === 3) {
      activeApprovalKey.value = 'rejected';
    } else if (approvalStatus === 2) {
      activeApprovalKey.value = 'approved';
    } else {
      activeApprovalKey.value = null;
    }

    const statusVal = searchWhere.value.status;
    activeStatusKey.value =
      statusVal === 0
        ? 'inactive'
        : statusVal === 1
          ? 'active'
          : statusVal === 2
            ? 'disabled'
            : statusVal === 3
              ? 'blacklist'
              : null;
  };

  const reload = (where?: SocialCapacityParam, pageNum?: number) => {
    if (where) {
      searchWhere.value = {
        ...where,
        approvalStatus: searchWhere.value.approvalStatus,
        approvalStatusIn: searchWhere.value.approvalStatusIn,
        status: searchWhere.value.status
      };
    }
    if (pageNum) {
      page.value = pageNum;
    }
    void loadData();
    void loadStats();
  };

  const onPageSizeChange = () => {
    page.value = 1;
    void loadData();
  };

  const onSearch = (where?: SocialCapacityParam) => {
    searchWhere.value = {
      ...(where ?? {}),
      approvalStatus: searchWhere.value.approvalStatus,
      approvalStatusIn: searchWhere.value.approvalStatusIn,
      status: searchWhere.value.status
    };
    reload(undefined, 1);
  };

  const onFilterReset = () => {
    activeApprovalKey.value = null;
    activeStatusKey.value = null;
    searchWhere.value = {
      keyword: '',
      source: undefined,
      approvalStatus: undefined,
      approvalStatusIn: undefined,
      status: undefined
    };
    reload(undefined, 1);
  };

  const onSelectApproval = (key: ApprovalCardKey) => {
    const toggleOff = activeApprovalKey.value === key;
    activeApprovalKey.value = toggleOff ? null : key;
    searchWhere.value = {
      ...searchWhere.value,
      ...(toggleOff ? clearApprovalFilter() : APPROVAL_KEY_TO_FILTER(key))
    };
    reload(undefined, 1);
  };

  const onSelectStatus = (key: StatusCardKey) => {
    const toggleOff = activeStatusKey.value === key;
    activeStatusKey.value = toggleOff ? null : key;
    searchWhere.value = {
      ...searchWhere.value,
      status: toggleOff ? undefined : STATUS_KEY_TO_VALUE[key]
    };
    reload(undefined, 1);
  };

  const onMutationDone = () => {
    reload();
  };

  const refreshPage = () => {
    syncCardKeysFromWhere();
    void loadStats();
    void loadData();
  };

  onMounted(refreshPage);
  onActivated(refreshPage);

  const openEdit = (row?: SocialCapacityListItem) => {
    editData.value = row ?? null;
    editVisible.value = true;
  };

  const openDetail = (row: SocialCapacityListItem) => {
    if (!row.id) return;
    detailId.value = row.id;
    detailVisible.value = true;
  };

  const openFund = (row: SocialCapacityListItem) => {
    if (!row.id) return;
    fundCapacity.value = row;
    fundVisible.value = true;
  };

  const openStatus = (row: SocialCapacityListItem) => {
    if (row.approvalStatus !== 2) {
      EleMessage.warning({
        message: '审核通过后才可调整启用状态',
        plain: true
      });
      return;
    }
    statusRow.value = row;
    statusVisible.value = true;
  };

  const submit = async (row: SocialCapacityListItem) => {
    if (!row.id) return;
    try {
      await ElMessageBox.confirm(
        '提交后将进入审核流程，确认提交？',
        '系统提示',
        {
          type: 'warning'
        }
      );
    } catch {
      return;
    }
    try {
      await submitSocialCapacity(row.id);
      EleMessage.success({ message: '已提交审核', plain: true });
      reload();
    } catch (e: any) {
      EleMessage.error({ message: e?.message ?? '提交失败', plain: true });
    }
  };

  const withdraw = async (row: SocialCapacityListItem) => {
    if (!row.id) return;
    try {
      await withdrawSocialCapacity(row.id);
      EleMessage.success({ message: '已撤回审核', plain: true });
      reload();
    } catch (e: any) {
      EleMessage.error({ message: e?.message ?? '撤回失败', plain: true });
    }
  };

  const remove = async (row: SocialCapacityListItem) => {
    try {
      await ElMessageBox.confirm(
        `确定要删除社会运力「${row.socialCode}」吗？`,
        '系统提示',
        { type: 'warning', draggable: true }
      );
    } catch {
      return;
    }
    try {
      await removeSocialCapacity(row.id!);
      EleMessage.success({ message: '删除成功', plain: true });
      reload();
    } catch (e: any) {
      EleMessage.error({ message: e?.message ?? '删除失败', plain: true });
    }
  };

  const buildCardMenuItems = (
    row: SocialCapacityListItem
  ): SocialCapacityCardMenuItem[] => {
    const items: SocialCapacityCardMenuItem[] = [
      { key: 'view', title: '查看' }
    ];

    const canEdit =
      row.approvalStatus === 0 ||
      row.approvalStatus === 3 ||
      row.approvalStatus === 2;
    if (canEdit) {
      items.push({ key: 'edit', title: '编辑' });
    }

    if (row.approvalStatus === 0 || row.approvalStatus === 3) {
      items.push({ key: 'submit', title: '提交审核' });
    }
    if (row.approvalStatus === 1) {
      items.push({ key: 'withdraw', title: '撤回审核' });
    }
    if (row.approvalStatus === 2) {
      items.push({ key: 'status', title: '状态变更申请' });
    }

    if (
      row.approvalStatus === 2 &&
      hasPermission('capacity:social_capacity:list:fund-account')
    ) {
      items.push({ key: 'fund', title: '资金账户' });
    }

    const canDelete =
      row.approvalStatus === 0 ||
      row.approvalStatus === 3 ||
      row.approvalStatus === 1 ||
      (row.approvalStatus === 2 && (row.status === 2 || row.status === 3));
    if (canDelete) {
      items.push({
        key: 'delete',
        title: '删除',
        danger: true,
        divided: true
      });
    }

    return items;
  };

  const handleCardAction = (key: string, row: SocialCapacityListItem) => {
    switch (key) {
      case 'view':
        openDetail(row);
        break;
      case 'edit':
        openEdit(row);
        break;
      case 'submit':
        void submit(row);
        break;
      case 'withdraw':
        void withdraw(row);
        break;
      case 'status':
        openStatus(row);
        break;
      case 'fund':
        openFund(row);
        break;
      case 'delete':
        void remove(row);
        break;
    }
  };
</script>

<style scoped>
  .sc-page__cards {
    margin-bottom: 12px;
  }

  .sc-list-toolbar {
    display: flex;
    justify-content: flex-start;
    margin-bottom: 12px;
  }

  .sc-list-body {
    min-height: 200px;
  }

  .sc-card-grid {
    display: grid;
    grid-template-columns: repeat(6, minmax(0, 1fr));
    gap: 12px;
  }

  @media (max-width: 1600px) {
    .sc-card-grid {
      grid-template-columns: repeat(5, minmax(0, 1fr));
    }
  }

  @media (max-width: 1280px) {
    .sc-card-grid {
      grid-template-columns: repeat(4, minmax(0, 1fr));
    }
  }

  @media (max-width: 992px) {
    .sc-card-grid {
      grid-template-columns: repeat(3, minmax(0, 1fr));
    }
  }

  @media (max-width: 768px) {
    .sc-card-grid {
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }
  }

  .sc-list-pagination {
    display: flex;
    justify-content: flex-end;
    margin-top: 16px;
    padding-top: 8px;
  }
</style>
