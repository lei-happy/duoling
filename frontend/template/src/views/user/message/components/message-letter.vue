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
      :export-config="{ fileName: '用户私信数据' }"
    >
      <template #toolbar>
        <el-button type="primary" class="ele-btn-icon" @click="readBatch">
          标记已读
        </el-button>
        <el-button type="danger" class="ele-btn-icon" @click="remove()">
          删除消息
        </el-button>
      </template>
      <template #status="{ row }">
        <ele-text v-if="row.status === 0" type="warning">未读</ele-text>
        <ele-text v-else-if="row.status === 1" type="info">已读</ele-text>
      </template>
      <template #action="{ row }">
        <el-link type="primary" underline="never" @click="reply(row)">
          回复
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
  import { pageLetters } from '@/api/example';
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
      label: '私信内容',
      minWidth: 220
    },
    {
      prop: 'time',
      label: '发送时间',
      width: 180,
      align: 'center'
    },
    {
      prop: 'status',
      label: '状态',
      width: 100,
      align: 'center',
      slot: 'status',
      formatter: (row) => (row.status == 0 ? '未读' : '已读')
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
    return pageLetters({ ...where, ...orders, ...pages });
  };

  /** 回复 */
  const reply = (row: Message) => {
    console.log(JSON.parse(JSON.stringify(row)));
    messageIns.success('点击了回复');
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

  /** 标记已读 */
  const readBatch = () => {
    if (!selections.value.length) {
      messageIns.error('请至少选择一条数据');
      return;
    }
    messageIns.success('点击了标记已读');
    updateUnReadNum();
  };

  /** 触发更新未读数量事件 */
  const updateUnReadNum = () => {
    emit('reload');
  };
</script>
