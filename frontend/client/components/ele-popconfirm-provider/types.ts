import type { ElePopconfirmPropsAndEmits } from '../ele-app/plus';

/**
 * 提供气泡确认框操作给子组件
 */
export interface PopconfirmProvider {
  openPopconfirm: (triggerEl: any, props?: ElePopconfirmPropsAndEmits) => void;
}
