<template>
  <ele-page>
    <route-search @search="(w) => reload(w, 1)" />
    <ele-card :body-style="{ paddingTop: '8px' }">
      <ele-pro-table
        ref="tableRef"
        row-key="id"
        :columns="columns"
        :datasource="datasource"
        :pagination="{ pageSize: 20 }"
        :show-overflow-tooltip="true"
        :highlight-current-row="true"
        v-model:selections="selections"
        :default-sort="{ prop: 'createdAt', order: 'descending' }"
        cache-key="ResourceRouteTable"
      >
        <template #toolbar>
          <btn-items
            :items="[
              { preset: 'add', title: '新增线路', onClick: () => openEdit() }
            ]"
          />
        </template>
        <template #status="{ row }">
          <el-tag
            v-if="row.status === 1"
            type="success"
            size="small"
            disable-transitions
          >
            正常
          </el-tag>
          <el-tag
            v-else-if="row.status === 0"
            type="warning"
            size="small"
            disable-transitions
          >
            停用
          </el-tag>
        </template>
        <template #action="{ row }">
          <div
            class="route-actions"
            :key="`route-actions-${row.id}-${row.status ?? ''}`"
          >
            <btn-items
              divider
              type="link"
              :wrap="false"
              :items="actionItems(row)"
            />
          </div>
        </template>
      </ele-pro-table>
    </ele-card>
    <route-edit v-model:visible="editVisible" :data="editData" @done="reload" />
  </ele-page>
</template>

<script lang="ts" setup>
  import { nextTick, ref } from 'vue';
  import { ElMessageBox } from 'element-plus';
  import { VideoPause, VideoPlay } from '@element-plus/icons-vue';
  import { EleMessage } from 'ele-admin-plus';
  import type { EleProTable } from 'ele-admin-plus';
  import type {
    ButtonDropdownItem,
    ButtonItem
  } from 'ele-admin-plus/es/ele-buttons/types';
  import type {
    DatasourceFunction,
    Columns
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import RouteEdit from './components/route-edit.vue';
  import RouteSearch from './components/route-search.vue';
  import { pageRoutes, removeRoute, updateRoute } from '@/api/resource/route';
  import type { Route, RouteParam } from '@/api/resource/route/model';
  import { DeleteOutlined } from '@/components/icons';
  import { formatDateTime } from '@/utils/date-util';

  defineOptions({ name: 'ResourceRoute' });

  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);
  const selections = ref<Route[]>([]);
  const editVisible = ref(false);
  const editData = ref<Route | null>(null);

  const columns = ref<Columns>([
    { prop: 'routeName', label: '线路名称', minWidth: 140 },
    { prop: 'origin', label: '起点', minWidth: 140 },
    { prop: 'destination', label: '终点', minWidth: 140 },
    {
      prop: 'distance',
      label: '里程(km)',
      minWidth: 90,
      align: 'right'
    },
    {
      prop: 'estimatedHours',
      label: '预计时长(h)',
      minWidth: 90,
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
      prop: 'createdAt',
      label: '创建时间',
      width: 170,
      align: 'center',
      formatter: (row) => formatDateTime(row.createdAt)
    },
    {
      columnKey: 'action',
      label: '操作',
      width: 128,
      align: 'center',
      slot: 'action',
      fixed: 'right',
      hideInPrint: true,
      hideInExport: true
    }
  ]);

  const datasource: DatasourceFunction = ({ pages, where }) => {
    return pageRoutes({
      ...(where as RouteParam | undefined),
      ...pages
    }).then((res) => ({
      list: res?.list ?? [],
      count: res?.count ?? 0
    }));
  };

  const reload = (where?: RouteParam, page?: number) => {
    const t = tableRef.value;
    if (!t) return;
    const hasWhere = where !== undefined;
    const hasPage = page !== undefined;
    if (!hasWhere && !hasPage) {
      nextTick(() => t.reload?.());
      return;
    }
    const opt: { where?: RouteParam; page?: number } = {};
    if (hasWhere) opt.where = where;
    if (hasPage) opt.page = page;
    t.reload?.(opt);
  };

  const openEdit = (row?: Route) => {
    editData.value = row ?? null;
    editVisible.value = true;
  };

  const toggleRouteStatus = async (row: Route, status: number) => {
    if (!row.id) return;
    const loading = EleMessage.loading({
      message: '请求中..',
      plain: true
    });
    try {
      await updateRoute({ id: row.id, status });
      loading.close();
      EleMessage.success({
        message: status === 1 ? '已启用' : '已停用',
        plain: true
      });
      reload();
    } catch (e: unknown) {
      loading.close();
      const msg = e instanceof Error ? e.message : '操作失败';
      EleMessage.error({ message: msg, plain: true });
    }
  };

  const actionItems = (row: Route): ButtonItem[] => {
    const dropdown: ButtonDropdownItem[] = [];
    if (row.status === 1) {
      dropdown.push({
        title: '停用',
        icon: VideoPause,
        onClick: () => {
          void toggleRouteStatus(row, 0);
        }
      });
    } else {
      dropdown.push({
        title: '启用',
        icon: VideoPlay,
        onClick: () => {
          void toggleRouteStatus(row, 1);
        }
      });
    }
    dropdown.push({
      title: '删除',
      icon: DeleteOutlined,
      danger: true,
      divided: true,
      onClick: () => remove(row)
    });
    return [
      {
        preset: 'edit',
        title: '编辑',
        type: 'link',
        onClick: () => openEdit(row)
      },
      { preset: 'more', dropdownItems: dropdown }
    ];
  };

  const remove = (row: Route) => {
    ElMessageBox.confirm(`确定要删除线路"${row.routeName}"吗?`, '系统提示', {
      type: 'warning',
      draggable: true
    })
      .then(() => {
        const loading = EleMessage.loading({
          message: '请求中..',
          plain: true
        });
        removeRoute(row.id!)
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
