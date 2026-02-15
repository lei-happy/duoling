import type {
  Editor as TinyMCEEditor,
  EditorEvent,
  RawEditorSettings
} from 'tinymce';
const BASE_URL = import.meta.env.BASE_URL;
//const BASE_URL = `${location.protocol}//${location.host}${import.meta.env.BASE_URL}`;

/** 默认加载插件 */
const PLUGINS: string = [
  'code',
  'preview',
  'fullscreen',
  'paste',
  'searchreplace',
  //'save',
  //'autosave',
  'link',
  'autolink',
  'image',
  'media',
  'table',
  'codesample',
  'lists',
  'advlist',
  'hr',
  'charmap',
  'emoticons',
  'anchor',
  'directionality',
  'pagebreak',
  'quickbars',
  'nonbreaking',
  'visualblocks',
  'visualchars',
  'wordcount'
].join(' ');

/** 默认工具栏布局 */
const TOOLBAR: string = [
  'fullscreen',
  'preview',
  'code',
  '|',
  'undo',
  'redo',
  '|',
  'forecolor',
  'backcolor',
  '|',
  'bold',
  'italic',
  'underline',
  'strikethrough',
  '|',
  'alignleft',
  'aligncenter',
  'alignright',
  'alignjustify',
  '|',
  'outdent',
  'indent',
  '|',
  'numlist',
  'bullist',
  '|',
  'formatselect',
  'fontselect',
  'fontsizeselect',
  '|',
  'link',
  'image',
  'media',
  'emoticons',
  'charmap',
  'anchor',
  'pagebreak',
  'codesample',
  '|',
  'ltr',
  'rtl'
].join(' ');

/** 默认配置 */
export const DEFAULT_CONFIG: RawEditorSettings = {
  height: 300,
  branding: false,
  skin_url: BASE_URL + 'tinymce/skins/ui/oxide',
  content_css: BASE_URL + 'tinymce/skins/content/default/content.min.css',
  language_url: BASE_URL + 'tinymce/langs/zh_CN.js',
  language: 'zh_CN',
  plugins: PLUGINS,
  toolbar: TOOLBAR,
  draggable_modal: true,
  toolbar_mode: 'sliding',
  quickbars_insert_toolbar: '',
  convert_urls: false,
  file_picker_types: 'media image file'
};

/** 暗黑主题配置 */
export const DARK_CONFIG: RawEditorSettings = {
  skin_url: BASE_URL + 'tinymce/skins/ui/oxide-dark',
  content_css: BASE_URL + 'tinymce/skins/content/dark/content.min.css'
};

/** 支持监听的事件 */
export const VALID_EVENTS = [
  'onActivate',
  'onAddUndo',
  'onBeforeAddUndo',
  'onBeforeExecCommand',
  'onBeforeGetContent',
  'onBeforeRenderUI',
  'onBeforeSetContent',
  'onBeforePaste',
  'onBlur',
  'onChange',
  'onClearUndos',
  'onClick',
  'onContextMenu',
  'onCopy',
  'onCut',
  'onDblclick',
  'onDeactivate',
  'onDirty',
  'onDrag',
  'onDragDrop',
  'onDragEnd',
  'onDragGesture',
  'onDragOver',
  'onDrop',
  'onExecCommand',
  'onFocus',
  'onFocusIn',
  'onFocusOut',
  'onGetContent',
  'onHide',
  'onInit',
  'onKeyDown',
  'onKeyPress',
  'onKeyUp',
  'onLoadContent',
  'onMouseDown',
  'onMouseEnter',
  'onMouseLeave',
  'onMouseMove',
  'onMouseOut',
  'onMouseOver',
  'onMouseUp',
  'onNodeChange',
  'onObjectResizeStart',
  'onObjectResized',
  'onObjectSelected',
  'onPaste',
  'onPostProcess',
  'onPostRender',
  'onPreProcess',
  'onProgressState',
  'onRedo',
  'onRemove',
  'onReset',
  'onSaveContent',
  'onSelectionChange',
  'onSetAttrib',
  'onSetContent',
  'onShow',
  'onSubmit',
  'onUndo',
  'onVisualAid'
];

let unique = 0;

/**
 * 生成编辑器 id
 */
export function uuid(prefix: string): string {
  const time = Date.now();
  const random = Math.floor(Math.random() * 1000000000);
  unique++;
  return `${prefix}_${random}${unique}${String(time)}`;
}

/**
 * 绑定事件
 */
export function bindHandlers(
  initEvent: EditorEvent<any>,
  listeners: Record<string, any>,
  editor: TinyMCEEditor
): void {
  const validEvents = VALID_EVENTS.map((event) => event.toLowerCase());
  Object.keys(listeners)
    .filter((key: string) => validEvents.includes(key.toLowerCase()))
    .forEach((key: string) => {
      const handler = listeners[key];
      if (typeof handler === 'function') {
        if (key === 'onInit') {
          handler(initEvent, editor);
        } else {
          editor.on(key.substring(2), (e: EditorEvent<any>) =>
            handler(e, editor)
          );
        }
      }
    });
}

/**
 * 弹出提示框
 */
export function openAlert(
  editor: TinyMCEEditor | null,
  option: AlertOption = {}
) {
  editor?.windowManager?.open?.({
    title: option.title ?? '提示',
    body: {
      type: 'panel',
      items: [
        {
          type: 'htmlpanel',
          html: `<p>${option.content ?? ''}</p>`
        }
      ]
    },
    buttons: [
      {
        type: 'cancel',
        name: 'closeButton',
        text: '确定',
        primary: true
      }
    ]
  });
}

/**
 * 弹出提示框参数
 */
export interface AlertOption {
  /** 标题 */
  title?: string;
  /** 内容 */
  content?: string;
}
