import 'element-plus/global';
import './typings/global';

declare module 'vue' {
  export interface GlobalComponents {
    BtnItems: (typeof import('@/components/BtnItems/index.vue'))['default'];
    ByteMdEditor: (typeof import('@/components/ByteMdEditor/index.vue'))['default'];
    ByteMdViewer: (typeof import('@/components/ByteMdViewer/index.vue'))['default'];
    CodeViewer: (typeof import('@/components/CodeViewer/index.vue'))['default'];
    CommonUpload: (typeof import('@/components/CommonUpload/index.vue'))['default'];
    DepartmentSelect: (typeof import('@/components/DepartmentSelect/index.vue'))['default'];
    DictData: (typeof import('@/components/DictData/index.vue'))['default'];
    FilePicker: (typeof import('@/components/FilePicker/index.vue'))['default'];
    FileUpload: (typeof import('@/components/FileUpload/index.vue'))['default'];
    IconSelect: (typeof import('@/components/IconSelect/index.vue'))['default'];
    ImageUpload: (typeof import('@/components/ImageUpload/index.vue'))['default'];
    MonacoEditor: (typeof import('@/components/MonacoEditor/index.vue'))['default'];
    ProCrud: (typeof import('@/components/ProCrud/index.vue'))['default'];
    ProCrudBuilder: (typeof import('@/components/ProCrudBuilder/index.vue'))['default'];
    ProForm: (typeof import('@/components/ProForm/index.vue'))['default'];
    ProFormBuilder: (typeof import('@/components/ProFormBuilder/index.vue'))['default'];
    RedirectLayout: (typeof import('@/components/RedirectLayout/index.vue'))['default'];
    RegionsSelect: (typeof import('@/components/RegionsSelect/index.vue'))['default'];
    RoleSelect: (typeof import('@/components/RoleSelect/index.vue'))['default'];
    RouterLayout: (typeof import('@/components/RouterLayout/index.vue'))['default'];
    TinymceEditor: (typeof import('@/components/TinymceEditor/index.vue'))['default'];
    TinymceViewer: (typeof import('@/components/TinymceViewer/index.vue'))['default'];
    UserSelect: (typeof import('@/components/UserSelect/index.vue'))['default'];
  }
}

export {};
