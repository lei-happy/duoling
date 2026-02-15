<template>
  <EleSplitPanel
    :space="0"
    :size="220"
    flexTable="auto"
    :allowCollapse="true"
    :collapseBtnOffset="2"
    v-model:collapse="collapse"
    class="ele-user-select-wrapper"
  >
    <div class="ele-user-select-tree-search">
      <ElInput
        :clearable="true"
        v-model="treeSearchKeywords"
        :placeholder="lang.searchPlaceholder"
        :prefixIcon="SearchOutlined"
      />
    </div>
    <EleLoading :loading="treeLoading" class="ele-user-select-tree-wrapper">
      <ElTree
        ref="treeRef"
        :data="treeData"
        :props="treeProps"
        :nodeKey="deptIdField"
        :filterNodeMethod="filterTreeNode"
        :expandOnClickNode="false"
        :defaultExpandAll="true"
        :highlightCurrent="true"
        class="ele-user-select-tree"
        @nodeClick="handleTreeItemClick"
      >
        <template #default="{ node }">
          <span
            class="el-tree-node__label ele-user-select-tree-label"
            :title="node.label"
          >
            <ElIcon>
              <component v-if="itemIcon" :is="itemIcon" />
              <CityOutlined v-else />
            </ElIcon>
            <span>{{ node.label }}</span>
          </span>
        </template>
      </ElTree>
    </EleLoading>
    <template #body>
      <div class="ele-user-select-body">
        <!-- 搜索表单 -->
        <ElForm
          labelWidth="78px"
          class="ele-user-select-search"
          @keyup.enter="handleSearch"
          @submit.prevent=""
        >
          <ElRow :gutter="16">
            <ElCol :lg="7" :md="8" :sm="9" :xs="24">
              <ElFormItem :label="lang.labelNickname">
                <ElInput
                  :clearable="true"
                  v-model.trim="form.nickname"
                  placeholder=""
                />
              </ElFormItem>
            </ElCol>
            <ElCol :lg="7" :md="8" :sm="9" :xs="24">
              <ElFormItem :label="lang.labelPhone">
                <ElInput
                  :clearable="true"
                  v-model.trim="form.phone"
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
      <div class="ele-user-select-right">
        <div class="ele-user-select-right-header">
          <div class="ele-user-select-right-title">
            <span>{{ lang.selected }}</span>
            <span>{{ selectedItems.length || 0 }}</span>
            <span>{{ lang.selectedUnit }}</span>
          </div>
          <ElLink
            type="danger"
            underline="never"
            class="ele-user-select-right-clear"
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
          class="ele-user-select-right-body"
          :class="{ 'is-sortable': multiple }"
          :modelValue="selectedItems"
          @update:modelValue="updateModelValue"
        >
          <template #item="{ element: item }">
            <div class="ele-user-select-right-item">
              <ElIcon v-if="itemIcon" class="ele-user-select-right-icon">
                <component :is="itemIcon" />
              </ElIcon>
              <div
                v-else-if="item.data?.[avatarField]"
                class="ele-user-select-right-avatar"
              >
                <img :src="item.data?.[avatarField]" />
              </div>
              <div v-else class="ele-user-select-right-avatar is-icon">
                {{
                  item.label && item.label.length > 2
                    ? item.label.substring(item.label.length - 2)
                    : item.label
                }}
              </div>
              <div class="ele-user-select-right-label">{{ item.label }}</div>
              <ElIcon
                class="ele-user-select-right-del"
                @click="handleRemove(item)"
              >
                <CloseOutlined />
              </ElIcon>
            </div>
          </template>
        </VueDraggable>
      </div>
    </template>
  </EleSplitPanel>
</template>

