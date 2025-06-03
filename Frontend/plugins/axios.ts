// ~/plugins/api.ts
import axios from "axios";
import { useCookie, useRuntimeConfig, navigateTo, useRoute } from "#app";

export default defineNuxtPlugin(() => {
  const route = useRoute();

  const config = useRuntimeConfig();

  const api = axios.create({
    baseURL: config.public.apiBase,
    timeout: 10000,
  });

  // Attach token from localStorage
  api.interceptors.request.use((config) => {
    const token = localStorage.getItem("token");
    console.log(token);
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  });

  // Handle 401 (unauthenticated)
  api.interceptors.response.use(
    (response) => response,
    (error) => {
      if (error.response?.status === 401 && route.path !== "/auth/login") {
        localStorage.removeItem("token");
        navigateTo("/auth/login");
      }
      return Promise.reject(error);
    }
  );

  return {
    provide: {
      api,
    },
  };
});
