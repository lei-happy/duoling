<!-- 高级表单 -->
<template>
  <EleProForm
    v-bind="{ ...emitProps, ...$props }"
    ref="proFormRef"
    :httpRequest="request"
  >
    <template
      v-for="name in Object.keys($slots).filter((k) => !ownSlots.includes(k))"
      #[name]="slotProps"
    >
      <slot :name="name" v-bind="slotProps || {}"></slot>
    </template>
    <template #dictRadio="{ item, modelValue, updateValue }">
      <DictData
        code=""
        v-bind="item.props || {}"
        type="radio"
        :modelValue="modelValue"
        @update:modelValue="updateValue"
      />
    </template>
    <template #dictCheckbox="{ item, modelValue, updateValue }">
      <DictData
        code=""
        v-bind="item.props || {}"
        type="checkbox"
        :modelValue="modelValue"
        @update:modelValue="updateValue"
      />
    </template>
    <template #dictSelect="{ item, modelValue, updateValue }">
      <DictData
        code=""
        v-bind="item.props || {}"
        type="select"
        :modelValue="modelValue"
        @update:modelValue="updateValue"
      />
    </template>
    <template #dictMultipleSelect="{ item, modelValue, updateValue }">
      <DictData
        code=""
        v-bind="item.props || {}"
        type="multipleSelect"
        :modelValue="modelValue"
        @update:modelValue="updateValue"
      />
    </template>
    <template
      #imageUpload="{ item, modelValue, updateValue, itemComponentRef }"
    >
      <ImageUpload
        v-bind="item.props || {}"
        :ref="itemComponentRef"
        :modelValue="modelValue"
        @update:modelValue="updateValue"
      />
    </template>
    <template #fileUpload="{ item, modelValue, updateValue, itemComponentRef }">
      <FileUpload
        v-bind="item.props || {}"
        :ref="itemComponentRef"
        :modelValue="modelValue"
        @update:modelValue="updateValue"
      />
    </template>
    <template #regions="{ item, modelValue, updateValue }">
      <RegionsSelect
        v-bind="item.props || {}"
        :modelValue="modelValue"
        @update:modelValue="updateValue"
      />
    </template>
    <template #multipleRegions="{ item, modelValue, updateValue }">
      <RegionsSelect
        v-bind="item.props || {}"
        :multiple="true"
        :modelValue="modelValue"
        @update:modelValue="updateValue"
      />
    </template>
    <template #iconSelect="{ item, modelValue, updateValue }">
      <IconSelect
        v-bind="item.props || {}"
        :modelValue="modelValue"
        @update:modelValue="updateValue"
      />
    </template>
    <template #editor="{ item, modelValue, updateValue }">
      <TinymceEditor
        v-bind="item.props || {}"
        :modelValue="modelValue"
        @update:modelValue="updateValue"
      />
    </template>
  </EleProForm>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import type { EleProFormInstance } from 'ele-admin-plus/es/ele-app/plusx';
  import {
    useComponentEvents,
    useComponentExpose
  } from 'ele-admin-plus/es/utils/hook';
  import {
    proFormProps,
    proFormEmits
  } from 'ele-admin-plus/es/ele-pro-form/props';
  import DictData from '@/components/DictData/index.vue';
  import ImageUpload from '@/components/ImageUpload/index.vue';
  import FileUpload from '@/components/FileUpload/index.vue';
  import RegionsSelect from '@/components/RegionsSelect/index.vue';
  import IconSelect from '@/components/IconSelect/index.vue';
  import TinymceEditor from '@/components/TinymceEditor/index.vue';
  import request from '@/utils/request';
  const ownSlots = [
    'default',
    'dictRadio',
    'dictCheckbox',
    'dictSelect',
    'dictMultipleSelect',
    'imageUpload',
    'fileUpload',
    'regions',
    'multipleRegions',
    'iconSelect',
    'editor'
  ];

  defineOptions({ name: 'ProForm' });

  defineProps(proFormProps);

  const emit = defineEmits(proFormEmits);

  const { emitProps } = useComponentEvents(proFormEmits, emit);

  /** 高级表单组件 */
  const proFormRef = ref<EleProFormInstance>(null);

  const exposeValues = useComponentExpose(
    proFormRef,
    [
      'validate',
      'validateField',
      'resetFields',
      'scrollToField',
      'clearValidate'
    ],
    ['formRef']
  );

  defineExpose({ ...exposeValues, proFormRef });
</script>
