import {
  defineComponent,
  inject,
  onBeforeUnmount,
  onActivated,
  onDeactivated
} from 'vue';
import ItemRender from './components/item-render.vue';
import { MODAL_UTIL_KEY, MODAL_HOLDER_KEY, useModalRender } from './util';
import type { ModalItem, ModalItemId, UseModalMethods } from './types';

export function useModal() {
  /** 是否在当前组件中渲染 */
  let isHolderRender = false;

  /** 弹窗渲染器容器 */
  const renderProvider = inject(MODAL_UTIL_KEY, null);

  /** 直接父级的弹窗渲染器 */
  const holderProvider = inject(MODAL_HOLDER_KEY, null);

  /** 在当前组件渲染时的操作方法 */
  const {
    modals,
    openModal,
    closeModal,
    closeAllModal,
    removeModal,
    updateModalVisible,
    updateModalProps
  } = useModalRender();

  /** 当前组件中打开的弹窗 */
  const modalIds: ModalItemId[] = [];

  /** 不在销毁时关闭的弹窗 */
  const aliveModalIds: ModalItemId[] = [];

  /** 在当前组件渲染时的弹窗容器 */
  const ModalHolder = defineComponent({
    name: 'ModalHolder',
    setup() {
      isHolderRender = true;
      const renderModal = (item: ModalItem) => {
        return (
          <ItemRender
            key={item.modalId}
            item={item}
            onRemoveItem={removeModal}
            onUpdateItemVisible={updateModalVisible}
            onUpdateItemProps={updateModalProps}
          >
            {{ ...(item.slots || {}) }}
          </ItemRender>
        );
      };
      return () => modals.value.map((item) => renderModal(item));
    }
  });

  /** 弹窗操作方法 */
  const methods: UseModalMethods = {
    openModal: (option: ModalItem) => {
      if (isHolderRender || !renderProvider) {
        const modalId = openModal(option);
        if (modalId != null) {
          modalIds.push(modalId);
          if (option.keepAlive) {
            aliveModalIds.push(modalId);
          }
        }
        return modalId;
      }
      const modalId = renderProvider.openModal(option);
      if (modalId != null) {
        modalIds.push(modalId);
        if (option.keepAlive) {
          aliveModalIds.push(modalId);
        }
      }
      return modalId;
    },
    closeAllModal: (current?: boolean) => {
      if (isHolderRender || !renderProvider) {
        closeAllModal();
        return;
      }
      if (!current) {
        renderProvider.closeAllModal();
        return;
      }
      // 只关闭当前组件中打开的弹窗
      modalIds.forEach((modalId) => {
        if (renderProvider) {
          renderProvider.closeModal(modalId);
        }
      });
    },
    closeModal: (modalId?: ModalItemId) => {
      if (modalId == null) {
        // 内容组件关闭自己当前的弹窗
        holderProvider && holderProvider.closeModal();
        return;
      }
      if (isHolderRender || !renderProvider) {
        closeModal(modalId);
        return;
      }
      renderProvider.closeModal(modalId);
    },
    setModalProps: (
      modalId?: ModalItemId | Record<string, any>,
      options?: Record<string, any>
    ) => {
      if (modalId == null || typeof modalId === 'object') {
        if (modalId != null && holderProvider) {
          holderProvider.setModalProps(modalId);
        }
        return;
      }
      if (isHolderRender || !renderProvider) {
        updateModalProps(modalId, options);
        return;
      }
      renderProvider.updateModalProps(modalId, options);
    }
  };

  /** 组件销毁时关闭打开的弹窗 */
  onBeforeUnmount(() => {
    modalIds.forEach((modalId) => {
      if (!aliveModalIds.includes(modalId)) {
        methods.closeModal(modalId);
      }
    });
  });

  /** 更新弹窗失活状态 */
  onDeactivated(() => {
    if (isHolderRender) {
      return;
    }
    modalIds.forEach((modalId) => {
      if (!renderProvider || aliveModalIds.includes(modalId)) {
        return;
      }
      renderProvider.updateModalState(modalId, true);
    });
  });

  onActivated(() => {
    if (isHolderRender) {
      return;
    }
    modalIds.forEach((modalId) => {
      if (!renderProvider) {
        return;
      }
      renderProvider.updateModalState(modalId, false);
    });
  });

  return {
    ...methods,
    ModalHolder,
    modalProps: holderProvider?.modalProps
  };
}
