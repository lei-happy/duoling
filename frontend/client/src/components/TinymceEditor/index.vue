<!-- 富文本编辑器 -->
<template>
  <component v-if="inlineEditor" :is="tagName" :id="elementId" />
  <textarea v-else :id="elementId"></textarea>
  <!-- 文件选择弹窗 -->
  <EleFormItemRest>
    <FilePicker
      title="文件选择"
      :limit="1"
      :accept="filePickerAccept ? filePickerAccept + '*' : void 0"
      :params="{ contentType: filePickerAccept }"
      :base-index="19990099"
      v-model="showFilePicker"
      @done="handleFilePickerDone"
      @close="handleFilePickerClose"
    />
  </EleFormItemRest>
</template>

<script lang="ts" setup>
  import {
    ref,
    watch,
    onMounted,
    onBeforeUnmount,
    onActivated,
    onDeactivated,
    nextTick,
    useAttrs
  } from 'vue';
  import FilePicker from '@/components/FilePicker/index.vue';
  import type { UserFile } from '@/api/system/user-file/model';
  import tinymce from 'tinymce/tinymce';
  import type {
    Editor as TinyMCEEditor,
    EditorEvent,
    RawEditorSettings
  } from 'tinymce';
  import 'tinymce/themes/silver';
  import 'tinymce/icons/default';
  import 'tinymce/plugins/code';
  import 'tinymce/plugins/preview';
  import 'tinymce/plugins/fullscreen';
  import 'tinymce/plugins/paste';
  import 'tinymce/plugins/searchreplace';
  //import 'tinymce/plugins/save';
  //import 'tinymce/plugins/autosave';
  import 'tinymce/plugins/link';
  import 'tinymce/plugins/autolink';
  import 'tinymce/plugins/image';
  import 'tinymce/plugins/media';
  import 'tinymce/plugins/table';
  import 'tinymce/plugins/codesample';
  import 'tinymce/plugins/lists';
  import 'tinymce/plugins/advlist';
  import 'tinymce/plugins/hr';
  import 'tinymce/plugins/charmap';
  import 'tinymce/plugins/emoticons';
  import 'tinymce/plugins/anchor';
  import 'tinymce/plugins/directionality';
  import 'tinymce/plugins/pagebreak';
  import 'tinymce/plugins/quickbars';
  import 'tinymce/plugins/nonbreaking';
  import 'tinymce/plugins/visualblocks';
  import 'tinymce/plugins/visualchars';
  import 'tinymce/plugins/wordcount';
  import 'tinymce/plugins/emoticons/js/emojis';
  import { storeToRefs } from 'pinia';
  import { useThemeStore } from '@/store/modules/theme';
  import { uploadFile } from '@/api/system/file';
  import {
    DEFAULT_CONFIG,
    DARK_CONFIG,
    uuid,
    bindHandlers,
    openAlert
  } from './util';
  import type { AlertOption } from './util';

  defineOptions({ name: 'TinymceEditor' });

  const props = withDefaults(
    defineProps<{
      /** 编辑器唯一id */
      id?: string;
      /** v-model */
      modelValue?: string;
      /** 编辑器配置 */
      init?: RawEditorSettings;
      /** 是否内联模式 */
      inline?: boolean;
      /** model events */
      modelEvents?: string;
      /** 内联模式标签名 */
      tagName?: string;
      /** 是否禁用 */
      disabled?: boolean;
      /** 是否跟随框架主题 */
      autoTheme?: boolean;
      /** 不跟随框架主题时是否使用暗黑主题 */
      darkTheme?: boolean;
    }>(),
    {
      inline: false,
      modelEvents: 'change input undo redo',
      tagName: 'div',
      autoTheme: true
    }
  );

  const emit = defineEmits<{
    (e: 'update:modelValue', value: string): void;
  }>();

  const attrs = useAttrs();
  const themeStore = useThemeStore();
  const { darkMode } = storeToRefs(themeStore);

  /** 编辑器唯一id */
  const elementId: string = props.id || uuid('tiny-vue');

  /** 实例导出 */
  const exposeData = {
    /** 编辑器实例 */
    editorIns: null as TinyMCEEditor | null,
    /** 弹出提示框 */
    alert(option?: AlertOption) {
      openAlert(this.editorIns, option);
    }
  };

  /** 是否内联模式 */
  const inlineEditor: boolean = props.init?.inline || props.inline;

  /** 更新value */
  const updateValue = (value: string) => {
    emit('update:modelValue', value);
  };

  /** 修改内容 */
  const setContent = (value?: string) => {
    if (
      exposeData.editorIns &&
      typeof value === 'string' &&
      value !== exposeData.editorIns.getContent()
    ) {
      exposeData.editorIns.setContent(value);
    }
  };

  /** 渲染编辑器 */
  const render = () => {
    const isDark = props.autoTheme ? darkMode.value : props.darkTheme;
    tinymce.init({
      ...DEFAULT_CONFIG,
      ...(isDark ? DARK_CONFIG : {}),
      images_upload_handler: (blobInfo: any, success: any, error: any) => {
        const file = blobInfo.blob();
        uploadFile(file, void 0, file.name)
          .then((res) => {
            success(res.url);
          })
          .catch((e) => {
            console.error(e);
            error(e.message);
          });
      },
      file_picker_callback: (callback: any, _value: any, meta: any) => {
        if (meta.filetype === 'image') {
          filePickerAccept.value = 'image/';
        } else if (meta.filetype === 'media') {
          filePickerAccept.value = 'video/';
        } else {
          filePickerAccept.value = void 0;
        }
        showFilePicker.value = true;
        currentEditorCallback = callback;
      },
      ...props.init,
      selector: `#${elementId}`,
      readonly: props.disabled,
      inline: inlineEditor,
      setup: (editor: TinyMCEEditor) => {
        exposeData.editorIns = editor;
        editor.on('init', (e: EditorEvent<any>) => {
          // 回显初始值
          if (props.modelValue) {
            setContent(props.modelValue);
          }
          // v-model
          editor.on(props.modelEvents, () => {
            updateValue(editor.getContent());
          });
          // valid events
          bindHandlers(e, attrs, editor);
        });
        if (typeof props.init?.setup === 'function') {
          props.init.setup(editor);
        }
      }
    });
  };

  /** 销毁编辑器 */
  const destory = () => {
    if (tinymce != null && exposeData.editorIns != null) {
      tinymce.remove(exposeData.editorIns as any);
      exposeData.editorIns = null;
    }
  };

  defineExpose(exposeData);

  watch(
    () => props.modelValue,
    (val, prevVal) => {
      if (val !== prevVal) {
        setContent(val || '');
      }
    }
  );

  watch(
    () => props.disabled,
    (disable) => {
      if (exposeData.editorIns !== null) {
        if (typeof exposeData.editorIns.mode?.set === 'function') {
          exposeData.editorIns.mode.set(disable ? 'readonly' : 'design');
        } else {
          exposeData.editorIns.setMode(disable ? 'readonly' : 'design');
        }
      }
    }
  );

  watch(
    () => props.tagName,
    () => {
      destory();
      nextTick(() => {
        render();
      });
    }
  );

  watch(darkMode, () => {
    if (props.autoTheme) {
      destory();
      nextTick(() => {
        render();
      });
    }
  });

  onMounted(() => {
    render();
  });

  onBeforeUnmount(() => {
    destory();
  });

  onActivated(() => {
    render();
  });

  onDeactivated(() => {
    destory();
  });

  /** 是否打开文件选择弹窗 */
  const showFilePicker = ref(false);

  /** 文件选择弹窗限制类型 */
  const filePickerAccept = ref<string>();

  /** 当前修改的文件项 */
  let currentEditorCallback: any = null;

  /** 文件选择弹窗选择完成事件 */
  const handleFilePickerDone = (files: UserFile[]) => {
    showFilePicker.value = false;
    if (files.length) {
      currentEditorCallback(files[0].url, {
        text: files[0].name,
        alt: files[0].name
      });
    }
    currentEditorCallback = null;
  };

  /** 文件选择弹窗关闭事件 */
  const handleFilePickerClose = () => {
    currentEditorCallback = null;
  };
</script>

<style lang="scss">
  @use 'ele-admin-plus/es/style/util.scss' as *;

  body {
    .tox.tox-tinymce-aux,
    &.tox-fullscreen .tox.tox-tinymce-aux {
      z-index: 19990000;
    }

    .tox-menu.tox-collection.tox-collection--list {
      max-height: 420px !important;
    }

    textarea[id^='tiny-vue'] {
      width: 0;
      height: 0;
      margin: 0;
      padding: 0;
      opacity: 0;
      box-sizing: border-box;
    }

    .tox .tox-menubar,
    .tox .tox-toolbar-overlord,
    .tox .tox-edit-area__iframe,
    .tox .tox-statusbar {
      background: none;
    }

    .tox .tox-toolbar,
    .tox .tox-toolbar__overflow,
    .tox .tox-toolbar__primary {
      background: none;
      box-shadow: 0 -0.8px 0 elVar('border-color', 'light') inset;
    }

    .tox.tox-tinymce.tox-fullscreen {
      background: elVar('bg-color');
    }
  }
</style>
