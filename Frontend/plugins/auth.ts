import { useAuthStore } from "~/stores/authStore";
import type { Pinia } from "pinia";
import type { NuxtApp } from "#app";

export default defineNuxtPlugin((nuxtApp: NuxtApp) => {
  const pinia = nuxtApp.$pinia as Pinia;
  const authStore = useAuthStore(pinia);
  return {
    provide: {
      auth: authStore,
    },
  };
});
