<template>
  <ele-page hide-footer :multi-card="false" flex-table="auto">
    <ele-card :body-style="{ padding: 0 }" flex-table="auto">
      <ele-split-panel
        :space="0"
        :size="258"
        allow-collapse
        :collapse-btn-offset="2"
        v-model:collapse="collapse"
        :custom-style="{ borderWidth: '0 1px 0 0' }"
        flex-table="auto"
      >
        <template #sideHeader>
          <el-input
            class="ele-fluid"
            clearable
            :maxlength="20"
            v-model="keywords"
            placeholder="输入机构名称搜索"
            :prefix-icon="SearchOutlined"
          />
        </template>
        <ele-loading
          :loading="loading"
          :spinner-style="{ background: 'none' }"
          :style="{ flex: '1 1 60px', overflow: 'auto' }"
        >
          <el-tree
            ref="treeRef"
            :data="data"
            highlight-current
            node-key="organizationId"
            :props="{ label: 'organizationName' }"
            :expand-on-click-node="false"
            :default-expand-all="true"
            :filter-node-method="filterNode"
            :current-node-key="current?.organizationId"
            :style="{
              '--ele-tree-item-height': '34px',
              '--ele-tree-expand-margin':
                '0 2px 0 calc(8px - var(--ele-tree-item-radius))',
              padding: '12px calc(var(--ele-tree-item-radius) * 3)'
            }"
            @node-click="handleNodeClick"
          >
            <template #default="{ node, data }">
              <span
                class="el-tree-node__label"
                :title="`${node.label} (${data.userCount ?? 0})`"
              >
                <el-icon style="margin-right: 4px; vertical-align: -2px">
                  <CityOutlined />
                </el-icon>
                <span>{{ node.label }}</span>
                <span class="user-org-tree-count"> ({{ data.userCount ?? 0 }})</span>
              </span>
            </template>
          </el-tree>
        </ele-loading>
        <template #bodyHeader>
          <user-search
            :organizationId="current?.organizationId"
            @search="(where) => reload(where, 1)"
          />
        </template>
        <template #body>
          <ele-pro-table
            ref="tableRef"
            row-key="userId"
            :columns="columns"
            :datasource="datasource"
            :show-overflow-tooltip="true"
            :highlight-current-row="true"
            :tools="proTableToolsWithExportPrint"
            :export-config="{ fileName: '用户数据', datasource: exportSource }"
            :print-config="{ datasource: exportSource }"
            :load-on-created="false"
            cache-key="SystemUserTable"
          >
            <template #toolbar>
              <btn-items
                :items="[
                  { preset: 'add', onClick: () => openEdit() },
                  { preset: 'import', onClick: () => openImport() }
                ]"
              />
            </template>
            <template #nickname="{ row }">
              <el-link
                type="primary"
                underline="never"
                @click="openDetail(row)"
              >
                {{ row.nickname }}
              </el-link>
            </template>
            <template #roles="{ row }">
              <el-tag
                v-for="item in row.roles"
                :key="item.roleId"
                size="small"
                :disable-transitions="true"
              >
                {{ item.roleName }}
              </el-tag>
            </template>
            <template #status="{ row }">
              <el-switch
                size="small"
                :model-value="row.status === 0"
                @change="(checked: boolean) => editStatus(checked, row)"
              />
            </template>
            <template #action="{ row }">
              <btn-items
                divider
                type="link"
                :items="[
                  { preset: 'edit', onClick: () => openEdit(row) },
                  {
                    preset: 'more',
                    dropdownItems: [
                      {
                        title: '删除用户',
                        icon: DeleteOutlined,
                        danger: true,
                        onClick: () => remove(row)
                      }
                    ]
                  }
                ]"
              />
            </template>
          </ele-pro-table>
        </template>
      </ele-split-panel>
    </ele-card>
  </ele-page>
