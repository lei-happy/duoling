<!-- 客户运营中心 - 共享表格组件 -->
<template>
  <ele-card :body-style="{ paddingTop: '8px' }">
    <ele-pro-table
      ref="tableRef"
      row-key="id"
      :columns="mergedColumns"
      :datasource="datasource"
      :show-overflow-tooltip="true"
      v-model:selections="selections"
      :highlight-current-row="true"
      :export-config="{ fileName: '客户数据' }"
      cache-key="CustomerTable"
    >
      <template #toolbar>
        <slot name="toolbar">
          <btn-items
            :items="toolbarItems"
          />
        </slot>
      </template>
      <template #status="{ row }">
        <el-tag
          :type="statusTagType(row.status)"
          size="small"
          :disable-transitions="true"
        >
          {{ statusText(row.status) }}
        </el-tag>
      </template>
      <template #dbInitialized="{ row }">
        <el-tag
          :type="row.dbInitialized === 1 ? 'success' : 'danger'"
          size="small"
          :disable-transitions="true"
        >
          {{ row.dbInitialized === 1 ? '已初始化' : '未初始化' }}
        </el-tag>
      </template>
      <template #sourceChannel="{ row }">
        <el-tag
          :type="channelTagType(row.sourceChannel)"
          size="small"
          :disable-transitions="true"
        >
          {{ channelText(row.sourceChannel) }}
        </el-tag>
      </template>
      <template #trialRemaining="{ row }">
        <el-tag
          :type="getTrialRemainingType(row)"
          size="small"
          :disable-transitions="true"
        >
          {{ getTrialRemainingText(row) }}
        </el-tag>
      </template>
      <template #expireTime="{ row }">
        <span :class="{ 'expire-warning': isExpireWarning(row) }">
          {{ row.expireTime || '-' }}
        </span>
      </template>
      <template #action="{ row }">
        <div class="action-wrapper">
          <btn-items
            :divider="true"
            type="link"
            :items="getPrimaryActions(row)"
          />
          <el-divider v-if="getMoreActions(row).length" direction="vertical" />
          <el-dropdown
            v-if="getMoreActions(row).length"
            trigger="hover"
            @command="(cmd: () => void) => cmd()"
          >
            <el-button type="primary" link>
              更多<el-icon class="el-icon--right"><ArrowDown /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item
                  v-for="(item, idx) in getMoreActions(row)"
                  :key="idx"
                  :command="item.onClick"
                  :class="{ 'action-danger': item.danger }"
                >
                  {{ item.title }}
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </template>
    </ele-pro-table>
  </ele-card>
</template>

