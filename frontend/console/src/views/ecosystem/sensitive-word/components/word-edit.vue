<!-- 敏感词 - 新增/编辑 -->
<template>
  <ele-modal
    form
    :width="520"
    v-model="visible"
    :title="isUpdate ? '编辑敏感词' : '添加敏感词'"
    @open="onOpen"
  >
    <el-form
      ref="formRef"
      label-width="88px"
      :model="form"
      :rules="rules"
      @submit.prevent="save"
    >
      <el-form-item label="敏感词" prop="word">
        <el-input
          clearable
          v-model="form.word"
          maxlength="64"
          show-word-limit
          placeholder="请输入要检查的词，至少 2 个字"
        />
        <div class="eco-tip">
          单字容易误伤正常内容，例如「枪」会拦下「枪型玩具模型」。
        </div>
      </el-form-item>

      <el-form-item label="分类" prop="category">
        <el-select v-model="form.category" style="width: 100%">
          <el-option
            v-for="c in options.categories"
            :key="c.value"
            :label="c.label"
            :value="c.value"
          />
        </el-select>
        <div class="eco-tip">
          选「违禁品」时，企业看到的提示会是「这类货物需要专门资质」。
        </div>
      </el-form-item>

      <el-form-item label="命中后" prop="action">
        <el-radio-group v-model="form.action">
          <el-radio
            v-for="a in options.actions"
            :key="a.value"
            :value="a.value"
            :label="a.value"
          >
            {{ a.label }}
          </el-radio>
        </el-radio-group>
        <div class="eco-tip">{{ actionTip }}</div>
      </el-form-item>

      <el-form-item label="适用范围" prop="scope">
        <el-select v-model="form.scope" style="width: 100%">
          <el-option
            v-for="s in options.scopes"
            :key="s.value"
            :label="s.label"
            :value="s.value"
          />
        </el-select>
      </el-form-item>

      <el-form-item v-if="isUpdate" label="状态">
        <el-switch
          v-model="form.status"
          :active-value="1"
          :inactive-value="0"
          active-text="启用中"
          inactive-text="已停用"
        />
      </el-form-item>

      <el-form-item label="备注">
        <el-input
          type="textarea"
          :rows="2"
          maxlength="255"
          v-model="form.remark"
          placeholder="选填，写下为什么加这个词，方便以后判断能不能删"
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" :loading="loading" @click="save">
        {{ isUpdate ? '保存' : '添加' }}
      </el-button>
    </template>
  </ele-modal>
</template>

<script lang="ts" setup>
  import { computed, ref } from 'vue';
  import { EleMessage } from 'ele-admin-plus';
  import type { FormInstance, FormRules } from 'element-plus';
  import {
    addSensitiveWord,
    updateSensitiveWord
  } from '@/api/ecosystem/sensitive-word';
  import type {
    SensitiveWord,
    SensitiveWordOptions,
    SensitiveWordSave
  } from '@/api/ecosystem/sensitive-word/model';

  const props = defineProps<{
    data?: SensitiveWord;
    options: SensitiveWordOptions;
  }>();

  const emit = defineEmits<{ (e: 'done'): void }>();

  const visible = defineModel<boolean>({ default: false });

  const formRef = ref<FormInstance | null>(null);
  const loading = ref(false);

  const isUpdate = computed(() => !!props.data?.id);

  const form = ref<SensitiveWordSave>({
    word: '',
    category: 9,
    action: 1,
    scope: 'all',
    status: 1,
    remark: ''
  });

  const rules: FormRules = {
    word: [
      { required: true, message: '请输入敏感词', trigger: 'blur' },
      { min: 2, message: '至少 2 个字，单字容易误伤', trigger: 'blur' }
    ],
    category: [{ required: true, message: '请选择分类', trigger: 'change' }],
    action: [
      { required: true, message: '请选择命中后的处理方式', trigger: 'change' }
    ],
    scope: [{ required: true, message: '请选择适用范围', trigger: 'change' }]
  };

  const actionTip = computed(() =>
    form.value.action === 1
      ? '企业提交时当场失败，并被提示修改内容。只用于明确违规的词。'
      : '不影响企业提交，但会标红进入人工审核队列。把握不大的词用这个。'
  );

  const onOpen = () => {
    if (props.data) {
      form.value = {
        id: props.data.id,
        word: props.data.word,
        category: props.data.category,
        action: props.data.action,
        scope: props.data.scope,
        status: props.data.status,
        remark: props.data.remark ?? ''
      };
    } else {
      form.value = {
        word: '',
        category: 9,
        action: 1,
        scope: 'all',
        status: 1,
        remark: ''
      };
    }
  };

  const save = () => {
    formRef.value?.validate?.((valid) => {
      if (!valid) {
        return;
      }
      loading.value = true;
      const payload = { ...form.value, word: form.value.word?.trim() };
      const req = isUpdate.value
        ? updateSensitiveWord(payload)
        : addSensitiveWord(payload);
      req
        .then((msg) => {
          loading.value = false;
          EleMessage.success({ message: msg as string, plain: true });
          visible.value = false;
          emit('done');
        })
        .catch((e) => {
          loading.value = false;
          EleMessage.error({ message: e.message, plain: true });
        });
    });
  };
</script>

<style lang="scss" scoped>
  .eco-tip {
    margin-top: 4px;
    font-size: 12px;
    line-height: 1.5;
    color: var(--el-text-color-secondary);
  }
</style>
