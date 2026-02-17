<template>
  <ele-page>
    <tenant-search @search="(where) => reload(where, 1)" />
    <ele-card :body-style="{ paddingTop: '8px' }">
      <ele-pro-table
        ref="tableRef"
        row-key="id"
        :columns="columns"
        :datasource="datasource"
        :show-overflow-tooltip="true"
        v-model:selections="selections"
        :highlight-current-row="true"
        :export-config="{ fileName: '企业数据' }"
        cache-key="TenantListTable"
      >
        <template #toolbar>
          <btn-items
            :items="[
              { preset: 'add', title: '注册企业', onClick: () => openEdit() },
              { preset: 'del', onClick: () => remove() }
            ]"
          />
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
        <template #action="{ row }">
          <btn-items
            :divider="true"
            type="link"
            :items="actionItems(row)"
          />
        </template>
      </ele-pro-table>
    </ele-card>
  </ele-page>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import { ElMessageBox } from 'element-plus';
  import { EleMessage, useModal } from 'ele-admin-plus';
  import type { EleProTable } from 'ele-admin-plus';
  import type {
    DatasourceFunction,
    Columns
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import TenantSearch from './components/tenant-search.vue';
  import { pageTenants, removeTenants, updateTenantStatus } from '@/api/tenant';
  import type { Tenant, TenantParam } from '@/api/tenant/model';

  defineOptions({ name: 'TenantList' });

  const { openModal } = useModal();

  /** 表格实例 */
  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);

  /** 表格列配置 */
  const columns = ref<Columns>([
    {
      prop: 'tenantCode',
      label: '企业编码',
      width: 110,
      align: 'center'
    },
    {
      prop: 'tenantName',
      label: '企业名称',
      minWidth: 160
    },
    {
      prop: 'contactPerson',
      label: '联系人',
      width: 110
    },
    {
      prop: 'contactPhone',
      label: '联系电话',
      width: 140
    },
    {
      prop: 'status',
      label: '状态',
      width: 100,
      align: 'center',
      slot: 'status',
      formatter: (row: Tenant) => statusText(row.status)
    },
    {
      prop: 'dbInitialized',
      label: '数据库',
      width: 110,
      align: 'center',
      slot: 'dbInitialized',
      formatter: (row: Tenant) =>
        row.dbInitialized === 1 ? '已初始化' : '未初始化'
    },
    {
      prop: 'expireTime',
      label: '到期时间',
      width: 170,
      align: 'center'
    },
    {
      prop: 'sourceChannel',
      label: '来源渠道',
      width: 110,
      align: 'center',
      slot: 'sourceChannel',
      formatter: (row: Tenant) => channelText(row.sourceChannel)
    },
    {
      prop: 'createTime',
      label: '创建时间',
      width: 170,
      align: 'center'
    },
    {
      columnKey: 'action',
      label: '操作',
      width: 260,
      align: 'center',
      slot: 'action',
      hideInPrint: true,
      hideInExport: true
    }
  ]);

  /** 表格选中数据 */
  const selections = ref<Tenant[]>([]);

  /** 表格数据源 */
  const datasource: DatasourceFunction = ({ pages, where, orders }) => {
    return pageTenants({ ...where, ...orders, ...pages });
  };

  /** 搜索 */
  const reload = (where?: TenantParam, page?: number) => {
    selections.value = [];
    tableRef.value?.reload?.({ where, page });
  };

  /** 状态文本 */
  const statusText = (status?: number) => {
    const map: Record<number, string> = {
      0: '停用',
      1: '正常',
      2: '待审核',
      3: '已过期'
    };
    return map[status ?? -1] || '未知';
  };

  /** 状态标签颜色 */
  const statusTagType = (status?: number) => {
    const map: Record<number, string> = {
      0: 'danger',
      1: 'success',
      2: 'warning',
      3: 'info'
    };
    return map[status ?? -1] || 'info';
  };

  /** 来源渠道文本 */
  const channelText = (channel?: string) => {
    const map: Record<string, string> = {
      website: '官网注册',
      console: '后台录入',
      referral: '企业推荐'
    };
    return map[channel ?? ''] || channel || '-';
  };

  /** 来源渠道标签颜色 */
  const channelTagType = (channel?: string) => {
    const map: Record<string, string> = {
      website: '',
      console: 'info',
      referral: 'success'
    };
    return map[channel ?? ''] || 'info';
  };

  /** 操作按钮列表 */
  const actionItems = (row: Tenant) => {
    const items: any[] = [
      { preset: 'edit', onClick: () => openEdit(row) },
      { title: '授权', onClick: () => openProduct(row) }
    ];
    // 状态切换按钮
    if (row.status === 1) {
      items.push({
        title: '停用',
        danger: true,
        onClick: () => toggleStatus(row, 0)
      });
    } else if (row.status === 0 || row.status === 2) {
      items.push({
        title: '启用',
        onClick: () => toggleStatus(row, 1)
      });
    }
    items.push({ preset: 'del', onClick: () => remove(row) });
    return items;
  };

  /** 打开编辑弹窗 */
  const openEdit = (row?: Tenant) => {
    // 后台新建企业时自动设置来源渠道为 console
    const editData = row ?? { sourceChannel: 'console' } as Tenant;
    openModal({
      custom: true,
      asyncComponent: () => import('./components/tenant-edit.vue'),
      componentProps: { data: editData, onDone: () => reload() }
    });
  };

  /** 打开产品授权弹窗 */
  const openProduct = (row: Tenant) => {
    openModal({
      custom: true,
      asyncComponent: () => import('./components/tenant-product.vue'),
      componentProps: { data: row, onDone: () => reload() }
    });
  };

  /** 切换状态 */
  const toggleStatus = (row: Tenant, status: number) => {
    const action = status === 1 ? '启用' : '停用';
    ElMessageBox.confirm(
      `确定要${action}"${row.tenantName}"吗?`,
      '系统提示',
      { type: 'warning', draggable: true }
    )
      .then(() => {
        const loading = EleMessage.loading({
          message: '请求中..',
          plain: true
        });
        updateTenantStatus({ id: row.id!, status })
          .then((msg) => {
            loading.close();
            EleMessage.success({ message: msg, plain: true });
            reload();
          })
          .catch((e) => {
            loading.close();
            EleMessage.error({ message: e.message, plain: true });
          });
      })
      .catch(() => {});
  };

  /** 删除 */
  const remove = (row?: Tenant) => {
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
        const loading = EleMessage.loading({
          message: '请求中..',
          plain: true
        });
        removeTenants(rows.map((d) => d.id))
          .then((msg) => {
            loading.close();
            EleMessage.success({ message: msg, plain: true });
            reload();
          })
          .catch((e) => {
            loading.close();
            EleMessage.error({ message: e.message, plain: true });
          });
      })
      .catch(() => {});
  };
</script>
