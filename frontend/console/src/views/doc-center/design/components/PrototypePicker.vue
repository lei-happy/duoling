<template>
  <div class="proto-picker">
    <div class="proto-picker-bar">
      <el-input
        :model-value="modelValue || ''"
        readonly
        placeholder="从 prototype/ 目录选择 HTML 原型"
        clearable
        @clear="emit('update:modelValue', null)"
      />
      <el-button @click="openDialog">选择原型</el-button>
      <el-button
        v-if="modelValue"
        type="primary"
        link
        @click="previewVisible = true"
      >
        预览
      </el-button>
    </div>

    <div v-if="previewSrc" class="proto-preview">
      <iframe
        :src="previewSrc"
        class="proto-iframe"
        title="产品原型预览"
      />
    </div>

    <el-dialog
      v-model="dialogVisible"
      title="选择产品原型"
      width="520px"
      destroy-on-close
      append-to-body
    >
      <el-input
        v-model="filterText"
        placeholder="搜索目录或原型名称…"
        clearable
        class="proto-search"
      />
      <el-scrollbar height="360px">
        <el-tree
          ref="treeRef"
          :data="treeData"
          :props="treeProps"
          node-key="key"
          highlight-current
          default-expand-all
          :filter-node-method="filterNode"
          @node-click="onNodeClick"
        >
          <template #default="{ node, data }">
            <span class="proto-tree-node">
              <el-icon>
                <Folder v-if="!data.isLeaf" />
                <Document v-else />
              </el-icon>
              <span>{{ node.label }}</span>
            </span>
          </template>
        </el-tree>
      </el-scrollbar>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :disabled="!pendingPath" @click="confirmSelect">
          确定
        </el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="previewVisible"
      title="原型预览"
      width="90%"
      top="4vh"
      destroy-on-close
      append-to-body
      class="proto-fullscreen-dialog"
    >
      <iframe
        v-if="previewSrc"
        :src="previewSrc"
        class="proto-iframe-full"
        title="产品原型全屏预览"
      />
    </el-dialog>
  </div>
</template>

<script lang="ts" setup>
  import { computed, ref, watch } from 'vue';
  import type { ElTree } from 'element-plus';
  import { Document, Folder } from '@element-plus/icons-vue';
  import { EleMessage } from 'ele-admin-plus';
  import {
    getPrototypeTree,
    ensurePrototypePreviewAuth,
    buildPrototypePreviewUrl
  } from '@/api/doc-center/prototype';
  import type { PrototypeTreeNode } from '@/api/doc-center/model/design-module';

  defineOptions({ name: 'PrototypePicker' });

  const props = defineProps<{
    modelValue?: string | null;
  }>();

  const emit = defineEmits<{
    (e: 'update:modelValue', value: string | null): void;
  }>();

  const dialogVisible = ref(false);
  const previewVisible = ref(false);
  const treeData = ref<PrototypeTreeNode[]>([]);
  const filterText = ref('');
  const pendingPath = ref<string | null>(null);
  const treeRef = ref<InstanceType<typeof ElTree>>();

  const treeProps = {
    label: 'title',
    children: 'children',
    isLeaf: 'isLeaf'
  };

  const previewSrc = computed(() => {
    ensurePrototypePreviewAuth();
    return buildPrototypePreviewUrl(props.modelValue);
  });

  const filterNode = (value: string, data: PrototypeTreeNode) => {
    if (!value) return true;
    return data.title.toLowerCase().includes(value.toLowerCase());
  };

  watch(filterText, (val) => {
    treeRef.value?.filter(val);
  });

  const loadTree = async () => {
    try {
      treeData.value = (await getPrototypeTree()) || [];
      if (!treeData.value.length) {
        EleMessage.warning({
          message: '原型目录为空，请先在仓库 prototype/ 下放入 HTML',
          plain: true
        });
      }
    } catch (e: any) {
      EleMessage.error({
        message: e?.message || '加载原型目录失败，请稍后重试',
        plain: true
      });
    }
  };

  const openDialog = async () => {
    pendingPath.value = props.modelValue || null;
    dialogVisible.value = true;
    await loadTree();
  };

  const onNodeClick = (data: PrototypeTreeNode) => {
    if (!data.isLeaf) return;
    pendingPath.value = data.key;
  };

  const confirmSelect = () => {
    if (!pendingPath.value) return;
    emit('update:modelValue', pendingPath.value);
    ensurePrototypePreviewAuth();
    dialogVisible.value = false;
  };

  watch(
    () => props.modelValue,
    () => {
      if (props.modelValue) ensurePrototypePreviewAuth();
    },
    { immediate: true }
  );
</script>

<style lang="scss" scoped>
  .proto-picker {
    width: 100%;
  }

  .proto-picker-bar {
    display: flex;
    gap: 8px;
    align-items: center;
    width: 100%;

    .el-input {
      flex: 1;
    }
  }

  .proto-search {
    margin-bottom: 12px;
  }

  .proto-tree-node {
    display: inline-flex;
    align-items: center;
    gap: 6px;
  }

  .proto-preview {
    margin-top: 10px;
  }

  .proto-iframe {
    width: 100%;
    height: 280px;
    border: 1px solid var(--el-border-color-lighter);
    border-radius: 6px;
    background: #fff;
  }

  .proto-iframe-full {
    width: 100%;
    height: 78vh;
    border: 1px solid var(--el-border-color-lighter);
    border-radius: 6px;
    background: #fff;
  }
</style>
