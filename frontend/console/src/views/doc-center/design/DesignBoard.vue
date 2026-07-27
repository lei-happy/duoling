<template>
  <div class="design-board">
    <ele-card class="design-board-card" :body-style="{ padding: '12px 16px', height: '100%' }">
      <div class="toolbar">
        <div class="toolbar-left">
          <el-input
            v-model="filters.keyword"
            placeholder="搜索模块名称、负责人…"
            clearable
            style="width: 220px"
            @keyup.enter="reload"
            @clear="reload"
          />
          <el-select
            v-model="filters.product_line"
            clearable
            placeholder="产品端"
            style="width: 120px"
            @change="reload"
          >
            <el-option
              v-for="opt in PRODUCT_LINE_OPTIONS"
              :key="opt.value"
              :label="opt.label"
              :value="opt.value"
            />
          </el-select>
          <el-select
            v-model="filters.priority"
            clearable
            placeholder="优先级"
            style="width: 110px"
            @change="reload"
          >
            <el-option
              v-for="opt in PRIORITY_OPTIONS"
              :key="opt.value"
              :label="opt.label"
              :value="opt.value"
            />
          </el-select>
          <el-select
            v-if="viewMode === 'list'"
            v-model="filters.status"
            clearable
            placeholder="状态"
            style="width: 120px"
            @change="reload"
          >
            <el-option
              v-for="opt in STATUS_OPTIONS"
              :key="opt.value"
              :label="opt.label"
              :value="opt.value"
            />
          </el-select>
          <el-button @click="reload">查询</el-button>
        </div>
        <div class="toolbar-right">
          <el-radio-group v-model="viewMode" size="default" @change="reload">
            <el-radio-button value="list">列表</el-radio-button>
            <el-radio-button value="board">看板</el-radio-button>
          </el-radio-group>
          <el-button type="primary" @click="openEdit()">新建模块</el-button>
        </div>
      </div>

      <!-- 列表 -->
      <div v-if="viewMode === 'list'" class="list-wrap">
        <el-table
          v-loading="loading"
          :data="list"
          height="100%"
          stripe
          @row-click="(row: DesignModule) => openEdit(row)"
        >
          <el-table-column prop="title" label="模块名称" min-width="160" show-overflow-tooltip />
          <el-table-column label="产品端" width="100" align="center">
            <template #default="{ row }">
              {{ productLineLabel(row.product_line) }}
            </template>
          </el-table-column>
          <el-table-column label="优先级" width="120" align="center">
            <template #default="{ row }">
              <el-select
                :model-value="row.priority"
                size="small"
                style="width: 90px"
                @click.stop
                @change="(v: number) => onPriorityChange(row, v)"
              >
                <el-option
                  v-for="opt in PRIORITY_OPTIONS"
                  :key="opt.value"
                  :label="opt.label"
                  :value="opt.value"
                />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column label="状态" width="140" align="center">
            <template #default="{ row }">
              <el-select
                :model-value="row.status"
                size="small"
                style="width: 110px"
                @click.stop
                @change="(v: number) => onStatusChange(row, v)"
              >
                <el-option
                  v-for="opt in STATUS_OPTIONS"
                  :key="opt.value"
                  :label="opt.label"
                  :value="opt.value"
                />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column prop="pm_name" label="产品" width="100" show-overflow-tooltip />
          <el-table-column prop="designer_name" label="设计" width="100" show-overflow-tooltip />
          <el-table-column prop="developer_name" label="开发" width="100" show-overflow-tooltip />
          <el-table-column prop="updated_at" label="更新时间" width="170" align="center" />
        </el-table>
        <div class="pager">
          <el-pagination
            v-model:current-page="page"
            v-model:page-size="limit"
            :total="total"
            layout="total, prev, pager, next"
            background
            @current-change="loadList"
            @size-change="loadList"
          />
        </div>
      </div>

      <!-- 看板 -->
      <div v-else v-loading="loading" class="kanban-wrap">
        <div
          v-for="col in STATUS_OPTIONS"
          :key="col.value"
          class="kanban-column"
        >
          <div class="kanban-column-header">
            <span>{{ col.label }}</span>
            <el-tag size="small" type="info" :disable-transitions="true">
              {{ (boardMap[col.value] || []).length }}
            </el-tag>
          </div>
          <vue-draggable
            v-model="boardMap[col.value]"
            item-key="id"
            group="design-module"
            :animation="200"
            :set-data="() => void 0"
            class="kanban-list"
            @change="() => onBoardChange(col.value)"
          >
            <template #item="{ element }">
              <div class="kanban-card" @click="openEdit(element)">
                <div class="kanban-card-title">{{ element.title }}</div>
                <div class="kanban-card-meta">
                  <el-tag
                    size="small"
                    :type="priorityType(element.priority) || undefined"
                    :disable-transitions="true"
                  >
                    {{ priorityLabel(element.priority) }}
                  </el-tag>
                  <span class="meta-text">
                    {{ productLineLabel(element.product_line) }}
                  </span>
                </div>
                <div class="kanban-card-people">
                  <span v-if="element.pm_name">PM {{ element.pm_name }}</span>
                  <span v-if="element.designer_name">设计 {{ element.designer_name }}</span>
                  <span v-if="element.developer_name">开发 {{ element.developer_name }}</span>
                </div>
              </div>
            </template>
          </vue-draggable>
        </div>
      </div>
    </ele-card>

    <module-edit-drawer
      v-model:visible="drawerVisible"
      :record="currentRecord"
      @saved="reload"
    />
  </div>
