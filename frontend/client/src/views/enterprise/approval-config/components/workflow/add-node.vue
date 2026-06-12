<!-- 节点间的「+」加节点入口（审批人 / 抄送人 / 条件分支） -->
<template>
  <div class="wf-add-node-btn">
    <el-popover
      v-if="!readonly"
      v-model:visible="visible"
      :width="200"
      trigger="click"
      placement="right-start"
      popper-class="wf-add-popover"
      :teleported="true"
    >
      <template #reference>
        <button type="button" class="wf-add-circle" @click.stop>
          <el-icon><Plus /></el-icon>
        </button>
      </template>
      <div class="wf-add-popover-body">
        <button
          type="button"
          class="wf-add-item approver"
          @click.stop="add('approval')"
        >
          <span class="wf-add-item-icon">
            <el-icon><UserFilled /></el-icon>
          </span>
          <span>审批人</span>
        </button>
        <button
          type="button"
          class="wf-add-item notifier"
          @click.stop="add('cc')"
        >
          <span class="wf-add-item-icon">
            <el-icon><Promotion /></el-icon>
          </span>
          <span>抄送人</span>
        </button>
        <button
          v-if="supportsConditionBranch"
          type="button"
          class="wf-add-item condition"
          @click.stop="add('condition')"
        >
          <span class="wf-add-item-icon">
            <el-icon><Share /></el-icon>
          </span>
          <span>条件分支</span>
        </button>
      </div>
    </el-popover>
    <button v-else type="button" class="wf-add-circle is-readonly" disabled>
      <el-icon><Plus /></el-icon>
    </button>
  </div>
</template>

<script lang="ts" setup>
  import { computed, inject, ref } from 'vue';
  import { Plus, UserFilled, Promotion, Share } from '@element-plus/icons-vue';
  import type { CanvasNode, CanvasNodeType } from '@/api/approval/model';
  import { createNode } from '@/api/approval/transform';
  import { WORKFLOW_CTX } from './context';

  const props = defineProps<{
    childNode?: CanvasNode | null;
    readonly?: boolean;
  }>();

  const emit = defineEmits<{
    (e: 'update:childNode', v: CanvasNode | null): void;
  }>();

  const ctx = inject(WORKFLOW_CTX);
  const supportsConditionBranch = computed(
    () => ctx?.supportsConditionBranch ?? false
  );

  const visible = ref(false);

  const add = (type: CanvasNodeType) => {
    const node = createNode(type);
    node.childNode = props.childNode ?? null;
    emit('update:childNode', node);
    visible.value = false;
  };
</script>
