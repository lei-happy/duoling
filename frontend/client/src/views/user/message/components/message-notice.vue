<template>
  <div>
    <ele-pro-table
      ref="tableRef"
      row-key="id"
      :columns="columns"
      :datasource="datasource"
      :show-overflow-tooltip="true"
      v-model:selections="selections"
      :highlight-current-row="true"
      :tools="proTableToolsWithExport"
      :export-config="{ fileName: '系统通知数据' }"
    >
      <template #toolbar>
        <el-button type="primary" class="ele-btn-icon" @click="confirm()">
          批量确认
        </el-button>
        <el-button type="danger" class="ele-btn-icon" @click="remove()">
          删除通知
        </el-button>
      </template>
      <template #status="{ row }">
        <ele-text v-if="row.status === 0" type="warning">未确认</ele-text>
        <ele-text v-else-if="row.status === 1" type="info">已确认</ele-text>
      </template>
      <template #action="{ row }">
        <el-link type="primary" underline="never" @click="confirm(row)">
          确认
        </el-link>
        <el-divider direction="vertical" />
        <el-link type="danger" underline="never" @click="remove(row)">
          删除
        </el-link>
      </template>
    </ele-pro-table>
  </div>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import { useMessage } from 'ele-admin-plus';
  import type { EleProTable } from 'ele-admin-plus';
  import type {
    DatasourceFunction,
    Columns
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import { proTableToolsWithExport } from '@/config/pro-table-tool-presets';
  import { pageNotices } from '@/api/example';
  import type { Message } from '@/api/example/model';

  const emit = defineEmits<{
    (e: 'reload'): void;
  }>();

  const messageIns = useMessage({ inner: true, plain: true });

  /** 表格实例 */
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
      prop: 'title',
      label: '通知标题',
      minWidth: 220
    },
    {
      prop: 'time',
      label: '通知时间',
      width: 180,
      align: 'center'
    },
    {
      prop: 'status',
      label: '状态',
      width: 90,
      align: 'center',
      slot: 'status',
      formatter: (row) => (row.status == 0 ? '未确认' : '已确认')
    },
    {
      columnKey: 'action',
      label: '操作',
      width: 120,
      align: 'center',
      slot: 'action',
      hideInPrint: true,
      hideInExport: true
    }
  ]);

  /** 列表选中数据 */
  const selections = ref<Message[]>([]);

  /** 表格数据源 */
  const datasource: DatasourceFunction = ({ pages, where, orders }) => {
    return pageNotices({ ...where, ...orders, ...pages });
  };

  /** 确认 */
  const confirm = (row?: Message) => {
    const rows = row == null ? selections.value : [row];
    if (!rows.length) {
      messageIns.error('请至少选择一条数据');
      return;
    }
    messageIns.success('点击了确认');
    updateUnReadNum();
  };

  /** 删除 */
  const remove = (row?: Message) => {
    const rows = row == null ? selections.value : [row];
    if (!rows.length) {
      messageIns.error('请至少选择一条数据');
      return;
    }
    messageIns.error('点击了删除');
  };

  /** 触发更新未读数量事件 */
  const updateUnReadNum = () => {
    emit('reload');
  };
</script>
