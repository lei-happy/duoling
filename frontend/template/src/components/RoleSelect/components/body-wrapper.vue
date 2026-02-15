<template>
  <div class="ele-role-select-wrapper">
    <div class="ele-role-select-body">
      <!-- 搜索表单 -->
      <ElForm
        labelWidth="78px"
        class="ele-role-select-search"
        @keyup.enter="handleSearch"
        @submit.prevent=""
      >
        <ElRow :gutter="16">
          <ElCol :lg="7" :md="8" :sm="9" :xs="24">
            <ElFormItem :label="lang.labelRoleName">
              <ElInput
                :clearable="true"
                v-model.trim="form.roleName"
                placeholder=""
              />
            </ElFormItem>
          </ElCol>
          <ElCol :lg="7" :md="8" :sm="9" :xs="24">
            <ElFormItem :label="lang.labelRoleCode">
              <ElInput
                :clearable="true"
                v-model.trim="form.roleCode"
                placeholder=""
              />
            </ElFormItem>
          </ElCol>
          <ElCol :lg="10" :md="8" :sm="6" :xs="24">
            <ElFormItem labelWidth="0px">
              <BtnItems
                :wrap="false"
                :items="[
                  { preset: 'search', onClick: () => handleSearch() },
                  { preset: 'reset', onClick: () => handleReset() }
                ]"
              />
            </ElFormItem>
          </ElCol>
        </ElRow>
      </ElForm>
      <!-- 表格 -->
      <slot></slot>
    </div>
    <!-- 已选列表 -->
    <div class="ele-role-select-right">
      <div class="ele-role-select-right-header">
        <div class="ele-role-select-right-title">
          <span>{{ lang.selected }}</span>
          <span>{{ selectedItems.length || 0 }}</span>
          <span>{{ lang.selectedUnit }}</span>
        </div>
        <ElLink
          type="danger"
          underline="never"
          class="ele-role-select-right-clear"
          @click="clearSelections"
        >
          {{ lang.clear }}
        </ElLink>
      </div>
      <VueDraggable
        itemKey="value"
        :animation="300"
        :setData="() => void 0"
        :delayOnTouchOnly="true"
        :delay="150"
        :disabled="!multiple"
        class="ele-role-select-right-body"
        :class="{ 'is-sortable': multiple }"
        :modelValue="selectedItems"
        @update:modelValue="updateModelValue"
      >
        <template #item="{ element: item }">
          <div class="ele-role-select-right-item">
            <ElIcon class="ele-role-select-right-icon">
              <component v-if="itemIcon" :is="itemIcon" />
              <IdcardOutlined v-else />
            </ElIcon>
            <div class="ele-role-select-right-label">{{ item.label }}</div>
            <ElIcon
              class="ele-role-select-right-del"
              @click="handleRemove(item)"
            >
              <CloseOutlined />
            </ElIcon>
          </div>
        </template>
      </VueDraggable>
    </div>
  </div>
</template>

<script lang="ts" setup>
  import { inject, unref, computed, onMounted } from 'vue';
  import VueDraggable from 'vuedraggable';
  import { CloseOutlined, IdcardOutlined } from 'ele-admin-plus/es/icons';
  import type { UserComponent } from 'ele-admin-plus/es/ele-app/types';
  import type {
    PopperType,
    SelectedItem
  } from 'ele-admin-plus/es/ele-basic-select/types';
  import { SELECT_DATA_KEY } from 'ele-admin-plus/es/ele-basic-select/util';
  import { useFormData } from '@/utils/use-form-data';
  import BtnItems from '@/components/BtnItems/index.vue';
  import type { RoleSelectLocale, RoleParam } from '../types';

  const props = defineProps<{
    /** 是否多选 */
    multiple?: boolean;
    /** 下拉组件类型 */
    popperType?: PopperType;
    /** 已选列表项图标组件 */
    itemIcon?: UserComponent;
    /** 组件文案 */
    lang: RoleSelectLocale;
  }>();

  const emit = defineEmits<{
    /** 搜索事件 */
    search: [form: RoleParam];
    /** 挂载事件 */
    bodyMounted: [];
  }>();

  /** 下拉组件选中标签数据操作 */
  const selectProvider = inject(SELECT_DATA_KEY, null);

  /** 是否是弹窗模式 */
  const isModalType = computed<boolean>(() => {
    return props.popperType === 'modal' || props.popperType === 'drawer';
  });

  /** 选中标签数据 */
  const selectedItems = computed<SelectedItem[]>(() => {
    const items = isModalType.value
      ? selectProvider?.tempSelectedItems
      : selectProvider?.selectedItems;
    return unref(items) || [];
  });

  /** 清空选中标签数据 */
  const clearSelections = () => {
    if (selectProvider) {
      if (isModalType.value) {
        selectProvider.clearTempSelectedItems();
      } else {
        selectProvider.clearSelectedItems();
      }
    }
  };

  /** 删除选中标签项 */
  const handleRemove = (item: SelectedItem) => {
    if (selectProvider) {
      if (isModalType.value) {
        selectProvider.removeTempSelectedItem(item);
      } else {
        selectProvider.removeSelectedItem(item);
      }
    }
  };

  /** 更新选中标签数据排序 */
  const updateModelValue = (items: SelectedItem[]) => {
    if (selectProvider) {
      if (isModalType.value) {
        selectProvider.updateTempSelectedItems(items);
      } else {
        selectProvider.updateSelectedItems(items);
      }
    }
  };

  /** 搜索表单数据 */
  const [form, resetFields] = useFormData<RoleParam>({
    roleName: '',
    roleCode: ''
  });

  /** 搜索 */
  const handleSearch = () => {
    emit('search', { ...form });
  };

  /** 重置 */
  const handleReset = () => {
    resetFields();
    handleSearch();
  };

  /** 触发挂载事件 */
  onMounted(() => {
    emit('bodyMounted');
  });
</script>
