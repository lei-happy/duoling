<template>
  <ele-page :multi-card="true">
    <ele-card>
      <!-- 按钮 -->
      <div style="margin-bottom: 16px">
        <el-button type="primary" class="ele-btn-icon" @click="setContent">
          修改内容
        </el-button>
        <el-button type="primary" class="ele-btn-icon" @click="showHtml">
          获取内容
        </el-button>
        <el-button
          class="ele-btn-icon"
          :type="disabled ? 'primary' : 'danger'"
          @click="toggleDisabled"
        >
          {{ disabled ? '启用' : '禁用' }}
        </el-button>
      </div>
      <!-- 编辑器 -->
      <tinymce-editor
        ref="editorRef"
        :init="config"
        v-model="content"
        :disabled="disabled"
      />
    </ele-card>
  </ele-page>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import { ElMessageBox } from 'element-plus';
  import TinymceEditor from '@/components/TinymceEditor/index.vue';

  defineOptions({ name: 'ExtensionEditor' });

  /** 编辑器 */
  const editorRef = ref<InstanceType<typeof TinymceEditor> | null>(null);

  /** 编辑器配置 */
  const config = ref({
    height: 520
  });

  /** 编辑器内容 */
  const content = ref('');

  /** 是否禁用 */
  const disabled = ref(false);

  /** 获取编辑器内容 */
  const showHtml = () => {
    ElMessageBox.alert(content.value, '编辑器内容', {
      confirmButtonText: '知道了',
      closeOnClickModal: true,
      callback: () => {},
      draggable: true
    });
  };

  /** 修改编辑器内容 */
  const setContent = () => {
    content.value = [
      '<div style="text-align: center;color: #fff;background-image: linear-gradient( 135deg, #4C83FF 10%, #2AFADF 100%);padding: 32px 0;">',
      '   <div style="font-size: 28px;margin-bottom: 16px;">EleAdminPlus后台管理模板</div>',
      '   <div style="font-size:18px">通用型后台管理模板，界面美观、开箱即用，拥有丰富的组件和模板</div>',
      '</div><br/>'
    ].join('');
  };

  /** 禁用启用切换 */
  const toggleDisabled = () => {
    disabled.value = !disabled.value;
  };
</script>
