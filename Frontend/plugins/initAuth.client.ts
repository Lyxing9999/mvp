// ~/plugins/initAuth.client.ts
import { useAuthStore } from "~/stores/authStore";
export default defineNuxtPlugin(() => {
  const auth = useAuthStore();
  auth.initAuth();
});
