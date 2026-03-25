<template>
  <el-dialog
    :title="isEdit ? '编辑线路' : '新增线路'"
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
          <el-form-item label="线路名称" prop="routeName">
            <el-input
              v-model="form.routeName"
              placeholder="请输入线路名称"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="线路编码" prop="routeCode">
            <el-input
              v-model="form.routeCode"
              placeholder="请输入线路编码"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="起点" prop="origin">
            <el-input v-model="form.origin" placeholder="请输入起点" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="终点" prop="destination">
            <el-input v-model="form.destination" placeholder="请输入终点" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="里程(km)">
            <el-input-number
              v-model="form.distance"
              :min="0"
              :precision="1"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="预计时长(h)">
            <el-input-number
              v-model="form.estimatedHours"
              :min="0"
              :precision="1"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
        <el-col :span="24">
          <el-form-item label="途经点">
            <el-input
              v-model="form.waypoints"
              type="textarea"
              :rows="2"
              placeholder="请输入途经点，多个用逗号分隔"
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
  import { addRoute, updateRoute } from '@/api/resource/route';
  import type { Route } from '@/api/resource/route/model';

  const props = defineProps<{
    visible: boolean;
    data: Route | null;
  }>();

  const emit = defineEmits<{
    (e: 'update:visible', value: boolean): void;
    (e: 'done'): void;
  }>();

  const isEdit = computed(() => !!props.data?.id);
  const formRef = ref<FormInstance>();
  const loading = ref(false);
  const form = reactive<Route>({});

  const rules = reactive<FormRules>({
    routeName: [
      { required: true, message: '请输入线路名称', trigger: 'blur' }
    ],
    routeCode: [
      { required: true, message: '请输入线路编码', trigger: 'blur' }
    ],
    origin: [{ required: true, message: '请输入起点', trigger: 'blur' }],
    destination: [{ required: true, message: '请输入终点', trigger: 'blur' }]
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
          await updateRoute(form);
        } else {
          await addRoute(form);
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
