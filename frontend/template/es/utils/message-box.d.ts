import { AppContext } from 'vue';
import { ElMessageBoxOptions, MessageBoxData as ElMessageBoxData } from 'element-plus';

/**
 * 消息弹窗配置
 */
export interface MessageBoxOptions extends ElMessageBoxOptions {
    /** 是否限制在主体内部 */
    inner?: boolean;
}
/**
 * 消息弹窗方法
 */
export type MessageBoxMethod = (message: ElMessageBoxOptions['message'], title: ElMessageBoxOptions['title'], options?: MessageBoxOptions, context?: AppContext | null) => Promise<ElMessageBoxData>;
/**
 * 消息弹窗
 */
export interface MessageBox {
    (options?: MessageBoxOptions, context?: AppContext | null): Promise<ElMessageBoxData>;
    alert: MessageBoxMethod;
    confirm: MessageBoxMethod;
    prompt: MessageBoxMethod;
    close: () => void;
}
export declare function useMessageBox(globalOpt?: MessageBoxOptions): MessageBox;