</template>

<script lang="ts" setup>
  import { onMounted, reactive, ref } from 'vue';
  import VueDraggable from 'vuedraggable';
  import { EleMessage } from 'ele-admin-plus';
  import ModuleEditDrawer from './components/ModuleEditDrawer.vue';
  import {
    pageDesignModules,
    boardDesignModules,
    updateDesignModuleStatus,
    updateDesignModulePriority,
    sortDesignModules
  } from '@/api/doc-center/design-module';
  import type { DesignModule } from '@/api/doc-center/model/design-module';
  import {
    PRODUCT_LINE_OPTIONS,
    PRIORITY_OPTIONS,
    STATUS_OPTIONS,
    productLineLabel,
    priorityLabel,
    priorityType
  } from './constants';

  defineOptions({ name: 'DesignBoard' });

  const viewMode = ref<'list' | 'board'>('list');
  const loading = ref(false);
  const list = ref<DesignModule[]>([]);
  const page = ref(1);
  const limit = ref(20);
  const total = ref(0);
  const boardMap = reactive<Record<number, DesignModule[]>>(
    Object.fromEntries(STATUS_OPTIONS.map((s) => [s.value, []])) as Record<
      number,
      DesignModule[]
    >
  );

  const filters = reactive<{
    keyword: string;
    product_line: string | null;
    priority: number | null;
    status: number | null;
  }>({
    keyword: '',
    product_line: null,
    priority: null,
    status: null
  });

  const drawerVisible = ref(false);
  const currentRecord = ref<DesignModule | null>(null);

  const openEdit = (row?: DesignModule) => {
    currentRecord.value = row || null;
    drawerVisible.value = true;
  };

  const loadList = async () => {
    loading.value = true;
    try {
      const data = await pageDesignModules({
        page: page.value,
        limit: limit.value,
        keyword: filters.keyword || undefined,
        product_line: filters.product_line,
        priority: filters.priority,
        status: filters.status
      });
      list.value = data?.list || [];
      total.value = data?.total || 0;
    } catch (e: any) {
      EleMessage.error({
        message: e?.message || '加载失败，请稍后重试',
        plain: true
      });
    } finally {
      loading.value = false;
    }
  };

  const loadBoard = async () => {
    loading.value = true;
    try {
      const board = await boardDesignModules({
        keyword: filters.keyword || undefined,
        product_line: filters.product_line,
        priority: filters.priority
      });
      STATUS_OPTIONS.forEach((s) => {
        boardMap[s.value] = board[String(s.value)] || [];
      });
    } catch (e: any) {
      EleMessage.error({
        message: e?.message || '加载失败，请稍后重试',
        plain: true
      });
    } finally {
      loading.value = false;
    }
  };

  const reload = () => {
    if (viewMode.value === 'list') {
      page.value = 1;
      loadList();
    } else {
      loadBoard();
    }
  };

  const onStatusChange = async (row: DesignModule, status: number) => {
    try {
      await updateDesignModuleStatus(row.id, status);
      row.status = status;
      EleMessage.success({ message: '状态已更新', plain: true });
    } catch (e: any) {
      EleMessage.error({
        message: e?.message || '更新失败，请稍后重试',
        plain: true
      });
      reload();
    }
  };

  const onPriorityChange = async (row: DesignModule, priority: number) => {
    try {
      await updateDesignModulePriority(row.id, priority);
      row.priority = priority;
      EleMessage.success({ message: '优先级已更新', plain: true });
    } catch (e: any) {
      EleMessage.error({
        message: e?.message || '更新失败，请稍后重试',
        plain: true
      });
      reload();
    }
  };

  let sortTimer: ReturnType<typeof setTimeout> | null = null;
  const onBoardChange = (_status: number) => {
    if (sortTimer) clearTimeout(sortTimer);
    sortTimer = setTimeout(async () => {
      const items: { id: number; sort_order: number; status: number }[] = [];
      STATUS_OPTIONS.forEach((col) => {
        (boardMap[col.value] || []).forEach((item, index) => {
          item.status = col.value;
          item.sort_order = index;
          items.push({ id: item.id, sort_order: index, status: col.value });
        });
      });
      try {
        await sortDesignModules(items);
      } catch (e: any) {
        EleMessage.error({
          message: e?.message || '排序保存失败，请稍后重试',
          plain: true
        });
        loadBoard();
      }
    }, 300);
  };

  onMounted(() => {
    reload();
  });
