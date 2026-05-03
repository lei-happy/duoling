<template>
  <el-dialog
    v-model="visible"
    :title="isEdit ? '编辑数字员工' : '新增数字员工'"
    width="780px"
    destroy-on-close
    :close-on-click-modal="false"
  >
    <el-form ref="formRef" :model="form" :rules="rules" label-width="120px">
      <el-form-item label="员工头像">
        <div class="ai-emp-avatar">
          <el-upload
            class="ai-emp-avatar__uploader"
            accept="image/png,image/jpeg,image/webp,image/gif"
            :show-file-list="false"
            :before-upload="beforeAvatarUpload"
          >
            <img v-if="avatarPreviewSrc" class="ai-emp-avatar__preview" :src="avatarPreviewSrc" alt="" />
            <el-icon v-else class="ai-emp-avatar__icon">
              <plus />
            </el-icon>
          </el-upload>
          <div class="ai-emp-avatar__side">
            <el-input
              v-model="form.avatar"
              placeholder="可直接填头像 URL，或上传后自动填充"
              clearable
              style="width: 360px"
            />
            <div class="ai-emp-avatar__hint">
              建议方形图片，PNG / JPG / WebP，单文件最大 2MB。
            </div>
          </div>
        </div>
      </el-form-item>

      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="员工编码" prop="code">
            <el-input
              v-model="form.code"
              placeholder="如 form_recorder_default"
              :disabled="isEdit"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="员工名称" prop="name">
            <el-input v-model="form.name" placeholder="如 录单员小智" />
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="员工类型" prop="employeeType">
            <el-select v-model="form.employeeType" style="width: 100%">
              <el-option label="录单员" value="form_recorder" />
              <el-option label="数据分析员" value="data_analyst" />
              <el-option label="档案管理员" value="archivist" />
              <el-option label="自定义" value="custom" />
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

      <el-form-item label="简介">
        <el-input
          v-model="form.description"
          type="textarea"
          :autosize="{ minRows: 2, maxRows: 4 }"
          placeholder="用户侧可见的一句话介绍"
        />
      </el-form-item>

      <el-form-item label="欢迎语">
        <el-input
          v-model="form.welcomeMessage"
          type="textarea"
          :autosize="{ minRows: 2, maxRows: 4 }"
          placeholder="新会话首条 assistant 消息"
        />
      </el-form-item>

      <el-form-item label="建议提问">
        <div v-for="(q, idx) in suggestedList" :key="idx" style="display: flex; gap: 8px; margin-bottom: 6px">
          <el-input v-model="suggestedList[idx]" placeholder="一条建议提问" />
          <el-button text type="danger" @click="suggestedList.splice(idx, 1)">删除</el-button>
        </div>
        <el-button text type="primary" @click="suggestedList.push('')">+ 添加</el-button>
      </el-form-item>

      <el-form-item label="系统提示词">
        <el-input
          v-model="form.systemPrompt"
          type="textarea"
          :autosize="{ minRows: 4, maxRows: 12 }"
          placeholder="角色提示词；可以以 @template:模板编码 引用平台提示词模板"
        />
      </el-form-item>

      <el-row :gutter="16">
        <el-col :span="8">
          <el-form-item label="Provider 编码">
            <el-input
              :model-value="form.modelConfig?.provider_code || ''"
              placeholder="留空使用默认"
              @update:model-value="(v: string) => setModelCfg('provider_code', v)"
            />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="模型覆写">
            <el-tooltip
              placement="top"
              content="留空将使用所选 Provider 的默认模型；如需覆写，请填写厂商完整模型 ID（如 kimi-k2.5、moonshot-v1-8k、qwen-plus、deepseek-chat）"
            >
              <el-input
                :model-value="form.modelConfig?.model || ''"
                placeholder="留空 = 用 Provider 默认；如填需用完整 ID"
                @update:model-value="(v: string) => setModelCfg('model', v)"
              />
            </el-tooltip>
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="Temperature">
            <el-input-number
              :model-value="form.modelConfig?.temperature ?? null"
              :min="0"
              :max="2"
              :step="0.1"
              style="width: 100%"
              @update:model-value="(v: any) => setModelCfg('temperature', v)"
            />
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="16">
        <el-col :span="8">
          <el-form-item label="Max Tokens">
            <el-input-number
              :model-value="form.modelConfig?.max_tokens ?? null"
              :min="64"
              :step="64"
              style="width: 100%"
              @update:model-value="(v: any) => setModelCfg('max_tokens', v)"
            />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="工具最大轮次">
            <el-input-number
              :model-value="form.modelConfig?.max_tool_loops ?? null"
              :min="1"
              :max="20"
              style="width: 100%"
              @update:model-value="(v: any) => setModelCfg('max_tool_loops', v)"
            />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="上下文窗口">
            <el-input-number
              :model-value="form.modelConfig?.context_window ?? null"
              :min="4"
              :max="100"
              style="width: 100%"
              @update:model-value="(v: any) => setModelCfg('context_window', v)"
            />
          </el-form-item>
        </el-col>
      </el-row>

      <el-form-item label="绑定工具">
        <el-checkbox-group v-model="form.toolIds">
          <div
            v-for="(group, cat) in groupedTools"
            :key="cat"
            style="margin-bottom: 8px; width: 100%"
          >
            <div style="font-size: 12px; color: var(--el-text-color-secondary); margin-bottom: 4px">
              {{ cat }}
            </div>
            <el-checkbox
              v-for="t in group"
              :key="t.id"
              :value="t.id"
              :label="`${t.name}（${t.code}）`"
            />
          </div>
        </el-checkbox-group>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" @click="handleOk">保存</el-button>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
  import { computed, ref, watch } from 'vue';
  import { ElMessage } from 'element-plus';
  import { Plus } from '@element-plus/icons-vue';
  import { addEmployee, updateEmployee } from '@/api/ai';
  import { uploadFile } from '@/api/system/file';
  import type {
    AiEmployeeDetail,
    AiEmployeeFormPayload,
    AiTool
  } from '@/api/ai/model';

  const props = defineProps<{
    modelValue: boolean;
    detail: AiEmployeeDetail | null;
    tools: AiTool[];
  }>();
  const emit = defineEmits<{
    (e: 'update:modelValue', v: boolean): void;
    (e: 'ok'): void;
  }>();

  const visible = computed({
    get: () => props.modelValue,
    set: (v) => emit('update:modelValue', v)
  });

  const isEdit = computed(() => !!props.detail?.id);

  const formRef = ref();
  const form = ref<AiEmployeeFormPayload & { toolIds: number[]; status: number }>({
    code: '',
    name: '',
    employeeType: 'custom',
    description: '',
    avatar: '',
    systemPrompt: '',
    welcomeMessage: '',
    suggestedQuestions: [],
    modelConfig: {},
    sortOrder: 0,
    status: 1,
    toolIds: []
  });
  const suggestedList = ref<string[]>([]);

  const rules = {
    code: [{ required: true, message: '请填写编码', trigger: 'blur' }],
    name: [{ required: true, message: '请填写名称', trigger: 'blur' }],
    employeeType: [{ required: true, message: '请选择类型', trigger: 'change' }]
  };

  const groupedTools = computed<Record<string, AiTool[]>>(() => {
    const map: Record<string, AiTool[]> = {};
    for (const t of props.tools) {
      const key = t.category || '未分类';
      (map[key] ||= []).push(t);
    }
    return map;
  });

  /** 头像预览 URL：相对路径补斜杠，绝对地址原样使用 */
  const avatarPreviewSrc = computed(() => {
    const p = (form.value.avatar || '').trim();
    if (!p) return '';
    if (p.startsWith('http://') || p.startsWith('https://') || p.startsWith('data:')) {
      return p;
    }
    return p.startsWith('/') ? p : `/${p}`;
  });

  function beforeAvatarUpload(file: File) {
    const okType = ['image/png', 'image/jpeg', 'image/webp', 'image/gif'].includes(
      file.type
    );
    if (!okType) {
      ElMessage.error('请上传 PNG / JPG / WebP / GIF 图片');
      return false;
    }
    if (file.size > 2 * 1024 * 1024) {
      ElMessage.error('图片不能超过 2MB');
      return false;
    }
    uploadFile(file, undefined, file.name, 'avatar')
      .then((res) => {
        if (res?.url) {
          form.value.avatar = res.url;
          ElMessage.success('上传成功');
        }
      })
      .catch((e: any) => ElMessage.error(e?.message || '上传失败'));
    return false;
  }

  function setModelCfg(key: string, v: any) {
    if (!form.value.modelConfig) form.value.modelConfig = {};
    if (v === '' || v === null || v === undefined) {
      delete form.value.modelConfig[key];
    } else {
      form.value.modelConfig[key] = v;
    }
  }

  watch(
    () => props.modelValue,
    (v) => {
      if (!v) return;
      const d = props.detail;
      form.value = {
        code: d?.code || '',
        name: d?.name || '',
        employeeType: d?.employeeType || 'custom',
        description: d?.description || '',
        avatar: d?.avatar || '',
        systemPrompt: d?.systemPrompt || '',
        welcomeMessage: d?.welcomeMessage || '',
        suggestedQuestions: d?.suggestedQuestions || [],
        modelConfig: { ...(d?.modelConfig || {}) },
        featureCode: d?.featureCode || '',
        sortOrder: d?.sortOrder ?? 0,
        status: d?.status ?? 1,
        toolIds: d?.toolIds ? [...d.toolIds] : []
      };
      suggestedList.value = [...(d?.suggestedQuestions || [])];
    }
  );

  async function handleOk() {
    await formRef.value?.validate?.();
    form.value.suggestedQuestions = suggestedList.value
      .map((s) => s.trim())
      .filter(Boolean);
    try {
      if (isEdit.value && props.detail?.id) {
        await updateEmployee(props.detail.id, form.value);
      } else {
        await addEmployee(form.value);
      }
      ElMessage.success('保存成功');
      visible.value = false;
      emit('ok');
    } catch (e: any) {
      ElMessage.error(e?.message || '保存失败');
    }
  }
</script>

<style lang="scss" scoped>
  .ai-emp-avatar {
    display: flex;
    align-items: flex-start;
    gap: 16px;

    &__uploader :deep(.el-upload) {
      width: 80px;
      height: 80px;
      border: 1px dashed var(--el-border-color);
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      overflow: hidden;
      transition: var(--el-transition-duration-fast);
      &:hover {
        border-color: var(--el-color-primary);
      }
    }

    &__preview {
      width: 80px;
      height: 80px;
      object-fit: cover;
    }

    &__icon {
      font-size: 22px;
      color: var(--el-text-color-placeholder);
    }

    &__side {
      display: flex;
      flex-direction: column;
      gap: 4px;
    }

    &__hint {
      font-size: 12px;
      color: var(--el-text-color-secondary);
    }
  }
</style>
