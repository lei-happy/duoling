<!-- 机构选择下拉框 -->
<template>
  <el-tree-select
    clearable
    filterable
    :data="data"
    check-strictly
    default-expand-all
    node-key="organizationId"
    :props="{ label: 'organizationName' }"
    :placeholder="placeholder"
    v-model="model"
    class="ele-fluid"
    :popper-options="{ strategy: 'fixed' }"
  />
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import { EleMessage, toTree } from 'ele-admin-plus';
  import { listOrganizations } from '@/api/system/organization';
  import type { Organization } from '@/api/system/organization/model';

  withDefaults(
    defineProps<{
      /** 提示信息 */
      placeholder?: string;
    }>(),
    {
      placeholder: '请选择所属机构'
    }
  );

  /** 选中的机构 */
  const model = defineModel<number | string>({ type: [Number, String] });

  /** 机构数据 */
  const data = ref<Organization[]>([]);

  /** 获取机构数据 */
  listOrganizations()
    .then((list) => {
      data.value = toTree({
        data: list,
        idField: 'organizationId',
        parentIdField: 'parentId'
      });
    })
    .catch((e) => {
      EleMessage.error({ message: e.message, plain: true });
    });
</script>
