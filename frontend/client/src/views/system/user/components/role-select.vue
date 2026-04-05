<!-- 角色选择下拉框 -->
<template>
  <floating-label
    type="select"
    :multiple="true"
    :model-value="roleIds"
    :label="placeholder"
    clearable
    @update:model-value="updateValue"
  >
    <el-option
      v-for="item in data"
      :key="item.roleId"
      :value="(item as any).roleId"
      :label="item.roleName"
    />
  </floating-label>
</template>

<script lang="ts" setup>
  import { ref, computed } from 'vue';
  import { EleMessage } from 'ele-admin-plus';
  import FloatingLabel from '@shared/FloatingLabel/index.vue';
  import { listRoles } from '@/api/system/role';
  import type { Role } from '@/api/system/role/model';

  const props = withDefaults(
    defineProps<{
      /** 选中的角色 */
      modelValue?: Role[];
      /** 提示文本 */
      placeholder?: string;
    }>(),
    {
      placeholder: '请选择角色'
    }
  );

  const emit = defineEmits<{
    (e: 'update:modelValue', value: Role[]): void;
  }>();

  /** 选中的角色id */
  const roleIds = computed(
    () => props.modelValue?.map?.((d) => d.roleId as number) ?? []
  );

  /** 角色数据 */
  const data = ref<Role[]>([]);

  /** 更新选中数据 */
  const updateValue = (value: number[] | undefined | null) => {
    if (value == null || !value.length) {
      emit('update:modelValue', []);
      return;
    }
    emit(
      'update:modelValue',
      value.map((v) => ({ roleId: v }))
    );
  };

  /** 获取角色数据 */
  listRoles()
    .then((list) => {
      data.value = list;
    })
    .catch((e) => {
      EleMessage.error({ message: e.message, plain: true });
    });
</script>
