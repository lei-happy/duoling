<template>
  <ele-page flex-table="auto" hide-footer :multi-card="false">
    <ele-card flex-table="auto" :body-style="{ padding: 0 }">
      <ele-split-panel
        flex-table="auto"
        :space="0"
        :size="258"
        allow-collapse
        :collapse-btn-offset="2"
        v-model:collapse="collapse"
        :custom-style="{ borderWidth: '0 1px 0 0' }"
      >
        <template #sideHeader>
          <el-input
            clearable
            :maxlength="20"
            v-model="keywords"
            placeholder="左侧树还支持鼠标右键"
            :prefix-icon="SearchOutlined"
          />
        </template>
        <btn-items
          :wrap="false"
          :items="[
            {
              preset: 'add',
              onClick: () => openTreeEdit(void 0, current?.organizationId)
            },
            {
              preset: 'edit',
              props: { disabled: !current },
              onClick: () => openTreeEdit(current)
            },
            {
              preset: 'del',
              props: { disabled: !current },
              onClick: () => removeTree(current)
            }
          ]"
          style="padding: 12px 0 12px 12px"
        />
        <ele-loading
          :loading="loading"
          :spinner-style="{ background: 'none' }"
          :style="{
            flex: '1 1 60px',
            padding: '0 0 12px 0',
            overflow: 'auto'
          }"
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
              padding: '0 calc(var(--ele-tree-item-radius) * 3)'
            }"
            @node-click="handleNodeClick"
            @node-contextmenu="handleTreeContextmenu"
          >
            <template #default="{ node, data: item }">
              <span class="el-tree-node__label" :title="node.label">
                <el-icon style="vertical-align: -3px; font-size: 16px">
                  <FolderOutlined
                    v-if="item.children?.length"
                    style="fill: currentColor; color: #ffd659"
                  />
                  <FileOutlined
                    v-else
                    style="transform: scale(0.9); color: #faad14"
                  />
                </el-icon>
                <span style="margin-left: 6px">{{ node.label }}</span>
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
            v-model:selections="selections"
            :highlight-current-row="true"
            :tools="proTableToolsWithExportPrint"
            :export-config="{ fileName: '用户数据', datasource: exportSource }"
            :print-config="{ datasource: exportSource }"
            :load-on-created="false"
            cache-key="listUserTable"
          >
            <template #toolbar>
              <btn-items
                :items="[
                  { preset: 'add', onClick: () => openEdit() },
                  { preset: 'del', onClick: () => remove() }
                ]"
              />
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
    <ele-dropdown
      ref="ctxMenuDropdownRef"
      trigger="contextmenu"
      :trigger-keys="[]"
      :icon-props="{ size: 15 }"
      :popper-options="{
        strategy: 'fixed',
        modifiers: [{ name: 'offset', options: { offset: [0, -4] } }]
      }"
      :persistent="false"
      component-type="pro"
      :prevent-contextmenu="true"
      :virtual-triggering="true"
      :virtual-ref="ctxMenuDropdownVirtualRef"
      :disabled="!ctxMenuDropdownItems.length"
      :items="ctxMenuDropdownItems"
      :popper-style="ctxMenuDropdownStyle"
      @command="handleItemCommand"
    />
  </ele-page>
</template>

