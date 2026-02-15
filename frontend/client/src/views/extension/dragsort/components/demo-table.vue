<template>
  <ele-card header="表格拖拽排序">
    <el-row :gutter="16">
      <el-col
        v-for="(item, index) in taskList"
        :key="index"
        :md="8"
        :sm="24"
        :xs="24"
      >
        <ele-table :border="true" class="demo-table">
          <thead>
            <tr>
              <th style="width: 40px"></th>
              <th>任务名称</th>
              <th style="text-align: center; width: 80px">状态</th>
            </tr>
          </thead>
          <vue-draggable
            tag="tbody"
            item-key="id"
            :animation="300"
            :modelValue="item"
            :force-fallback="true"
            group="demoDragTable"
            handle=".demo-table-handle"
            :set-data="() => void 0"
            @update:modelValue="(value) => updateModelValue(value, index)"
          >
            <template #item="{ element }">
              <tr>
                <td style="text-align: center; width: 40px">
                  <ele-text
                    :icon="DragOutlined"
                    type="placeholder"
                    class="demo-table-handle"
                    style="cursor: move"
                  />
                </td>
                <td>{{ element.taskName }}</td>
                <td style="text-align: center; width: 80px">
                  <ele-text v-if="element.status === 0" type="warning">
                    未开始
                  </ele-text>
                  <ele-text v-else-if="element.status === 1" type="success">
                    进行中
                  </ele-text>
                  <ele-text v-else-if="element.status === 2" type="info">
                    已完成
                  </ele-text>
                </td>
              </tr>
            </template>
            <template #footer v-if="!item.length">
              <tr>
                <td colspan="3" style="text-align: center; background: none">
                  <ele-text type="placeholder">暂无数据</ele-text>
                </td>
              </tr>
            </template>
          </vue-draggable>
        </ele-table>
      </el-col>
    </el-row>
  </ele-card>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import VueDraggable from 'vuedraggable';
  import { DragOutlined } from '@/components/icons';

  interface Task {
    id: number;
    taskName: string;
    status: number;
  }

  /** 数据 */
  const taskList = ref<Task[][]>([]);

  /** 更新数据 */
  const updateModelValue = (value: Task[], index: number) => {
    taskList.value[index] = value;
  };

  /** 处理数据, 每6条数据一个表格 */
  const temp: Task[][] = [];
  for (let i = 0; i < 18; i++) {
    const index = Number.parseInt(String(i / 6));
    if (temp[index] == null) {
      temp[index] = [];
    }
    temp[index].push({
      id: i,
      taskName: `测试任务${i + 1}`,
      status: 0
    });
  }
  taskList.value = temp;
</script>

<style lang="scss" scoped>
  .demo-table {
    margin-bottom: 12px;
    table-layout: fixed;

    tr.sortable-chosen {
      user-select: none;
    }

    tr.sortable-ghost {
      opacity: 0;
    }

    tr.sortable-fallback {
      opacity: 1 !important;
      display: table !important;

      td {
        background: var(--el-color-primary-light-8);
        border-radius: 0 !important;
      }
    }
  }
</style>
