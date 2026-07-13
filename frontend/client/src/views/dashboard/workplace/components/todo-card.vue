<!-- 我的待办 -->
<template>
  <ele-card
    :body-style="{ padding: '6px 0', height: '520px' }"
    class="todo-card"
  >
    <template #header>
      <div class="card-header">
        <span class="card-title">{{ title }}</span>
        <button type="button" class="create-link" @click="showCreateForm = true">
          <el-icon><CirclePlus /></el-icon>
          <span>创建待办</span>
        </button>
      </div>
    </template>
    <template #extra>
      <!-- 阻止工作台 Sortable 在 header/extra 区域抢 mousedown，否则下拉菜单点不到、刷新无效 -->
      <div class="todo-card-extra-inner" @mousedown.stop>
        <div class="todo-tabs">
          <!-- 状态筛选（文字下划线 tab） -->
          <button
            v-for="item in statusOptions"
            :key="item.value"
            :id="`todo-filter-status-${item.value}`"
            type="button"
            class="todo-tab"
            :class="{ 'is-active': activeStatus === item.value }"
            @click="switchStatus(item.value)"
          >
            {{ item.label }}
            <span class="status-count">({{ getStatusCount(item.value) }})</span>
          </button>
        </div>
        <more-icon
          :hide-edit="true"
          :hide-remove="true"
          @command="handleCommand"
        />
      </div>
    </template>

    <el-scrollbar :view-style="{ padding: '0px 20px 0 20px' }">
      <div v-if="loading" class="task-loading">
        <el-skeleton :rows="5" animated />
      </div>
      <div v-else-if="!tasks.length" class="task-empty">
        <el-empty description="暂无待办任务" />
      </div>
      <div v-else class="task-list">
        <div
          v-for="task in tasks"
          :key="task.id"
          class="task-item"
          :class="{
            completed: task.status === 2,
            'in-progress': task.status === 1
          }"
          @click="editTask(task)"
        >
          <!-- 复选框 -->
          <div class="task-checkbox" @click.stop>
            <el-checkbox
              :model-value="task.status === 2"
              @change="(val) => handleTaskToggle(task, val)"
              :disabled="task.status === 3"
              style="margin-top: -12px"
            />
          </div>

          <!-- 任务内容 -->
          <div class="task-content">
            <!-- 任务标题 -->
            <div
              class="task-title"
              :class="{ 'completed-title': task.status === 2 }"
            >
              {{ task.title }}
            </div>

            <!-- 任务描述 -->
            <div class="task-description" v-if="task.description">
              {{ task.description }}
            </div>

            <!-- 元信息行 -->
            <div class="task-meta-row">
              <div class="task-meta">
                <!-- 优先级 - 放在最前面 -->
                <span
                  v-if="task.priority > 0"
                  :class="[
                    'priority-indicator',
                    getPriorityClass(task.priority)
                  ]"
                >
                  {{ getPriorityText(task.priority) }}
                </span>

                <!-- 创建人 -->
                <span class="meta-item creator-info" v-if="task.creator_name">
                  <el-icon class="meta-icon"><EditPen /></el-icon>
                  <span class="meta-text">{{ task.creator_name }}</span>
                </span>

                <!-- 主责任人 -->
                <span class="meta-item assignee-info" v-if="task.assignee_name">
                  <el-icon class="meta-icon"><Avatar /></el-icon>
                  <span class="meta-text">指派：{{ task.assignee_name }}</span>
                </span>

                <!-- 已完成任务显示创建时间和完成时间 -->
                <span
                  class="meta-item"
                  v-if="task.status === 2 && task.create_time"
                >
                  <el-icon class="meta-icon"><Clock /></el-icon>
                  <span class="meta-text create-time">
                    创建时间：{{ formatCompletedTime(task.create_time) }}
                  </span>
                </span>

                <span
                  class="meta-item"
                  v-if="task.status === 2 && task.completed_time"
                >
                  <el-icon class="meta-icon"><Clock /></el-icon>
                  <span class="meta-text completed-time">
                    完成时间：{{ formatCompletedTime(task.completed_time) }}
                  </span>
                </span>

                <!-- 非已完成任务显示截止时间 -->
                <span
                  class="meta-item"
                  v-if="task.status !== 2 && task.due_time"
                >
                  <el-icon class="meta-icon"><Clock /></el-icon>
                  <span
                    class="meta-text"
                    :class="{ overdue: isOverdue(task.due_time) }"
                  >
                    截至：{{ formatTime(task.due_time) }}
                  </span>
                </span>
              </div>
            </div>
          </div>

          <!-- 更多操作：右上角竖排 -->
          <div class="task-more-action" @click.stop>
            <el-dropdown
              trigger="click"
              @command="(cmd) => handleTaskAction(task, cmd)"
            >
              <el-button
                link
                size="small"
                :icon="MoreFilled"
                class="action-btn"
              />
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="delete" class="delete-option">
                    <el-icon><Delete /></el-icon>
                    删除
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>

          <!-- 开始处理/任务完成：右侧垂直居中 -->
          <div class="task-quick-actions" @click.stop>
            <el-button
              v-if="task.status === 0"
              link
              size="small"
              @click="updateTaskStatus(task, 1)"
              class="quick-action-btn start-btn"
            >
              开始处理
            </el-button>
            <el-button
              v-if="task.status === 1"
              link
              size="small"
              @click="updateTaskStatus(task, 2)"
              class="quick-action-btn complete-btn"
            >
              任务完成
            </el-button>
          </div>
        </div>

        <!-- 加载更多指示器 -->
        <div
          v-if="hasMore && !loading"
          ref="loadMoreTrigger"
          class="load-more-trigger"
        >
          <div v-if="loadingMore" class="loading-more">
            <el-skeleton :rows="2" animated />
          </div>
        </div>

        <!-- 没有更多数据提示 -->
        <div v-if="!hasMore && tasks.length > 0" class="no-more-data">
          <span>已加载全部待办任务</span>
        </div>
      </div>
    </el-scrollbar>

    <!-- 创建任务对话框 -->
    <el-dialog
      v-model="showCreateForm"
      title="创建新任务"
      width="800px"
      :close-on-click-modal="false"
    >
      <el-form
        :model="createForm"
        :rules="createRules"
        ref="createFormRef"
        label-width="90px"
      >
        <el-form-item label="任务标题" prop="title" required>
          <el-input
            id="create-task-title"
            v-model="createForm.title"
            placeholder="请输入任务标题（必填）"
            maxlength="255"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="任务描述">
          <el-input
            id="create-task-description"
            v-model="createForm.description"
            type="textarea"
            placeholder="请输入任务描述（可选）"
            :rows="3"
            :autosize="{ minRows: 3, maxRows: 6 }"
            resize="vertical"
          />
        </el-form-item>

        <el-form-item label="优先级">
          <el-radio-group
            id="create-task-priority"
            v-model="createForm.priority"
            class="priority-radio-group"
          >
            <el-radio
              v-for="item in priorityOptions"
              :key="item.value"
              :id="`create-priority-${item.value}`"
              :value="item.value"
              class="priority-radio"
            >
              {{ item.label }}
            </el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="截止时间">
          <el-date-picker
            id="create-task-due-time"
            v-model="createForm.due_time"
            type="datetime"
            placeholder="选择截止时间（可选）"
            format="YYYY-MM-DD HH:mm"
            value-format="YYYY-MM-DD HH:mm:ss"
            :disabled-date="(time) => time.getTime() < Date.now() - 8.64e7"
            :disabled-hours="getDisabledHours"
            :disabled-minutes="getDisabledMinutes"
            :default-time="new Date(2000, 1, 1, 18, 0, 0)"
            style="width: 100%"
          />
        </el-form-item>

        <!-- @用户功能 -->
        <el-form-item label="指派给">
          <el-select
            id="create-task-assignee"
            v-model="createForm.assignee_id"
            placeholder="@某人设为主责任人（可选）"
            filterable
            remote
            :remote-method="searchUsers"
            :loading="searchLoading"
            clearable
            :clear-icon="undefined"
            @focus="handleUserSelectFocus"
            @clear="(createForm.assignee_id as any) = null"
            style="width: 100%"
          >
            <el-option
              v-for="user in userOptions"
              :key="user.id"
              :label="user.display_name"
              :value="user.id"
            />
          </el-select>
        </el-form-item>
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="closeCreateDialog">取消</el-button>
          <el-button type="primary" @click="createTask" :loading="createLoading"
            >创建</el-button
          >
        </span>
      </template>
    </el-dialog>

    <!-- 编辑任务对话框 -->
    <el-dialog
      v-model="showEditForm"
      title="编辑任务"
      width="800px"
      :close-on-click-modal="false"
    >
      <el-form
        :model="editForm"
        :rules="createRules"
        ref="editFormRef"
        label-width="90px"
      >
        <el-form-item label="任务标题" prop="title" required>
          <el-input
            id="edit-task-title"
            v-model="editForm.title"
            placeholder="请输入任务标题（必填）"
            maxlength="255"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="任务描述">
          <el-input
            id="edit-task-description"
            v-model="editForm.description"
            type="textarea"
            placeholder="请输入任务描述（可选）"
            :rows="3"
            :autosize="{ minRows: 3, maxRows: 6 }"
            resize="vertical"
          />
        </el-form-item>

        <el-form-item label="优先级">
          <el-radio-group
            id="edit-task-priority"
            v-model="editForm.priority"
            class="priority-radio-group"
          >
            <el-radio
              v-for="item in priorityOptions"
              :key="item.value"
              :id="`edit-priority-${item.value}`"
              :value="item.value"
              class="priority-radio"
            >
              {{ item.label }}
            </el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="截止时间">
          <el-date-picker
            id="edit-task-due-time"
            v-model="editForm.due_time"
            type="datetime"
            placeholder="选择截止时间（可选）"
            format="YYYY-MM-DD HH:mm"
            value-format="YYYY-MM-DD HH:mm:ss"
            :disabled-date="(time) => time.getTime() < Date.now() - 8.64e7"
            :disabled-hours="getDisabledHours"
            :disabled-minutes="getDisabledMinutes"
            :default-time="new Date(2000, 1, 1, 18, 0, 0)"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="状态">
          <el-radio-group
            id="edit-task-status"
            v-model="editForm.status"
            class="status-radio-group"
          >
            <el-radio
              v-for="item in editStatusOptions"
              :key="item.value"
              :id="`edit-status-${item.value}`"
              :value="item.value"
              class="status-radio"
            >
              {{ item.label }}
            </el-radio>
          </el-radio-group>
        </el-form-item>

        <!-- 编辑时的@用户功能 -->
        <el-form-item label="指派给">
          <el-select
            id="edit-task-assignee"
            v-model="editForm.assignee_id"
            placeholder="@某人设为主责任人（可选）"
            filterable
            remote
            :remote-method="searchUsers"
            :loading="searchLoading"
            clearable
            @focus="handleUserSelectFocus"
            @clear="(editForm.assignee_id as any) = null"
            style="width: 100%"
          >
            <el-option
              v-for="user in userOptions"
              :key="user.id"
              :label="user.display_name"
              :value="user.id"
            />
          </el-select>
        </el-form-item>
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showEditForm = false">取消</el-button>
          <el-button type="primary" @click="saveEditTask" :loading="editLoading"
            >保存</el-button
          >
        </span>
      </template>
    </el-dialog>
  </ele-card>
