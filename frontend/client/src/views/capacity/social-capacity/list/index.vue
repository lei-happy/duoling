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
      <ele-pro-table
        ref="tableRef"
        row-key="id"
        :columns="columns"
        :datasource="datasource"
        :show-overflow-tooltip="true"
        :highlight-current-row="true"
        :default-sort="{ prop: 'createdAt', order: 'descending' }"
        cache-key="SocialCapacityTable"
      >
        <template #toolbar>
          <btn-items
            :items="[
              {
                preset: 'add',
                title: '新增运力',
                onClick: () => openEdit()
              }
            ]"
          />
        </template>
        <template #plateNumber="{ row }">
          <plate-number-tag
            :text="row.plateNumber"
            :category="row.plateCategory"
          />
        </template>
        <template #vehicleType="{ row }">
          <dict-data
            type="text"
            :code="dictCodeVehicleType"
            :model-value="row.vehicleTypeLabel"
          />
        </template>
        <template #defaultAccount="{ row }">
          <span v-if="row.defaultAccount">
            {{ accountTypeLabel(row.defaultAccount.accountType) }} / {{ row.defaultAccount.accountName }}
          </span>
          <span v-else>—</span>
        </template>
        <template #ratingLevel="{ row }">
          <el-tag v-if="row.ratingLevel" size="small">{{ ratingLabel(row.ratingLevel) }}</el-tag>
          <span v-else>—</span>
        </template>
        <template #approvalStatus="{ row }">
          <el-tag size="small" :type="approvalTagType(row.approvalStatus)">
            {{ approvalLabel(row.approvalStatus) }}
          </el-tag>
        </template>
        <template #status="{ row }">
          <el-tag size="small" :type="statusTagType(row.status)">
            {{ statusLabel(row.status) }}
          </el-tag>
        </template>
        <template #action="{ row }">
          <btn-items divider type="link" :items="actionItems(row)" />
        </template>
      </ele-pro-table>
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
  </ele-page>
</template>

