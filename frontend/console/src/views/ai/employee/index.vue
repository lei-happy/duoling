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
          v-model="searchForm.employeeType"
          clearable
          placeholder="员工类型"
          style="width: 180px"
        >
          <el-option label="录单员" value="form_recorder" />
          <el-option label="数据分析员" value="data_analyst" />
          <el-option label="档案管理员" value="archivist" />
          <el-option label="自定义" value="custom" />
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
        <el-button type="primary" plain @click="openEdit()">新增数字员工</el-button>
      </div>

      <el-table
        v-loading="loading"
        :data="list"
        row-key="id"
        border
        style="margin-top: 12px"
      >
        <el-table-column prop="code" label="编码" width="180" />
        <el-table-column prop="name" label="名称" width="160" />
        <el-table-column prop="employeeType" label="类型" width="120">
          <template #default="{ row }">
            {{ empTypeText(row.employeeType) }}
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" />
        <el-table-column label="工具数" width="80">
          <template #default="{ row }">{{ (row.toolIds || []).length }}</template>
        </el-table-column>
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-tag size="small" :type="row.status === 1 ? 'success' : 'info'">
              {{ row.status === 1 ? '启用' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160">
          <template #default="{ row }">
            <el-button text type="primary" size="small" @click="openEdit(row)">编辑</el-button>
            <el-button text type="danger" size="small" @click="onDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next, jumper"
        background
        style="margin-top: 12px; justify-content: flex-end"
        @size-change="loadList"
        @current-change="loadList"
      />
    </ele-card>

    <employee-edit
      v-model="editVisible"
      :detail="editingDetail"
      :tools="allTools"
      @ok="loadList"
    />
  </ele-page>
</template>

<script lang="ts" setup>
  import { onMounted, reactive, ref } from 'vue';
  import { ElMessage, ElMessageBox } from 'element-plus';
  import {
    deleteEmployee,
    pageEmployees,
    pageTools
  } from '@/api/ai';
  import type { AiEmployeeDetail, AiTool } from '@/api/ai/model';
  import EmployeeEdit from './components/employee-edit.vue';

  defineOptions({ name: 'AiEmployeeManage' });

  const loading = ref(false);
  const list = ref<AiEmployeeDetail[]>([]);
  const total = ref(0);
  const page = ref(1);
  const pageSize = ref(20);
  const searchForm = reactive<{
    keyword?: string;
    employeeType?: string;
    status?: number;
  }>({});
  const allTools = ref<AiTool[]>([]);
  const editVisible = ref(false);
  const editingDetail = ref<AiEmployeeDetail | null>(null);

  function empTypeText(t?: string): string {
    switch (t) {
      case 'form_recorder':
        return '录单员';
      case 'data_analyst':
        return '数据分析员';
      case 'archivist':
        return '档案管理员';
      default:
        return '自定义';
    }
  }

  async function loadList() {
    loading.value = true;
    try {
      const data = await pageEmployees({
        page: page.value,
        limit: pageSize.value,
        ...searchForm
      });
      list.value = (data?.list ?? []) as AiEmployeeDetail[];
      total.value = data?.total ?? 0;
    } catch (e: any) {
      ElMessage.error(e?.message || '加载失败');
    } finally {
      loading.value = false;
    }
  }

  async function loadAllTools() {
    try {
      const data = await pageTools({ page: 1, limit: 200 });
      allTools.value = (data?.list ?? []) as AiTool[];
    } catch (e: any) {
      ElMessage.error(e?.message || '加载工具失败');
    }
  }

  function resetSearch() {
    searchForm.keyword = '';
    searchForm.employeeType = undefined;
    searchForm.status = undefined;
    page.value = 1;
    loadList();
  }

  function openEdit(row?: AiEmployeeDetail) {
    editingDetail.value = row ? { ...row } : null;
    editVisible.value = true;
  }

  async function onDelete(row: AiEmployeeDetail) {
    try {
      await ElMessageBox.confirm(`确定删除「${row.name}」？`, '提示', {
        type: 'warning'
      });
    } catch {
      return;
    }
    try {
      await deleteEmployee(row.id);
      ElMessage.success('已删除');
      await loadList();
    } catch (e: any) {
      ElMessage.error(e?.message || '删除失败');
    }
  }

  onMounted(() => {
    loadList();
    loadAllTools();
  });
</script>

<style lang="scss" scoped>
  .ai-toolbar {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
  }
</style>
