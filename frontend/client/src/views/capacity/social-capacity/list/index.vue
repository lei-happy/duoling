<template>
  <ele-page>
    <social-capacity-search @search="(where) => reload(where, 1)" />
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
      @done="reload"
    />
    <social-capacity-detail
      v-model:visible="detailVisible"
      :social-capacity-id="detailId"
    />
    <social-capacity-status
      v-model:visible="statusVisible"
      :row="statusRow"
      @done="reload"
    />
  </ele-page>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import { ElMessageBox } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import { DeleteOutlined } from '@/components/icons';
  import type { EleProTable } from 'ele-admin-plus';
  import type {
    DatasourceFunction,
    Columns
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import SocialCapacitySearch from './components/social-capacity-search.vue';
  import SocialCapacityEdit from './components/social-capacity-edit.vue';
  import SocialCapacityDetail from './components/social-capacity-detail.vue';
  import SocialCapacityStatus from './components/social-capacity-status.vue';
  import {
    pageSocialCapacities,
    removeSocialCapacity,
    submitSocialCapacity,
    withdrawSocialCapacity
  } from '@/api/capacity/social-capacity/list';
  import type {
    SocialCapacityListItem,
    SocialCapacityParam
  } from '@/api/capacity/social-capacity/list/model';
  import { formatDateTime } from '@/utils/date-util';

  defineOptions({ name: 'CapacitySocial' });

  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);

  const editVisible = ref(false);
  const editData = ref<SocialCapacityListItem | null>(null);

  const detailVisible = ref(false);
  const detailId = ref<number | undefined>(undefined);

  const statusVisible = ref(false);
  const statusRow = ref<SocialCapacityListItem | null>(null);

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
    { prop: 'plateNumber', label: '车牌号', minWidth: 110 },
    { prop: 'vehicleTypeLabel', label: '车辆类型', minWidth: 100 },
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
      prop: 'approvalStatus',
      label: '审核状态',
      width: 100,
      align: 'center',
      slot: 'approvalStatus'
    },
    {
      prop: 'status',
      label: '启用状态',
      width: 100,
      align: 'center',
      slot: 'status'
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
      width: 200,
      align: 'center',
      slot: 'action',
      hideInPrint: true,
      hideInExport: true,
      fixed: 'right'
    }
  ]);

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
    tableRef.value?.reload?.({ where, page });
  };

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
    const items: any[] = [
      { title: '查看', onClick: () => openDetail(row) }
    ];

    // 草稿 / 已驳回 → 编辑 + 提交审核 + 删除
    if (row.approvalStatus === 0 || row.approvalStatus === 3) {
      items.push({ title: '编辑', onClick: () => openEdit(row) });
      items.push({
        title: '提交审核',
        onClick: () => submit(row)
      });
    }

    // 待审核 → 撤回
    if (row.approvalStatus === 1) {
      items.push({ title: '撤回审核', onClick: () => withdraw(row) });
    }

    // 已通过 → 编辑(账户/备注) + 状态变更
    if (row.approvalStatus === 2) {
      items.push({ title: '编辑', onClick: () => openEdit(row) });
      items.push({
        title: '状态变更',
        onClick: () => openStatus(row)
      });
    }

    // 删除：草稿 / 已驳回 / 待审核 / 已停用 / 黑名单
    const canDelete =
      row.approvalStatus === 0 ||
      row.approvalStatus === 3 ||
      row.approvalStatus === 1 ||
      (row.approvalStatus === 2 &&
        (row.status === 2 || row.status === 3));
    if (canDelete) {
      items.push({
        title: '删除',
        divided: true,
        danger: true,
        icon: DeleteOutlined,
        onClick: () => remove(row)
      });
    }

    return items;
  };
</script>
