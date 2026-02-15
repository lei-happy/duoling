import type { PropType, ExtractPropTypes } from 'vue';
import type { EleMessageBoxOptions } from '../ele-app/plus';
import type {
  TableGlobalConfig,
  MessageGlobalConfig,
  EleLocale
} from './types';

/**
 * 属性
 */
export const configProviderProps = {
  /** 国际化 */
  locale: Object as PropType<EleLocale>,
  /** 表格全局配置 */
  table: Object as PropType<TableGlobalConfig>,
  /** 消息提示全局配置 */
  message: Object as PropType<MessageGlobalConfig>,
  /** 消息弹窗全局配置 */
  messageBox: Object as PropType<EleMessageBoxOptions>,
  /** license */
  license: String,
  /** 高德地图key */
  mapKey: String
};

export type ConfigProviderProps = ExtractPropTypes<typeof configProviderProps>;
