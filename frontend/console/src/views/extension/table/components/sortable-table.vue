<template>
  <div style="padding-top: 8px">
    <ele-pro-table
      ref="tableRef"
      row-key="userId"
      :columns="columns"
      :datasource="datasource"
      :show-overflow-tooltip="true"
      :pagination="false"
      v-model:selections="selections"
      class="sortable-table"
      :export-config="{ fileName: '用户数据' }"
    >
      <template #handle>
        <ele-text
          :icon="HolderOutlined"
          type="placeholder"
          class="sort-handle"
        />
      </template>
      <template #status="{ row }">
        <ele-dot v-if="row.status === 0" text="正常" size="8px" />
        <ele-dot
          v-else-if="row.status === 1"
          text="冻结"
          type="danger"
          :ripple="false"
          size="8px"
        />
      </template>
      <template #toolbar>
        <el-button type="primary" @click="getSelections" class="ele-btn-icon">
          获取选中
        </el-button>
      </template>
    </ele-pro-table>
  </div>
</template>

<script lang="ts" setup>
  import { ref, onMounted, onBeforeUnmount } from 'vue';
  import { EleMessage } from 'ele-admin-plus';
  import SortableJs from 'sortablejs';
  import type { EleProTable } from 'ele-admin-plus';
  import type {
    DatasourceFunction,
    Columns
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import { HolderOutlined } from '@/components/icons';
  import type { User } from '@/api/system/user/model';
  import { listUsers } from '@/api/system/user';

  /** 排序实例 */
  let sortableIns: SortableJs | null = null;

  /** 表格实例 */
  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);

  /** 表格选中数据 */
  const selections = ref<User[]>([]);

  /** 表格列配置 */
  const columns = ref<Columns>([
    {
      columnKey: 'handle',
      width: 58,
      align: 'center',
      slot: 'handle',
      hideInPrint: true,
      hideInExport: true
    },
    {
      type: 'selection',
      columnKey: 'selection',
      width: 50,
      align: 'center',
      reserveSelection: true
    },
    {
      prop: 'username',
      label: '用户账号',
      minWidth: 110
    },
    {
      prop: 'nickname',
      label: '用户名',
      minWidth: 110
    },
    {
      columnKey: 'sex',
      prop: 'sexName',
      label: '性别',
      width: 110,
      align: 'center',
      filters: [
        { text: '男', value: '1' },
        { text: '女', value: '2' }
      ],
      filterMultiple: false
    },
    {
      prop: 'createTime',
      label: '创建时间',
      width: 180,
      align: 'center'
    },
    {
      prop: 'status',
      label: '状态',
      width: 130,
      align: 'center',
      slot: 'status',
      formatter: (row) => (row.status == 0 ? '正常' : '冻结')
    }
  ]);

  /** 表格数据 */
  const datasource: DatasourceFunction = ({ where, orders, filters }) => {
    return listUsers({ ...where, ...orders, ...filters });
  };

  onMounted(() => {
    // 支持拖拽排序
    const tableEl = tableRef.value?.$el;
    if (!tableEl) {
      return;
    }
    const tbodyEl = tableEl.querySelector(
      '.el-table__inner-wrapper > .el-table__body-wrapper .el-table__body > tbody'
    ) as HTMLElement;
    sortableIns = new SortableJs(tbodyEl, {
      animation: 300,
      draggable: '.el-table__row',
      handle: '.sort-handle',
      forceFallback: true,
      onUpdate: ({ oldDraggableIndex, newDraggableIndex }) => {
        if (
          typeof oldDraggableIndex === 'number' &&
          typeof newDraggableIndex === 'number'
        ) {
          const temp = [...(tableRef.value?.getData?.() ?? [])];
          temp.splice(
            newDraggableIndex,
            0,
            temp.splice(oldDraggableIndex, 1)[0]
          );
          tableRef.value?.setData?.(temp);
          Array.from(
            tbodyEl.querySelectorAll('.el-table__row.hover-row')
          ).forEach((el) => {
            el.classList.remove('hover-row');
          });
        }
      },
      onChange: () => {
        Array.from(
          tbodyEl.querySelectorAll('.el-table__row.hover-row')
        ).forEach((el) => {
          el.classList.remove('hover-row');
        });
      },
      setData: () => {}
    });
  });

  onBeforeUnmount(() => {
    if (sortableIns) {
      sortableIns.destroy();
      sortableIns = null;
    }
  });

  /** 获取选中数据 */
  const getSelections = () => {
    const data = tableRef.value?.getData?.() ?? [];
    const result = [...selections.value].sort((a, b) => {
      const ai = data.findIndex((d) => d.userId === a.userId);
      const bi = data.findIndex((d) => d.userId === b.userId);
      return ai - bi;
    });
    console.log(JSON.parse(JSON.stringify(result)));
    EleMessage.success({
      message: `共选中 ${selections.value.length} 条数据, 已打印在控制台`,
      plain: true
    });
  };
</script>

<style lang="scss" scoped>
  .sort-handle {
    cursor: move;
  }

  .sortable-table :deep(.el-table) {
    .el-table__row {
      &.sortable-chosen {
        user-select: none;
      }

      &.sortable-ghost {
        opacity: 0;
      }

      &.sortable-fallback {
        opacity: 1 !important;

        td.el-table__cell {
          background: var(--el-color-primary-light-8);
        }
      }
    }

    &:has(.el-table__row.sortable-chosen) .el-table__row td.el-table__cell {
      cursor: move;

      & > .cell {
        pointer-events: none;
      }
    }
  }
</style>