<script lang="ts" setup>
  import { ref, computed } from 'vue';
  import { ElMessageBox } from 'element-plus';
  import { ArrowDown } from '@element-plus/icons-vue';
  import { EleMessage, useModal } from 'ele-admin-plus';
  import type { EleProTable } from 'ele-admin-plus';
  import type {
    DatasourceFunction,
    Columns
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import {
    pageCustomers,
    removeCustomers,
    updateCustomerStatus
  } from '@/api/customer';
  import type { Customer, CustomerParam } from '@/api/customer/model';

  export type LifecycleType = 'trial' | 'paid' | 'churned';

  const props = withDefaults(
    defineProps<{
      lifecycle: LifecycleType;
      versionCode?: string;
      expireWarning?: boolean;
      showAddButton?: boolean;
      showDeleteButton?: boolean;
    }>(),
    {
      showAddButton: false,
      showDeleteButton: false,
      expireWarning: false
    }
  );

  const emit = defineEmits<{
    (e: 'reload'): void;
  }>();

  const { openModal } = useModal();

  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);
  const selections = ref<Customer[]>([]);

  const baseColumns: Columns = [
    { prop: 'tenantCode', label: '企业编码', width: 110, align: 'center' },
    { prop: 'tenantName', label: '企业名称', minWidth: 160 },
    { prop: 'contactPerson', label: '联系人', width: 110 },
    { prop: 'contactPhone', label: '联系电话', width: 140 },
    {
      prop: 'status', label: '状态', width: 100, align: 'center',
      slot: 'status',
      formatter: (row: Customer) => statusText(row.status)
    },
    {
      prop: 'sourceChannel', label: '来源渠道', width: 110, align: 'center',
      slot: 'sourceChannel',
      formatter: (row: Customer) => channelText(row.sourceChannel)
    },
    {
      prop: 'expireTime', label: '到期时间', width: 170, align: 'center',
      slot: 'expireTime'
    },
    { prop: 'createTime', label: '创建时间', width: 170, align: 'center' },
    {
      columnKey: 'action', label: '操作', width: 200, align: 'center',
      slot: 'action', hideInPrint: true, hideInExport: true, fixed: 'right'
    }
  ];

  const mergedColumns = computed<Columns>(() => {
    const cols = [...baseColumns];
    if (props.lifecycle === 'trial') {
      const insertIdx = cols.findIndex((c) => c.prop === 'expireTime');
      cols.splice(insertIdx, 0, {
        columnKey: 'trialRemaining', label: '试用剩余', width: 110, align: 'center',
        slot: 'trialRemaining'
      });
    }
    return cols;
  });

  const toolbarItems = computed(() => {
    const items: any[] = [];
    if (props.showAddButton) {
      items.push({ preset: 'add', title: '注册企业', onClick: () => openEdit() });
    }
    if (props.showDeleteButton) {
      items.push({ preset: 'del', onClick: () => remove() });
    }
    return items;
  });

  const datasource: DatasourceFunction = ({ pages, where, orders }) => {
    const params: CustomerParam = {
      ...where,
      ...orders,
      ...pages,
      lifecycle: props.lifecycle,
      versionCode: props.versionCode,
      expireWarning: props.expireWarning || undefined
    };
    return pageCustomers(params);
  };

  const reload = (opts?: { where?: CustomerParam; page?: number }) => {
    selections.value = [];
    tableRef.value?.reload?.(opts);
  };

  const statusText = (status?: number) => {
    const map: Record<number, string> = {
      0: '停用',
      1: '正常',
      3: '已过期'
    };
    return map[status ?? -1] || '未知';
  };

  const statusTagType = (status?: number) => {
    const map: Record<number, string> = {
      0: 'danger',
      1: 'success',
      3: 'info'
    };
    return map[status ?? -1] || 'info';
  };

  const channelText = (channel?: string) => {
    const map: Record<string, string> = {
      website: '官网注册',
      console: '后台录入',
      referral: '企业推荐'
    };
    return map[channel ?? ''] || channel || '-';
  };

  const channelTagType = (channel?: string) => {
    const map: Record<string, string> = {
      website: '',
      console: 'info',
      referral: 'success'
    };
    return map[channel ?? ''] || 'info';
  };

  const isExpireWarning = (row: Customer) => {
    if (!row.expireTime) return false;
    const expire = new Date(row.expireTime).getTime();
    const now = Date.now();
    const days30 = 30 * 24 * 60 * 60 * 1000;
    return expire > now && expire - now <= days30;
  };

  const MAX_INLINE_ACTIONS = 2;

  const getTrialRemainingDays = (row: Customer) => {
    if (!row.expireTime) return -1;
    const expire = new Date(row.expireTime).getTime();
    const now = Date.now();
    return Math.ceil((expire - now) / (24 * 60 * 60 * 1000));
  };

  const getTrialRemainingText = (row: Customer) => {
    const days = getTrialRemainingDays(row);
    if (days < 0) return '已到期';
    if (days === 0) return '今天到期';
    return `${days}天`;
  };

  const getTrialRemainingType = (row: Customer) => {
    const days = getTrialRemainingDays(row);
    if (days < 0) return 'info';
    if (days <= 3) return 'danger';
    if (days <= 7) return 'warning';
    return 'success';
  };

  const getActionItems = (row: Customer) => {
    const items: any[] = [];

    items.push({ preset: 'edit', onClick: () => openEdit(row) });

    if (props.lifecycle === 'trial') {
      items.push({ title: '升级版本', onClick: () => openProduct(row) });
    }

    if (props.lifecycle === 'paid') {
      items.push({ title: '授权管理', onClick: () => openProduct(row) });
    }

    if (props.lifecycle === 'churned') {
      items.push({ title: '重新激活', onClick: () => toggleStatus(row, 1) });
    }

    if (row.status === 1 && props.lifecycle !== 'churned') {
      items.push({ title: '停用', danger: true, onClick: () => toggleStatus(row, 0) });
    }

    return items;
  };

  const getPrimaryActions = (row: Customer) => {
    return getActionItems(row).slice(0, MAX_INLINE_ACTIONS);
  };

  const getMoreActions = (row: Customer) => {
    return getActionItems(row).slice(MAX_INLINE_ACTIONS);
  };

  const openEdit = (row?: Customer) => {
    const editData = row ?? { sourceChannel: 'console' } as Customer;
    openModal({
      custom: true,
      asyncComponent: () => import('./customer-edit.vue'),
      componentProps: { data: editData, onDone: () => { reload(); emit('reload'); } }
    });
  };

  const openProduct = (row: Customer) => {
    openModal({
      custom: true,
      asyncComponent: () => import('./customer-product.vue'),
      componentProps: { data: row, onDone: () => { reload(); emit('reload'); } }
    });
  };

  const toggleStatus = (row: Customer, status: number) => {
    const action = status === 1 ? '启用' : '停用';
    ElMessageBox.confirm(
      `确定要${action}"${row.tenantName}"吗?`,
      '系统提示',
      { type: 'warning', draggable: true }
    )
      .then(() => {
        const loading = EleMessage.loading({ message: '请求中..', plain: true });
        updateCustomerStatus({ id: row.id!, status })
          .then((msg) => {
            loading.close();
            EleMessage.success({ message: msg, plain: true });
            reload();
            emit('reload');
          })
          .catch((e) => {
            loading.close();
            EleMessage.error({ message: e.message, plain: true });
          });
      })
      .catch(() => {});
  };

  const remove = (row?: Customer) => {
    const rows = row == null ? selections.value : [row];
    if (!rows.length) {
      EleMessage.error({ message: '请至少选择一条数据', plain: true });
      return;
    }
    ElMessageBox.confirm(
      `确定要删除"${rows.map((d) => d.tenantName).join(', ')}"吗?`,
      '系统提示',
      { type: 'warning', draggable: true }
    )
      .then(() => {
        const loading = EleMessage.loading({ message: '请求中..', plain: true });
        removeCustomers(rows.map((d) => d.id))
          .then((msg) => {
            loading.close();
            EleMessage.success({ message: msg, plain: true });
            reload();
            emit('reload');
          })
          .catch((e) => {
            loading.close();
            EleMessage.error({ message: e.message, plain: true });
          });
      })
      .catch(() => {});
  };

  defineExpose({ reload });
</script>

<style scoped>
  .expire-warning {
    color: var(--el-color-danger);
    font-weight: 600;
  }

  .action-wrapper {
    display: inline-flex;
    align-items: center;
    gap: 4px;
  }

  .action-danger {
    color: var(--el-color-danger) !important;
  }
</style>
