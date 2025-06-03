import { defineStore } from "pinia";
import { ref, computed } from "vue";
import type { AuthUser } from "~/types/auth";

export const useAuthStore = defineStore("auth", () => {
  const token = useCookie<string | null>("token");
  const user = ref<AuthUser | null>(null);

  const login = (newToken: string, userInfo: AuthUser) => {
    token.value = newToken;
    user.value = userInfo;
    localStorage.setItem("token", newToken);
    localStorage.setItem("user", JSON.stringify(userInfo));
    console.log(token.value, user.value);
  };
  const logout = () => {
    token.value = null;
    user.value = null;
    localStorage.removeItem("token");
    localStorage.removeItem("user");
  };
  const isAuthenticated = computed(() => !!token.value);
  function initAuth() {
    if (process.client) {
      const savedToken = localStorage.getItem("token");
      const savedUser = localStorage.getItem("user");
      if (savedToken && savedUser) {
        token.value = savedToken;
        user.value = JSON.parse(savedUser);
      }
    }
  }
  onMounted(() => {
    initAuth();
  });

  return { token, user, login, logout, isAuthenticated, initAuth };
});
