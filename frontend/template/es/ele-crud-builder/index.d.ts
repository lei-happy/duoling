import { EleCrudProps } from '../ele-app/plusx';

declare function __VLS_template(): Partial<Record<string, (_: any) => any>> & Partial<Record<string, (_: any) => any>> & Partial<Record<string, (_: any) => any>> & Partial<Record<string, (_: any) => any>>;
declare const __VLS_component: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    modelValue: import('vue').PropType<EleCrudProps>;
    headerTools: {
        type: import('vue').PropType<boolean | import('./types').HeaderRightToolName[]>;
        default: () => undefined;
    };
    templateData: import('vue').PropType<import('./types').TemplateItem[]>;
    pageConfigFormItems: import('vue').PropType<import('../ele-pro-form/types').ProFormItemProps[]>;
    fieldEditFormItems: import('vue').PropType<import('../ele-pro-form/types').ProFormItemProps[]>;
    splitPanelProps: import('vue').PropType<import('../ele-app/plus').EleSplitPanelProps>;
    crudComponent: import('vue').PropType<import('../ele-app/types').UserComponent>;
    proFormComponent: import('vue').PropType<import('../ele-app/types').UserComponent>;
    proFormBuilderComponent: import('vue').PropType<import('../ele-app/types').UserComponent>;
    proFormBuilderProps: import('vue').PropType<import('../ele-app/plusx').EleProFormBuilderProps>;
    codeEditerComponent: import('vue').PropType<import('../ele-app/types').UserComponent>;
    jsonEditerComponent: import('vue').PropType<import('../ele-app/types').UserComponent>;
    codeViewerComponent: import('vue').PropType<import('../ele-app/types').UserComponent>;
    itemTypeData: import('vue').PropType<import('../ele-pro-form/types').ProFormItemTypeData[]>;
    httpRequest: (ObjectConstructor | FunctionConstructor)[];
}>, {}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    "update:modelValue": (_config?: EleCrudProps | undefined) => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    modelValue: import('vue').PropType<EleCrudProps>;
    headerTools: {
        type: import('vue').PropType<boolean | import('./types').HeaderRightToolName[]>;
        default: () => undefined;
    };
    templateData: import('vue').PropType<import('./types').TemplateItem[]>;
    pageConfigFormItems: import('vue').PropType<import('../ele-pro-form/types').ProFormItemProps[]>;
    fieldEditFormItems: import('vue').PropType<import('../ele-pro-form/types').ProFormItemProps[]>;
    splitPanelProps: import('vue').PropType<import('../ele-app/plus').EleSplitPanelProps>;
    crudComponent: import('vue').PropType<import('../ele-app/types').UserComponent>;
    proFormComponent: import('vue').PropType<import('../ele-app/types').UserComponent>;
    proFormBuilderComponent: import('vue').PropType<import('../ele-app/types').UserComponent>;
    proFormBuilderProps: import('vue').PropType<import('../ele-app/plusx').EleProFormBuilderProps>;
    codeEditerComponent: import('vue').PropType<import('../ele-app/types').UserComponent>;
    jsonEditerComponent: import('vue').PropType<import('../ele-app/types').UserComponent>;
    codeViewerComponent: import('vue').PropType<import('../ele-app/types').UserComponent>;
    itemTypeData: import('vue').PropType<import('../ele-pro-form/types').ProFormItemTypeData[]>;
    httpRequest: (ObjectConstructor | FunctionConstructor)[];
}>> & Readonly<{
    "onUpdate:modelValue"?: ((_config?: EleCrudProps | undefined) => any) | undefined;
}>, {
    headerTools: boolean | import('./types').HeaderRightToolName[];
}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
declare const _default: __VLS_WithTemplateSlots<typeof __VLS_component, ReturnType<typeof __VLS_template>>;
export default _default;
type __VLS_WithTemplateSlots<T, S> = T & {
    new (): {
        $slots: S;
    };
};
