import { PropType, ExtractPropTypes } from 'vue';
import { UserComponent } from '../ele-app/types';
import { IconType } from './types';

/**
 * 属性
 */
export declare const iconProps: {
    /** 图标名称 */
    name: PropType<UserComponent>;
    /** 图标类型 */
    iconType: PropType<IconType>;
    size: {
        readonly type: PropType<string | number>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    color: {
        readonly type: PropType<string>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
};
export type IconProps = ExtractPropTypes<typeof iconProps>;
