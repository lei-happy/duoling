<template>
  <ele-card header="表格后端分页">
    <div style="max-width: 260px">
      <ele-table-select
        clearable
        placeholder="请选择"
        value-key="userId"
        label-key="nickname"
        v-model="selectedValue"
        :table-props="tableProps"
        :popper-width="580"
        :disabled="disabled"
        :cache-data="cacheData"
        @select="handleSelect"
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
    <div style="margin-top: 12px; display: flex; align-items: center">
      <div style="padding-right: 12px">禁用:</div>
      <el-radio-group v-model="disabled">
        <el-radio :value="false" label="否" />
        <el-radio :value="true" label="是" />
      </el-radio-group>
    </div>
    <div style="margin-top: 8px">
      <el-button type="primary" @click="setValue">回显数据</el-button>
    </div>
  </ele-card>
</template>

<script lang="ts" setup>
  import { ref, reactive } from 'vue';
  import { pageUsers } from '@/api/system/user';
  import type { TableSelectProps } from 'ele-admin-plus/es/ele-table-select/props';
  import type { User } from '@/api/system/user/model';
  type SelectTableProps = Exclude<TableSelectProps['tableProps'], undefined>;

  /** 表格下拉选中值 */
  const selectedValue = ref<number>();

  /** 表格配置 */
  const tableProps = reactive<SelectTableProps>({
    datasource: ({ pages, where, orders }) => {
      return pageUsers({ ...where, ...orders, ...pages });
    },
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

  /** 禁用 */
  const disabled = ref(false);

  /** 缓存数据 */
  const cacheData = ref<Partial<User>[]>();

  /** 回显数据 */
  const setValue = () => {
    cacheData.value = [{ userId: 40, nickname: '管理员' }];
    selectedValue.value = 40;
  };

  /** 选中事件 */
  const handleSelect = (item: User) => {
    console.log(JSON.parse(JSON.stringify(item)));
  };
</script>
