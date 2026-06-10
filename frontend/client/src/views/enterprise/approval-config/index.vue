<template>
  <ele-page>
    <ele-card :body-style="{ paddingTop: '8px' }">
      <div class="approval-toolbar">
        <el-input
          v-model="keyword"
          clearable
          placeholder="搜索流程名称"
          style="width: 220px"
          @keyup.enter="reload(1)"
          @clear="reload(1)"
        />
        <el-select
          v-model="bizType"
          clearable
          placeholder="审批类型"
          style="width: 180px"
          @change="reload(1)"
        >
          <el-option
            v-for="t in bizTypeOptions"
            :key="t.value"
            :value="t.value"
            :label="t.label"
          />
        </el-select>
        <el-button type="primary" @click="reload(1)">查询</el-button>
        <div class="approval-toolbar-right">
          <el-button type="primary" @click="openEdit()">新增流程</el-button>
        </div>
      </div>
      <ele-pro-table
        ref="tableRef"
        row-key="id"
        :columns="columns"
        :datasource="datasource"
        :show-overflow-tooltip="true"
        cache-key="ApprovalFlowTable"
      >
        <template #bizType="{ row }">
          {{ bizTypeLabel(row.bizType) }}
        </template>
        <template #isDefault="{ row }">
          <el-tag v-if="row.isDefault" size="small" type="warning">默认</el-tag>
          <span v-else>—</span>
        </template>
        <template #status="{ row }">
          <el-tag size="small" :type="flowStatusTag(row.status)">
            {{ flowStatusLabel(row.status) }}
          </el-tag>
        </template>
        <template #action="{ row }">
          <btn-items divider type="link" :items="actionItems(row)" />
        </template>
      </ele-pro-table>
    </ele-card>

    <flow-edit
      v-model:visible="editVisible"
      :flow-id="editId"
      @done="reload()"
    />
  </ele-page>
</template>

<script lang="ts" setup>
  import { onMounted, ref } from 'vue';
  import { ElMessageBox } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import type { EleProTable } from 'ele-admin-plus';
  import type {
    DatasourceFunction,
    Columns
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import FlowEdit from './components/flow-edit.vue';
  import {
    pageFlows,
    publishFlow,
    disableFlow,
    deleteFlow
  } from '@/api/approval';
  import type { FlowOut } from '@/api/approval/model';
  import { bizTypeLabel } from '@/views/approval/constants';

  defineOptions({ name: 'EnterpriseApprovalConfig' });

  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);
  const keyword = ref('');
  const bizType = ref<string | undefined>(undefined);

  const editVisible = ref(false);
  const editId = ref<number | undefined>(undefined);

  const bizTypeOptions = [
    { value: 'social_capacity_audit', label: '社会运力准入审核' }
  ];

  const flowStatusLabel = (s?: number) =>
    s === 1 ? '已发布' : s === 2 ? '已停用' : '草稿';
  const flowStatusTag = (s?: number): 'info' | 'success' | 'danger' =>
    s === 1 ? 'success' : s === 2 ? 'danger' : 'info';

  const columns = ref<Columns>([
    { prop: 'flowName', label: '流程名称', minWidth: 180 },
    { prop: 'bizType', label: '审批类型', width: 160, slot: 'bizType' },
    {
      prop: 'isDefault',
      label: '默认',
      width: 80,
      align: 'center',
      slot: 'isDefault'
    },
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
    { prop: 'version', label: '版本', width: 70, align: 'center' },
    {
      columnKey: 'action',
      label: '操作',
      width: 220,
      align: 'center',
      slot: 'action',
      fixed: 'right'
    }
  ]);

  const datasource: DatasourceFunction = async ({ pages }) => {
    const res = await pageFlows({
      keyword: keyword.value || undefined,
      bizType: bizType.value,
      ...pages
    });
    return { list: res?.list ?? [], count: res?.count ?? 0 };
  };

  const reload = (page?: number) => {
    tableRef.value?.reload?.(page ? { page } : undefined);
  };

  const openEdit = (row?: FlowOut) => {
    editId.value = row?.id;
    editVisible.value = true;
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

  const onDelete = (row: FlowOut) => {
    ElMessageBox.confirm('确认删除该流程模板？', '提示', { type: 'warning' })
      .then(async () => {
        await deleteFlow(row.id);
        EleMessage.success({ message: '已删除', plain: true });
        reload();
      })
      .catch(() => {});
  };

  const actionItems = (row: FlowOut) => {
    const items: any[] = [{ title: '编辑', onClick: () => openEdit(row) }];
    if (row.status !== 1) {
      items.push({ title: '发布', onClick: () => onPublish(row) });
    }
    if (row.status === 1) {
      items.push({ title: '停用', onClick: () => onDisable(row) });
    }
    items.push({ title: '删除', danger: true, onClick: () => onDelete(row) });
    return items;
  };

  onMounted(() => reload());
</script>

<style lang="scss" scoped>
  .approval-toolbar {
    display: flex;
    gap: 8px;
    margin-bottom: 12px;
    align-items: center;
  }
  .approval-toolbar-right {
    margin-left: auto;
  }
</style>
