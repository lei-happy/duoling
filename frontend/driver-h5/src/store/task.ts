import { defineStore } from 'pinia';
import { ref } from 'vue';
import type { TaskListItem } from '@/api/task';

/**
 * 任务短缓存：仅在同次会话中缓存列表，切换企业 / 强制刷新时清空。
 */
export const useTaskStore = defineStore('task', () => {
  const list = ref<TaskListItem[]>([]);
  const total = ref(0);
  const page = ref(1);
  const pageSize = ref(20);
  const statusFilter = ref<number | undefined>(undefined);
  const cachedAt = ref<number>(0);

  function setList(items: TaskListItem[], totalCount: number, p: number, ps: number) {
    list.value = items;
    total.value = totalCount;
    page.value = p;
    pageSize.value = ps;
    cachedAt.value = Date.now();
  }

  function clear() {
    list.value = [];
    total.value = 0;
    page.value = 1;
    cachedAt.value = 0;
  }

  return { list, total, page, pageSize, statusFilter, cachedAt, setList, clear };
});