<script lang="ts" setup>
  import { ref, nextTick, watch, reactive, markRaw } from 'vue';
  import { ElMessageBox } from 'element-plus';
  import type { ElTree } from 'element-plus';
  import { EleMessage, toTree, queryChild, useModal } from 'ele-admin-plus';
  import type { EleProTable } from 'ele-admin-plus';
  import type {
    DatasourceFunction,
    Columns
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import { proTableToolsWithExportPrint } from '@/config/pro-table-tool-presets';
  import type { EleDropdownInstance } from 'ele-admin-plus/es/ele-app/plus';
  import type { DropdownItem } from 'ele-admin-plus/es/ele-dropdown/types';
  import {
    PlusOutlined,
    EditOutlined,
    DeleteOutlined,
    SearchOutlined,
    FolderOutlined,
    FileOutlined,
  } from '@/components/icons';
  import { useMobile } from '@/utils/use-mobile';
  import UserSearch from '@/views/system/user/components/user-search.vue';
  import {
    listOrganizations,
    removeOrganization
  } from '@/api/system/organization';
  import type { Organization } from '@/api/system/organization/model';
  import {
    pageUsers,
    removeUsers,
    updateUserStatus,
    listUsers
  } from '@/api/system/user';
  import type { User, UserParam } from '@/api/system/user/model';

  defineOptions({ name: 'ListUser' });

  const { openModal } = useModal();

  /** 是否是移动端 */
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

  /** 查询 */
  const query = () => {
    loading.value = true;
    listOrganizations()
      .then((list) => {
        loading.value = false;
        data.value = toTree({
          data: list,
          idField: 'organizationId',
          parentIdField: 'parentId'
        });
        handleNodeClick(data.value[0]);
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

  /** 打开树编辑弹窗 */
  const openTreeEdit = (item?: Organization | null, id?: number) => {
    openModal({
      custom: true,
      asyncComponent: () =>
        import('@/views/system/organization/components/organization-edit.vue'),
      componentProps: {
        data: item,
        organizationId: id,
        onDone: () => reload()
      }
    });
  };

  /** 删除树 */
  const removeTree = (item?: Organization | null) => {
    const row = item;
    if (!row) {
      return;
    }
    ElMessageBox.confirm(`确定要删除“${row.organizationName}”吗?`, '系统提示', {
      type: 'warning',
      draggable: true
    })
      .then(() => {
        const loading = EleMessage.loading({
          message: '请求中..',
          plain: true
        });
        removeOrganization(row.organizationId)
          .then((msg) => {
            loading.close();
            EleMessage.success({ message: msg, plain: true });
            query();
          })
          .catch((e) => {
            loading.close();
            EleMessage.error({ message: e.message, plain: true });
          });
      })
      .catch(() => {});
  };

  /** 树右键菜单组件 */
  const ctxMenuDropdownRef = ref<EleDropdownInstance>(null);

  /** 树右键菜单数据 */
  const ctxMenuDropdownItems = ref<DropdownItem[]>([]);

  /** 树右键菜单虚拟触发节点 */
  const ctxMenuDropdownVirtualRef = ref<any>();

  /** 树当前打开的右键菜单对应的数据 */
  let ctxMenuCurrentData: Organization | null = null;

  /** 树右键菜单调整位置 */
  const ctxMenuDropdownStyle = reactive({ marginLeft: '0px' });

  /** 树获取右键菜单数据 */
  const getContextMenus = (_item: Organization) => {
    return [
      { title: '添加下级', command: 'add', icon: markRaw(PlusOutlined) },
      { title: '修改机构', command: 'edit', icon: markRaw(EditOutlined) },
      {
        title: '删除机构',
        command: 'del',
        icon: markRaw(DeleteOutlined),
        divided: true,
        danger: true
      }
    ];
  };

  /** 树打开右键菜单 */
  const openCtxMenuDropdown = (triggerEl: any, item: Organization) => {
    ctxMenuDropdownRef.value && ctxMenuDropdownRef.value.handleClose();
    nextTick(() => {
      ctxMenuCurrentData = item;
      ctxMenuDropdownItems.value = getContextMenus(item) || [];
      ctxMenuDropdownVirtualRef.value = triggerEl;
      if (ctxMenuDropdownItems.value.length) {
        nextTick(() => {
          ctxMenuDropdownRef.value && ctxMenuDropdownRef.value.handleOpen();
        });
      }
    });
  };

  /** 树右键菜单项点击事件 */
  const handleItemCommand = (command: string) => {
    if (ctxMenuCurrentData == null) {
      return;
    }
    if (command === 'add') {
      openTreeEdit(void 0, ctxMenuCurrentData.organizationId);
    } else if (command === 'edit') {
      openTreeEdit(ctxMenuCurrentData);
    } else if (command === 'del') {
      removeTree(ctxMenuCurrentData);
    }
  };

  /** 树组件右键事件 */
  const handleTreeContextmenu = (e: MouseEvent, item: Organization) => {
    const triggerEl = queryChild(
      e.currentTarget as HTMLElement,
      'el-tree-node__content'
    ) as HTMLElement;
    const rect = triggerEl.getBoundingClientRect();
    ctxMenuDropdownStyle.marginLeft = `${e.clientX - rect.left - rect.width / 2}px`;
    openCtxMenuDropdown(triggerEl, item);
  };

  /** 表格组件 */
  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);

  /** 表格列配置 */
  const columns = ref<Columns>([
    {
      type: 'selection',
      columnKey: 'selection',
      width: 50,
      align: 'center'
    },
    {
      type: 'index',
      columnKey: 'index',
      width: 50,
      align: 'center'
    },
    {
      prop: 'username',
      label: '用户账号',
      sortable: 'custom',
      minWidth: 110
    },
    {
      prop: 'nickname',
      label: '用户名',
      sortable: 'custom',
      minWidth: 110
    },
    {
      prop: 'sexName',
      label: '性别',
      sortable: 'custom',
      width: 90,
      align: 'center'
    },
    {
      columnKey: 'roles',
      label: '角色',
      minWidth: 120,
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
      sortable: 'custom',
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

  /** 表格选中数据 */
  const selections = ref<User[]>([]);

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
        onDone: () => reload()
      }
    });
  };

  /** 删除 */
  const remove = (row?: User) => {
    const rows = row == null ? selections.value : [row];
    if (!rows.length) {
      EleMessage.error({ message: '请至少选择一条数据', plain: true });
      return;
    }
    ElMessageBox.confirm(
      `确定要删除“${rows.map((d) => d.nickname).join(', ')}”吗?`,
      '系统提示',
      { type: 'warning', draggable: true }
    )
      .then(() => {
        const loading = EleMessage.loading({
          message: '请求中..',
          plain: true
        });
        removeUsers(rows.map((d) => d.userId))
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

  /** 查询树数据 */
  query();
</script>
