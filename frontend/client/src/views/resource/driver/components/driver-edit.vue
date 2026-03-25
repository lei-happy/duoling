<template>
  <el-dialog
    :title="isEdit ? '编辑司机' : '新增司机'"
    :model-value="visible"
    @update:model-value="updateVisible"
    width="700px"
    draggable
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="100px"
      @submit.prevent=""
    >
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="姓名" prop="name">
            <el-input v-model="form.name" placeholder="请输入姓名" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="手机号" prop="phone">
            <el-input v-model="form.phone" placeholder="请输入手机号" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="身份证号">
            <el-input v-model="form.idCard" placeholder="请输入身份证号" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="性别">
            <el-select
              v-model="form.gender"
              placeholder="请选择性别"
              style="width: 100%"
            >
              <el-option label="男" :value="1" />
              <el-option label="女" :value="2" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="驾照类型" prop="licenseType">
            <el-select
              v-model="form.licenseType"
              placeholder="请选择驾照类型"
              style="width: 100%"
            >
              <el-option label="A1" value="A1" />
              <el-option label="A2" value="A2" />
              <el-option label="B1" value="B1" />
              <el-option label="B2" value="B2" />
              <el-option label="C1" value="C1" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="驾照号码">
            <el-input v-model="form.licenseNo" placeholder="请输入驾照号码" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="驾照到期">
            <el-date-picker
              v-model="form.licenseExpire"
              type="date"
              value-format="YYYY-MM-DD"
              placeholder="选择日期"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="资格证号">
            <el-input
              v-model="form.qualificationNo"
              placeholder="请输入资格证号"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="资格证到期">
            <el-date-picker
              v-model="form.qualificationExpire"
              type="date"
              value-format="YYYY-MM-DD"
              placeholder="选择日期"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="紧急联系人">
            <el-input
              v-model="form.emergencyContact"
              placeholder="请输入紧急联系人"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="紧急电话">
            <el-input
              v-model="form.emergencyPhone"
              placeholder="请输入紧急联系电话"
            />
          </el-form-item>
        </el-col>
        <el-col :span="24">
          <el-form-item label="备注">
            <el-input
              v-model="form.remark"
              type="textarea"
              :rows="3"
              placeholder="请输入备注"
            />
          </el-form-item>
        </el-col>
      </el-row>
    </el-form>
    <template #footer>
      <el-button @click="updateVisible(false)">取消</el-button>
      <el-button type="primary" :loading="loading" @click="handleSubmit">
        保存
      </el-button>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
  import { ref, reactive, watch, computed } from 'vue';
  import type { FormInstance, FormRules } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import { addDriver, updateDriver } from '@/api/resource/driver';
  import type { Driver } from '@/api/resource/driver/model';

  const props = defineProps<{
    visible: boolean;
    data: Driver | null;
  }>();

  const emit = defineEmits<{
    (e: 'update:visible', value: boolean): void;
    (e: 'done'): void;
  }>();

  const isEdit = computed(() => !!props.data?.id);
  const formRef = ref<FormInstance>();
  const loading = ref(false);
  const form = reactive<Driver>({});

  const rules = reactive<FormRules>({
    name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
    phone: [{ required: true, message: '请输入手机号', trigger: 'blur' }],
    licenseType: [
      { required: true, message: '请选择驾照类型', trigger: 'change' }
    ]
  });

  watch(
    () => props.visible,
    (val) => {
      if (val) {
        if (props.data) {
          Object.assign(form, props.data);
        } else {
          Object.keys(form).forEach((k) => {
            (form as any)[k] = undefined;
          });
        }
      }
    }
  );

  const updateVisible = (val: boolean) => {
    emit('update:visible', val);
  };

  const handleSubmit = () => {
    formRef.value?.validate(async (valid) => {
      if (!valid) return;
      loading.value = true;
      try {
        if (isEdit.value) {
          await updateDriver(form);
        } else {
          await addDriver(form);
        }
        EleMessage.success({ message: '操作成功', plain: true });
        updateVisible(false);
        emit('done');
      } catch (e: any) {
        EleMessage.error({ message: e.message, plain: true });
      } finally {
        loading.value = false;
      }
    });
  };
</script>
