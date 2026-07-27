<template>
  <el-drawer
    :model-value="visible"
    :title="isEdit ? '模块详情' : '新建模块'"
    size="620px"
    destroy-on-close
    @close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="96px"
      class="module-form"
    >
      <el-form-item label="模块名称" prop="title">
        <el-input
          v-model="form.title"
          maxlength="200"
          show-word-limit
          placeholder="如：菜单管理"
        />
      </el-form-item>
      <el-form-item label="产品端" prop="product_line">
        <el-select v-model="form.product_line" style="width: 100%">
          <el-option
            v-for="opt in PRODUCT_LINE_OPTIONS"
            :key="opt.value"
            :label="opt.label"
            :value="opt.value"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="优先级" prop="priority">
        <el-select v-model="form.priority" style="width: 100%">
          <el-option
            v-for="opt in PRIORITY_OPTIONS"
            :key="opt.value"
            :label="opt.label"
            :value="opt.value"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="状态" prop="status">
        <el-select v-model="form.status" style="width: 100%">
          <el-option
            v-for="opt in STATUS_OPTIONS"
            :key="opt.value"
            :label="opt.label"
            :value="opt.value"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="需求说明" prop="description">
        <el-input
          v-model="form.description"
          type="textarea"
          :rows="4"
          maxlength="2000"
          show-word-limit
          placeholder="简要说明需求背景、范围与验收点"
        />
      </el-form-item>
      <el-form-item label="产品负责人">
        <el-select
          v-model="form.pm_user_id"
          filterable
          clearable
          placeholder="选择产品负责人"
          style="width: 100%"
          @change="(v: number | null) => onUserChange('pm', v)"
        >
          <el-option
            v-for="u in userOptions"
            :key="u.userId"
            :label="userLabel(u)"
            :value="u.userId!"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="设计师">
        <el-select
          v-model="form.designer_user_id"
          filterable
          clearable
          placeholder="选择设计师"
          style="width: 100%"
          @change="(v: number | null) => onUserChange('designer', v)"
        >
          <el-option
            v-for="u in userOptions"
            :key="u.userId"
            :label="userLabel(u)"
            :value="u.userId!"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="开发负责人">
        <el-select
          v-model="form.developer_user_id"
          filterable
          clearable
          placeholder="选择开发负责人"
          style="width: 100%"
          @change="(v: number | null) => onUserChange('developer', v)"
        >
          <el-option
            v-for="u in userOptions"
            :key="u.userId"
            :label="userLabel(u)"
            :value="u.userId!"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="产品原型">
        <prototype-picker v-model="form.prototype_path" />
      </el-form-item>
      <el-form-item label="Figma 链接" prop="figma_url">
        <el-input
          v-model="form.figma_url"
          placeholder="粘贴 Figma 分享链接"
          clearable
        />
      </el-form-item>
      <el-form-item v-if="figmaEmbedUrl" label="设计预览">
        <div class="figma-preview">
          <iframe
            :src="figmaEmbedUrl"
            allowfullscreen
            class="figma-iframe"
          />
          <el-link
            :href="form.figma_url || undefined"
            target="_blank"
            type="primary"
            :underline="false"
          >
            在新窗口打开 Figma
          </el-link>
        </div>
      </el-form-item>
      <el-form-item v-else-if="form.figma_url" label="设计预览">
        <el-link
          :href="form.figma_url"
          target="_blank"
          type="primary"
          :underline="false"
        >
          无法嵌入预览，点击在新窗口打开
        </el-link>
      </el-form-item>
    </el-form>

    <template #footer>
      <div class="drawer-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button
          v-if="isEdit"
          type="danger"
          plain
          :loading="deleting"
          @click="handleDelete"
        >
          删除
        </el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">
          保存
        </el-button>
      </div>
    </template>
  </el-drawer>
</template>

