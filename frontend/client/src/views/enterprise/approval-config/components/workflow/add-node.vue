<!-- 节点间的「+」加节点入口（审批人 / 抄送人 / 条件分支） -->
<template>
  <div class="wf-add-node-btn">
    <div class="wf-add-line"></div>
    <el-popover
      v-if="!readonly"
      :width="180"
      trigger="click"
      placement="right-start"
      popper-class="wf-add-popover"
      :visible="visible"
      @update:visible="(v: boolean) => (visible = v)"
    >
      <template #reference>
        <button type="button" class="wf-add-circle" @click="visible = true">
          <el-icon><Plus /></el-icon>
        </button>
      </template>
      <div class="wf-add-popover-body">
        <a class="wf-add-item approver" @click="add('approval')">
          <span class="wf-add-item-icon"
            ><el-icon><UserFilled /></el-icon
          ></span>
          <span>审批人</span>
        </a>
        <a class="wf-add-item notifier" @click="add('cc')">
          <span class="wf-add-item-icon"
            ><el-icon><Promotion /></el-icon
          ></span>
          <span>抄送人</span>
        </a>
        <a class="wf-add-item condition" @click="add('condition')">
          <span class="wf-add-item-icon"
            ><el-icon><Share /></el-icon
          ></span>
          <span>条件分支</span>
        </a>
      </div>
    </el-popover>
    <button v-else type="button" class="wf-add-circle is-readonly" disabled>
      <el-icon><Plus /></el-icon>
    </button>
  </div>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import { Plus, UserFilled, Promotion, Share } from '@element-plus/icons-vue';
  import type { CanvasNode, CanvasNodeType } from '@/api/approval/model';
  import { createNode } from '@/api/approval/transform';

  const props = defineProps<{
    childNode?: CanvasNode | null;
    readonly?: boolean;
  }>();

  const emit = defineEmits<{
    (e: 'update:childNode', v: CanvasNode | null): void;
  }>();

  const visible = ref(false);

  const add = (type: CanvasNodeType) => {
    const node = createNode(type);
    // 新节点接管原有后继链，实现「在此处插入」
    node.childNode = props.childNode ?? null;
    emit('update:childNode', node);
    visible.value = false;
  };
</script>
