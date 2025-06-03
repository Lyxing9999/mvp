// https://nuxt.com/docs/api/configuration/nuxt-config
import tailwindcss from "@tailwindcss/vite";
export default defineNuxtConfig({
  compatibilityDate: "2025-05-29",
  modules: ["@element-plus/nuxt", "@pinia/nuxt"],
  devtools: false,
  css: ["@/styles/css/main.css"],
  vite: {
    plugins: [tailwindcss()],
    define: {
      __DEV__: true,
    },
  },
  ssr: false,
  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE,
    },
  },
  router: {
    middleware: ["auth"],
  },
});
