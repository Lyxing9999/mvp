import type { ComponentPublicInstance } from 'vue';
import type { PinInputRootEmits, PinInputRootProps } from 'reka-ui';
import type { AppConfig } from '@nuxt/schema';
import theme from '#build/ui/pin-input';
import type { ComponentConfig } from '../types/utils';
type PinInput = ComponentConfig<typeof theme, AppConfig, 'pinInput'>;
export interface PinInputProps extends Pick<PinInputRootProps, 'defaultValue' | 'disabled' | 'id' | 'mask' | 'modelValue' | 'name' | 'otp' | 'placeholder' | 'required' | 'type'> {
    /**
     * The element or component this component should render as.
     * @defaultValue 'div'
     */
    as?: any;
    /**
     * @defaultValue 'primary'
     */
    color?: PinInput['variants']['color'];
    /**
     * @defaultValue 'outline'
     */
    variant?: PinInput['variants']['variant'];
    /**
     * @defaultValue 'md'
     */
    size?: PinInput['variants']['size'];
    /**
     * The number of input fields.
     * @defaultValue 5
     */
    length?: number | string;
    autofocus?: boolean;
    autofocusDelay?: number;
    highlight?: boolean;
    class?: any;
    ui?: PinInput['slots'];
}
export type PinInputEmits = PinInputRootEmits & {
    change: [payload: Event];
    blur: [payload: Event];
};
declare const _default: import("vue").DefineComponent<PinInputProps, {
    inputsRef: import("vue").Ref<ComponentPublicInstance[], ComponentPublicInstance[]>;
}, {}, {}, {}, import("vue").ComponentOptionsMixin, import("vue").ComponentOptionsMixin, {
    blur: (payload: Event) => any;
    complete: (value: string[]) => any;
    change: (payload: Event) => any;
    "update:modelValue": (value: string[]) => any;
}, string, import("vue").PublicProps, Readonly<PinInputProps> & Readonly<{
    onBlur?: ((payload: Event) => any) | undefined;
    onComplete?: ((value: string[]) => any) | undefined;
    onChange?: ((payload: Event) => any) | undefined;
    "onUpdate:modelValue"?: ((value: string[]) => any) | undefined;
}>, {
    length: number | string;
    type: "text" | "number";
    autofocusDelay: number;
}, {}, {}, {}, string, import("vue").ComponentProvideOptions, false, {}, any>;
export default _default;
