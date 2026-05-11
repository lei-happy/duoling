<template>
  <ele-page>
    <carrier-search @search="(where) => reload(where, 1)" />
    <ele-card :body-style="{ paddingTop: '8px' }">
      <ele-pro-table
        ref="tableRef"
        row-key="id"
        :columns="columns"
        :datasource="datasource"
        :show-overflow-tooltip="true"
        :highlight-current-row="true"
        :default-sort="{ prop: 'createdAt', order: 'descending' }"
        cache-key="PartnerCarrierTable"
      >
        <template #toolbar>
          <btn-items
            :items="[
              { preset: 'add', title: '新增承运商', onClick: () => openEdit() }
            ]"
          />
        </template>
        <template #carrierType="{ row }">
          <el-tag
            v-if="row.carrierType === 0"
            size="small"
            :disable-transitions="true"
          >
            公司车队
          </el-tag>
          <el-tag
            v-else-if="row.carrierType === 1"
            type="success"
            size="small"
            :disable-transitions="true"
          >
            个体/小车队
          </el-tag>
          <el-tag v-else type="info" size="small" :disable-transitions="true">
            其他
          </el-tag>
        </template>
        <template #defaultSettlement="{ row }">
          <span v-if="row.defaultSettlementType != null">
            {{ SETTLEMENT_TYPE_TEXT[row.defaultSettlementType] }}
            <small v-if="row.defaultSettlementLabel" style="color: #999">
              ({{ row.defaultSettlementLabel }})
            </small>
          </span>
          <span v-else style="color: #999">未设置</span>
        </template>
        <template #inviteStatus="{ row }">
          <el-tag
            :type="inviteStatusTagType(row.inviteStatus)"
            size="small"
            :disable-transitions="true"
          >
            {{ INVITE_STATUS_TEXT[row.inviteStatus] || '未邀请' }}
          </el-tag>
          <el-tooltip
            v-if="row.linkedTenantCode"
            :content="`已与租户 ${row.linkedTenantCode} 建立互联`"
          >
            <el-icon style="margin-left: 4px; color: #67c23a">
              <CircleCheck />
            </el-icon>
          </el-tooltip>
        </template>
        <template #status="{ row }">
          <el-tag
            v-if="row.status === 1"
            type="success"
            size="small"
            :disable-transitions="true"
          >
            正常
          </el-tag>
          <el-tag
            v-else-if="row.status === 0"
            type="info"
            size="small"
            :disable-transitions="true"
          >
            停用
          </el-tag>
          <el-tag
            v-else-if="row.status === 2"
            type="danger"
            size="small"
            :disable-transitions="true"
          >
            黑名单
          </el-tag>
        </template>
        <template #action="{ row }">
          <div class="partner-carrier-actions">
            <btn-items
              divider
              type="link"
              :wrap="false"
              :items="rowActions(row)"
            />
          </div>
        </template>
      </ele-pro-table>
    </ele-card>

    <carrier-edit
      v-model:visible="editVisible"
      :data="editData"
      @done="reload"
    />
    <carrier-invite-dialog
      v-model:visible="inviteVisible"
      :data="inviteData"
      @done="reload"
    />
    <carrier-invitation-history
      v-model:visible="historyVisible"
      :data="historyData"
    />
  </ele-page>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import { ElMessageBox } from 'element-plus';
  import { CircleCheck, Promotion, RefreshLeft } from '@element-plus/icons-vue';
  import { EleMessage } from 'ele-admin-plus';
  import type {
    ButtonDropdownItem,
    ButtonItem
  } from 'ele-admin-plus/es/ele-buttons/types';
  import type { EleProTable } from 'ele-admin-plus';
  import type {
    DatasourceFunction,
    Columns
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import CarrierSearch from './components/carrier-search.vue';
  import CarrierEdit from './components/carrier-edit.vue';
  import CarrierInviteDialog from './components/carrier-invite-dialog.vue';
  import CarrierInvitationHistory from './components/carrier-invitation-history.vue';
  import {
    pageCarriers,
    removeCarrier,
    revokeCarrierInvite
  } from '@/api/partner/carrier';
  import {
    INVITE_STATUS_TEXT,
    SETTLEMENT_TYPE_TEXT,
    type CarrierListItem,
    type CarrierParam
  } from '@/api/partner/carrier/model';
  import { formatDateTime } from '@/utils/date-util';
  import { DeleteOutlined } from '@/components/icons';

  defineOptions({ name: 'PartnerCarrier' });

  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);
  const editVisible = ref(false);
  const editData = ref<CarrierListItem | null>(null);
  const inviteVisible = ref(false);
  const inviteData = ref<CarrierListItem | null>(null);
  const historyVisible = ref(false);
  const historyData = ref<CarrierListItem | null>(null);

  const columns = ref<Columns>([
    { prop: 'carrierName', label: '承运商', minWidth: 200 },
    { prop: 'carrierCode', label: '编码', minWidth: 140 },
    {
      prop: 'carrierType',
      label: '类型',
      width: 110,
      align: 'center',
      slot: 'carrierType'
    },
    { prop: 'contactPerson', label: '联系人', minWidth: 100 },
    { prop: 'contactPhone', label: '联系电话', minWidth: 120 },
    {
      prop: 'defaultSettlement',
      label: '默认结算',
      minWidth: 160,
      slot: 'defaultSettlement'
    },
    {
      prop: 'inviteStatus',
      label: '互联状态',
      width: 130,
      align: 'center',
      slot: 'inviteStatus'
    },
    {
      prop: 'status',
      label: '状态',
      width: 90,
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
      minWidth: 230,
      align: 'center',
      slot: 'action',
      hideInPrint: true,
      hideInExport: true,
      fixed: 'right'
    }
  ]);

  const datasource: DatasourceFunction = ({ pages, where, orders }) => {
    return pageCarriers({ ...where, ...orders, ...pages });
  };

  const reload = (where?: CarrierParam, page?: number) => {
    tableRef.value?.reload?.({ where, page });
  };

  const openEdit = (row?: CarrierListItem) => {
    editData.value = row ?? null;
    editVisible.value = true;
  };

  const openInvite = (row: CarrierListItem) => {
    inviteData.value = row;
    inviteVisible.value = true;
  };

  const openHistory = (row: CarrierListItem) => {
    historyData.value = row;
    historyVisible.value = true;
  };

  const remove = (row: CarrierListItem) => {
    ElMessageBox.confirm(
      `确定要删除承运商"${row.carrierName}"吗？已激活互联的承运商需先解除互联。`,
      '系统提示',
      { type: 'warning', draggable: true }
    )
      .then(async () => {
        const loading = EleMessage.loading({
          message: '请求中..',
          plain: true
        });
        try {
          await removeCarrier(row.id);
          loading.close();
          EleMessage.success({ message: '删除成功', plain: true });
          reload();
        } catch (e: any) {
          loading.close();
          EleMessage.error({ message: e.message, plain: true });
        }
      })
      .catch(() => {});
  };

  const revoke = (row: CarrierListItem) => {
    ElMessageBox.confirm(
      `确定要撤回承运商"${row.carrierName}"的进行中邀请吗？`,
      '系统提示',
      { type: 'warning', draggable: true }
    )
      .then(async () => {
        try {
          await revokeCarrierInvite(row.id);
          EleMessage.success({ message: '已撤回邀请', plain: true });
          reload();
        } catch (e: any) {
          EleMessage.error({ message: e.message, plain: true });
        }
      })
      .catch(() => {});
  };

  function rowActions(row: CarrierListItem): ButtonItem[] {
    const items: ButtonItem[] = [
      { preset: 'edit', onClick: () => openEdit(row) }
    ];
    // 互联：未邀请 / A 已撤回 / B 已拒绝 / 失败 / 解绑 → 邀请（文字链 + 图标，勿用 type 以免变成实心按钮）
    if ([0, 3, 5, 6, 8, 9].includes(row.inviteStatus)) {
      items.push({
        title: '邀请激活',
        icon: Promotion,
        onClick: () => openInvite(row)
      });
    }
    if (row.inviteStatus === 1) {
      items.push({
        title: '撤回邀请',
        icon: RefreshLeft,
        onClick: () => revoke(row)
      });
    }
    const dropdownItems: ButtonDropdownItem[] = [
      {
        title: '邀请历史',
        onClick: () => openHistory(row)
      },
      {
        title: '删除',
        icon: DeleteOutlined,
        divided: true,
        danger: true,
        disabled: !!row.linkedTenantCode,
        onClick: () => remove(row)
      }
    ];
    items.push({
      preset: 'more',
      dropdownItems
    });
    return items;
  }

  function inviteStatusTagType(s: number): any {
    if (s === 2) return 'success';
    if (s === 1 || s === 4 || s === 7) return 'warning';
    if (s === 0) return 'info';
    return 'danger';
  }
</script>

<style scoped>
  .partner-carrier-actions {
    text-align: center;
    white-space: nowrap;
  }
</style>
