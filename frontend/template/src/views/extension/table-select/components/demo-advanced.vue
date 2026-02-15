<template>
  <ele-card header="可搜索">
    <div style="max-width: 260px">
      <ele-table-select
        ref="selectRef"
        multiple
        clearable
        placeholder="请选择"
        value-key="userId"
        label-key="nickname"
        v-model="selectedValue"
        :table-props="tableProps"
        :popper-width="580"
        :cache-data="cacheData"
        @select="handleSelect"
        :popper-options="{ strategy: 'fixed' }"
      >
        <template #topExtra>
          <demo-advanced-search @search="handleSearch" />
        </template>
        <!-- 角色列 -->
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
      </ele-table-select>
    </div>
    <div style="margin-top: 14px">
      <el-button type="primary" @click="setValue">回显数据</el-button>
    </div>
    <div style="margin: 22px 0 8px 0">使用默认的搜索框:</div>
    <div style="max-width: 260px">
      <ele-table-select
        filterable
        clearable
        placeholder="请选择"
        value-key="userId"
        label-key="nickname"
        v-model="selectedValue2"
        :table-props="tableProps2"
        :popper-width="580"
        @filterChange="handleFilterChange"
        @visibleChange="handleVisibleChange"
        :popper-options="{ strategy: 'fixed' }"
      >
        <!-- 角色列 -->
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
      </ele-table-select>
    </div>
  </ele-card>
</template>

<script lang="ts" setup>
  import { ref, reactive } from 'vue';
  import DemoAdvancedSearch from './demo-advanced-search.vue';
  import { pageUsers, listUsers } from '@/api/system/user';
  import type { EleTableSelect } from 'ele-admin-plus';
  import type { TableSelectProps } from 'ele-admin-plus/es/ele-table-select/props';
  import type { User, UserParam } from '@/api/system/user/model';
  type SelectTableProps = Exclude<TableSelectProps['tableProps'], undefined>;

  /** 表格下拉选中值 */
  const selectedValue = ref<number[]>([]);

  /** 选择框实例 */
  const selectRef = ref<InstanceType<typeof EleTableSelect> | null>(null);

  /** 表格配置 */
  const tableProps = reactive<SelectTableProps>({
    datasource: ({ pages, where, orders }) => {
      return pageUsers({ ...where, ...orders, ...pages });
    },
    columns: [
      {
        type: 'selection',
        columnKey: 'selection',
        width: 50,
        align: 'center',
        reserveSelection: true
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
        sortable: 'custom'
      },
      {
        prop: 'nickname',
        label: '用户名',
        sortable: 'custom',
        slot: 'nickname'
      },
      {
        prop: 'sexName',
        label: '性别',
        sortable: 'custom',
        width: 80
      },
      {
        columnKey: 'roles',
        label: '角色',
        slot: 'roles'
      }
    ],
    showOverflowTooltip: true,
    toolbar: false,
    pagination: {
      pageSize: 6,
      layout: 'total, prev, pager, next, jumper',
      style: { padding: '0px' }
    },
    rowClickChecked: true
  });

  /** 缓存数据 */
  const cacheData = ref<User[]>();

  /** 回显数据 */
  const setValue = () => {
    cacheData.value = [
      {
        userId: 40,
        nickname: '管理员'
      },
      {
        userId: 44,
        nickname: '用户四'
      },
      {
        userId: 45,
        nickname: '用户五'
      }
    ];
    selectedValue.value = [40, 44, 45];
  };

  /** 搜索 */
  const handleSearch = (where: UserParam) => {
    selectRef.value?.tableRef?.reload?.({ where, page: 1 });
  };

  /** 选中事件 */
  const handleSelect = (selection: User[]) => {
    console.log(JSON.parse(JSON.stringify(selection)));
  };

  /** 表格下拉选中值 */
  const selectedValue2 = ref<number>();

  /** 表格配置 */
  const tableProps2 = reactive<SelectTableProps>({
    datasource: [],
    columns: [
      {
        type: 'index',
        columnKey: 'index',
        width: 50,
        align: 'center'
      },
      {
        prop: 'username',
        label: '用户账号',
        sortable: 'custom'
      },
      {
        prop: 'nickname',
        label: '用户名',
        sortable: 'custom',
        slot: 'nickname'
      },
      {
        prop: 'sexName',
        label: '性别',
        sortable: 'custom',
        width: 80
      },
      {
        columnKey: 'roles',
        label: '角色',
        slot: 'roles'
      }
    ],
    showOverflowTooltip: true,
    highlightCurrentRow: true,
    toolbar: false,
    pagination: {
      pageSize: 6,
      layout: 'total, prev, pager, next, jumper',
      style: { padding: '0px' }
    },
    rowStyle: { cursor: 'pointer' }
  });

  let allData: User[] = [];

  /** 查询表格数据 */
  listUsers().then((data) => {
    tableProps2.datasource = data;
    allData = data;
  });

  /** 筛选输入框值改变事件 */
  const handleFilterChange = (keyword: string) => {
    tableProps2.datasource = allData.filter((d) => {
      return (
        d.username?.includes?.(keyword) ||
        d.nickname?.includes?.(keyword) ||
        d.sexName?.includes?.(keyword) ||
        d.roles?.some?.((r) => r.roleName?.includes?.(keyword))
      );
    });
  };

  /** 下拉框展开状态改变事件 */
  const handleVisibleChange = (visible: boolean) => {
    if (visible) {
      tableProps2.datasource = allData;
    }
  };
</script>
