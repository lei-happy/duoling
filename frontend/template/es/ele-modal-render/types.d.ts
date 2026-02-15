import type { Ref, AsyncComponentLoader, AsyncComponentOptions } from 'vue';
import type { UserComponent, SlotObject } from '../ele-app/types';
import type {
  EleModalPropsAndEmits,
  EleDrawerPropsAndEmits
} from '../ele-app/plus';

/**
 * 提供给内容组件的弹窗数据
 */
export interface ModalHolderProvider {
  /** 关闭弹窗方法 */
  closeModal: () => void;
  /** 移除弹窗方法 */
  removeModal: () => void;
  /** 修改弹窗属性方法 */
  setModalProps: (option?: Record<string, any>) => void;
  /** 弹窗属性 */
  modalProps: Ref<EleModalPropsAndEmits | EleDrawerPropsAndEmits>;
}

/**
 * 弹窗类型
 */
export type ModalItemType = 'modal' | 'drawer';

/**
 * 弹窗 id
 */
export type ModalItemId = string | number;

/**
 * 弹窗内容组件属性
 */
export type ModalItemComponentProps =
  | Record<string, any>
  | ((data: ModalHolderProvider) => Record<string, any>);

/**
 * 弹窗数据配置
 */
export interface ModalItemOption<T extends ModalItemType> {
  /** 弹窗类型 */
  type?: T;
  /** 弹窗内容组件 */
  component?: UserComponent;
  /** 弹窗内容异步组件 */
  asyncComponent?: AsyncComponentLoader;
  /** 弹窗内容异步组件配置 */
  asyncComponentOptions?: Partial<AsyncComponentOptions>;
  /** 弹窗内容组件属性 */
  componentProps?: ModalItemComponentProps;
  /** 弹窗属性 */
  props?: T extends 'drawer' ? EleDrawerPropsAndEmits : EleModalPropsAndEmits;
  /** 传递插槽 */
  slots?: SlotObject;
  /** 是否自定义弹窗组件 */
  custom?: boolean;
  /** 不为自定义弹窗组件时异步组件加载状态 */
  compLoading?: boolean;
  /** 弹窗打开状态 */
  visible?: boolean;
  /** 弹窗是否是失活状态 */
  isDeactivated?: boolean;
  /** 是否在页面销毁后不关闭弹窗 */
  keepAlive?: boolean;
  /** 弹窗 id */
  modalId?: ModalItemId;
}

/**
 * 打开的弹窗数据
 */
export type ModalItem = ModalItemOption<'drawer'> | ModalItemOption<'modal'>;

/**
 * 提供给后代组件的弹窗操作方法
 */
export interface ModalUtilProvider {
  /** 打开弹窗 */
  openModal: (option: ModalItem) => ModalItemId;
  /** 关闭弹窗 */
  closeModal: (modalId?: ModalItemId) => void;
  /** 关闭所有弹窗 */
  closeAllModal: () => void;
  /** 修改弹窗失活状态 */
  updateModalState: (modalId?: ModalItemId, deactivated?: boolean) => void;
  /** 修改弹窗属性 */
  updateModalProps: (
    modalId?: ModalItemId,
    option?: Record<string, any>
  ) => void;
}

/**
 * 弹窗操作方法
 */
export interface UseModalMethods {
  /** 打开弹窗 */
  openModal: (option: ModalItem) => ModalItemId;
  /** 关闭所有弹窗(是否只关闭当前组件中打开的弹窗) */
  closeAllModal: (current?: boolean) => void;
  /** 关闭弹窗(指定弹窗 id 或者当前内容组件所在弹窗) */
  closeModal: (modalId?: ModalItemId) => void;
  /** 修改弹窗属性(指定弹窗 id 或者当前内容组件所在弹窗) */
  setModalProps: (
    modalId?: ModalItemId | Record<string, any>,
    options?: Record<string, any>
  ) => void;
}

/**
 * useModalRender 返回类型
 */
export interface UseModalRenderResult {
  modals: Ref<ModalItem[]>;
  openModal: (option: ModalItem) => ModalItemId;
  closeModal: (modalId?: ModalItemId) => void;
  closeAllModal: () => void;
  removeModal: (modalId?: ModalItemId) => void;
  removeAllModal: () => void;
  updateModalVisible: (modalId?: ModalItemId, visible?: boolean) => void;
  updateModalState: (modalId?: ModalItemId, deactivated?: boolean) => void;
  updateModalProps: (
    modalId?: ModalItemId,
    option?: Record<string, any>
  ) => void;
}