<script lang="ts" setup>
  import { inject, unref, computed, ref, watch } from 'vue';
  import VueDraggable from 'vuedraggable';
  import {
    CloseOutlined,
    SearchOutlined,
    CityOutlined
  } from 'ele-admin-plus/es/icons';
  import { EleMessage, toTree } from 'ele-admin-plus';
  import type { UserComponent } from 'ele-admin-plus/es/ele-app/types';
  import type { ElTreeInstance } from 'ele-admin-plus/es/ele-app/el';
  import type {
    PopperType,
    SelectedItem
  } from 'ele-admin-plus/es/ele-basic-select/types';
  import { SELECT_DATA_KEY } from 'ele-admin-plus/es/ele-basic-select/util';
  import { useMobile } from '@/utils/use-mobile';
  import { useFormData } from '@/utils/use-form-data';
  import BtnItems from '@/components/BtnItems/index.vue';
  import type { UserSelectLocale, UserParam, Organization } from '../types';
  import {
    deptIdField,
    deptNameField,
    deptParentIdField,
    listDeptApi,
    avatarField
  } from '../config';

  const props = defineProps<{
    /** 是否多选 */
    multiple?: boolean;
    /** 下拉组件类型 */
    popperType?: PopperType;
    /** 已选列表项图标组件 */
    itemIcon?: UserComponent;
    /** 树数据源 */
    treeListApi?: () => Promise<Organization[]>;
    /** 组件文案 */
    lang: UserSelectLocale;
  }>();

  const emit = defineEmits<{
    /** 搜索事件 */
    search: [form: UserParam];
  }>();

  /** 下拉组件选中标签数据操作 */
  const selectProvider = inject(SELECT_DATA_KEY, null);

  /** 是否是弹窗模式 */
  const isModalType = computed<boolean>(() => {
    return props.popperType === 'modal' || props.popperType === 'drawer';
  });

  /** 选中标签数据 */
  const selectedItems = computed(() => {
    const items = isModalType.value
      ? selectProvider?.tempSelectedItems
      : selectProvider?.selectedItems;
    return unref(items) || [];
  });

  /** 树组件 */
  const treeRef = ref<ElTreeInstance>(null);

  /** 树配置属性 */
  const treeProps = { label: deptNameField };

  /** 树数据 */
  const treeData = ref<Organization[]>([]);

  /** 树数据请求状态 */
  const treeLoading = ref(true);

  /** 树搜索关键字 */
  const treeSearchKeywords = ref('');

  /** 树选中值 */
  const treeSelectValue = ref<string | number>();

  /** 分割面板是否折叠 */
  const collapse = ref(false);

  /** 是否是移动端小屏幕 */
  const { mobile } = useMobile((m) => {
    collapse.value = m;
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
  const [form, resetFields] = useFormData<UserParam>({
    nickname: '',
    phone: ''
  });

  /** 搜索 */
  const handleSearch = () => {
    const where: Record<string, any> = { ...form };
    where[deptIdField] = treeSelectValue.value;
    emit('search', where);
  };

  /** 重置 */
  const handleReset = () => {
    resetFields();
    handleSearch();
  };

  /** 树过滤方法 */
  const filterTreeNode = (keyword: string, data: Organization) => {
    if (!keyword) {
      return true;
    }
    const name = data[deptNameField];
    return name ? name.includes(keyword) : false;
  };

  /** 树点击选择事件 */
  const handleTreeItemClick = (item: Organization) => {
    if (mobile.value) {
      collapse.value = true;
    }
    const itemId = item ? item[deptIdField] : void 0;
    treeRef.value && treeRef.value.setCurrentKey(itemId);
    treeSelectValue.value = itemId;
    handleSearch();
  };

  /** 树过滤 */
  watch(treeSearchKeywords, (keyword) => {
    treeRef.value && treeRef.value.filter(keyword);
  });

  /** 查询树数据 */
  const queryTreeData = () => {
    treeLoading.value = true;
    (props.treeListApi || listDeptApi)()
      .then((list) => {
        treeLoading.value = false;
        treeData.value = toTree({
          data: list,
          idField: deptIdField,
          parentIdField: deptParentIdField
        });
      })
      .catch((e) => {
        treeLoading.value = false;
        EleMessage.error({ message: e.message, plain: true });
      });
  };

  queryTreeData();
</script>
