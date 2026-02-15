import { EleProFormProps } from '../ele-app/plusx';
import { ProFormItemProps } from '../ele-pro-form/types';

declare function __VLS_template(): Partial<Record<string, (_: any) => any>> & Partial<Record<string, (_: any) => any>> & Partial<Record<string, (_: any) => any>> & Partial<Record<string, (_: any) => any>>;
declare const __VLS_component: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    modelValue: import('vue').PropType<EleProFormProps>;
    headerTools: {
        type: import('vue').PropType<boolean | import('./types').HeaderRightToolName[]>;
        default: () => undefined;
    };
    componentData: import('vue').PropType<import('./types').ComponentGroup[]>;
    templateData: import('vue').PropType<import('./types').TemplateItem[]>;
    configFormItems: import('vue').PropType<ProFormItemProps[]>;
    configFormPresetProps: import('vue').PropType<import('./types').TemplateFormProps>;
    proFormInitialProps: import('vue').PropType<import('./types').TemplateFormProps>;
    splitPanelProps: import('vue').PropType<import('../ele-app/plus').EleSplitPanelProps>;
    rightSplitPanelProps: import('vue').PropType<import('../ele-app/plus').EleSplitPanelProps>;
    proFormComponent: import('vue').PropType<import('../ele-app/types').UserComponent>;
    codeEditerComponent: import('vue').PropType<import('../ele-app/types').UserComponent>;
    jsonEditerComponent: import('vue').PropType<import('../ele-app/types').UserComponent>;
    htmlEditerComponent: import('vue').PropType<import('../ele-app/types').UserComponent>;
    codeViewerComponent: import('vue').PropType<import('../ele-app/types').UserComponent>;
    itemTypeData: import('vue').PropType<import('../ele-pro-form/types').ProFormItemTypeData[]>;
    httpRequest: (ObjectConstructor | FunctionConstructor)[];
}>, {}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    "update:modelValue": (_config: EleProFormProps) => void;
    previewFormSubmit: (_data: Record<string, any>) => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    modelValue: import('vue').PropType<EleProFormProps>;
    headerTools: {
        type: import('vue').PropType<boolean | import('./types').HeaderRightToolName[]>;
        default: () => undefined;
    };
    componentData: import('vue').PropType<import('./types').ComponentGroup[]>;
    templateData: import('vue').PropType<import('./types').TemplateItem[]>;
    configFormItems: import('vue').PropType<ProFormItemProps[]>;
    configFormPresetProps: import('vue').PropType<import('./types').TemplateFormProps>;
    proFormInitialProps: import('vue').PropType<import('./types').TemplateFormProps>;
    splitPanelProps: import('vue').PropType<import('../ele-app/plus').EleSplitPanelProps>;
    rightSplitPanelProps: import('vue').PropType<import('../ele-app/plus').EleSplitPanelProps>;
    proFormComponent: import('vue').PropType<import('../ele-app/types').UserComponent>;
    codeEditerComponent: import('vue').PropType<import('../ele-app/types').UserComponent>;
    jsonEditerComponent: import('vue').PropType<import('../ele-app/types').UserComponent>;
    htmlEditerComponent: import('vue').PropType<import('../ele-app/types').UserComponent>;
    codeViewerComponent: import('vue').PropType<import('../ele-app/types').UserComponent>;
    itemTypeData: import('vue').PropType<import('../ele-pro-form/types').ProFormItemTypeData[]>;
    httpRequest: (ObjectConstructor | FunctionConstructor)[];
}>> & Readonly<{
    "onUpdate:modelValue"?: ((_config: EleProFormProps) => any) | undefined;
    onPreviewFormSubmit?: ((_data: Record<string, any>) => any) | undefined;
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
