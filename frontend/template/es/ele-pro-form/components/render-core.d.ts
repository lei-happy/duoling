import { ElColProps } from '../../ele-app/el';
import { ProFormItemProps, ScreenSize } from '../types';

/**
 * 编辑模式拖拽排序分组名称
 */
export declare const sortableGroupName = "ProFormBuilderBodySortGroup";
/**
 * 代码字符串前缀
 */
export declare const codeStringPrefix = "/*__PRO_FORM__*/";
/**
 * 获取栅格响应式对象属性
 * @param prop 栅格响应式属性
 */
export declare function getColObjectProp(prop?: number | Record<string, number>): Record<string, number>;
/**
 * 获取屏幕尺寸对应的栅格属性
 * @param screenSize 屏幕尺寸
 * @param gridColProps 父级栅格布局属性
 * @param itemColProps 栅格属性
 */
export declare function getScreenSizeColProps(screenSize?: ScreenSize, gridColProps?: ElColProps, itemColProps?: ElColProps): ElColProps;
/**
 * 获取搜索表单底栏栅格默认属性
 * @param grid 表单栅格布局属性
 * @param itemsLength 表单项数量
 */
export declare function computeContentExtraCol(grid?: ElColProps, itemsLength?: number): ElColProps;
/**
 * 执行代码字符串
 * @param code 代码字符串
 * @param form 表单数据
 * @param items 全部表单项
 * @param searchExpand 搜索表单折叠展开状态
 * @param httpRequest 远程数据源请求工具
 * @param getProFormRefs 获取表单组件的组件引用数据的方法
 */
export declare function getCodeResult(code: string, form: Record<string, any> | undefined, items: ProFormItemProps[], searchExpand?: boolean, httpRequest?: any, getProFormRefs?: () => Record<string, any>): any;
/**
 * 判断表单项是否展示
 * @param item 表单项
 * @param form 表单数据
 * @param items 表单项数据
 * @param searchExpand 搜索表单展开状态
 * @param editable 是否是编辑模式
 */
export declare function isShowItem(item: ProFormItemProps, form: Record<string, any> | undefined, items: ProFormItemProps[], searchExpand?: boolean, editable?: boolean): any;
/**
 * 解析代码字符串
 * @param code 值
 * @param form 表单数据
 * @param items 全部表单项
 * @param searchExpand 搜索表单折叠展开状态
 * @param httpRequest 远程数据源请求工具
 * @param getProFormRefs 获取表单组件的组件引用数据的方法
 * @param getAndCacheCode 获取并缓存代码解析结果方法
 */
export declare function translateJsCode(code: any, form: Record<string, any> | undefined, items: ProFormItemProps[], searchExpand?: boolean, httpRequest?: any, getProFormRefs?: () => Record<string, any>, getAndCacheCode?: (code: string, codeResult: any) => any): {
    result: any;
    isCode: boolean;
};
