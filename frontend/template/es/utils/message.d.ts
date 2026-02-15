import { AppContext, InjectionKey } from 'vue';
import { MessageHandler as ElMessageHandler, MessageOptions as ElMessageOptions, MessageFn as ElMessageFn } from 'element-plus/es/components/message';

/**
 * 消息提示配置
 */
export interface MessageOptions extends ElMessageOptions {
    /** 是否为原始风格 */
    original?: boolean | 'plain';
    /** 是否显示遮罩层 */
    mask?: boolean;
    /** 是否居中显示 */
    centered?: boolean;
    /** 是否限制在主体内部 */
    inner?: boolean;
    /** 限制在主体内部的分组标识 */
    groupKey?: string;
}
/**
 * 消息提示方法参数
 */
export type MessageParams = MessageOptions | ElMessageOptions['message'];
/**
 * 消息提示方法
 */
export type MessageFn = (options?: MessageParams, context?: null | AppContext) => ElMessageHandler;
/**
 * 消息提示
 */
export interface Message extends MessageFn {
    closeAll: ElMessageFn['closeAll'];
    success: MessageFn;
    warning: MessageFn;
    error: MessageFn;
    info: MessageFn;
    loading: MessageFn;
}
/**
 * 消息提示依赖注入
 */
interface MessageProvide {
    /** 限制在主体内部的分组标识 */
    groupKey: string;
    /** 获取限制在主体内部的容器 */
    getInnerWrap: () => HTMLElement;
}
/**
 * 消息提示依赖注入key
 */
type MessageKey = InjectionKey<MessageProvide>;
/**
 * 提供各种调用方法
 * @param options 参数
 * @param context 上下文
 */
declare const EleMessage: Message;
export { EleMessage };
/**
 * 消息提示依赖注入key
 */
export declare const MESSAGE_KEY: MessageKey;
/**
 * 带当前上下文的消息提示
 * @param globalOpt 参数
 */
export declare function useMessage(globalOpt?: MessageOptions): Message;