<script lang="ts" setup>
  import { onActivated, onMounted, ref } from 'vue';
  import { ElMessageBox } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import { DeleteOutlined } from '@/components/icons';
  import type { EleProTable } from 'ele-admin-plus';
  import type {
    DatasourceFunction,
    Columns
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import SocialCapacitySearch from './components/social-capacity-search.vue';
  import SocialCapacityStatsCards from './components/social-capacity-stats-cards.vue';
  import type {
    ApprovalCardKey,
    StatusCardKey
  } from './components/social-capacity-stats-cards.vue';
  import SocialCapacityEdit from './components/social-capacity-edit.vue';
  import SocialCapacityDetail from './components/social-capacity-detail.vue';
  import SocialCapacityStatus from './components/social-capacity-status.vue';
  import PlateNumberTag from '@/components/PlateNumberTag/index.vue';
  import DictData from '@/components/DictData/index.vue';
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
  import { DICT_CODE_VEHICLE_TYPE } from '@/constants/dict-codes';
  import { formatDateTime } from '@/utils/date-util';

  defineOptions({ name: 'CapacitySocial' });

  const dictCodeVehicleType = DICT_CODE_VEHICLE_TYPE;

  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);

  const editVisible = ref(false);
  const editData = ref<SocialCapacityListItem | null>(null);

  const detailVisible = ref(false);
  const detailId = ref<number | undefined>(undefined);

  const statusVisible = ref(false);
  const statusRow = ref<SocialCapacityListItem | null>(null);

  const searchWhere = ref<SocialCapacityParam>({});
  const stats = ref<SocialCapacityListStats | null>(null);
  const activeApprovalKey = ref<ApprovalCardKey | null>(null);
  const activeStatusKey = ref<StatusCardKey | null>(null);

  const APPROVAL_PENDING_PROCESS = '0,1,3';

  const APPROVAL_KEY_TO_FILTER = (
    key: ApprovalCardKey
  ): Pick<SocialCapacityParam, 'approvalStatus' | 'approvalStatusIn'> => {
    if (key === 'pending_process') {
      return { approvalStatus: undefined, approvalStatusIn: APPROVAL_PENDING_PROCESS };
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

  const approvalLabel = (s?: number) =>
    s === 0
      ? '草稿'
      : s === 1
        ? '待审核'
        : s === 2
          ? '已通过'
          : s === 3
            ? '已驳回'
            : '—';
  const approvalTagType = (
    s?: number
  ): 'info' | 'primary' | 'success' | 'danger' =>
    s === 1 ? 'primary' : s === 2 ? 'success' : s === 3 ? 'danger' : 'info';
  const statusLabel = (s?: number) =>
    s === 0
      ? '未生效'
      : s === 1
        ? '正常'
        : s === 2
          ? '停用'
          : s === 3
            ? '黑名单'
            : '—';
  const statusTagType = (
    s?: number
  ): 'info' | 'success' | 'warning' | 'danger' =>
    s === 1 ? 'success' : s === 2 ? 'warning' : s === 3 ? 'danger' : 'info';
  const ratingLabel = (level?: number) =>
    level === 1
      ? 'A'
      : level === 2
        ? 'B'
        : level === 3
          ? 'C'
          : level === 4
            ? 'D'
            : '—';
  const accountTypeLabel = (t?: number) =>
    t === 1
      ? '银行卡'
      : t === 2
        ? '支付宝'
        : t === 3
          ? '微信'
          : t === 4
            ? '其他'
            : '—';

  const columns = ref<Columns>([
    { prop: 'socialCode', label: '编号', minWidth: 130 },
    { prop: 'driverName', label: '姓名', minWidth: 90 },
    { prop: 'driverPhone', label: '手机号', minWidth: 120 },
    {
      prop: 'plateNumber',
      label: '车牌号',
      minWidth: 130,
      slot: 'plateNumber'
    },
    {
      prop: 'approvalStatus',
      label: '审核状态',
      width: 100,
      align: 'center',
      slot: 'approvalStatus'
    },
    {
      prop: 'status',
      label: '运力状态',
      width: 100,
      align: 'center',
      slot: 'status'
    },
    {
      prop: 'vehicleTypeLabel',
      label: '车辆类型',
      minWidth: 100,
      slot: 'vehicleType'
    },
    {
      prop: 'defaultAccount',
      label: '默认结算',
      minWidth: 160,
      slot: 'defaultAccount'
    },
    {
      prop: 'ratingLevel',
      label: '评级',
      width: 80,
      align: 'center',
      slot: 'ratingLevel'
    },

    {
      prop: 'createdAt',
      label: '创建时间',
      sortable: 'custom',
      width: 170,
      align: 'center',
      formatter: (row) => formatDateTime(row.createdAt)
    },
    {
      columnKey: 'action',
      label: '操作',
      width: 130,
      align: 'center',
      slot: 'action',
      hideInPrint: true,
      hideInExport: true,
      fixed: 'right'
    }
  ]);

  const buildStatsParams = (): SocialCapacityParam => ({ ...searchWhere.value });

  const loadStats = async () => {
    try {
      stats.value = (await socialCapacityListStats(buildStatsParams())) ?? null;
    } catch (e: unknown) {
      const msg = (e as { message?: string }).message;
      if (msg) EleMessage.error({ message: msg, plain: true });
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

  const normalizeSortOrders = (
    orders: Record<string, string | undefined> | undefined
  ) => {
    if (!orders?.sort && !orders?.order) return {};
    const sort = orders.sort;
    let order = orders.order;
    if (typeof order === 'string') {
      const lo = order.toLowerCase();
      if (lo === 'descending') order = 'desc';
      else if (lo === 'ascending') order = 'asc';
    }
    const out: Record<string, string> = {};
    if (sort) out.sort = sort;
    if (order) out.order = order;
    return out;
  };

  const datasource: DatasourceFunction = async ({ pages, where, orders }) => {
    const res = await pageSocialCapacities({
      ...searchWhere.value,
      ...where,
      ...normalizeSortOrders(orders as Record<string, string | undefined>),
      ...pages
    });
    const raw = res as { list?: SocialCapacityListItem[]; count?: number; total?: number };
    return {
      list: raw?.list ?? [],
      count: raw?.count ?? raw?.total ?? 0
    };
  };

  const reload = (where?: SocialCapacityParam, page?: number) => {
    if (where) {
      searchWhere.value = {
        ...where,
        approvalStatus: searchWhere.value.approvalStatus,
        approvalStatusIn: searchWhere.value.approvalStatusIn,
        status: searchWhere.value.status
      };
    }
    tableRef.value?.reload?.({ where: searchWhere.value, page });
    loadStats();
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
    loadStats();
    tableRef.value?.reload?.({ where: searchWhere.value });
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

  const openStatus = (row: SocialCapacityListItem) => {
    if (row.approvalStatus !== 2) {
      EleMessage.warning({ message: '审核通过后才可调整启用状态', plain: true });
      return;
    }
    statusRow.value = row;
    statusVisible.value = true;
  };

  const submit = async (row: SocialCapacityListItem) => {
    if (!row.id) return;
    try {
      await ElMessageBox.confirm('提交后将进入审核流程，确认提交？', '系统提示', {
        type: 'warning'
      });
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

  const actionItems = (row: SocialCapacityListItem) => {
    const dropdownItems: any[] = [];

    const canEdit =
      row.approvalStatus === 0 ||
      row.approvalStatus === 3 ||
      row.approvalStatus === 2;
    if (canEdit) {
      dropdownItems.push({
        preset: 'edit',
        onClick: () => openEdit(row)
      });
    }

    if (row.approvalStatus === 0 || row.approvalStatus === 3) {
      dropdownItems.push({
        title: '提交审核',
        onClick: () => submit(row)
      });
    }
    if (row.approvalStatus === 1) {
      dropdownItems.push({
        title: '撤回审核',
        onClick: () => withdraw(row)
      });
    }
    if (row.approvalStatus === 2) {
      dropdownItems.push({
        title: '状态变更申请',
        onClick: () => openStatus(row)
      });
    }

    const canDelete =
      row.approvalStatus === 0 ||
      row.approvalStatus === 3 ||
      row.approvalStatus === 1 ||
      (row.approvalStatus === 2 && (row.status === 2 || row.status === 3));
    if (canDelete) {
      dropdownItems.push({
        title: '删除',
        divided: true,
        danger: true,
        icon: DeleteOutlined,
        onClick: () => remove(row)
      });
    }

    return [
      { title: '查看', onClick: () => openDetail(row) },
      {
        preset: 'more',
        dropdownItems
      }
    ];
  };
</script>

<style scoped>
  .sc-page__cards {
    margin-bottom: 12px;
  }
</style>
