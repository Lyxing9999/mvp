// https://nuxt.com/docs/api/configuration/nuxt-config
import tailwindcss from "@tailwindcss/vite";
export default defineNuxtConfig({
  modules: ["@element-plus/nuxt"],
  css: ["@/styles/css/main.css"],
  vite: {
    plugins: [tailwindcss()],
    define: {
      __DEV__: false,
    },
  },
});