</script>

<style lang="scss" scoped>
  .design-board {
    flex: 1;
    min-height: 0;
    overflow: hidden;
    display: flex;
  }

  .design-board-card {
    flex: 1;
    min-height: 0;

    :deep(.el-card) {
      height: 100%;
      display: flex;
      flex-direction: column;
    }

    :deep(.el-card__body) {
      flex: 1;
      min-height: 0;
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }
  }

  .toolbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
    flex-wrap: wrap;
    margin-bottom: 12px;
    flex-shrink: 0;
  }

  .toolbar-left,
  .toolbar-right {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
  }

  .list-wrap {
    flex: 1;
    min-height: 0;
    display: flex;
    flex-direction: column;
  }

  .pager {
    display: flex;
    justify-content: flex-end;
    padding-top: 12px;
    flex-shrink: 0;
  }

  .kanban-wrap {
    flex: 1;
    min-height: 0;
    display: flex;
    gap: 12px;
    overflow-x: auto;
    padding-bottom: 4px;
  }

  .kanban-column {
    width: 240px;
    min-width: 240px;
    background: var(--el-fill-color-light);
    border-radius: 8px;
    display: flex;
    flex-direction: column;
    max-height: 100%;
  }

  .kanban-column-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 10px 12px;
    font-weight: 600;
    font-size: 13px;
    flex-shrink: 0;
  }

  .kanban-list {
    flex: 1;
    overflow-y: auto;
    padding: 0 8px 8px;
    min-height: 80px;
  }

  .kanban-card {
    background: var(--el-bg-color);
    border: 1px solid var(--el-border-color-lighter);
    border-radius: 8px;
    padding: 10px 12px;
    margin-bottom: 8px;
    cursor: pointer;
    transition: box-shadow 0.15s ease;

    &:hover {
      box-shadow: var(--el-box-shadow-light);
    }
  }

  .kanban-card-title {
    font-size: 13px;
    font-weight: 500;
    margin-bottom: 8px;
    line-height: 1.4;
  }

  .kanban-card-meta {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 6px;
  }

  .meta-text {
    font-size: 12px;
    color: var(--el-text-color-secondary);
  }

  .kanban-card-people {
    display: flex;
    flex-direction: column;
    gap: 2px;
    font-size: 12px;
    color: var(--el-text-color-secondary);
  }
</style>