<script lang="ts" setup>
  import { computed, reactive, ref, watch } from 'vue';
  import type { FormInstance, FormRules } from 'element-plus';
  import { ElMessageBox } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import PrototypePicker from './PrototypePicker.vue';
  import { listUsers } from '@/api/system/user';
  import type { User } from '@/api/system/user/model';
  import {
    createDesignModule,
    updateDesignModule,
    removeDesignModule
  } from '@/api/doc-center/design-module';
  import type {
    DesignModule,
    DesignModuleForm
  } from '@/api/doc-center/model/design-module';
  import {
    PRODUCT_LINE_OPTIONS,
    PRIORITY_OPTIONS,
    STATUS_OPTIONS,
    toFigmaEmbedUrl
  } from '../constants';

  defineOptions({ name: 'ModuleEditDrawer' });

  const props = defineProps<{
    visible: boolean;
    record?: DesignModule | null;
  }>();

  const emit = defineEmits<{
    (e: 'update:visible', value: boolean): void;
    (e: 'saved'): void;
  }>();

  const formRef = ref<FormInstance>();
  const saving = ref(false);
  const deleting = ref(false);
  const userOptions = ref<User[]>([]);

  const isEdit = computed(() => !!props.record?.id);

  const form = reactive<DesignModuleForm>({
    title: '',
    product_line: 'other',
    description: '',
    priority: 1,
    status: 0,
    prototype_path: null,
    figma_url: '',
    pm_user_id: null,
    pm_name: null,
    designer_user_id: null,
    designer_name: null,
    developer_user_id: null,
    developer_name: null
  });

  const rules: FormRules = {
    title: [{ required: true, message: '请填写模块名称', trigger: 'blur' }],
    product_line: [
      { required: true, message: '请选择产品端', trigger: 'change' }
    ]
  };

  const figmaEmbedUrl = computed(() => toFigmaEmbedUrl(form.figma_url));

  const userLabel = (u: User) => {
    if (u.nickname && u.phone) return `${u.nickname}（${u.phone}）`;
    return u.nickname || u.phone || String(u.userId);
  };

  const onUserChange = (
    role: 'pm' | 'designer' | 'developer',
    userId: number | null
  ) => {
    const user = userOptions.value.find((u) => u.userId === userId);
    const name = user?.nickname || user?.phone || null;
    if (role === 'pm') {
      form.pm_user_id = userId;
      form.pm_name = name;
    } else if (role === 'designer') {
      form.designer_user_id = userId;
      form.designer_name = name;
    } else {
      form.developer_user_id = userId;
      form.developer_name = name;
    }
  };

  const resetForm = () => {
    form.title = '';
    form.product_line = 'other';
    form.description = '';
    form.priority = 1;
    form.status = 0;
    form.prototype_path = null;
    form.figma_url = '';
    form.pm_user_id = null;
    form.pm_name = null;
    form.designer_user_id = null;
    form.designer_name = null;
    form.developer_user_id = null;
    form.developer_name = null;
  };

  const fillForm = (record: DesignModule) => {
    form.title = record.title;
    form.product_line = record.product_line || 'other';
    form.description = record.description || '';
    form.priority = record.priority;
    form.status = record.status;
    form.prototype_path = record.prototype_path || null;
    form.figma_url = record.figma_url || '';
    form.pm_user_id = record.pm_user_id ?? null;
    form.pm_name = record.pm_name ?? null;
    form.designer_user_id = record.designer_user_id ?? null;
    form.designer_name = record.designer_name ?? null;
    form.developer_user_id = record.developer_user_id ?? null;
    form.developer_name = record.developer_name ?? null;
  };

  const loadUsers = async () => {
    try {
      userOptions.value = (await listUsers()) || [];
    } catch (e) {
      console.error(e);
      userOptions.value = [];
    }
  };

  watch(
    () => props.visible,
    async (val) => {
      if (!val) return;
      await loadUsers();
      if (props.record) {
        fillForm(props.record);
      } else {
        resetForm();
      }
    }
  );

  const handleClose = () => {
    emit('update:visible', false);
  };

  const handleSave = async () => {
    const valid = await formRef.value?.validate().catch(() => false);
    if (!valid) return;

    saving.value = true;
    const loading = EleMessage.loading({
      message: '正在保存，请稍候…',
      plain: true
    });
    try {
      const payload: DesignModuleForm = {
        ...form,
        prototype_path: form.prototype_path || null,
        figma_url: form.figma_url?.trim() || null
      };
      if (isEdit.value && props.record?.id) {
        await updateDesignModule(props.record.id, payload);
        EleMessage.success({ message: '已保存', plain: true });
      } else {
        await createDesignModule(payload);
        EleMessage.success({ message: '已创建模块', plain: true });
      }
      emit('saved');
      handleClose();
    } catch (e: any) {
      EleMessage.error({
        message: e?.message || '保存失败，请稍后重试',
        plain: true
      });
    } finally {
      loading.close();
      saving.value = false;
    }
  };

  const handleDelete = async () => {
    if (!props.record?.id) return;
    try {
      await ElMessageBox.confirm(
        `确定删除「${props.record.title}」吗？删除后不可恢复。`,
        '删除确认',
        { type: 'warning', draggable: true }
      );
    } catch {
      return;
    }
    deleting.value = true;
    try {
      await removeDesignModule(props.record.id);
      EleMessage.success({ message: '已删除该模块', plain: true });
      emit('saved');
      handleClose();
    } catch (e: any) {
      EleMessage.error({
        message: e?.message || '删除失败，请稍后重试',
        plain: true
      });
    } finally {
      deleting.value = false;
    }
  };
</script>

<style lang="scss" scoped>
  .module-form {
    padding-right: 8px;
  }

  .figma-preview {
    width: 100%;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .figma-iframe {
    width: 100%;
    height: 320px;
    border: 1px solid var(--el-border-color-lighter);
    border-radius: 6px;
  }

  .drawer-footer {
    display: flex;
    justify-content: flex-end;
    gap: 8px;
  }
</style>
