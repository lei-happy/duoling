<template>
  <ele-page>
    <ele-card header="基础用法">
      <ele-edit-tag
        v-model="tags"
        :size="size"
        :type="type"
        :effect="effect"
        :validator="validator"
        :tooltip-props="{ effect: 'danger' }"
        style="margin-top: 0"
        :readonly="readonly"
        :disabled="disabled"
        :round="round"
        :hit="hit"
      />
      <ele-text type="secondary" style="padding: 8px 0">{{
        JSON.stringify(tags)
      }}</ele-text>
      <option-item label="尺寸选择">
        <el-radio-group v-model="size">
          <el-radio value="large" label="large" />
          <el-radio value="default" label="default" />
          <el-radio value="small" label="small" />
        </el-radio-group>
      </option-item>
      <option-item label="主题颜色" style="margin-top: 8px">
        <el-radio-group v-model="type">
          <el-radio value="primary" label="primary" />
          <el-radio value="success" label="success" />
          <el-radio value="info" label="info" />
          <el-radio value="warning" label="warning" />
          <el-radio value="danger" label="danger" />
        </el-radio-group>
      </option-item>
      <option-item label="主题风格" style="margin-top: 8px">
        <el-radio-group v-model="effect">
          <el-radio value="light" label="light" />
          <el-radio value="dark" label="dark" />
          <el-radio value="plain" label="plain" />
        </el-radio-group>
      </option-item>
      <option-item label="椭圆风格" style="margin-top: 8px">
        <el-radio-group v-model="round">
          <el-radio :value="false" label="否" />
          <el-radio :value="true" label="是" />
        </el-radio-group>
      </option-item>
      <option-item label="加深边框" style="margin-top: 8px">
        <el-radio-group v-model="hit">
          <el-radio :value="false" label="否" />
          <el-radio :value="true" label="是" />
        </el-radio-group>
      </option-item>
      <option-item label="是否禁用" style="margin-top: 8px">
        <el-radio-group v-model="disabled">
          <el-radio :value="false" label="否" />
          <el-radio :value="true" label="是" />
        </el-radio-group>
      </option-item>
      <option-item label="是否只读" style="margin-top: 8px">
        <el-radio-group v-model="readonly">
          <el-radio :value="false" label="否" />
          <el-radio :value="true" label="是" />
        </el-radio-group>
      </option-item>
    </ele-card>
    <ele-card header="进阶用法">
      <div style="margin-bottom: 12px">自定义异步验证:</div>
      <ele-edit-tag
        v-model="tags2"
        :size="size"
        :type="type"
        :effect="effect"
        :validator="validator2"
        :tooltip-props="{
          effect: 'danger',
          popperOptions: { strategy: 'fixed' }
        }"
        :round="round"
        :hit="hit"
      />
      <div style="margin: 22px 0 12px 0">输入 `,` 自动分割为多个:</div>
      <ele-edit-tag
        :model-value="tags3"
        @update:modelValue="updateModelValue3"
        :size="size"
        :type="type"
        :effect="effect"
        :round="round"
        :hit="hit"
      />
    </ele-card>
  </ele-page>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import type { TagProps } from 'element-plus';
  import OptionItem from '@/views/extension/avatar/components/option-item.vue';

  defineOptions({ name: 'ExtensionTag' });

  /** 选中尺寸 */
  const size = ref<TagProps['size']>('default');

  /** 选中类型 */
  const type = ref<TagProps['type']>('info');

  /** 选中主题 */
  const effect = ref<TagProps['effect']>('light');

  /** 标签输入 */
  const tags = ref(['标签一', '标签二', '标签三']);

  /** 是否圆形 */
  const round = ref(false);

  /** 是否边框 */
  const hit = ref(false);

  /** 是否只读 */
  const readonly = ref(false);

  /** 是否禁用 */
  const disabled = ref(false);

  /** 限制不能重复添加 */
  const validator = (value: string) => {
    return new Promise<void>((resolve, reject) => {
      if (tags.value.includes(value)) {
        reject(new Error(value + '已经存在'));
        return;
      }
      resolve();
    });
  };

  /** 标签输入 */
  const tags2 = ref(['标签一', '标签二', '标签三']);

  /** 自定义异步验证 */
  const validator2 = (value: string) => {
    return new Promise<void>((resolve, reject) => {
      setTimeout(() => {
        if (value !== 'eleadmin') {
          reject(new Error('只能输入eleadmin'));
          return;
        }
        resolve();
      }, 1000);
    });
  };

  /** 标签输入 */
  const tags3 = ref(['标签一', '标签二', '标签三']);

  const updateModelValue3 = (modelValue: string[]) => {
    tags3.value = modelValue.map((d) => d.split(',')).flat();
  };
</script>
