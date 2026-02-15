/** 弹窗渲染器 */
import type { PropType } from 'vue';
import { defineComponent } from 'vue';
import ItemRender from './components/item-render.vue';
import type { ModalItem, ModalItemId } from './types';

export default defineComponent({
  name: 'EleModalRender',
  props: {
    modals: Array as PropType<ModalItem[]>
  },
  emits: {
    removeItem: (_modalId?: ModalItemId) => true,
    updateItemVisible: (_modalId?: ModalItemId, _visible?: boolean) => true,
    updateItemProps: (_modalId?: ModalItemId, _opt?: Record<string, any>) =>
      true
  },
  setup(props, { emit }) {
    const handleRemoveItem = (modalId?: ModalItemId) => {
      emit('removeItem', modalId);
    };

    const handleUpdateItemVisible = (
      modalId?: ModalItemId,
      visible?: boolean
    ) => {
      emit('updateItemVisible', modalId, visible);
    };

    const handleUpdateItemProps = (modalId?: ModalItemId, opt?: any) => {
      emit('updateItemProps', modalId, opt);
    };

    const renderModal = (item: ModalItem) => {
      return (
        <ItemRender
          key={item.modalId}
          item={item}
          onRemoveItem={handleRemoveItem}
          onUpdateItemVisible={handleUpdateItemVisible}
          onUpdateItemProps={handleUpdateItemProps}
        >
          {{ ...(item.slots || {}) }}
        </ItemRender>
      );
    };
    return () => (props.modals || []).map((item) => renderModal(item));
  }
});
