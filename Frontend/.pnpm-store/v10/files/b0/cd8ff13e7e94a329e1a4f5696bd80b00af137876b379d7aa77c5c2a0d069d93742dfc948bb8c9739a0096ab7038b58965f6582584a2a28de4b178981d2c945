<script>
import theme from "#build/ui/slideover";
</script>

<script setup>
import { computed, toRef } from "vue";
import { DialogRoot, DialogTrigger, DialogPortal, DialogOverlay, DialogContent, DialogTitle, DialogDescription, DialogClose, VisuallyHidden, useForwardPropsEmits } from "reka-ui";
import { reactivePick } from "@vueuse/core";
import { useAppConfig } from "#imports";
import { useLocale } from "../composables/useLocale";
import { usePortal } from "../composables/usePortal";
import { tv } from "../utils/tv";
import UButton from "./Button.vue";
const props = defineProps({
  title: { type: String, required: false },
  description: { type: String, required: false },
  content: { type: Object, required: false },
  overlay: { type: Boolean, required: false, default: true },
  transition: { type: Boolean, required: false, default: true },
  side: { type: null, required: false, default: "right" },
  portal: { type: [Boolean, String], required: false, skipCheck: true, default: true },
  close: { type: [Boolean, Object], required: false, default: true },
  closeIcon: { type: String, required: false },
  dismissible: { type: Boolean, required: false, default: true },
  class: { type: null, required: false },
  ui: { type: null, required: false },
  open: { type: Boolean, required: false },
  defaultOpen: { type: Boolean, required: false },
  modal: { type: Boolean, required: false, default: true }
});
const emits = defineEmits(["after:leave", "after:enter", "close:prevent", "update:open"]);
const slots = defineSlots();
const { t } = useLocale();
const appConfig = useAppConfig();
const rootProps = useForwardPropsEmits(reactivePick(props, "open", "defaultOpen", "modal"), emits);
const portalProps = usePortal(toRef(() => props.portal));
const contentProps = toRef(() => props.content);
const contentEvents = computed(() => {
  const defaultEvents = {
    closeAutoFocus: (e) => e.preventDefault()
  };
  if (!props.dismissible) {
    const events = ["pointerDownOutside", "interactOutside", "escapeKeyDown", "closeAutoFocus"];
    return events.reduce((acc, curr) => {
      acc[curr] = (e) => {
        e.preventDefault();
        emits("close:prevent");
      };
      return acc;
    }, {});
  }
  return defaultEvents;
});
const ui = computed(() => tv({ extend: tv(theme), ...appConfig.ui?.slideover || {} })({
  transition: props.transition,
  side: props.side
}));
</script>

<template>
  <DialogRoot v-slot="{ open }" v-bind="rootProps">
    <DialogTrigger v-if="!!slots.default" as-child :class="props.class">
      <slot :open="open" />
    </DialogTrigger>

    <DialogPortal v-bind="portalProps">
      <DialogOverlay v-if="overlay" :class="ui.overlay({ class: props.ui?.overlay })" />

      <DialogContent
        :data-side="side"
        :class="ui.content({ class: [!slots.default && props.class, props.ui?.content] })"
        v-bind="contentProps"
        @after-enter="emits('after:enter')"
        @after-leave="emits('after:leave')"
        v-on="contentEvents"
      >
        <VisuallyHidden v-if="!!slots.content && (title || !!slots.title || (description || !!slots.description))">
          <DialogTitle v-if="title || !!slots.title">
            <slot name="title">
              {{ title }}
            </slot>
          </DialogTitle>

          <DialogDescription v-if="description || !!slots.description">
            <slot name="description">
              {{ description }}
            </slot>
          </DialogDescription>
        </VisuallyHidden>

        <slot name="content">
          <div v-if="!!slots.header || (title || !!slots.title) || (description || !!slots.description) || (close || !!slots.close)" :class="ui.header({ class: props.ui?.header })">
            <slot name="header">
              <div :class="ui.wrapper({ class: props.ui?.wrapper })">
                <DialogTitle v-if="title || !!slots.title" :class="ui.title({ class: props.ui?.title })">
                  <slot name="title">
                    {{ title }}
                  </slot>
                </DialogTitle>

                <DialogDescription v-if="description || !!slots.description" :class="ui.description({ class: props.ui?.description })">
                  <slot name="description">
                    {{ description }}
                  </slot>
                </DialogDescription>
              </div>

              <DialogClose v-if="close || !!slots.close" as-child>
                <slot name="close" :ui="ui">
                  <UButton
                    v-if="close"
                    :icon="closeIcon || appConfig.ui.icons.close"
                    size="md"
                    color="neutral"
                    variant="ghost"
                    :aria-label="t('slideover.close')"
                    v-bind="typeof close === 'object' ? close : {}"
                    :class="ui.close({ class: props.ui?.close })"
                  />
                </slot>
              </DialogClose>
            </slot>
          </div>

          <div :class="ui.body({ class: props.ui?.body })">
            <slot name="body" />
          </div>

          <div v-if="!!slots.footer" :class="ui.footer({ class: props.ui?.footer })">
            <slot name="footer" />
          </div>
        </slot>
      </DialogContent>
    </DialogPortal>
  </DialogRoot>
</template>