</template>

<script lang="ts" setup>
  import { ref, reactive, onMounted, onUnmounted, nextTick } from 'vue';
  import { ElMessage, ElMessageBox } from 'element-plus';
  import {
    Delete,
    Clock,
    MoreFilled,
    EditPen,
    Avatar,
    CirclePlus
  } from '@element-plus/icons-vue';
  import MoreIcon from './more-icon.vue';
  import type { Command } from '../model';

  import {
    getTodoTaskList,
    createTodoTask,
    updateTodoTask,
    deleteTodoTask,
    updateTaskStatus as updateTaskStatusAPI,
    getUsersForAssignment,
    getTodoTaskStats
  } from '@/api/home/workbench/todo';

  import type { TodoTask } from '@/api/home/workbench/todo/types';

  defineOptions({ name: 'TodoCard' });

  // Props
  interface Props {
    title?: string;
  }

  withDefaults(defineProps<Props>(), {
    title: '我的待办'
  });

  const emit = defineEmits<{
    (e: 'command', command: Command): void;
  }>();

  // 状态选项
  const statusOptions = [
    { label: '待处理', value: 0 },
    { label: '进行中', value: 1 },
    { label: '已完成', value: 2 }
  ];

  // 编辑时的状态选项（不包括全部）
  const editStatusOptions = [
    { label: '待处理', value: 0 },
    { label: '进行中', value: 1 },
    { label: '已完成', value: 2 }
  ];

  // 优先级选项
  const priorityOptions = [
    { label: '低', value: 0 },
    { label: '中', value: 1 },
    { label: '高', value: 2 }
  ];

  // 响应式数据
  const loading = ref(false);
  const activeStatus = ref(0); // 默认显示待处理任务
  const tasks = ref<TodoTask[]>([]);
  const stats = ref({ total: 0, pending: 0, in_progress: 0, completed: 0 });

  // 分页相关状态
  const currentPage = ref(1);
  const pageSize = ref(50);
  const hasMore = ref(true);
  const loadingMore = ref(false);

  // 创建表单
  const showCreateForm = ref(false);
  const createLoading = ref(false);
  const createFormRef = ref();
  const createForm = reactive({
    title: '',
    description: '',
    priority: 1, // 默认中等优先级
    due_time: '',
    status: 0, // 默认待处理状态
    assignee_id: undefined as number | undefined
  });

  // 编辑表单
  const showEditForm = ref(false);
  const editLoading = ref(false);
  const editFormRef = ref();
  const editForm = reactive({
    id: undefined as number | undefined,
    title: '',
    description: '',
    priority: 1,
    due_time: '',
    status: 0,
    assignee_id: undefined as number | undefined
  });

  // 用户选择
  const userOptions = ref<any[]>([]);
  const searchLoading = ref(false);

  // 滚动加载相关
  const loadMoreTrigger = ref<HTMLElement>();
  const observer = ref<IntersectionObserver | null>(null);

  // 表单验证规则
  const createRules = {
    title: [
      { required: true, message: '请输入任务标题', trigger: 'blur' },
      { min: 1, message: '任务标题不能为空', trigger: 'blur' },
      { max: 255, message: '标题长度不能超过255字符', trigger: 'blur' }
    ]
  };

  // 获取所有状态的统计信息
  const fetchStats = async () => {
    try {
      const res = await getTodoTaskStats();
      const statsData = (res.data as any)?.data;

      if (statsData) {
        stats.value = {
          total: statsData.total,
          pending: statsData.pending,
          in_progress: statsData.in_progress,
          completed: statsData.completed
        };
      }
    } catch (error) {
      console.error('获取统计信息失败:', error);
      // 如果获取失败，使用默认值
      stats.value = {
        total: 0,
        pending: 0,
        in_progress: 0,
        completed: 0
      };
    }
  };

  // 方法
  const fetchTasks = async (reset: boolean = true) => {
    try {
      if (reset) {
        loading.value = true;
        currentPage.value = 1;
        hasMore.value = true;
      } else {
        loadingMore.value = true;
      }

      const res = await getTodoTaskList({
        my_tasks: true,
        page: currentPage.value,
        page_size: pageSize.value,
        status: activeStatus.value
      });

      const responseData = (res.data as any)?.data;
      const newTasks = responseData?.items || [];
      const totalPages = responseData?.pages || 1;

      if (reset) {
        tasks.value = newTasks;
      } else {
        tasks.value.push(...newTasks);
      }

      // 检查是否还有更多数据
      hasMore.value = currentPage.value < totalPages;
    } catch (error) {
      ElMessage.error('获取任务列表失败');
    } finally {
      loading.value = false;
      loadingMore.value = false;
    }
  };

  // 获取所有用户列表（参考station-comment的实现）
  const fetchAllUsers = async () => {
    try {
      const res = await getUsersForAssignment(); // 不传关键词，获取所有用户
      userOptions.value = (res.data as any)?.data || [];
    } catch (error) {
      console.error('获取用户列表失败:', error);
    }
  };

  const searchUsers = async (query: string) => {
    // 如果查询为空或只有@符号，显示所有用户
    if (!query || query === '@') {
      await fetchAllUsers();
      return;
    }

    try {
      searchLoading.value = true;
      const res = await getUsersForAssignment(query);
      userOptions.value = (res.data as any)?.data || [];
    } catch (error) {
      console.error('搜索用户失败:', error);
    } finally {
      searchLoading.value = false;
    }
  };

  const handleStatusChange = async (status: number) => {
    console.log('状态切换到:', status);
    // 状态切换时重新获取数据
    await fetchTasks(true);
    // 同时更新统计信息
    await fetchStats();
  };

  /** 切换状态 tab（先更新选中态再拉取数据） */
  const switchStatus = (status: number) => {
    if (activeStatus.value === status) {
      return;
    }
    activeStatus.value = status;
    handleStatusChange(status);
  };

  // 加载更多任务
  const loadMoreTasks = async () => {
    if (!hasMore.value || loadingMore.value) {
      return;
    }

    currentPage.value += 1;
    await fetchTasks(false);
  };

  // 处理用户选择框聚焦事件
  const handleUserSelectFocus = async () => {
    // 如果用户列表为空，则加载所有用户
    if (userOptions.value.length === 0) {
      await fetchAllUsers();
    }
  };

  const handleTaskToggle = async (task: TodoTask, checked: any) => {
    const newStatus = checked ? 2 : 0;
    await updateTaskStatus(task, newStatus);
  };

  const updateTaskStatus = async (task: TodoTask, status: number) => {
    try {
      const res = await updateTaskStatusAPI(task.id, status);
      // 使用API返回的完整数据更新本地任务对象
      const updatedTask = (res.data as any)?.data;
      if (updatedTask) {
        Object.assign(task, updatedTask);
      } else {
        // 如果API没有返回完整数据，至少更新状态和时间
        task.status = status;
        if (status === 2) {
          task.completed_time = new Date().toISOString();
        } else {
          task.completed_time = undefined;
        }
      }

      // 更新统计信息
      await fetchStats();

      // 如果任务的新状态与当前选中的状态不匹配，从显示列表中移除
      if (task.status !== activeStatus.value) {
        const index = tasks.value.findIndex((t) => t.id === task.id);
        if (index !== -1) {
          tasks.value.splice(index, 1);
        }
      }

      ElMessage.success(`任务状态已更新为${getStatusText(status)}`);
    } catch (error) {
      ElMessage.error('更新任务状态失败');
    }
  };

  const getStatusText = (status: number) => {
    const statusMap = { 0: '待处理', 1: '进行中', 2: '已完成', 3: '已关闭' };
    return statusMap[status] || '未知';
  };

  const createTask = async () => {
    if (!createFormRef.value) return;

    try {
      await createFormRef.value.validate();
      createLoading.value = true;

      // 构建符合后端schema要求的数据
      const taskData = {
        title: createForm.title,
        description: createForm.description || undefined,
        priority: createForm.priority,
        status: createForm.status,
        due_time: createForm.due_time || undefined, // 空字符串转换为undefined
        assignee_id: createForm.assignee_id as number | null | undefined // 允许null
      };

      // 移除值为undefined的字段
      Object.keys(taskData).forEach((key) => {
        if (taskData[key] === undefined) {
          delete taskData[key];
        }
      });

      await createTodoTask(taskData);
      ElMessage.success('任务创建成功');

      // 重置表单
      resetCreateForm();
      showCreateForm.value = false;

      // 刷新列表和统计信息
      await fetchTasks();
      await fetchStats();
    } catch (error) {
      if (error !== false) {
        // 表单验证失败时返回false
        console.error('创建任务失败:', error);
        ElMessage.error('创建任务失败');
      }
    } finally {
      createLoading.value = false;
    }
  };

  const editTask = (task: TodoTask) => {
    Object.assign(editForm, {
      id: task.id,
      title: task.title,
      description: task.description || '',
      priority: task.priority,
      due_time: task.due_time || '',
      status: task.status,
      assignee_id: task.assignee_id // 保持原值，不转换null为undefined
    });

    showEditForm.value = true;
  };

  const saveEditTask = async () => {
    if (!editFormRef.value) return;

    try {
      await editFormRef.value.validate();
      editLoading.value = true;

      const { id, ...updateData } = editForm;

      // 构建符合后端schema要求的数据
      const taskUpdateData = {
        title: updateData.title,
        description: updateData.description || undefined,
        priority: updateData.priority,
        status: updateData.status,
        due_time: updateData.due_time || undefined, // 空字符串转换为undefined
        assignee_id: updateData.assignee_id as number | null | undefined // 允许null来清空指派人
      };

      // 移除值为undefined的字段（但保留null值用于清空指派人）
      // 特别注意：null值需要保留以清空assignee_id
      Object.keys(taskUpdateData).forEach((key) => {
        const value = taskUpdateData[key];
        if (value === undefined) {
          delete taskUpdateData[key];
        }
        // 保留null值不删除，让后端知道要清空此字段
      });

      const res = await updateTodoTask(id as number, taskUpdateData);
      const updatedTaskData = (res.data as any)?.data;

      ElMessage.success('任务更新成功');
      showEditForm.value = false;

      // 更新统计信息
      await fetchStats();

      // 如果任务状态发生了变化，需要处理显示列表
      if (updatedTaskData && updatedTaskData.status !== activeStatus.value) {
        // 如果任务的新状态与当前选中的状态不匹配，从显示列表中移除
        const index = tasks.value.findIndex((t) => t.id === id);
        if (index !== -1) {
          tasks.value.splice(index, 1);
        }
      } else if (updatedTaskData) {
        // 如果状态匹配，更新任务数据
        const index = tasks.value.findIndex((t) => t.id === id);
        if (index !== -1) {
          Object.assign(tasks.value[index], updatedTaskData);
        }
      }
    } catch (error) {
      if (error !== false) {
        // 表单验证失败时返回false
        console.error('更新任务失败:', error);
        ElMessage.error('更新任务失败');
      }
    } finally {
      editLoading.value = false;
    }
  };

  const handleTaskAction = async (task: TodoTask, command: string) => {
    switch (command) {
      case 'delete':
        await deleteTask(task);
        break;
    }
  };

  const deleteTask = async (task: TodoTask) => {
    try {
      await ElMessageBox.confirm(`确定要删除任务"${task.title}"吗？`, '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      });

      await deleteTodoTask(task.id);
      ElMessage.success('任务删除成功');

      // 刷新列表和统计信息
      await fetchTasks();
      await fetchStats();
    } catch (error) {
      if (error !== 'cancel') {
        ElMessage.error('删除任务失败');
      }
    }
  };

  const closeCreateDialog = () => {
    resetCreateForm();
    showCreateForm.value = false;
  };

  const resetCreateForm = () => {
    if (createFormRef.value) {
      createFormRef.value.resetFields();
    }
    Object.assign(createForm, {
      title: '',
      description: '',
      priority: 1, // 默认中等优先级
      due_time: '',
      status: 0, // 默认待处理状态
      assignee_id: undefined as number | undefined
    });
    userOptions.value = [];
  };

  const getPriorityText = (priority: number) => {
    const texts = ['低', '中', '高'];
    return texts[priority] || '低';
  };

  // 获取优先级样式类
  const getPriorityClass = (priority: number) => {
    const classes = ['low', 'medium', 'high'];
    return classes[priority] || 'low';
  };

  // 获取状态计数
  const getStatusCount = (status: number) => {
    switch (status) {
      case 0:
        return stats.value.pending;
      case 1:
        return stats.value.in_progress;
      case 2:
        return stats.value.completed;
      default:
        return 0;
    }
  };

  // 判断是否过期
  const isOverdue = (dueTime: string) => {
    if (!dueTime) return false;
    const date = new Date(dueTime);
    const now = new Date();
    return date.getTime() < now.getTime();
  };

  const formatTime = (time: string) => {
    if (!time) return '';
    const date = new Date(time);
    const now = new Date();

    // 格式化为 MM-DD HH:mm
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');

    const formattedTime = `${month}-${day} ${hours}:${minutes}`;

    // 判断是否过期，用于样式标识
    const isExpired = date.getTime() < now.getTime();
    return isExpired ? `${formattedTime} (已过期)` : formattedTime;
  };

  const formatCompletedTime = (time: string) => {
    if (!time) return '';
    const date = new Date(time);

    // 格式化为 MM-DD HH:mm，完成时间不显示过期状态
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');

    return `${month}-${day} ${hours}:${minutes}`;
  };

  // 禁用历史小时（当选择今天时才禁用过去的小时）
  const getDisabledHours = () => {
    const now = new Date();
    const today = new Date().toDateString();

    // 检查当前选择的日期是否是今天（通过表单值判断）
    const selectedDateStr = createForm.due_time || editForm.due_time || '';
    if (selectedDateStr) {
      const selectedDate = new Date(selectedDateStr);
      if (selectedDate.toDateString() === today) {
        // 如果选择的是今天，禁用当前小时之前的小时
        const hours: number[] = [];
        for (let i = 0; i < now.getHours(); i++) {
          hours.push(i);
        }
        return hours;
      }
    }

    return [];
  };

  // 禁用历史分钟（当选择今天且当前小时时才禁用过去的分钟）
  const getDisabledMinutes = (selectedHour: number) => {
    const now = new Date();
    const today = new Date().toDateString();

    // 检查当前选择的日期是否是今天
    const selectedDateStr = createForm.due_time || editForm.due_time || '';
    if (selectedDateStr) {
      const selectedDate = new Date(selectedDateStr);
      if (
        selectedDate.toDateString() === today &&
        selectedHour === now.getHours()
      ) {
        // 如果选择的是今天且是当前小时，禁用当前分钟及之前的分钟
        const minutes: number[] = [];
        for (let i = 0; i <= now.getMinutes(); i++) {
          minutes.push(i);
        }
        return minutes;
      }
    }

    return [];
  };

  /** 解析 ele-dropdown 下发的 command（兼容字符串或对象） */
  const normalizeCommand = (command: unknown): string => {
    if (command == null) return '';
    if (typeof command === 'string') return command;
    if (typeof command === 'object' && 'command' in command) {
      const c = (command as { command: unknown }).command;
      return c != null ? String(c) : '';
    }
    return String(command);
  };

  /** 处理更多操作命令 */
  const handleCommand = async (command: unknown) => {
    const cmd = normalizeCommand(command);
    if (cmd === 'refresh') {
      try {
        await Promise.all([fetchTasks(true), fetchStats()]);
      } catch {
        /* fetchTasks / fetchStats 内已提示 */
      }
      return;
    }
    emit('command', cmd as Command);
  };

  // 初始化滚动加载监听器
  const initInfiniteScroll = () => {
    if (!loadMoreTrigger.value || observer.value) return;

    observer.value = new IntersectionObserver(
      (entries) => {
        const [entry] = entries;
        if (entry.isIntersecting && hasMore.value && !loadingMore.value) {
          loadMoreTasks();
        }
      },
      {
        root: null,
        rootMargin: '20px',
        threshold: 0.1
      }
    );

    observer.value.observe(loadMoreTrigger.value);
  };

  // 清理观察器
  const cleanupObserver = () => {
    if (observer.value) {
      observer.value.disconnect();
      observer.value = null;
    }
  };

  // 生命周期
  onMounted(async () => {
    // 同时获取任务列表和统计信息
    await Promise.all([fetchTasks(), fetchStats(), fetchAllUsers()]);

    // 使用 nextTick 确保DOM已渲染
    await nextTick();
    initInfiniteScroll();
  });

  onUnmounted(() => {
    cleanupObserver();
  });
</script>

<style lang="scss" scoped>
  // ============ 卡片基础样式 ============
  .todo-card {
    :deep(.ele-card-header) {
      align-items: center;
      border-bottom: none;
    }
  }

  // ============ 卡片头部（标题 + 创建待办链接） ============
  .card-header {
    display: flex;
    align-items: center;
    gap: 14px;
  }

  .card-title {
    font-size: 16px;
    font-weight: 600;
    color: var(--el-text-color-primary);
  }

  // 创建待办：文字链接样式
  .create-link {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 0;
    border: none;
    background: none;
    cursor: pointer;
    font-size: 13px;
    color: var(--el-color-primary);
    transition: opacity 0.2s;

    .el-icon {
      font-size: 15px;
    }

    &:hover {
      opacity: 0.8;
    }
  }

  // ============ 头部操作区 ============
  .todo-card-extra-inner {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 8px;
  }

  .todo-tabs {
    display: inline-flex;
    align-items: center;
    gap: 18px;
    pointer-events: all;
    z-index: 10;
  }

  // 文字下划线 tab
  .todo-tab {
    position: relative;
    padding: 0 0 6px;
    border: none;
    background: none;
    cursor: pointer;
    font-size: 13px;
    color: var(--el-text-color-secondary);
    pointer-events: all !important;
    transition: color 0.2s;

    &:hover {
      color: var(--el-text-color-primary);
    }

    &.is-active {
      color: var(--el-color-primary);
      font-weight: 600;

      &::after {
        content: '';
        position: absolute;
        left: 50%;
        bottom: 0;
        transform: translateX(-50%);
        width: 20px;
        height: 2px;
        border-radius: 2px;
        background: var(--el-color-primary);
      }
    }
  }

  .status-count {
    font-size: 12px;
    margin-left: 2px;
    opacity: 0.85;
    font-weight: 400;
  }

  // ============ 加载和空状态 ============
  .task-loading,
  .task-empty {
    padding: 20px;
  }

  // ============ 滚动加载相关 ============
  .load-more-trigger {
    padding: 10px 0;
    min-height: 1px; // 确保元素可见以便 Intersection Observer 检测
  }

  .loading-more {
    padding: 10px 0;
  }

  .no-more-data {
    text-align: center;
    padding: 15px 0;
    color: var(--el-text-color-placeholder);
    font-size: 13px;

    span {
      position: relative;
      background-color: var(--el-bg-color);
      padding: 0 15px;

      &::before {
        content: '';
        position: absolute;
        left: -50px;
        top: 50%;
        width: 50px;
        height: 1px;
        background-color: var(--el-border-color-lighter);
      }

      &::after {
        content: '';
        position: absolute;
        right: -50px;
        top: 50%;
        width: 50px;
        height: 1px;
        background-color: var(--el-border-color-lighter);
      }
    }
  }

  // ============ 任务列表 ============
  .task-list {
    .task-item {
      position: relative;
      display: flex;
      align-items: flex-start;
      padding: 14px 8px;
      border-bottom: 1px solid var(--el-border-color-lighter);
      cursor: pointer;
      transition: background-color 0.2s;

      &:hover {
        background-color: var(--el-fill-color-lighter);
        border-radius: 4px;
      }

      &:last-child {
        border-bottom: none;
      }

      &.completed {
        .task-title {
          text-decoration: line-through;
          color: var(--el-text-color-secondary);
        }

        .task-description {
          opacity: 0.6;
          text-decoration: line-through;
        }
      }
    }
  }

  // 复选框
  .task-checkbox {
    margin-right: 12px;
    margin-top: 2px;
    flex-shrink: 0;
  }

  // 任务内容（右侧预留操作区宽度）
  .task-content {
    flex: 1;
    min-width: 0;
    padding-right: 116px;
  }

  // 任务标题
  .task-title {
    font-size: 15px;
    font-weight: 600;
    color: var(--el-text-color-primary);
    line-height: 1.3;
    letter-spacing: 0.02em;
    margin-bottom: 6px;

    &.completed-title {
      color: var(--el-text-color-secondary);
      font-weight: 500;
    }
  }

  // 更多操作按钮 - 右侧竖排，垂直居中
  .task-more-action {
    position: absolute;
    top: 50%;
    right: 12px;
    transform: translateY(-50%);
  }

  // 任务描述
  .task-description {
    font-size: 13px;
    color: var(--el-text-color-regular);
    margin-bottom: 8px;
    line-height: 1.4;
    font-weight: 400;
    opacity: 0.9;
  }

  // 元信息行
  .task-meta-row {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  // 元信息
  .task-meta {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
    flex: 1;
    min-width: 0;
  }

  // 开始处理/任务完成 - 右侧垂直居中
  .task-quick-actions {
    position: absolute;
    top: 50%;
    right: 40px;
    transform: translateY(-50%);
    display: flex;
    align-items: center;
    gap: 6px;
  }

  .meta-item {
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: 12px;
    color: var(--el-text-color-secondary);
  }

  .meta-icon {
    font-size: 12px;
    color: var(--el-text-color-placeholder);
  }

  .meta-text {
    &.overdue {
      color: var(--el-color-danger);
      font-weight: 500;
      margin-top: 2px;
    }

    &.completed-time {
      color: var(--el-color-success);
      font-weight: 500;
      margin-top: 2px;
    }

    &.create-time {
      color: var(--el-color-info);
      font-weight: 500;
      margin-top: 2px;
    }
  }

  // 创建人和主责任人样式区分
  .creator-info {
    .meta-icon {
      color: var(--el-color-info);
    }
    .meta-text {
      color: var(--el-color-info-dark-2);
      margin-top: 2px;
    }
  }

  .assignee-info {
    .meta-icon {
      color: var(--el-color-primary);
    }
    .meta-text {
      color: var(--el-color-primary-dark-2);
      font-weight: 500;
      margin-top: 2px;
    }
  }

  // 优先级指示器
  .priority-indicator {
    display: inline-flex;
    align-items: center;
    padding: 2px 12px;
    border-radius: 5px;
    font-size: 12px;
    font-weight: 600;
    margin-right: 0px;
    flex-shrink: 0;

    &.low {
      background-color: var(--el-color-info-light-8);
      color: var(--el-color-info);
    }

    &.medium {
      background-color: var(--el-color-warning-light-8);
      color: var(--el-color-warning-dark-2);
    }

    &.high {
      background-color: var(--el-color-danger-light-8);
      color: var(--el-color-danger);
    }
  }

  // 快速操作按钮样式 - 更紧凑的设计
  .quick-action-btn {
    font-size: 12px;
    height: 30px;
    padding: 0 14px;
    border-radius: 4px;
    font-weight: 400;
    min-width: 72px;
    white-space: nowrap;
    background-color: #fff;

    &.start-btn {
      color: var(--el-color-primary);
      border: 1px solid var(--el-color-primary);

      &:hover {
        background-color: var(--el-color-primary-light-9);
      }
    }

    &.complete-btn {
      color: var(--el-color-success);
      border: 1px solid var(--el-color-success);

      &:hover {
        background-color: var(--el-color-success-light-9);
      }
    }
  }

  // 更多操作按钮样式
  .action-btn {
    color: var(--el-text-color-placeholder);
    transition: color 0.2s;
    opacity: 0.8;

    &:hover {
      color: var(--el-text-color-primary);
      opacity: 1;
    }
  }

  // 任务项悬停时更多操作按钮更明显
  .task-item:hover .action-btn {
    opacity: 1;
  }

  .delete-option {
    color: var(--el-color-danger);
  }

  // ============ 对话框样式 ============
  :deep(.el-dialog__header) {
    padding: 16px 20px 12px;
  }

  :deep(.el-dialog__body) {
    padding: 12px 20px 20px;
  }

  :deep(.el-form-item__label) {
    font-weight: 500;
  }
</style>
