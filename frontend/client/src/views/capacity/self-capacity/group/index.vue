<template>
  <ele-page>
    <group-search @search="onSearch" />
    <ele-card :body-style="{ paddingTop: '8px' }">
      <ele-pro-table
        ref="tableRef"
        row-key="id"
        :columns="columns"
        :datasource="datasource"
        :show-overflow-tooltip="true"
        :highlight-current-row="true"
        cache-key="CapacitySelfGroupTable"
      >
        <template #toolbar>
          <btn-items
            :items="[
              { preset: 'add', title: '新建分组', onClick: () => openEdit() }
            ]"
          />
        </template>
        <template #groupName="{ row }">
          <span class="group-name-tag">
            <span
              class="group-name-dot"
              :style="{ background: row.color || 'var(--el-color-primary)' }"
            />
            {{ row.groupName }}
          </span>
        </template>
        <template #memberCount="{ row }">
          <el-button link type="primary" @click="openMembers(row)">
            {{ row.memberCount ?? 0 }} 条运力
          </el-button>
        </template>
        <template #status="{ row }">
          <el-tag
            :type="row.status === 1 ? 'success' : 'info'"
            size="small"
            :disable-transitions="true"
          >
            {{ row.status === 1 ? '启用' : '停用' }}
          </el-tag>
        </template>
        <template #action="{ row }">
          <btn-items
            divider
            type="link"
            :items="[
              { title: '成员', onClick: () => openMembers(row) },
              { preset: 'edit', onClick: () => openEdit(row) },
              {
                title: row.status === 1 ? '停用' : '启用',
                onClick: () => toggleStatus(row)
              },
              { preset: 'del', onClick: () => remove(row) }
            ]"
          />
        </template>
      </ele-pro-table>
    </ele-card>

    <group-edit v-model:visible="editVisible" :data="editData" @done="reload" />
    <group-members
      v-model:visible="membersVisible"
      :group="membersGroup"
      @changed="reload"
    />
  </ele-page>
</template>

<script lang="ts" setup>
  import { ref, reactive } from 'vue';
  import { ElMessageBox } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import type { EleProTable } from 'ele-admin-plus';
  import type {
    DatasourceFunction,
    Columns
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import GroupSearch from './components/group-search.vue';
  import GroupEdit from './components/group-edit.vue';
  import GroupMembers from './components/group-members.vue';
  import {
    pageCapacityGroups,
    removeCapacityGroup,
    updateCapacityGroupStatus
  } from '@/api/capacity/self-capacity/group';
  import type {
    CapacityGroup,
    CapacityGroupParam
  } from '@/api/capacity/self-capacity/group/model';
  import { formatDateTime } from '@/utils/date-util';

  defineOptions({ name: 'CapacitySelfGroup' });

  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);
  const editVisible = ref(false);
  const editData = ref<CapacityGroup | null>(null);
  const membersVisible = ref(false);
  const membersGroup = ref<CapacityGroup | null>(null);

  const where = reactive<
    Pick<CapacityGroupParam, 'keyword' | 'status' | 'enterpriseId'>
  >({
    keyword: '',
    status: void 0,
    enterpriseId: void 0
  });

  const onSearch = (
    payload: Pick<CapacityGroupParam, 'keyword' | 'status' | 'enterpriseId'>
  ) => {
    where.keyword = payload.keyword ?? '';
    where.status = payload.status;
    where.enterpriseId = payload.enterpriseId;
    tableRef.value?.reload?.({ page: 1 });
  };

  const columns = ref<Columns>([
    { prop: 'groupName', label: '分组名称', minWidth: 160, slot: 'groupName' },
    { prop: 'groupCode', label: '分组编码', minWidth: 120, align: 'center' },
    {
      prop: 'memberCount',
      label: '成员数量',
      width: 120,
      align: 'center',
      slot: 'memberCount'
    },
    { prop: 'status', label: '状态', width: 90, align: 'center', slot: 'status' },
    { prop: 'remark', label: '备注', minWidth: 140, align: 'center' },
    {
      prop: 'createdAt',
      label: '创建时间',
      minWidth: 170,
      align: 'center',
      formatter: (row) => formatDateTime(row.createdAt)
    },
    {
      columnKey: 'action',
      label: '操作',
      width: 220,
      align: 'center',
      slot: 'action',
      hideInPrint: true,
      hideInExport: true,
      fixed: 'right'
    }
  ]);

  const datasource: DatasourceFunction = async ({ page, limit, pages }) => {
    const p = page ?? (Number(pages?.page) || 1);
    const l = limit ?? (Number(pages?.limit) || 10);
    const res = await pageCapacityGroups({ ...where, page: p, limit: l });
    const raw = res as { list?: CapacityGroup[]; count?: number; total?: number };
    return {
      list: raw?.list ?? [],
      count: raw?.count ?? raw?.total ?? 0
    };
  };

  const reload = () => {
    tableRef.value?.reload?.();
  };

  const openEdit = (row?: CapacityGroup) => {
    editData.value = row ?? null;
    editVisible.value = true;
  };

  const openMembers = (row: CapacityGroup) => {
    membersGroup.value = row;
    membersVisible.value = true;
  };

  const toggleStatus = (row: CapacityGroup) => {
    const next = row.status === 1 ? 0 : 1;
    updateCapacityGroupStatus(row.id!, next)
      .then((msg) => {
        EleMessage.success({ message: msg, plain: true });
        reload();
      })
      .catch((e) => {
        EleMessage.error({ message: e.message, plain: true });
      });
  };

  const remove = (row: CapacityGroup) => {
    ElMessageBox.confirm(
      `确定删除分组「${row.groupName}」吗？该分组下的成员归属会一并清除；若已被成本规则引用，相关规则将不再命中该分组。`,
      '系统提示',
      { type: 'warning', draggable: true }
    )
      .then(() => {
        const loading = EleMessage.loading({
          message: '正在删除分组，请稍候…',
          plain: true
        });
        removeCapacityGroup(row.id!)
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

<style scoped>
  .group-name-tag {
    display: inline-flex;
    align-items: center;
    gap: 6px;
  }
  .group-name-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    display: inline-block;
    flex-shrink: 0;
  }
</style>
