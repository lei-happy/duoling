<template>
  <el-dialog
    :title="isEdit ? '编辑成本政策' : '新增成本政策'"
    :model-value="visible"
    width="560px"
    draggable
    :close-on-click-modal="false"
    @update:model-value="updateVisible"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="96px"
      @submit.prevent=""
    >
      <el-form-item label="政策编号" prop="policyNo">
        <el-input
          v-model.trim="form.policyNo"
          :disabled="isEdit"
          placeholder="请输入政策编号"
          clearable
        />
      </el-form-item>
      <el-form-item label="政策名称" prop="policyName">
        <el-input
          v-model.trim="form.policyName"
          placeholder="请输入政策名称"
          clearable
        />
      </el-form-item>
      <el-form-item label="适用范围" prop="scopeType">
        <el-select v-model="form.scopeType" placeholder="请选择适用范围">
          <el-option label="全局默认" :value="0" />
          <el-option label="指定承运商" :value="1" />
          <el-option label="指定司机" :value="2" />
          <el-option label="指定运力" :value="3" />
        </el-select>
      </el-form-item>
      <el-form-item
        v-if="form.scopeType !== 0"
        label="范围对象ID"
        prop="scopeId"
      >
        <el-input-number
          v-model="form.scopeId"
          :min="1"
          controls-position="right"
          placeholder="承运商/司机/运力ID"
          style="width: 100%"
        />
      </el-form-item>
      <el-form-item label="承运类型" prop="carrierType">
        <el-select v-model="form.carrierType" placeholder="不限" clearable>
          <el-option label="自有车" :value="1" />
          <el-option label="承运商" :value="2" />
          <el-option label="社会运力" :value="3" />
        </el-select>
      </el-form-item>
      <el-form-item label="生效期" prop="period">
        <el-date-picker
          v-model="form.period"
          type="daterange"
          value-format="YYYY-MM-DD"
          range-separator="~"
          start-placeholder="开始"
          end-placeholder="结束（可空=长期）"
          :clearable="true"
          style="width: 100%"
        />
      </el-form-item>
      <el-form-item label="优先级" prop="priority">
        <el-input-number
          v-model="form.priority"
          :min="0"
          controls-position="right"
          style="width: 100%"
        />
      </el-form-item>
      <el-form-item label="备注">
        <el-input
          v-model="form.remark"
          type="textarea"
          :rows="2"
          placeholder="请输入备注"
        />
      </el-form-item>
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
  import { ref, reactive, watch, computed, nextTick } from 'vue';
  import type { FormInstance, FormRules } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import { addPolicy, updatePolicy } from '@/api/billing/cost-policy';
  import type { CostPolicy } from '@/api/billing/cost-policy/model';

  interface PolicyForm {
    id?: number;
    policyNo?: string;
    policyName?: string;
    scopeType: number;
    scopeId?: number | null;
    carrierType?: number | null;
    period: [string, string] | null;
    priority: number;
    remark?: string | null;
    status?: number;
  }

  const props = defineProps<{
    visible: boolean;
    data: CostPolicy | null;
  }>();

  const emit = defineEmits<{
    (e: 'update:visible', value: boolean): void;
    (e: 'done'): void;
  }>();

  const isEdit = computed(() => !!props.data?.id);
  const formRef = ref<FormInstance>();
  const loading = ref(false);
  const form = reactive<PolicyForm>({
    scopeType: 0,
    period: null,
    priority: 0
  });

  const rules = reactive<FormRules>({
    policyNo: [{ required: true, message: '请输入政策编号', trigger: 'blur' }],
    policyName: [
      { required: true, message: '请输入政策名称', trigger: 'blur' }
    ],
    scopeType: [
      { required: true, message: '请选择适用范围', trigger: 'change' }
    ],
    scopeId: [
      {
        validator: (_r, v, cb) => {
          if (form.scopeType !== 0 && !v) {
            cb(new Error('请填写范围对象ID'));
            return;
          }
          cb();
        },
        trigger: 'blur'
      }
    ],
    period: [{ required: true, message: '请选择生效期', trigger: 'change' }]
  });

  function resetForCreate() {
    Object.assign(form, {
      id: undefined,
      policyNo: undefined,
      policyName: undefined,
      scopeType: 0,
      scopeId: undefined,
      carrierType: undefined,
      period: null,
      priority: 0,
      remark: undefined,
      status: undefined
    });
  }

  watch(
    () => props.visible,
    (val) => {
      if (!val) return;
      if (props.data?.id) {
        Object.assign(form, {
          id: props.data.id,
          policyNo: props.data.policyNo,
          policyName: props.data.policyName,
          scopeType: props.data.scopeType,
          scopeId: props.data.scopeId,
          carrierType: props.data.carrierType,
          priority: props.data.priority ?? 0,
          remark: props.data.remark,
          status: props.data.status,
          period:
            props.data.effectiveDate && props.data.expiryDate
              ? [props.data.effectiveDate, props.data.expiryDate]
              : props.data.effectiveDate
                ? [props.data.effectiveDate, props.data.effectiveDate]
                : null
        });
      } else {
        resetForCreate();
      }
      nextTick(() => formRef.value?.clearValidate());
    }
  );

  const updateVisible = (val: boolean) => emit('update:visible', val);

  const handleSubmit = () => {
    formRef.value?.validate(async (valid) => {
      if (!valid) return;
      loading.value = true;
      try {
        const payload: CostPolicy = {
          id: form.id,
          policyNo: form.policyNo as string,
          policyName: form.policyName as string,
          scopeType: form.scopeType,
          scopeId: form.scopeType === 0 ? null : form.scopeId,
          carrierType: form.carrierType ?? null,
          effectiveDate: form.period?.[0] as string,
          expiryDate: form.period?.[1] ?? null,
          priority: form.priority,
          remark: form.remark,
          status: form.status
        };
        if (isEdit.value) {
          await updatePolicy(payload);
        } else {
          await addPolicy(payload);
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
