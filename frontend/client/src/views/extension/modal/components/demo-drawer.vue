<template>
  <ele-card header="抽屉组件">
    <option-item label="方向" :responsive="false">
      <el-radio-group v-model="direction">
        <el-radio value="rtl" label="右" />
        <el-radio value="ltr" label="左" />
        <el-radio value="btt" label="下" />
        <el-radio value="ttb" label="上" />
      </el-radio-group>
    </option-item>
    <option-item label="显示头部" :responsive="false" style="margin-top: 16px">
      <el-switch v-model="withHeader" size="small" />
    </option-item>
    <option-item label="显示底部" :responsive="false">
      <el-switch v-model="withFooter" size="small" />
    </option-item>
    <option-item label="限制在主体区域" :responsive="false">
      <el-switch v-model="inner" size="small" />
    </option-item>
    <option-item label="支持拉伸大小" :responsive="false">
      <el-switch v-model="resizable" size="small" />
    </option-item>
    <div style="margin-top: 20px">
      <el-button class="ele-btn-icon" @click="openDrawer">打开抽屉</el-button>
    </div>
  </ele-card>
  <ele-drawer
    :direction="direction"
    :with-header="withHeader"
    :inner="inner"
    :resizable="resizable"
    :size="430"
    title="表单项配置"
    v-model="visible"
    :body-style="{ paddingBottom: '8px' }"
    @closed="cancelDrawer"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="70px"
      @submit.prevent=""
    >
      <el-form-item label="用户名" prop="nickname">
        <el-input
          clearable
          v-model="form.nickname"
          placeholder="请输入用户名"
        />
      </el-form-item>
      <el-form-item label="性别" prop="sex">
        <el-select
          clearable
          v-model="form.sex"
          placeholder="请选择性别"
          class="ele-fluid"
        >
          <el-option value="男">男</el-option>
          <el-option value="女">女</el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="手机号" prop="phone">
        <el-input clearable v-model="form.phone" placeholder="请输入手机号" />
      </el-form-item>
      <el-form-item label="邮箱" prop="email">
        <el-input clearable v-model="form.email" placeholder="请输入邮箱" />
      </el-form-item>
      <el-form-item label="个人简介">
        <el-input
          :rows="4"
          type="textarea"
          v-model="form.introduction"
          placeholder="请输入个人简介"
        />
      </el-form-item>
    </el-form>
    <template v-if="withFooter" #footer>
      <el-button @click="cancelDrawer">取消</el-button>
      <el-button type="primary" @click="handleSave">保存</el-button>
    </template>
  </ele-drawer>
</template>

<script lang="ts" setup>
  import { ref, reactive } from 'vue';
  import type { FormInstance, FormRules } from 'element-plus';
  import { useMessage } from 'ele-admin-plus';
  import { useFormData } from '@/utils/use-form-data';
  import OptionItem from '@/views/extension/avatar/components/option-item.vue';

  const messageIns = useMessage({ plain: true });

  /** 抽屉是否打开 */
  const visible = ref(false);

  /** 方向 */
  const direction = ref<'rtl' | 'ltr' | 'btt' | 'ttb'>('rtl');

  /** 显示头部 */
  const withHeader = ref(true);

  /** 显示底部 */
  const withFooter = ref(true);

  /** 限制在主体区域 */
  const inner = ref(false);

  /** 支持拉伸大小 */
  const resizable = ref(false);

  /** 打开抽屉 */
  const openDrawer = () => {
    visible.value = true;
  };

  /** 表单实例 */
  const formRef = ref<FormInstance | null>(null);

  /** 表单数据 */
  const [form, resetFields] = useFormData({
    nickname: '',
    sex: void 0,
    phone: '',
    email: '',
    introduction: ''
  });

  /** 表单验证规则 */
  const rules = reactive<FormRules>({
    nickname: [
      {
        required: true,
        message: '请输入用户名',
        type: 'string',
        trigger: 'blur'
      }
    ],
    sex: [
      {
        required: true,
        message: '请选择性别',
        type: 'string',
        trigger: 'change'
      }
    ],
    phone: [
      {
        required: true,
        message: '请输入手机号',
        type: 'string',
        trigger: 'blur'
      }
    ],
    email: [
      {
        required: true,
        message: '请输入邮箱',
        type: 'string',
        trigger: 'blur'
      }
    ]
  });

  /** 关闭抽屉 */
  const cancelDrawer = () => {
    resetFields();
    formRef.value?.clearValidate?.();
    visible.value = false;
  };

  /** 保存编辑 */
  const handleSave = () => {
    formRef.value?.validate?.((valid) => {
      if (!valid) {
        return;
      }
      messageIns.success({ message: '保存成功', inner: inner.value });
    });
  };
</script>
