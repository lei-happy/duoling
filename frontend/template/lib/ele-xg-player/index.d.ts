import { PropType } from 'vue';
import { default as Player, IPlayerOptions } from 'xgplayer';

declare const _default: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    config: {
        type: PropType<IPlayerOptions>;
        required: true;
    };
}>, {
    player: null;
}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    player: (_player: Player | null) => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    config: {
        type: PropType<IPlayerOptions>;
        required: true;
    };
}>> & Readonly<{
    onPlayer?: ((_player: Player | null) => any) | undefined;
}>, {}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
export default _default;
