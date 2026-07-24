<template>
  <ele-modal
    form
    :width="560"
    :title="isUpdate ? '编辑 MCP 连接' : '新建 MCP 连接'"
    :loading="loading"
    v-bind="modalProps"
  >
    <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
      <el-form-item label="连接名称" prop="display_name">
        <el-input
          v-model.trim="form.display_name"
          :maxlength="50"
          placeholder="在 AI 工具里显示的名称，如「智途运输助手」"
          clearable
        />
        <div class="op-hint" v-if="isUpdate"
          >改名不会影响已经配置好的连接，可放心修改。</div
        >
      </el-form-item>
      <el-form-item label="开放给 AI 使用的能力" prop="enabled_capabilities">
        <el-select
          v-model="form.enabled_capabilities"
          multiple
          filterable
          collapse-tags
          collapse-tags-tooltip
          placeholder="勾选允许 AI 工具调用的能力"
          style="width: 100%"
        >
          <el-option
            v-for="c in capabilities"
            :key="c.code"
            :label="`${c.name}（${c.code}）`"
            :value="c.code"
          />
        </el-select>
      </el-form-item>
    </el-form>
    <template #footer>
      <btn-items
        :items="[
          { preset: 'cancel', onClick: () => closeModal() },
          { preset: 'save', onClick: () => save() }
        ]"
      />
    </template>
  </ele-modal>
</template>

<script lang="ts" setup>
  import { ref, reactive, onMounted } from 'vue';
  import type { FormInstance, FormRules } from 'element-plus';
  import { EleMessage, useModal } from 'ele-admin-plus';
  import {
    listCapabilities,
    createMcpConfig,
    updateMcpConfig
  } from '@/api/open-platform';
  import type { Capability, McpConfig } from '@/api/open-platform/model';

  const props = defineProps<{
    appId: number;
    data?: McpConfig | null;
  }>();

  const emit = defineEmits<{
    (e: 'done'): void;
    (e: 'reveal', cfg: McpConfig): void;
  }>();

  const { modalProps, closeModal } = useModal();

  const isUpdate = ref(!!props.data);
  const loading = ref(false);
  const formRef = ref<FormInstance | null>(null);
  const capabilities = ref<Capability[]>([]);

  const form = reactive<{
    display_name: string;
    enabled_capabilities: string[];
  }>({
    display_name: props.data?.display_name || '',
    enabled_capabilities: props.data?.enabled_capabilities
      ? [...props.data.enabled_capabilities]
      : []
  });

  const rules = reactive<FormRules>({
    display_name: [
      { required: true, message: '请填写连接名称', trigger: 'blur' }
    ],
    enabled_capabilities: [
      {
        required: true,
        type: 'array',
        min: 1,
        message: '请至少勾选一个能力',
        trigger: 'change'
      }
    ]
  });

  const save = () => {
    formRef.value?.validate?.((valid) => {
      if (!valid) return;
      loading.value = true;
      const fail = (e: any) => {
        loading.value = false;
        EleMessage.error({
          message: e.message || '操作失败，请稍后重试',
          plain: true
        });
      };
      if (isUpdate.value && props.data) {
        updateMcpConfig(props.data.id, {
          display_name: form.display_name,
          enabled_capabilities: form.enabled_capabilities
        })
          .then(() => {
            loading.value = false;
            EleMessage.success({ message: '已保存', plain: true });
            closeModal();
            emit('done');
          })
          .catch(fail);
      } else {
        createMcpConfig(props.appId, {
          display_name: form.display_name,
          enabled_capabilities: form.enabled_capabilities
        })
          .then((cfg) => {
            loading.value = false;
            closeModal();
            emit('done');
            if (cfg) emit('reveal', cfg);
          })
          .catch(fail);
      }
    });
  };

  onMounted(async () => {
    try {
      capabilities.value = await listCapabilities('mcp');
    } catch (e: any) {
      EleMessage.error({
        message: e.message || '加载能力目录失败，请稍后重试',
        plain: true
      });
    }
  });
</script>

<style lang="scss" scoped>
  .op-hint {
    color: var(--el-text-color-secondary);
    font-size: 12px;
    margin-top: 4px;
  }
</style>
