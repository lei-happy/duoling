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
          v-model="searchForm.scene"
          clearable
          placeholder="场景"
          style="width: 160px"
        >
          <el-option label="system" value="system" />
          <el-option label="role" value="role" />
          <el-option label="scenario" value="scenario" />
        </el-select>
        <el-button type="primary" @click="loadList">查询</el-button>
        <el-button @click="resetSearch">重置</el-button>
        <el-button type="primary" plain @click="openEdit()">新增模板</el-button>
      </div>

      <el-table
        v-loading="loading"
        :data="list"
        row-key="id"
        border
        style="margin-top: 12px"
      >
        <el-table-column prop="code" label="编码" width="200" />
        <el-table-column prop="name" label="名称" width="200" />
        <el-table-column prop="scene" label="场景" width="100" />
        <el-table-column prop="description" label="说明" />
        <el-table-column prop="version" label="版本" width="80" />
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

    <el-dialog
      v-model="editVisible"
      :title="editing?.id ? '编辑模板' : '新增模板'"
      width="720px"
      destroy-on-close
      :close-on-click-modal="false"
    >
      <el-form :model="form" label-width="100px" ref="formRef">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="编码" prop="code" :rules="[{ required: true }]">
              <el-input v-model="form.code" :disabled="!!editing?.id" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="名称" prop="name" :rules="[{ required: true }]">
              <el-input v-model="form.name" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="场景">
              <el-select v-model="form.scene" style="width: 100%">
                <el-option label="system" value="system" />
                <el-option label="role" value="role" />
                <el-option label="scenario" value="scenario" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态">
              <el-switch
                v-model="form.status"
                :active-value="1"
                :inactive-value="0"
                active-text="启用"
                inactive-text="停用"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="说明">
          <el-input v-model="form.description" />
        </el-form-item>
        <el-form-item label="模板内容" prop="content" :rules="[{ required: true }]">
          <el-input
            v-model="form.content"
            type="textarea"
            :autosize="{ minRows: 8, maxRows: 18 }"
            placeholder="支持 {{variable}} 占位"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </ele-page>
</template>

<script lang="ts" setup>
  import { onMounted, reactive, ref } from 'vue';
  import { ElMessage, ElMessageBox } from 'element-plus';
  import {
    addPrompt,
    deletePrompt,
    pagePrompts,
    updatePrompt
  } from '@/api/ai';
  import type { AiPromptTemplate } from '@/api/ai/model';

  defineOptions({ name: 'AiPromptManage' });

  const loading = ref(false);
  const list = ref<AiPromptTemplate[]>([]);
  const total = ref(0);
  const page = ref(1);
  const pageSize = ref(20);
  const searchForm = reactive<{ keyword?: string; scene?: string }>({});

  const editVisible = ref(false);
  const editing = ref<AiPromptTemplate | null>(null);
  const form = ref<Partial<AiPromptTemplate>>({
    code: '',
    name: '',
    scene: 'role',
    content: '',
    description: '',
    status: 1
  });
  const formRef = ref();

  async function loadList() {
    loading.value = true;
    try {
      const data = await pagePrompts({
        page: page.value,
        limit: pageSize.value,
        ...searchForm
      });
      list.value = (data?.list ?? []) as AiPromptTemplate[];
      total.value = data?.total ?? 0;
    } catch (e: any) {
      ElMessage.error(e?.message || '加载失败');
    } finally {
      loading.value = false;
    }
  }

  function resetSearch() {
    searchForm.keyword = '';
    searchForm.scene = undefined;
    page.value = 1;
    loadList();
  }

  function openEdit(row?: AiPromptTemplate) {
    editing.value = row ? { ...row } : null;
    form.value = row
      ? { ...row }
      : {
          code: '',
          name: '',
          scene: 'role',
          content: '',
          description: '',
          status: 1
        };
    editVisible.value = true;
  }

  async function handleSave() {
    await formRef.value?.validate?.();
    try {
      if (editing.value?.id) {
        await updatePrompt(editing.value.id, form.value);
      } else {
        await addPrompt(form.value);
      }
      ElMessage.success('保存成功');
      editVisible.value = false;
      loadList();
    } catch (e: any) {
      ElMessage.error(e?.message || '保存失败');
    }
  }

  async function onDelete(row: AiPromptTemplate) {
    try {
      await ElMessageBox.confirm(`确定删除「${row.name}」？`, '提示', {
        type: 'warning'
      });
    } catch {
      return;
    }
    try {
      await deletePrompt(row.id);
      ElMessage.success('已删除');
      loadList();
    } catch (e: any) {
      ElMessage.error(e?.message || '删除失败');
    }
  }

  onMounted(loadList);
</script>

<style lang="scss" scoped>
  .ai-toolbar {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
  }
</style>
