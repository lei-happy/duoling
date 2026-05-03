<template>
  <ele-page>
    <ele-card>
      <div class="ai-toolbar">
        <el-input
          v-model="searchForm.keyword"
          clearable
          placeholder="编码 / 名称"
          style="width: 220px"
          @keyup.enter="loadList"
        />
        <el-select
          v-model="searchForm.category"
          clearable
          placeholder="分类"
          style="width: 180px"
        >
          <el-option v-for="c in categories" :key="c" :label="c" :value="c" />
        </el-select>
        <el-select
          v-model="searchForm.status"
          clearable
          placeholder="状态"
          style="width: 140px"
        >
          <el-option label="启用" :value="1" />
          <el-option label="停用" :value="0" />
        </el-select>
        <el-button type="primary" @click="loadList">查询</el-button>
        <el-button @click="resetSearch">重置</el-button>
        <el-button type="warning" plain @click="onSync">从代码同步</el-button>
      </div>

      <el-alert
        type="info"
        :closable="false"
        style="margin-top: 12px"
        title="工具实现位于代码中（@register_tool 装饰器）。本页只用于查看与启停，不可直接编辑工具签名。"
      />

      <el-table
        v-loading="loading"
        :data="list"
        row-key="id"
        border
        style="margin-top: 12px"
      >
        <el-table-column prop="code" label="编码" width="200" />
        <el-table-column prop="name" label="名称" width="160" />
        <el-table-column prop="category" label="分类" width="100" />
        <el-table-column prop="description" label="描述" />
        <el-table-column label="风险" width="80">
          <template #default="{ row }">
            <el-tag
              size="small"
              :type="row.riskLevel === 'high' ? 'danger' : row.riskLevel === 'medium' ? 'warning' : 'info'"
            >
              {{ row.riskLevel }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="需确认" width="80">
          <template #default="{ row }">
            <el-tag size="small" :type="row.confirmRequired ? 'warning' : 'info'">
              {{ row.confirmRequired ? '是' : '否' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="requiredPermission" label="权限码" width="180" />
        <el-table-column label="代码内置" width="80">
          <template #default="{ row }">
            <el-tag size="small" :type="row.isBuiltin ? 'success' : 'danger'">
              {{ row.isBuiltin ? '是' : '已下线' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-switch
              :model-value="row.status === 1"
              @update:model-value="(v: boolean) => onToggleStatus(row, v)"
            />
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        background
        style="margin-top: 12px; justify-content: flex-end"
        @size-change="loadList"
        @current-change="loadList"
      />
    </ele-card>
  </ele-page>
</template>

<script lang="ts" setup>
  import { onMounted, reactive, ref } from 'vue';
  import { ElMessage } from 'element-plus';
  import {
    listToolCategories,
    pageTools,
    syncTools,
    updateToolStatus
  } from '@/api/ai';
  import type { AiTool } from '@/api/ai/model';

  defineOptions({ name: 'AiToolManage' });

  const loading = ref(false);
  const list = ref<AiTool[]>([]);
  const total = ref(0);
  const page = ref(1);
  const pageSize = ref(50);
  const categories = ref<string[]>([]);
  const searchForm = reactive<{
    keyword?: string;
    category?: string;
    status?: number;
  }>({});

  async function loadList() {
    loading.value = true;
    try {
      const data = await pageTools({
        page: page.value,
        limit: pageSize.value,
        ...searchForm
      });
      list.value = (data?.list ?? []) as AiTool[];
      total.value = data?.total ?? 0;
    } catch (e: any) {
      ElMessage.error(e?.message || '加载失败');
    } finally {
      loading.value = false;
    }
  }

  async function loadCategories() {
    try {
      categories.value = await listToolCategories();
    } catch {
      categories.value = [];
    }
  }

  function resetSearch() {
    searchForm.keyword = '';
    searchForm.category = undefined;
    searchForm.status = undefined;
    page.value = 1;
    loadList();
  }

  async function onToggleStatus(row: AiTool, v: boolean) {
    try {
      await updateToolStatus(row.id, v ? 1 : 0);
      row.status = v ? 1 : 0;
      ElMessage.success('已更新');
    } catch (e: any) {
      ElMessage.error(e?.message || '更新失败');
    }
  }

  async function onSync() {
    try {
      const r = await syncTools();
      ElMessage.success(
        `同步完成：新增 ${r?.inserted ?? 0}，更新 ${r?.updated ?? 0}，孤立 ${r?.orphan ?? 0}`
      );
      await loadList();
      await loadCategories();
    } catch (e: any) {
      ElMessage.error(e?.message || '同步失败');
    }
  }

  onMounted(() => {
    loadList();
    loadCategories();
  });
</script>

<style lang="scss" scoped>
  .ai-toolbar {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
  }
</style>
