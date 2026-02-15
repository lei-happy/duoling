import { StyleValue } from '../ele-app/types';
import { MutationOption } from '../ele-watermark/types';

export declare function useMutation(option: MutationOption): {
    imageId: import('vue').Ref<number, number>;
    imageStyleId: import('vue').Ref<number, number>;
    imageStyle: import('vue').Ref<string, string>;
    observe: () => void;
    observeText: (text: string) => string;
    updateImageStyle: () => void;
};
export declare function useSvgOption(): {
    svgProps: Record<string, any>;
    svgKey: import('vue').Ref<any, any>;
    imageId: import('vue').ComputedRef<any>;
};
export declare function mergeStyle(commonStyle: StyleValue, data: string | undefined, width: number, height: number, left: number, top: number): string;
export declare const MARK_SIZE = 2;