</template>
<style scoped>
.ele-card-body {
  :deep(.ele-card-body) {
    padding: 8px 0 8px 0 !important;
  }
}
</style>
<script lang="ts" setup>
  import { ref, watch, onActivated } from 'vue';
  import { useRouter } from 'vue-router';
  import { ElMessageBox } from 'element-plus';
  import type { ElTree } from 'element-plus';
  import { EleMessage, toTree, useModal } from 'ele-admin-plus';
  import type { EleProTable } from 'ele-admin-plus';
  import type {
    DatasourceFunction,
    Columns
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import { proTableToolsWithExportPrint } from '@/config/pro-table-tool-presets';
  import {
    CityOutlined,
    SearchOutlined,
    DeleteOutlined
  } from '@/components/icons';
  import { usePageTab } from '@/utils/use-page-tab';
  import { useMobile } from '@/utils/use-mobile';
  import UserSearch from './components/user-search.vue';
  import { listOrganizations } from '@/api/system/organization';
  import type { Organization } from '@/api/system/organization/model';
  import {
    pageUsers,
    removeUser,
    updateUserStatus,
    listUsers
  } from '@/api/system/user';
  import type { User, UserParam } from '@/api/system/user/model';

  defineOptions({ name: 'SystemUser' });

  const { push } = useRouter();
  const { openModal } = useModal();
  const { addPageTab } = usePageTab();
  const { mobile } = useMobile();

  /** 分割面板是否折叠 */
  const collapse = ref(mobile.value);

  /** 树组件 */
  const treeRef = ref<InstanceType<typeof ElTree> | null>(null);

  /** 加载状态 */
  const loading = ref(true);

  /** 树数据 */
  const data = ref<Organization[]>([]);

  /** 树选中数据 */
  const current = ref<Organization | null>(null);

  /** 树搜索关键字 */
  const keywords = ref('');

  const findOrgInTree = (
    nodes: Organization[],
    id: number
  ): Organization | undefined => {
    for (const n of nodes) {
      if (n.organizationId === id) {
        return n;
      }
      if (n.children?.length) {
        const hit = findOrgInTree(n.children, id);
        if (hit) {
          return hit;
        }
      }
    }
  };

  /** 查询树数据；preserveSelection 为 true 时在刷新人数后尽量保持当前选中部门 */
  const query = (preserveSelection?: boolean) => {
    const prevId = preserveSelection ? current.value?.organizationId : undefined;
    loading.value = true;
    listOrganizations()
      .then((list) => {
        loading.value = false;
        data.value = toTree({
          data: list,
          idField: 'organizationId',
          parentIdField: 'parentId'
        });
        if (preserveSelection && prevId != null) {
          const row = findOrgInTree(data.value, prevId);
          handleNodeClick(row ?? data.value[0]);
        } else {
          handleNodeClick(data.value[0]);
        }
      })
      .catch((e) => {
        loading.value = false;
        EleMessage.error({ message: e.message, plain: true });
      });
  };

  /** 树选中数据 */
  const handleNodeClick = (row?: Organization) => {
    if (row && row.organizationId) {
      current.value = row;
    } else {
      current.value = null;
    }
    reload({}, 1);
    // 移动端自动收起左侧
    if (current.value != null && mobile.value) {
      collapse.value = true;
    }
  };

  /** 树过滤方法 */
  const filterNode = (value: string, data: Organization) => {
    if (value) {
      return !!(data.organizationName && data.organizationName.includes(value));
    }
    return true;
  };

  /** 树过滤 */
  watch(keywords, (value) => {
    treeRef.value?.filter?.(value);
  });

  /** 表格组件 */
  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);

  /** 表格列配置 */
  const columns = ref<Columns>([
    {
      prop: 'nickname',
      label: '姓名',
      minWidth: 110,
      slot: 'nickname'
    },
    {
      prop: 'phone',
      label: '手机号',
      minWidth: 120
    },
    {
      prop: 'sexName',
      label: '性别',
      width: 90,
      align: 'center'
    },
    {
      columnKey: 'roles',
      label: '角色',
      minWidth: 110,
      slot: 'roles',
      align: 'center',
      formatter: (row: User) => (row.roles || []).map((d) => d.roleName).join()
    },
    {
      prop: 'createTime',
      label: '创建时间',
      sortable: 'custom',
      width: 180,
      align: 'center'
    },
    {
      prop: 'status',
      label: '状态',
      width: 90,
      align: 'center',
      slot: 'status',
      formatter: (row) => (row.status == 0 ? '正常' : '冻结')
    },
    {
      columnKey: 'action',
      label: '操作',
      width: 148,
      align: 'center',
      slot: 'action',
      hideInPrint: true,
      hideInExport: true
    }
  ]);

  /** 表格数据源 */
  const datasource: DatasourceFunction = ({ pages, where, orders }) => {
    return pageUsers({
      ...where,
      ...orders,
      ...pages,
      organizationId: current.value?.organizationId
    });
  };

  /** 搜索 */
  const reload = (where?: UserParam, page?: number) => {
    tableRef.value?.reload?.({ where, page });
  };

  /** 打开编辑弹窗 */
  const openEdit = (row?: User) => {
    openModal({
      custom: true,
      asyncComponent: () => import('./components/user-edit.vue'),
      componentProps: {
        data: row,
        organizationId: current.value?.organizationId,
        onDone: () => {
          reload();
          query(true);
        }
      }
    });
  };

  /** 打开导入弹窗 */
  const openImport = () => {
    openModal({
      custom: true,
      asyncComponent: () => import('./components/user-import.vue'),
      componentProps: {
        onDone: () => {
          reload();
          query(true);
        }
      }
    });
  };

  /** 删除（单行，不支持批量） */
  const remove = (row: User) => {
    if (row.userId == null) {
      return;
    }
    ElMessageBox.confirm(
      `确定要删除“${row.nickname}”吗?`,
      '系统提示',
      { type: 'warning', draggable: true }
    )
      .then(() => {
        const loading = EleMessage.loading({
          message: '请求中..',
          plain: true
        });
        removeUser(row.userId)
          .then((msg) => {
            loading.close();
            EleMessage.success({ message: msg, plain: true });
            reload();
            query(true);
          })
          .catch((e) => {
            loading.close();
            EleMessage.error({ message: e.message, plain: true });
          });
      })
      .catch(() => {});
  };

  /** 修改用户状态 */
  const editStatus = (checked: boolean, row: User) => {
    const status = checked ? 0 : 1;
    updateUserStatus(row.userId, status)
      .then((msg) => {
        row.status = status;
        EleMessage.success({ message: msg, plain: true });
      })
      .catch((e) => {
        EleMessage.error({ message: e.message, plain: true });
      });
  };

  /** 导出和打印全部数据的数据源 */
  const exportSource: DatasourceFunction = ({ where, orders }) => {
    return listUsers({
      ...where,
      ...orders,
      organizationId: current.value?.organizationId
    });
  };

  /** 查看详情 */
  const openDetail = (row: User) => {
    const path = `/system/user/details/${row.userId}`;
    addPageTab({
      title: `用户详情[${row.nickname}]`,
      key: path,
      closable: true,
      meta: { icon: 'UserOutlined' }
    });
    push(path);
  };

  /** 查询树数据 */
  query();

  /** 页签切换回来时重新加载部门树 */
  onActivated(() => {
    query();
  });
</script>
