<template>
  <ele-page>
    <flow-search @search="onSearch" />
    <ele-card :body-style="{ paddingTop: '8px' }">
      <ele-pro-table
        ref="tableRef"
        row-key="id"
        :columns="columns"
        :datasource="datasource"
        :pagination="{ pageSize: 20 }"
        :show-overflow-tooltip="true"
        :highlight-current-row="true"
        cache-key="ApprovalFlowTable"
      >
        <template #toolbar>
          <btn-items
            :items="[
              { preset: 'add', title: '新增流程', onClick: () => openEdit() }
            ]"
          />
        </template>
        <template #bizType="{ row }">
          {{ bizTypeLabel(row.bizType) }}
        </template>
        <template #status="{ row }">
          <el-tag size="small" :type="flowStatusTag(row.status)">
            {{ flowStatusLabel(row.status) }}
          </el-tag>
        </template>
        <template #version="{ row }">
          <el-link
            v-if="flowStatus(row) !== 0"
            type="primary"
            :underline="false"
            @click="openVersionHistory(row)"
          >
            v{{ row.version }}
          </el-link>
          <span v-else style="color: var(--el-text-color-secondary)">—</span>
        </template>
        <template #action="{ row }">
          <btn-items divider type="link" :items="actionItems(row)" />
        </template>
      </ele-pro-table>
    </ele-card>

    <flow-edit
      v-model:visible="editVisible"
      :flow-id="editId"
      @done="onEditDone"
    />
    <flow-version-history
      v-model:visible="versionVisible"
      :flow-id="versionFlowId"
      :flow-name="versionFlowName"
    />
  </ele-page>
</template>

<script lang="ts" setup>
  import { ref, reactive } from 'vue';
  import { useRouter } from 'vue-router';
  import { ElMessageBox } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import type { EleProTable } from 'ele-admin-plus';
  import type {
    DatasourceFunction,
    Columns
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import FlowEdit from './components/flow-edit.vue';
  import FlowSearch from './components/flow-search.vue';
  import FlowVersionHistory from './components/flow-version-history.vue';
  import {
    pageFlows,
    publishFlow,
    disableFlow,
    enableFlow,
    deleteFlow
  } from '@/api/approval';
  import type { FlowOut } from '@/api/approval/model';
  import { bizTypeLabel } from '@/views/approval/constants';

  defineOptions({ name: 'EnterpriseApprovalConfig' });

  const router = useRouter();
  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);

  const where = reactive<{ keyword: string; bizType: string | undefined }>({
    keyword: '',
    bizType: void 0
  });

  const editVisible = ref(false);
  const editId = ref<number | undefined>(undefined);
  const versionVisible = ref(false);
  const versionFlowId = ref<number | null>(null);
  const versionFlowName = ref('');

  const flowStatus = (row: FlowOut) => Number(row.status);

  const flowStatusLabel = (s?: number) => {
    const status = Number(s);
    return status === 1 ? '已发布' : status === 2 ? '已停用' : '草稿';
  };
  const flowStatusTag = (s?: number): 'info' | 'success' | 'danger' => {
    const status = Number(s);
    return status === 1 ? 'success' : status === 2 ? 'danger' : 'info';
  };

  const columns = ref<Columns>([
    { prop: 'flowName', label: '流程名称', minWidth: 180 },
    { prop: 'bizType', label: '审批场景', width: 160, slot: 'bizType' },
    {
      prop: 'priority',
      label: '优先级',
      width: 80,
      align: 'center'
    },
    {
      prop: 'status',
      label: '状态',
      width: 100,
      align: 'center',
      slot: 'status'
    },
    {
      prop: 'version',
      label: '版本',
      width: 80,
      align: 'center',
      slot: 'version'
    },
    {
      columnKey: 'action',
      label: '操作',
      width: 330,
      align: 'center',
      slot: 'action',
      fixed: 'right'
    }
  ]);

  const datasource: DatasourceFunction = async ({ pages }) => {
    const res = await pageFlows({
      keyword: where.keyword || undefined,
      bizType: where.bizType,
      ...pages
    });
    return { list: res?.list ?? [], count: res?.count ?? 0 };
  };

  const onSearch = (payload: {
    keyword: string;
    bizType: string | undefined;
  }) => {
    where.keyword = payload.keyword ?? '';
    where.bizType = payload.bizType;
    tableRef.value?.reload?.({ page: 1 });
  };

  const reload = () => {
    tableRef.value?.reload?.();
  };

  const openEdit = (row?: FlowOut) => {
    editId.value = row?.id;
    editVisible.value = true;
  };

  const openVersionHistory = (row: FlowOut) => {
    versionFlowId.value = row.id;
    versionFlowName.value = row.flowName;
    versionVisible.value = true;
  };

  const onEditDone = (createdId?: number) => {
    reload();
    if (createdId) {
      router.push(`/enterprise/approval-config/flow/${createdId}`);
    }
  };

  const onPublish = (row: FlowOut) => {
    ElMessageBox.confirm('确认发布该流程？发布后将用于新提交的审批。', '提示', {
      type: 'warning'
    })
      .then(async () => {
        await publishFlow(row.id);
        EleMessage.success({ message: '已发布', plain: true });
        reload();
      })
      .catch(() => {});
  };

  const onDisable = (row: FlowOut) => {
    ElMessageBox.confirm('确认停用该流程？停用后将不再匹配新审批。', '提示', {
      type: 'warning'
    })
      .then(async () => {
        await disableFlow(row.id);
        EleMessage.success({ message: '已停用', plain: true });
        reload();
      })
      .catch(() => {});
  };

  const onEnable = (row: FlowOut) => {
    ElMessageBox.confirm(
      '确认重新启用该流程？启用后将恢复匹配新审批。',
      '提示',
      {
        type: 'warning'
      }
    )
      .then(async () => {
        await enableFlow(row.id);
        EleMessage.success({ message: '已启用', plain: true });
        reload();
      })
      .catch(() => {});
  };

  const onDelete = (row: FlowOut) => {
    ElMessageBox.confirm('确认删除该流程模板？', '提示', { type: 'warning' })
      .then(async () => {
        await deleteFlow(row.id);
        EleMessage.success({ message: '已删除', plain: true });
        reload();
      })
      .catch(() => {});
  };

  const openFlowDesign = (row: FlowOut) => {
    router.push(`/enterprise/approval-config/flow/${row.id}`);
  };

  const actionItems = (row: FlowOut) => {
    const status = flowStatus(row);
    const items: any[] = [
      { title: '编辑', onClick: () => openEdit(row) },
      { title: '审批流程配置', onClick: () => openFlowDesign(row) }
    ];
    if (status === 0) {
      items.push({ title: '发布', onClick: () => onPublish(row) });
    } else if (status === 1) {
      items.push({ title: '停用', onClick: () => onDisable(row) });
    } else if (status === 2) {
      items.push({ title: '启用', onClick: () => onEnable(row) });
    }
    items.push({ title: '删除', danger: true, onClick: () => onDelete(row) });
    return items;
  };
</script>
