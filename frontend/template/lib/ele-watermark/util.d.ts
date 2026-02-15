import { svgText, svgContents } from '../ele-qr-code-svg/qrcodegen';
import { ImageOption, GetOption } from './types';

export declare function getImageData<T extends Record<string, any>>(option: ImageOption<T>, markCount: number): void;
export declare function getProps(contents?: any): {
    svgKey: import('vue').Ref<any, any>;
    svgProps: Record<string, any>;
    svgConfig: import('../ele-config-provider/types').GlobalProvide;
    imageId: import('vue').ComputedRef<any>;
};
export declare const getOption: GetOption;
export declare const svgProp: any;
export { svgText, svgContents };
