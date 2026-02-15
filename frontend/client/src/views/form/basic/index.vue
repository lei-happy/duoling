<template>
  <div>
    <ele-card style="border-radius: 0">
      <ele-text type="heading" size="lg">基础表单</ele-text>
      <ele-text type="placeholder" style="margin-top: 6px">
        表单页用于向用户收集或验证信息，基础表单常见于数据项较少的表单场景。
      </ele-text>
    </ele-card>
    <ele-page :multi-card="false">
      <ele-card>
        <el-form
          status-icon
          ref="formRef"
          :model="form"
          :rules="rules"
          label-width="80px"
          :scroll-to-error="true"
          style="max-width: 700px; margin: 10px auto"
          @submit.prevent=""
        >
          <el-form-item label="标题" prop="title">
            <el-input clearable v-model="form.title" placeholder="请输入标题" />
          </el-form-item>
          <el-form-item label="起止日期" prop="datetime">
            <el-date-picker
              unlink-panels
              type="daterange"
              v-model="form.datetime"
              range-separator="-"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              class="ele-fluid"
            />
          </el-form-item>
          <el-form-item label="目标描述" prop="goal">
            <el-input
              show-word-limit
              maxlength="800"
              :rows="4"
              type="textarea"
              v-model="form.goal"
              placeholder="请输入目标描述"
            />
          </el-form-item>
          <el-form-item label="衡量标准" prop="standard">
            <el-input
              :rows="4"
              type="textarea"
              v-model="form.standard"
              placeholder="请输入衡量标准"
            />
          </el-form-item>
          <el-form-item label="地点" prop="address">
            <el-select
              clearable
              v-model="form.address"
              placeholder="请选择地点"
              class="ele-fluid"
              :popper-options="{ strategy: 'fixed' }"
            >
              <el-option value="1" label="地点一" />
              <el-option value="2" label="地点二" />
              <el-option value="3" label="地点三" />
            </el-select>
          </el-form-item>
          <el-form-item label="邀评人" prop="invites">
            <el-select
              multiple
              clearable
              v-model="form.invites"
              placeholder="请选择邀评人"
              class="ele-fluid"
              :popper-options="{ strategy: 'fixed' }"
            >
              <el-option-group label="分组一">
                <el-option :value="1" label="SunSmile" />
                <el-option :value="2" label="你的名字很好听" />
                <el-option :value="3" label="全村人的希望" />
              </el-option-group>
              <el-option-group label="分组二">
                <el-option :value="4" label="Jasmine" />
                <el-option :value="5" label="酷酷的大叔" />
              </el-option-group>
            </el-select>
          </el-form-item>
          <el-form-item label="权重" prop="weight">
            <el-input-number
              :min="0"
              :max="100"
              v-model="form.weight"
              controls-position="right"
              class="ele-fluid"
              style="max-width: 160px"
            />
            <div style="padding-left: 8px">%</div>
          </el-form-item>
          <el-form-item label="目标公开" style="margin-bottom: 0">
            <el-radio-group v-model="form.publicType">
              <el-radio :value="1" label="公开" />
              <el-radio :value="2" label="部分公开" />
              <el-radio :value="3" label="不公开" />
            </el-radio-group>
          </el-form-item>
          <el-form-item
            v-if="form.publicType === 2"
            style="margin-bottom: 16px"
          >
            <el-input
              clearable
              v-model="form.publicValue"
              placeholder="公开给"
              class="ele-fluid"
            />
          </el-form-item>
          <el-form-item>
            <ele-text type="placeholder" style="line-height: 1.6">
              客户、邀评人默认被分享
            </ele-text>
          </el-form-item>
          <el-form-item>
            <el-button @click="finishPageTab()">关闭</el-button>
            <el-button type="primary" :loading="loading" @click="submit">
              提交
            </el-button>
          </el-form-item>
        </el-form>
      </ele-card>
    </ele-page>
  </div>
</template>

<script lang="ts" setup>
  import { ref, reactive } from 'vue';
  import type { FormInstance, FormRules } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import { useFormData } from '@/utils/use-form-data';
  import { usePageTab } from '@/utils/use-page-tab';

  defineOptions({ name: 'FormBasic' });

  const { finishPageTab } = usePageTab();

  /** 加载状态 */
  const loading = ref(false);

  /** 表单数据类型 */
  interface FormData {
    title?: string;
    datetime?: [string, string];
    goal?: string;
    standard?: string;
    address?: string;
    invites?: string[];
    weight?: number;
    publicType?: number;
    publicValue?: string;
  }

  /** 表单实例 */
  const formRef = ref<FormInstance | null>(null);

  /** 表单数据 */
  const [form, resetFields] = useFormData<FormData>({
    title: '',
    datetime: void 0,
    goal: '',
    standard: '',
    address: void 0,
    invites: [],
    weight: 0,
    publicType: 1,
    publicValue: ''
  });

  /** 表单验证规则 */
  const rules = reactive<FormRules>({
    title: [
      {
        required: true,
        message: '请输入标题',
        type: 'string',
        trigger: 'blur'
      }
    ],
    datetime: [
      {
        required: true,
        message: '请选择起止日期',
        type: 'array',
        trigger: 'change'
      }
    ],
    goal: [
      {
        required: true,
        message: '请输入目标描述',
        type: 'string',
        trigger: 'blur'
      }
    ],
    standard: [
      {
        required: true,
        message: '请输入衡量标准',
        type: 'string',
        trigger: 'blur'
      }
    ],
    address: [
      {
        required: true,
        message: '请选择地点',
        type: 'string',
        trigger: 'change'
      }
    ],
    invites: [
      {
        required: true,
        message: '请选择邀评人',
        type: 'array',
        trigger: 'change'
      }
    ],
    weight: [
      {
        required: true,
        message: '请输入权重',
        type: 'number',
        trigger: 'change'
      }
    ]
  });

  /** 提交 */
  const submit = () => {
    formRef.value?.validate?.((valid) => {
      if (!valid) {
        return;
      }
      loading.value = true;
      setTimeout(() => {
        loading.value = false;
        resetFields();
        EleMessage.success({ message: '提交成功', plain: true });
      }, 1500);
    });
  };
</script>
