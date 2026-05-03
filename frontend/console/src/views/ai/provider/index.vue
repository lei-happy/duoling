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
        <el-button type="primary" plain @click="openEdit()">新增 Provider</el-button>
      </div>

      <el-table
        v-loading="loading"
        :data="list"
        row-key="id"
        border
        style="margin-top: 12px"
      >
        <el-table-column prop="code" label="编码" width="160" />
        <el-table-column prop="name" label="名称" width="160" />
        <el-table-column prop="providerType" label="类型" width="140" />
        <el-table-column prop="modelName" label="默认模型" width="180" />
        <el-table-column prop="baseUrl" label="Base URL" />
        <el-table-column prop="apiKeyMasked" label="API Key" width="180" />
        <el-table-column label="默认" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.isDefault" size="small" type="warning">默认</el-tag>
            <el-button
              v-else
              text
              type="primary"
              size="small"
              :disabled="row.status !== 1"
              @click="onSetDefault(row)"
            >
              设为默认
            </el-button>
          </template>
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

    <el-dialog
      v-model="editVisible"
      :title="editing?.id ? '编辑 Provider' : '新增 Provider'"
      width="680px"
      destroy-on-close
      :close-on-click-modal="false"
    >
      <el-form :model="form" label-width="120px" ref="formRef">
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
            <el-form-item label="类型">
              <el-select v-model="form.providerType" style="width: 100%">
                <el-option label="OpenAI 兼容" value="openai_compat" />
                <el-option label="OpenAI" value="openai" />
                <el-option label="Azure OpenAI" value="azure_openai" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="超时(秒)">
              <el-input-number v-model="form.timeoutSeconds" :min="5" :max="600" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="Base URL">
          <el-input v-model="form.baseUrl" placeholder="如 https://dashscope.aliyuncs.com/compatible-mode/v1" />
        </el-form-item>
        <el-form-item label="默认模型" prop="modelName" :rules="[{ required: true }]">
          <el-input v-model="form.modelName" placeholder="如 qwen-plus / deepseek-chat" />
        </el-form-item>
        <el-form-item label="API Key">
          <el-input
            v-model="form.apiKey"
            type="password"
            show-password
            :placeholder="editing?.id ? '不修改请留空（当前已加密保存）' : '请填写明文 Key'"
          />
        </el-form-item>
        <el-form-item label="高级参数">
          <el-input
            v-model="extraParamsText"
            type="textarea"
            :autosize="{ minRows: 3, maxRows: 8 }"
            placeholder='JSON 格式。例如 Kimi K2.5/K2.6 这种 thinking 模型：&#10;{"fixed_temperature": 1, "omit_params": ["max_tokens"], "disable_tools": false}'
          />
          <div class="provider-hint">
            可选键：<code>fixed_temperature</code>（强制 temperature 值）、
            <code>omit_params</code>（剔除字段列表，如
            <code>["temperature","max_tokens"]</code>）、
            <code>include_usage</code>（开启
            <code>stream_options.include_usage</code>）、
            <code>disable_tools</code>（关闭工具调用）。
          </div>
        </el-form-item>
        <el-form-item label="设为默认">
          <el-switch v-model="form.isDefault" />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch
            v-model="form.status"
            :active-value="1"
            :inactive-value="0"
            active-text="启用"
            inactive-text="停用"
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
    addProvider,
    deleteProvider,
    pageProviders,
    setDefaultProvider,
    updateProvider
  } from '@/api/ai';
  import type { AiProvider } from '@/api/ai/model';

  defineOptions({ name: 'AiProviderManage' });

  const loading = ref(false);
  const list = ref<AiProvider[]>([]);
  const total = ref(0);
  const page = ref(1);
  const pageSize = ref(20);
  const searchForm = reactive<{ keyword?: string; status?: number }>({});

  const editVisible = ref(false);
  const editing = ref<AiProvider | null>(null);
  const form = ref<Partial<AiProvider> & { apiKey?: string }>({
    code: '',
    name: '',
    providerType: 'openai_compat',
    baseUrl: '',
    modelName: '',
    timeoutSeconds: 60,
    isDefault: false,
    status: 1,
    apiKey: ''
  });
  const extraParamsText = ref<string>('');
  const formRef = ref();

  async function loadList() {
    loading.value = true;
    try {
      const data = await pageProviders({
        page: page.value,
        limit: pageSize.value,
        ...searchForm
      });
      list.value = (data?.list ?? []) as AiProvider[];
      total.value = data?.total ?? 0;
    } catch (e: any) {
      ElMessage.error(e?.message || '加载失败');
    } finally {
      loading.value = false;
    }
  }

  function resetSearch() {
    searchForm.keyword = '';
    searchForm.status = undefined;
    page.value = 1;
    loadList();
  }

  function openEdit(row?: AiProvider) {
    editing.value = row ? { ...row } : null;
    form.value = row
      ? { ...row, apiKey: '' }
      : {
          code: '',
          name: '',
          providerType: 'openai_compat',
          baseUrl: '',
          modelName: '',
          timeoutSeconds: 60,
          isDefault: false,
          status: 1,
          apiKey: ''
        };
    extraParamsText.value = row?.extraParams
      ? JSON.stringify(row.extraParams, null, 2)
      : '';
    editVisible.value = true;
  }

  async function handleSave() {
    await formRef.value?.validate?.();
    // 解析高级参数 JSON
    let extraParams: any = null;
    const txt = (extraParamsText.value || '').trim();
    if (txt) {
      try {
        extraParams = JSON.parse(txt);
        if (typeof extraParams !== 'object' || Array.isArray(extraParams)) {
          throw new Error('需为 JSON 对象');
        }
      } catch (e: any) {
        ElMessage.error(`高级参数 JSON 不合法：${e?.message || e}`);
        return;
      }
    }

    try {
      const payload: any = { ...form.value, extraParams };
      if (!payload.apiKey) delete payload.apiKey;
      if (editing.value?.id) {
        await updateProvider(editing.value.id, payload);
      } else {
        await addProvider(payload);
      }
      ElMessage.success('保存成功');
      editVisible.value = false;
      loadList();
    } catch (e: any) {
      ElMessage.error(e?.message || '保存失败');
    }
  }

  async function onSetDefault(row: AiProvider) {
    try {
      await ElMessageBox.confirm(
        `确定将「${row.name}」设为默认 Provider？设置后所有未指定 Provider 的数字员工都会使用它。`,
        '设为默认',
        { type: 'warning' }
      );
    } catch {
      return;
    }
    try {
      await setDefaultProvider(row.id);
      ElMessage.success('已设为默认 Provider');
      loadList();
    } catch (e: any) {
      ElMessage.error(e?.message || '设置失败');
    }
  }

  async function onDelete(row: AiProvider) {
    try {
      await ElMessageBox.confirm(`确定删除「${row.name}」？`, '提示', {
        type: 'warning'
      });
    } catch {
      return;
    }
    try {
      await deleteProvider(row.id);
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
  .provider-hint {
    margin-top: 4px;
    font-size: 12px;
    color: var(--el-text-color-secondary);
    line-height: 1.6;
    code {
      background: var(--el-fill-color);
      padding: 0 4px;
      border-radius: 3px;
      font-size: 12px;
    }
  }
</style>
