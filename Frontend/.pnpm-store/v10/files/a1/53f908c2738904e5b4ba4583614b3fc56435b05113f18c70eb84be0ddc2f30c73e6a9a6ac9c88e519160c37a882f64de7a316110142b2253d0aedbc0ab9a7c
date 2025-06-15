import type { FormSchema, FormError, FormInputEvents, FormErrorEvent, FormSubmitEvent, Form, InferInput, InferOutput } from '../types/form';
export interface FormProps<S extends FormSchema> {
    id?: string | number;
    /** Schema to validate the form state. Supports Standard Schema objects, Yup, Joi, and Superstructs. */
    schema?: S;
    /** An object representing the current state of the form. */
    state: Partial<InferInput<S>>;
    /**
     * Custom validation function to validate the form state.
     * @param state - The current state of the form.
     * @returns A promise that resolves to an array of FormError objects, or an array of FormError objects directly.
     */
    validate?: (state: Partial<InferInput<S>>) => Promise<FormError[]> | FormError[];
    /**
     * The list of input events that trigger the form validation.
     * @defaultValue `['blur', 'change', 'input']`
     */
    validateOn?: FormInputEvents[];
    /** Disable all inputs inside the form. */
    disabled?: boolean;
    /**
     * Delay in milliseconds before validating the form on input events.
     * @defaultValue `300`
     */
    validateOnInputDelay?: number;
    /**
     * If true, schema transformations will be applied to the state on submit.
     * @defaultValue `true`
     */
    transform?: boolean;
    /**
     * If true, this form will attach to its parent Form (if any) and validate at the same time.
     * @defaultValue `true`
     */
    attach?: boolean;
    /**
     * When `true`, all form elements will be disabled on `@submit` event.
     * This will cause any focused input elements to lose their focus state.
     * @defaultValue `true`
     */
    loadingAuto?: boolean;
    class?: any;
    onSubmit?: ((event: FormSubmitEvent<InferOutput<S>>) => void | Promise<void>) | (() => void | Promise<void>);
}
export interface FormEmits<S extends FormSchema> {
    (e: 'submit', payload: FormSubmitEvent<InferOutput<S>>): void;
    (e: 'error', payload: FormErrorEvent): void;
}
export interface FormSlots {
    default(props?: {
        errors: FormError[];
    }): any;
}
declare const _default: <S extends FormSchema>(__VLS_props: NonNullable<Awaited<typeof __VLS_setup>>["props"], __VLS_ctx?: __VLS_PrettifyLocal<Pick<NonNullable<Awaited<typeof __VLS_setup>>, "attrs" | "emit" | "slots">>, __VLS_expose?: NonNullable<Awaited<typeof __VLS_setup>>["expose"], __VLS_setup?: Promise<{
    props: __VLS_PrettifyLocal<Pick<Partial<{}> & Omit<{
        readonly onError?: ((payload: FormErrorEvent) => any) | undefined;
        readonly onSubmit?: ((payload: FormSubmitEvent<InferOutput<S>>) => any) | undefined;
    } & import("vue").VNodeProps & import("vue").AllowedComponentProps & import("vue").ComponentCustomProps, never>, "onError" | "onSubmit"> & FormProps<S> & Partial<{}>> & import("vue").PublicProps;
    expose(exposed: import("vue").ShallowUnwrapRef<Form<InferInput<S>>>): void;
    attrs: any;
    slots: FormSlots;
    emit: FormEmits<S>;
}>) => import("vue").VNode & {
    __ctx?: Awaited<typeof __VLS_setup>;
};
export default _default;
type __VLS_PrettifyLocal<T> = {
    [K in keyof T]: T[K];
} & {};
